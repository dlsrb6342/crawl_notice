import requests, json
from bs4 import BeautifulSoup
from datetime import datetime

result = []
URL = "http://cs.skku.edu/ajax/board/view/notice/1133" 
response = requests.post(URL)
if response.status_code != requests.codes.ok:
    break

jsonify_response = json.loads(response.text)

if jsonify_response['result']:
    notice_json = json.loads(response.text)["post"]
    
    soup = BeautifulSoup(notice_json['text'], 'html5lib')
    contents = soup.text
    link = "http://cs.skku.edu/open/notice/view/" + str(notice_json['id'])
    notice = {
        'title': notice_json['title'],
        'last_num': notice_json['id'],
        'contents': contents,
        'link': link
    }
    result.append(notice)
else:
    break

