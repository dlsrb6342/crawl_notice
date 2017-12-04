import logging, time
import pymysql, requests, json
from datetime import datetime
from elasticsearch import Elasticsearch
from fb import get_facebook_feed
from skku import get_skku_notice
from cs import get_cs_notice
from icc import get_icc_notice
from common import get_common_notice
from extract_marker import extract_marker


with open('config.json') as json_data_file:
    config = json.load(json_data_file)
mysql = config['mysql']

function_dict = { 
  'skku': get_skku_notice, 'cs' : get_cs_notice, 
  'icc': get_icc_notice, 'shb': get_common_notice,
  'cscience': get_common_notice, 'biotech': get_common_notice,
  'ecostat': get_common_notice, 'scos': get_common_notice,
  'liberalarts': get_common_notice, 'law': get_common_notice,
  'sscience': get_common_notice, 'coe': get_common_notice,
  'art': get_common_notice
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
            curs.execute('SELECT * FROM category') 
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
            update_num_sql = 'UPDATE category SET last_num = %s WHERE id = %s'
            update_time_sql = 'UPDATE page SET time = %s WHERE id = %s'
            result = []

            for page in pages:
                fb_result = get_facebook_feed(page, logger)

                if len(fb_result) != 0:
                    curs.execute(update_time_sql, (fb_result[0]['time'], page['id']))
                    result += fb_result
                
            for row in rows:
                rows = curs.fetchall()
                
                hp_result = function_dict[row['name']](row, logger)
                
                if len(hp_result) != 0:
                    curs.execute(update_num_sql, (hp_result[len(hp_result) - 1]['last_num'], row['id']))
                    result += hp_result

            dt = datetime.now()

            for r in result:
                marker_id = extract_marker(r['contents'], r['type'])
                curs.execute(insert_sql[r['ntype']], (r['title'], r['contents'], r['id'], dt, marker_id, r['link'], r['img_src'], r['ntype']))
                curs.execute('SELECT * FROM marker WHERE id = %s', (marker_id))
                marker = curs.fetchone()
                doc = {
                    "contents": r['contents'],
                    "title": r['title'],
                    "marker": marker,
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
