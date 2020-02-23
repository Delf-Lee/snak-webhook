import os
import json
import botocore.vendored.requests as requests

from datetime import datetime

SLACK_WEBHOOK = os.environ['SLACK_WEBHOOK']
SNAK_API = "https://snak.news/api/news"
SNAK_URL = "https://snak.news/newsList/news/{_id}"

def get_todays_querystring():
    today = datetime.today().strftime('%Y-%m-%d')
    return f"?startDateTime={today}T00:00&endDateTime={today}T23:59"
    
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


def mk_sentence(_id, topic, category, title):
    link = SNAK_URL.format(_id=_id)
    return f"[{topic}-{category}] {title} {link}"


def slack_noti(webhook, news_list):
    data = json.dumps({'text': '\n\n'.join(news_list)})
    r = requests.post(webhook, data=data)
    
def lambda_handler(event, context):
    qs = get_todays_querystring()
    snak_list = get_new_snak(f"{SNAK_API}{qs}")
    
    news = []
    for snak in snak_list:
        _id, topic, category, title = get_essential_info(snak)
        sentence = mk_sentence(_id, topic, category, title)
        news.append(sentence)

    slack_noti(SLACK_WEBHOOK, news)

    return 'success'