import logging, time
import pymysql, requests, json
from datetime import datetime
from elasticsearch import Elasticsearch
from fb import get_facebook_feed
from skku import get_skku_notice
from cs import get_cs_notice
from icc import get_icc_notice
from extract_marker import extract_marker


with open('config.json') as json_data_file:
    config = json.load(json_data_file)
mysql = config['mysql']


def crawl_notice():
    conn = pymysql.connect(host=mysql['host'], port=mysql['port'],
        user=mysql['user'], password=mysql['password'], 
        db=mysql['db'], charset=mysql['charset'],
        cursorclass=pymysql.cursors.DictCursor)
    
    logger = logging.getLogger("crumbs") 
    logger.setLevel(logging.DEBUG) 
    logger.info('Start Periodic Task')

    try:
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM notice_category') 
            rows = curs.fetchall()
            curs.execute('SELECT max(id) FROM notice')
            row = curs.fetchone()
            max_id = 1 if row['max(id)'] is None else row['max(id)'] + 1
            insert_sql = 'INSERT INTO notice (title, contents, c_id, time, l_id,' + \
                'link, img_src) VALUES (%s, %s, %s, %s, %s, %s, %s)'
            update_num_sql = 'UPDATE notice_category SET last_num = %s WHERE id = %s'
            update_time_sql = 'UPDATE notice_category SET time = %s WHERE id = %s'

            for row in rows:
                _id, last_num, name = row['id'], row['last_num'], row['name']
                page_id, _time, _type = row['page_id'], row['time'], row['type']
                if name == 'cs':
                    hp_result = get_cs_notice(last_num, logger)
                    fb_result = get_facebook_feed(page_id, _time, logger)
                elif name == 'skku':
                    hp_result = get_skku_notice(last_num, logger)
                    fb_result = get_facebook_feed(page_id, _time, logger)
                elif name == 'icc':
                    hp_result = get_icc_notice(last_num, logger)
                    fb_result = get_facebook_feed(page_id, _time, logger)
                
                if len(hp_result) != 0:
                    curs.execute(update_num_sql, (hp_result[0]['last_num'], _id))
                if len(fb_result) != 0:
                    curs.execute(update_time_sql, (fb_result[len(fb_result)-1]['time'], _id))

                result = hp_result + fb_result 
                for r in result:
                    location_id = extract_marker(r['contents'], _type)
                    dt = datetime.now()
                    curs.execute(insert_sql, (r['title'], r['contents'], _id, dt, location_id, r['link'], r['img_src']))
                    curs.execute('SELECT * FROM location WHERE id = %s', (location_id))
                    location = curs.fetchone()
                    doc = {
                        "category": row,
                        "contents": r['contents'],
                        "title": r['title'],
                        "location": location,
                        "id": max_id,
                        "img_src": r['img_src'],
                        "link": r['link'],
                        "time": int(time.mktime(dt.timetuple()) * 1000)
                    } 
                    es = Elasticsearch('localhost:9200')
                    res = es.index(index="eunjeon", doc_type='notices', id=max_id, body=doc)
                    max_id = max_id + 1
                conn.commit()

    finally:
        del logger
        conn.close()
