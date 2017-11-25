from konlpy.tag import Mecab
import pymysql, json


with open('config.json') as json_data_file:
    config = json.load(json_data_file)
mysql = config['mysql']


def extract_marker(contents, _type):
    conn = pymysql.connect(host=mysql['host'], port=mysql['port'],
        user=mysql['user'], password=mysql['password'], 
        db=mysql['db'], charset=mysql['charset'])
    mecab = Mecab()
    if _type == 'MY':
        sql = 'SELECT id, name, type, detail FROM marker WHERE marker_category_id = 11 OR marker_category_id = 12'
    else:
        c_id = 11 if _type == 'Y' else 12
        sql = 'SELECT id, name, type, detail FROM marker WHERE marker_category_id = ' + str(c_id)

    try:
        with conn.cursor() as curs:
            curs.execute(sql)
            rows = curs.fetchall()

            marker_set = set(map(lambda r: r[1], rows))
            nouns_list = mecab.nouns(contents)
            nouns_set = set(nouns_list)
            
            extracted_marker = list(marker_set & nouns_set)
            
            if len(extracted_marker) == 0:
                marker_id = 0 
            else:
                if len(extracted_marker) == 1:
                    marker_name = extracted_marker[0] 
                else:
                    counts = []
                    for marker in extracted_marker:
                        counts.append(nouns_list.count(marker))
                    marker_name = extracted_marker[counts.index(max(counts))]
                    
                marker = [r for r in rows if r[1] == marker_name][0]
                if marker[2] == "abbreviation":
                    marker_id = int(marker[3])
                else:
                    marker_id = marker[0]

    finally:
        conn.close()
        return marker_id
