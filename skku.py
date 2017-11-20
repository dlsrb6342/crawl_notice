import requests
from bs4 import BeautifulSoup
from datetime import datetime


def get_skku_notice(last_num, logger):
    result = []
    num_list = get_notice_num_list(last_num)[::-1]
    for i in num_list:
        URL = "http://www.skku.edu/new_home/campus/skk_comm/notice_view.jsp?bCode=0&page=1&boardNum="
        URL = URL + str(i) + "&virtualNum=0&skey=BOARD_SUBJECT&keyword=&bName=board_news&bCode=0"
        response = requests.get(URL)
        if response.status_code != requests.codes.ok:
            break
        try:
            soup = BeautifulSoup(response.text, 'html5lib')
            title = soup.td.extract().text
            soup.td.extract()
            soup.td.extract()
            soup.td.extract()
            contents = soup.find(id="contents").div.text.strip()
            img_src = ""
            for img in soup.find(id="contents").div.findAll('img'):
                img_src = img_src + img['src'] + '#'
            img_src = img_src[:len(img_src)-1]
            if contents == "":
                src_list = img_src.split("#")
                if len(src_list) == 0:
                    URL = "http://www.skku.edu/new_home/campus/skk_comm/news_list.jsp" 
                    img_src = ""
                else:
                    for src in src_list:
                        response = requests.get(src)
                        if response.status_code != requests.codes.ok:
                            URL = "http://www.skku.edu/new_home/campus/skk_comm/news_list.jsp" 
                            img_src = ""
            notice = {
                'title': title,
                'last_num': i,
                'contents': contents,
                'link': URL,
                'img_src': img_src
            }
            result.append(notice)
        except:
            break

    logger.info('get '+ str(len(result)) + ' new skku notice')
    return result


def get_notice_num_list(last_num): 
    page = 1
    num_list = []
    index_list = [ 5 * x for x in range(0, 10) ]
    while True:
        URL = 'http://www.skku.edu/new_home/campus/skk_comm/notice_list.jsp?bName=board_news&bCode=0&page=' + str(page)
        response = requests.get(URL)
        if response.status_code != requests.codes.ok:
            return num_list
        try:
            soup = BeautifulSoup(response.text, 'html5lib')
            notice_list = soup.findAll('td')
            for i in index_list:
                if notice_list[i].text == str(last_num):
                    return num_list
                num_list.append(notice_list[i].text)
            page += 1
        except:
            return num_list
