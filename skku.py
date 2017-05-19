import requests
from bs4 import BeautifulSoup
from datetime import datetime


def get_skku_notice(last_num, logger):
    result = []
    
    while True:
        find_num = last_num + 1
        URL = "http://www.skku.edu/new_home/campus/skk_comm/notice_view.jsp?bCode=0&page=1&boardNum="
        URL = URL + str(find_num) + "&virtualNum=0&skey=BOARD_SUBJECT&keyword=&bName=board_news&bCode=0"
        response = requests.get(URL)
        if response.status_code != requests.codes.ok:
            break
        try:
            soup = BeautifulSoup(response.text, 'html5lib')
            title = soup.td.extract().text
            soup.td.extract()
            last_num = int(soup.td.extract().text)
            soup.td.extract()
            soup.td.extract()
            contents = soup.find(id="contents").div.text.strip()
            img_src = ""
            for img in soup.find(id="contents").div.findAll('img'):
                img_src = img_src + img['src'] + '#'
            img_src = img_src[:len(img_src)-1]
            notice = {
                'title': title,
                'last_num': last_num,
                'contents': contents,
                'link': URL,
                'img_src': img_src
            }
            result.append(notice)
        except:
            break

    logger.info('get '+ str(len(result)) + ' new skku notice')
    return result
