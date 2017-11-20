import requests
from bs4 import BeautifulSoup


def get_shb_notice(last_num, logger):
    result = []
    link_list = get_notice_link_list(last_num)[::-1]
    for link, i in link_list:
        response = requests.get(link)
        if response.status_code != requests.codes.ok:
            break
        try:
            soup = BeautifulSoup(response.text, 'html5lib')
            title = soup.title.text
            contents = soup.table.find(id="article_text").text.strip()
            img_src = ""
            for img in soup.table.find(id="article_text").findAll('img'):
                img_src = img_src + img['src'] + '#'
            img_src = img_src[:len(img_src)-1]
            notice = {
                'title': title,
                'last_num': i,
                'contents': contents,
                'link': link,
                'img_src': img_src
            }
            result.append(notice)
        except:
            break
    
    logger.info('get ' + str(len(result)) + ' new shb notice')
    return result


def get_notice_link_list(last_num):
    page = 0
    link_list = []
    prefix = 'http://shb.skku.edu/enc/menu_6/sub6_2.jsp'
    while True:
        URL = 'http://shb.skku.edu/enc/menu_6/sub6_2.jsp?mode=list&board_no=1377&pager.offset=' + str(page)
        response = requests.get(URL)
        if response.status_code != requests.codes.ok:
            return link_list
        try:
            soup = BeautifulSoup(response.text, 'html5lib')
            notice_list = soup.table.findAll('tr')[1:]
            for notice in notice_list:
                if int(notice.td.text) > last_num:
                    link_list.append((prefix + notice.a['href'], int(notice.td.text)))
                else:
                    return link_list
            page += 10
        except:
            return link_list
