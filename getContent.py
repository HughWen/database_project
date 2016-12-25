# -*- coding: utf-8 -*-
import requests
from pymongo import MongoClient
import time
from redis import StrictRedis
import traceback
from parsel import Selector
import urlparse
#redis config
import json
import re
from multiprocessing import Pool
from collections import Counter
redis_setting = {
    'dev': {
        'host': 'localhost',
        'port': 6379,
        'max_connections': 200,
        'db': 1,
    },
}


REDIS_CLIENT = StrictRedis(**redis_setting['dev'])

MONGO_CLIENT = MongoClient('secret')

db = MONGO_CLIENT['nodebb']
articles_coll = db['articles']
tags_coll = db['tags']

headers = {
    "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36',
    'Host': '36kr.com',
    'Cookie': 'aliyungf_tc=AQAAAMGySVIwkwgAgvgS2msFHJgu8btb; gr_user_id=2e2031d6-a43e-4df9-945d-97d4ed397646; kr_stat_uuid=ovuey24484520; c_name=point; gr_session_id_76d36bd044527820a1787b198651e2f1=7205350b-dc5f-42d2-9031-c6917d91e3cf; Hm_lvt_713123c60a0e86982326bae1a51083e1=1469071201; Hm_lpvt_713123c60a0e86982326bae1a51083e1=1469073547; krchoasss=eyJpdiI6IkpqS2tSbWVmcEtmMDBRVlkwOFdGNFE9PSIsInZhbHVlIjoiUVo2QkdLOUpKZ0pRYjRETnNTR2I0XC9ZSVJcL3FaTHhKd0JPUXBXK2MreFJ4ZGEzVzV1MFRndTdmRXNGMnNhalphWk4xVHZoSlhoTGlTNTRQcHdqSFwvMWc9PSIsIm1hYyI6Ijk0NmFjOTIwZGVkMjcyOWNlYTY4ZGZiYTBlMjY4M2I4MTM4Y2FjMjYxYTU5YmI2NTIxNTAzNjY1ZjZhZGMxNzIifQ%3D%3D'

}
to_get_tags = []
body_x='//script'
API='http://36kr.com/p/%s.html'
API_ID='http://36kr.com/api/info-flow/main_site/posts?column_id=&b_id=%s&per_page=%s'
set_name='html_id_set'
tag_x='//meta[@name="keywords"]/@content'

def parse_value(response, selector, all=True):
    if all:
        rlts = filter(lambda value: value.strip() != '',
                          response.xpath(selector).extract())
        return map(lambda rlt: rlt.strip(), rlts)
    else:
        rlt = response.xpath(selector).extract_first()
        if rlt:
            return rlt.strip()
        return ''

def save_article(id, data):
    if not (articles_coll.find_one({'id': id})):
        print('>>>>> add new: %s' % id)
        articles_coll.insert_one(data)
    else:
        print('%s existed'%id)

def save_tags(id, item):
    if not (tags_coll.find_one({'id': id})):
        print('>>>>> add new: %s' % id)
        tags_coll.insert_one(item)
    else:
        print('%s existed'%id)

def parse_tags(id_get):
    if not (tags_coll.find_one({'id': id_get})):
        url = API%id_get
        resp = requests.get(url, headers=headers, timeout=10)
        hxs = Selector(text=resp.text)
        tags=parse_value(hxs,tag_x)[0]
        print tags
        item = {
            'id':id_get,
            'tags':tags
        }
        save_tags(id_get, item)
        return item
    else:
        item = tags_coll.find_one({'id': id_get})
        return item

def parse(id_get):

    url = API%id_get
    resp = requests.get(url, headers=headers, timeout=10)
    hxs = Selector(text=resp.text)
    body=parse_value(hxs,body_x)
    set=body[5].split(',locationnal=')
    text=set[0].replace('<script>var props=','')
    data = json.loads(text)
    detail=data['detailArticle|post']
    id=detail['id']
    '''date=detail['published_at']
    content=re.sub(r'<([^<>]*)>', '', detail['content'])
    tags=detail['extraction_tags']
    related_company_type=detail['related_company_type']
    catch_title=detail['catch_title']
    summary=detail['summary']
    title=detail['title']
    author=detail['user']['name']
    answer = {
        'id': id,
        'content':content,
        'author':author,
        'tags':tags,
        'related_company_type':related_company_type,
        'catch_title':catch_title,
        'summary': summary,
        'answer_content': text
                }'''
    print data
    return detail
    save_article(id,detail)


def get_id(in_id, id_num):
    url_now = API_ID%(in_id, id_num)
    resp = requests.get(url_now, headers=headers)
    items = json.loads(resp.content)['data']['items']
    for item in items:
        REDIS_CLIENT.sadd(set_name,item['id'])

def get_article():
    while True:
        try:
            id=REDIS_CLIENT.spop(set_name)
            parse(id)
            print('<<<< success')
        except Exception,e:
            print e
            REDIS_CLIENT.sadd(set_name, id)
            traceback.print_exc()
            print('xxxx Failed')

def get_tags(id_list):
    fail_list = []
    while REDIS_CLIENT.scard(set_name) != 0:
        try:
            in_id = REDIS_CLIENT.spop(set_name)
            id_list.append(in_id)
            parse_tags(in_id)
        except Exception, e:
	    if in_id not in fail_list:
            	REDIS_CLIENT.sadd(set_name, id)
            	print('xxxx Failed')
		fail_list.append(in_id)
            	print e
	    else:
		print e

def retrieve_tags(in_id):
    if (tags_coll.find_one({'id': in_id})):
        item = tags_coll.find_one({'id': in_id})
        tags = item['tags']
        return tags
    else:
        item = parse_tags(in_id)
        tags = item['tags']
        return tags

def get_tag_list(in_id, id_num):
    tag_list = []
    id_list = []
    get_id(in_id, id_num)
    pool = Pool()
    pool.map(get_tags(id_list), range(10))
    pool.close()
    pool.join()
    for id in id_list:
        print id
        tags = retrieve_tags(id)
        tag_list.extend(tags.replace(u'创业资讯,科技新闻,','').split(','))
    counter1 = Counter(tag_list)
    return counter1

if __name__ == '__main__':
    '''
    pool = Pool()
    pool.map(get_article(),range(10))
    pool.close()
    pool.join()
    '''
    counter1 = get_tag_list(5058359, 100)
    print counter1
    list1 = counter1.most_common(5)
    for i in range(5):
        print list1[i][0], list1[i][1]

    #print retrieve_tags(303769651)
    #taglist = parse_tag(5058359)
    #print retrieve_tags(5058255)
