import os
import json
import botocore.vendored.requests as requests

from datetime import datetime
from datetime import timedelta

SLACK_WEBHOOK = os.environ['SLACK_WEBHOOK']
SNAK_URL = "https://snak.news"
SNAK_API = SNAK_URL + "/api/news"
SNAK_NEWS_REQUEST = SNAK_URL + "/newsList/news/{_id}"

HEADER_SENTENCE = ':pray::skin-tone-2: 안녕하세요 여러분! %s 스낵 전달드립니다.' % datetime.today().strftime('%-m월 %-d일')
FOOTER_SENTENCE = '더 많은 소식들을 보고 싶다면?:man-raising-hand:\n' + SNAK_URL

def get_todays_querystring():
    today = datetime.today().strftime('%Y-%m-%d')
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    return f"?startDateTime={yesterday}T09:01&endDateTime={today}T09:00"
    
def get_new_snak(url):
    ret = requests.get(url)
    if ret.status_code != 200:
        raise BaseException("snack api failed")
    return ret.json()['data']
    
def get_essential_info(data):
    _id = data['id']
    topic = ",".join(topic['name'] for topic in data['topics'])
    category = data['category']['title']
    title = data['title']

    return _id, topic, category, title


def mk_newslist_sentence(_id, topic, category, title):
    link = SNAK_NEWS_REQUEST.format(_id=_id)
    return f"{':eyes:' + title}\n{link}"
    
def slack_noti(webhook, news_list):
    news_list_sentence = '\n\n'.join(news_list)
    whole_sentence = HEADER_SENTENCE + '\n\n' + news_list_sentence + '\n\n' + FOOTER_SENTENCE
    data = json.dumps({'text': whole_sentence})
    print(data)
    r = requests.post(webhook, data=data)
    
def lambda_handler(event, context):
    qs = get_todays_querystring()
    snak_list = get_new_snak(f"{SNAK_API}{qs}")
    
    news = []
    for snak in snak_list:
        _id, topic, category, title = get_essential_info(snak)
        sentence = mk_newslist_sentence(_id, topic, category, title)
        news.append(sentence)

    slack_noti(SLACK_WEBHOOK, news)

    return 'success'
