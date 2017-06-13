import logging, time
import pymysql, requests, json
from datetime import datetime
from elasticsearch import Elasticsearch
from fb import get_facebook_feed
from skku import get_skku_notice
from cs import get_cs_notice
from icc import get_icc_notice
from extract_location import extract_location


def crawl_notice():
    conn = pymysql.connect(host='hostname', 
        user='user', password='password', 
        db='dbname', charset='charset',
        cursorclass=pymysql.cursors.DictCursor)
    
    logger = logging.getLogger("crumbs") 
    logger.setLevel(logging.DEBUG) 
    logger.info('Start Periodic Task')

    try:
        with conn.cursor() as curs:
            curs.execute('select * from notice_category') 
            rows = curs.fetchall()
            curs.execute('select max(id) from notice')
            max_id = curs.fetchone()['max(id)'] + 1
            insert_sql = 'INSERT INTO notice (title, contents, c_id, time, l_id, link, img_src) values (%s, %s, %s, %s, %s, %s, %s)'
            update_sql = 'UPDATE notice_category set last_num = %s where id = %s'

            for row in rows:
                id, last_num, name, page_id  = row['id'], row['last_num'], row['name'], row['page_id']
                if name == 'cs':
                    if page_id == 0:
                        result = get_cs_notice(last_num, logger)
                    else:
                        result = get_facebook_feed(page_id, last_num, logger)
                elif name == 'skku':
                    if page_id == 0:
                        result = get_skku_notice(last_num, logger)
                    else:
                        result = get_facebook_feed(page_id, last_num, logger)
                elif name == 'icc':
                    if page_id == 0:
                        result = get_icc_notice(last_num, logger)
                    else:
                        result = get_facebook_feed(page_id, last_num, logger)
                
                if len(result) != 0:
                    if page_id != 0:
                        curs.execute(update_sql, (result[0]['last_num'], id))
                    else:
                        curs.execute(update_sql, (result[len(result)-1]['last_num'], id))
       
                for r in result:
                    location_id = extract_location(r['contents'])
                    dt = datetime.now()
                    curs.execute(insert_sql, (r['title'], r['contents'], id, dt, location_id, r['link'], r['img_src']))
                    curs.execute('select * from location where id = %s', (location_id))
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
