#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Ben'

import logging; logging.basicConfig(level=logging.INFO)

import orm
import spider
import asyncio
import os
from config import configs
import parameters
import models
import ast
from parameters import Channel
import random

'''
    把队列放进loop中会以协程的方式执行队列中的任务，一个队列过多任务，可能会导致访问站点失败。
'''

async def init_sql(loop):
    logging.info(configs)
    await orm.create_pool(loop, **configs.db)

async def re_request():
    logging.info('开始循环失败请求')

    cycle_type = True
    while cycle_type:
        request_models = await models.Failure_requests.findAll()
        if len(request_models) > 0:
           for re in request_models:
                if re.failure_type == 0:
                    params_dict = ast.literal_eval(re.params)
                    await spider.start(params_dict)
                    await models.Failure_requests.remove(re)

                elif re.failure_type == 1:
                    params_dict = ast.literal_eval(re.params)
                    await spider.main_spider(params_dict, re.district)
                    await models.Failure_requests.remove(re)

                elif re.failure_type == 2:
                    await spider.request_content(re.url, re.district, re.announcement_type)
                    await models.Failure_requests.remove(re)
        else:
             cycle_type = False


async def delay():
    s = random.randint(1, 5)
    await asyncio.sleep(s)


async def districts_zhongbiao():
    await delay()
    arr = parameters.create_districts(Channel.zhongbiao)
    total = len(arr)
    for i, item in enumerate(arr):
        logging.info('区县：第%d个组合，共%d个组合, %s, 关键字词：%s' % (i, total, item['sitewebId'], item['title']))
        await spider.start(item)

async def districts_zhaobiao_one():
    await delay()
    arr = parameters.create_districts_one(Channel.zhaobiao)
    for item in arr:
        await spider.start(item)

async def districts_zhaobiao_two():
    await delay()
    arr = parameters.create_districts_two(Channel.zhaobiao)
    for item in arr:
        await spider.start(item)

async def districts_zhaobiao_three():
    await delay()
    arr = parameters.create_districts_three(Channel.zhaobiao)
    for item in arr:
        await spider.start(item)

async def districts_zhaobiao_four():
    await delay()
    arr = parameters.create_districts_four(Channel.zhaobiao)
    for item in arr:
        await spider.start(item)




async def districts_zhongbiao_one():
    await delay()
    arr = parameters.create_districts_one(Channel.zhongbiao)
    for item in arr:
        await spider.start(item)

async def districts_zhongbiao_two():
    await delay()
    arr = parameters.create_districts_two(Channel.zhongbiao)
    for item in arr:
        await spider.start(item)

async def districts_zhongbiao_three():
    await delay()
    arr = parameters.create_districts_three(Channel.zhongbiao)
    for item in arr:
        await spider.start(item)

async def districts_zhongbiao_four():
    await delay()
    arr = parameters.create_districts_four(Channel.zhongbiao)
    for item in arr:
        await spider.start(item)

async def province_zhongbiao():
    await delay()
    arr = parameters.create_provinces(Channel.zhongbiao)
    total = len(arr)
    for i, item in enumerate(arr):
        logging.info('广东省：第%d个组合，共%d个组合, %s, 关键字词：%s' % (i, total, item['sitewebId'], item['title']))
        await spider.start(item)

async def cities_zhongbiao():
    await delay()
    arr = parameters.create_cities(Channel.zhongbiao)
    total = len(arr)
    for i, item in enumerate(arr):
        logging.info('城市：第%d个组合，共%d个组合, %s, 关键字词：%s' % (i, total, item['sitewebId'], item['title']))
        await spider.start(item)

# 招标队列 
# tasks = [districts_zhaobiao_four(), districts_zhaobiao_one(), districts_zhaobiao_three(), districts_zhaobiao_two()]
# 中标队列
# task1 = [districts_zhongbiao_one(), districts_zhongbiao_two(), districts_zhongbiao_three(), districts_zhongbiao_four()]
# task2 = [cities_zhongbiao()]
# task3 = [province_zhongbiao()]


task = [cities_zhongbiao(), province_zhongbiao(), districts_zhongbiao()]

async def content():
    await delay()
    cycle_type = True
    while cycle_type:
        request_models = await models.Failure_ann.findAll()
        if len(request_models) > 0:
           for re in request_models:
                url = re.url
                url = url.replace('http://www.gdgpo.gov.cn', '')
                await spider.request_content(url, re.district, re.announcement_type)
                await models.Failure_ann.remove(re)
        else:
             cycle_type = False
    # await spider.request_content(url, 'guangz', 0)

loop = asyncio.get_event_loop()
loop.run_until_complete(init_sql(loop))
# loop.run_until_complete(asyncio.wait(content))
loop.run_until_complete(content())
loop.run_until_complete(re_request()) 

loop.close()