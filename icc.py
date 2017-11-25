import requests
from bs4 import BeautifulSoup


def get_icc_notice(_id, last_num, logger):
    result = []
    URL_list = ["http://icc.skku.ac.kr/icc_new/board_view_square?boardName=board_notice&listPage=1&postSeq=", 
                "http://icc.skku.ac.kr/icc_new/board_view_square?boardName=board_news&listPage=1&postSeq=", 
                "http://icc.skku.ac.kr/icc_new/board_view_square?boardName=board_seminar&listPage=1&postSeq=",
                "http://icc.skku.ac.kr/icc_new/board_view_square?boardName=board_recruit&listPage=1&postSeq="
               ]
    postfix = "&menu=board_list_square"
    count = 0
    last_num = last_num + 1
    while True:
        URL = URL_list[count] + str(last_num) + postfix
        response = requests.get(URL)
        response.encoding = 'UTF-8'
        soup = BeautifulSoup(response.text, 'html5lib')
        table = soup.table
        if table is None:
            count = count + 1
            if count == 4:
                break
            continue
        
        title = table.find("td", id="subject").text
        contents = table.find("td", id="content").text
        link = URL
        img_src = ""
        for img in table.findAll('img'):
            img_src = img_src + "http://icc.skku.ac.kr/" + img['src'] + "#"
        img_src = img_src[:len(img_src)-1]

        notice = {
            'id': _id,
            'title': title,
            'last_num': last_num,
            'contents': contents,
            'link': link,
            'img_src': img_src,
            'type': 'Y',
            'ntype': 'H'
        }
        result.append(notice)
        count = 0  
        last_num = last_num + 1

    logger.info('get '+ str(len(result)) + ' new icc notice') 
    return result
