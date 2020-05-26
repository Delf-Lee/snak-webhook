import os
import json
import requests

from datetime import datetime
from datetime import timedelta
from urllib import parse

SNAK_URL = "https://snak.news"
SNAK_API = SNAK_URL + "/api/news"
SNAK_NEWS_REQUEST = SNAK_URL + "/newsList/news/{_id}"

KST_today = datetime.today() + timedelta(hours=9)
HEADER_SENTENCE = ':pray::skin-tone-2: 안녕하세요 여러분! %s 스낵 전달드립니다.' % KST_today.strftime('%-m월 %-d일')
FOOTER_SENTENCE = '더 많은 소식들을 보고 싶다면?:man-raising-hand:\n' + SNAK_URL

def get_todays_querystring():
    today = KST_today
    yesterday = today - timedelta(days=1)
    return f"?startDateTime={yesterday.strftime('%Y-%m-%d')}T09:02&endDateTime={today.strftime('%Y-%m-%d')}T09:01"
    
def get_new_snak(url):
    ret = requests.get(url)
    if ret.status_code != 200:
        raise BaseException("API failed. News request error.")
    return ret.json()['data']
    
def get_essential_info(data):
    _id = data['id']
    topic = ",".join(topic['name'] for topic in data['topics'])
    category = data['category']['title']
    title = data['title']
    link = data['link']

    return _id, topic, category, title, link

def mk_newslist_sentence(_id, topic, category, title):
    encode_link = parse.unquote(link)
    return f"{':white_check_mark: ' + title}\n{encode_link}"
    
def slack_noti(webhook, news_list):
    news_list_sentence = '\n\n'.join(news_list)
    whole_sentence = HEADER_SENTENCE + '\n\n' + news_list_sentence + '\n\n' + FOOTER_SENTENCE
    data = json.dumps({'text': whole_sentence})
    r = requests.post(webhook, data=data)
    
def get_webhook_url(url):
    ret = requests.get(url)
    if ret.status_code != 200:
        raise BaseException("API failed. webhook-list request error.")
    return ret.json()

def lambda_handler(event, context):
    qs = get_todays_querystring()

    snak_list = get_new_snak(f"{SNAK_API}{qs}")
    
    news = []
    for snak in snak_list:
        _id, topic, category, title, link = get_essential_info(snak)
        sentence = mk_newslist_sentence(_id, topic, category, title, link)
        news.append(sentence)
    
    url_list = get_webhook_url("https://snak.news/api/slackbot/webhook-list")
    
    for webhook_url in url_list:
        slack_noti(webhook_url, news)

    return 'success'
