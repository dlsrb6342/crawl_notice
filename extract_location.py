from konlpy.tag import Mecab
import pymysql

def extract_location(contents):
    conn = pymysql.connect(host='hostname', 
        user='user', password='password', 
        db='dbname', charset='charset')
    mecab = Mecab()
 
    try:
        with conn.cursor() as curs:
            curs.execute('select id, name, type, detail from location where id < 45')
            rows = curs.fetchall()

            location_set = set(map(lambda r: r[1], rows))
            nouns_list = mecab.nouns(contents)
            nouns_set = set(nouns_list)
            
            extracted_location = list(location_set & nouns_set)
            
            if len(extracted_location) == 0:
                location_id = 0 
            else:
                if len(extracted_location) == 1:
                    location_name = extracted_location[0] 
                else:
                    counts = []
                    for location in extracted_location:
                        counts.append(nouns_list.count(location))
                    location_name = extracted_location[counts.index(max(counts))]
                    
                location = [r for r in rows if r[1] == location_name][0]
                if location[2] == "abbreviation":
                    location_id = int(location[3])
                else:
                    location_id = location[0]

    finally:
        conn.close()
        return location_id
