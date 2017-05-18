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
        URL = '/v2.9/' + str(page_id) + '/feed?limit=' + str(cnt * 5)
        page_feed = graph.get(URL)['data']

        for i in range((cnt - 1) * 5, cnt * 5):
            feed_created_time = datetime.strptime(page_feed[i]['created_time'], "%Y-%m-%dT%H:%M:%S+%f").timestamp()
            if feed_created_time <= last_created_time:
                logger.info('get '+ str(len(result)) + ' new facebook feed')
                return result
            else:
                if page_feed[i]['message']:
                    notice = {
                        'title': page_feed[i]['message'][:10] + '...',
                        'contents': page_feed[i]['message'],
                        'last_num': feed_created_time
                    }
                    result.append(notice)
                
        cnt = cnt + 1

