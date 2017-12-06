import requests, json
from bs4 import BeautifulSoup


with open('config.json') as json_data_file:
    config = json.load(json_data_file)
prefix = config['url']['prefix']
img_prefix = config['url']['img_prefix']
board_no = config['url']['board_no']


def get_common_notice(row, logger) :
    _id, last_num, name = row['id'], row['last_num'], row['name']
    result = []
    link_list = get_notice_link_list(last_num, name)[::-1]
    for link, i in link_list:
        response = requests.get(link)
        response.encoding = 'UTF-8'
        if response.status_code != requests.codes.ok:
            break
        try:
            soup = BeautifulSoup(response.text, 'html5lib')
            title = soup.table.tr.td.text
            contents = soup.table.find(id="article_text").text.strip()
            img_src = ""
            for img in soup.table.find(id="article_text").findAll('img'):
                src = img['src'] if img['src'].startswith('http') else img_prefix[name] + img['src']
                img_src = img_src + src + '#'
            img_src = img_src[:len(img_src)-1]
            notice = {
                'id': _id,
                'title': title,
                'last_num': i,
                'contents': contents,
                'link': link,
                'img_src': img_src,
                'type': row['type'],
                'ntype': 'H'
            }
            result.append(notice)
        except:
            break
    
    logger.info('get ' + str(len(result)) + ' new ' + name + ' notice')
    return result


def get_notice_link_list(last_num, name):
    page = 0
    link_list = []
    while True:
        URL = prefix[name] + '?mode=list&board_no='+board_no[name]+'&pager.offset=' + str(page)
        response = requests.get(URL)
        response.encoding = 'UTF-8'
        if response.status_code != requests.codes.ok:
            return link_list
        try:
            soup = BeautifulSoup(response.text, 'html5lib')
            notice_list = soup.table.findAll('tr')[1:]
            for notice in notice_list:
                if notice.td.text == '':
                    continue
                if int(notice.td.text) > last_num:
                    link_list.append((prefix[name] + notice.a['href'], int(notice.td.text)))
                else:
                    return link_list
            page += 10
        except:
            return link_list
