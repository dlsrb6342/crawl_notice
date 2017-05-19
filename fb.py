from facepy import utils, GraphAPI
from datetime import datetime

def get_facebook_feed(page_id, last_created_time, logger):
    result = []
    app_id = "app_id"
    app_secret = "app_secret"

    access_token = utils.get_application_access_token(app_id, app_secret)

    graph = GraphAPI(access_token)
    cnt = 1
    while True:
        URL = '/v2.9/' + str(page_id) + '/feed?fields=created_time,attachments,message&limit=' + str(cnt * 5)
        page_feed = graph.get(URL)['data']

        for i in range((cnt - 1) * 5, cnt * 5):
            feed_created_time = datetime.strptime(page_feed[i]['created_time'], "%Y-%m-%dT%H:%M:%S+%f").timestamp()
            if feed_created_time <= last_created_time:
                logger.info('get '+ str(len(result)) + ' new facebook feed')
                return result
            else:
                if page_feed[i]['message']:
                    link = "https://www.facebook.com/" + str(page_id) + "/posts/" + page_feed[i]['id'].split("_")[1]
                    attach = page_feed[i]['attachments']['data'][0]
                    img_src = ""
                    if attach['type'] == 'photo':
                        img_src = attach['media']['image']['src']
                    elif attach['type'] == 'album':
                        for data in attach['subattachments']['data']:
                            img_src = img_src + data['media']['image']['src'] + "#"
                        img_src = img_src[:len(img_src)-1]

                    notice = {
                        'title': page_feed[i]['message'][:10] + '...',
                        'contents': page_feed[i]['message'],
                        'last_num': feed_created_time,
                        'link': link,
                        'img_src': img_src
                    }
                    result.append(notice)
                
        cnt = cnt + 1

