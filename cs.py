import requests, json
from bs4 import BeautifulSoup
from datetime import datetime


def get_cs_notice(_id, last_num, logger):
    result = []
    URL_list = ["http://cs.skku.edu/ajax/board/view/notice/", "http://cs.skku.edu/ajax/board/view/news/", 
            "http://cs.skku.edu/ajax/board/view/seminar/", "http://cs.skku.edu/ajax/board/view/recruit/" ]
    category_list = ["notice", "news", "seminar", "recruit"]
    count = 0
    last_num = last_num + 1
    while True:
        URL = URL_list[count] + str(last_num)
        response = requests.post(URL)
        response.encoding = 'UTF-8'
        if response.status_code != requests.codes.ok:
            count = count + 1
            if count == 4:
                break
            continue

        jsonify_response = json.loads(response.text)

        if jsonify_response['result']:
            notice_json = json.loads(response.text)["post"]
            
            soup = BeautifulSoup(notice_json['text'], 'html5lib')
            img_src = ""
            for img in soup.findAll('img'):
                img_src = img_src + "http://cs.skku.edu" + img['src'] + "#"
            img_src = img_src[:len(img_src)-1]
            contents = soup.text
            link = "http://cs.skku.edu/open/" + category_list[count] + "/view/" + str(notice_json['id'])
            notice = {
                'id': _id,
                'title': notice_json['title'],
                'last_num': notice_json['id'],
                'contents': contents,
                'link': link,
                'img_src': img_src,
                'type': 'Y',
                'ntype': 'H'
            }
            result.append(notice)
            count = 0  
            last_num = last_num + 1
        else:
            break
    logger.info('get '+ str(len(result)) + ' new cs notice') 
    return result
