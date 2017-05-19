import requests, json
from bs4 import BeautifulSoup
from datetime import datetime


def get_cs_notice(last_num, logger):
    result = []
    while True:
        last_num = last_num + 1
        URL = "http://cs.skku.edu/ajax/board/view/notice/" + str(last_num)
        response = requests.post(URL)
        if response.status_code != requests.codes.ok:
            break

        jsonify_response = json.loads(response.text)

        if jsonify_response['result']:
            notice_json = json.loads(response.text)["post"]
            
            soup = BeautifulSoup(notice_json['text'], 'html5lib')
            img_src = ""
            for img in soup.findAll('img'):
                img_src = img_src + "http://cs.skku.edu" + img['src'] + "#"
            img_src = img_src[:len(img_src)-1]
            contents = soup.text
            link = "http://cs.skku.edu/open/notice/view/" + str(notice_json['id'])
            notice = {
                'title': notice_json['title'],
                'last_num': notice_json['id'],
                'contents': contents,
                'link': link,
                'img_src': img_src
            }
            result.append(notice)
        else:
            break
    logger.info('get '+ str(len(result)) + ' new cs notice') 
    return result
