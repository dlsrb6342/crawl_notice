import logging, time
import pymysql, requests, json
from datetime import datetime
from elasticsearch import Elasticsearch
from fb import get_facebook_feed
from skku import get_skku_notice
from cs import get_cs_notice
from icc import get_icc_notice
from shb import get_shb_notice
from extract_marker import extract_marker


with open('config.json') as json_data_file:
    config = json.load(json_data_file)
mysql = config['mysql']

function_dict = { 
  'skku': get_skku_notice, 'cs' : get_cs_notice, 
  'icc': get_icc_notice, 'shb': get_shb_notice 
}


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
            curs.execute('SELECT * FROM page')
            pages = curs.fetchall()
            curs.execute('SELECT max(id) FROM notice')
            row = curs.fetchone()
            max_id = 1 if row['max(id)'] is None else row['max(id)'] + 1
            insert_sql = { 
                'F': 'INSERT INTO notice (title, contents, p_id, time, m_id, ' + \
                  'link, img_src, ntype) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                'H': 'INSERT INTO notice (title, contents, c_id, time, m_id, ' + \
                  'link, img_src, ntype) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
            }
            update_num_sql = 'UPDATE notice_category SET last_num = %s WHERE id = %s'
            update_time_sql = 'UPDATE page SET time = %s WHERE id = %s'
            result = []

            for page in pages:
                _id, page_id, _time, _type = page['id'], page['page_id'], page['time'], page['type']
                fb_result = get_facebook_feed(_id, page_id, _time, logger, _type)

                if len(fb_result) != 0:
                    curs.execute(update_time_sql, (fb_result[len(fb_result)-1]['time'], _id))
                    result += fb_result
                
            for row in rows:
                _id, last_num, name = row['id'], row['last_num'], row['name']
                rows = curs.fetchall()
                
                hp_result = function_dict[name](_id, last_num, logger)
                
                if len(hp_result) != 0:
                    curs.execute(update_num_sql, (hp_result[0]['last_num'], _id))
                    result += hp_result

            dt = datetime.now()

            for r in result:
                marker_id = extract_marker(r['contents'], r['type'])
                curs.execute(insert_sql[r['ntype']], (r['title'], r['contents'], r['id'], dt, marker_id, r['link'], r['img_src'], r['ntype']))
                curs.execute('SELECT * FROM location WHERE id = %s', (location_id))
                location = curs.fetchone()
                doc = {
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
