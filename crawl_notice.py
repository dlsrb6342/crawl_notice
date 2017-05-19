import logging
import logging.handlers
import pymysql, requests, json
from datetime import datetime
from fb import get_facebook_feed
from skku import get_skku_notice
from cs import get_cs_notice


def crawl_notice():
    conn = pymysql.connect(host='hostname', 
        user='user', password='password', 
        db='dbname', charset='charset')
    
    logger = logging.getLogger("crumbs") 
    logger.setLevel(logging.DEBUG) 
    formatter = logging.Formatter('%(asctime)s > %(message)s')
    fileHandler = logging.FileHandler('./log/crawl.log')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    logger.info('Start Periodic Task')

    try:
        with conn.cursor() as curs:
            curs.execute('select * from category') 
            rows = curs.fetchall()
            insert_sql = 'INSERT INTO notice (title, contents, c_id, time, l_id, link, img_src) values (%s, %s, %s, %s, %s, %s, %s)'
            update_sql = 'UPDATE category set last_num = %s where id = %s'

            logger.info(rows)
            for r in rows:
                c_id, last_num, name, page_id  = r 
                if name == 'cs':
                    result = get_cs_notice(last_num, logger)
                    c_id = 1
                elif name == 'skku':
                    result = get_skku_notice(last_num, logger)
                    c_id = 2
                else:
                    result = get_facebook_feed(page_id, last_num, logger)
                    if page_id == 1046976762077651:
                        c_id = 3
                    else:
                        c_id = 4
        
                for r in result:
                    curs.execute(insert_sql, (r['title'], r['contents'], c_id, datetime.now(), 0, r['link'], r['img_src']))
                if len(result) != 0:
                    if c_id == 3 or c_id == 4:
                        curs.execute(update_sql, (result[0]['last_num'], c_id))
                    else:
                        curs.execute(update_sql, (result[len(result)-1]['last_num'], c_id))

                conn.commit()

    finally:
        conn.close()
