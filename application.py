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

    request_models = await models.Failure_requests.findAll()
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


async def delay():
    s = random.randint(1, 5)
    await asyncio.sleep(s)

async def provinces_zhaobbiao():
    await delay()
    arr = parameters.create_provinces(Channel.zhaobiao)
    for item in arr:
        await spider.start(item)

async def cities_zhaobiao():
    await delay()
    arr = parameters.create_cities(Channel.zhaobiao)
    for item in arr:
        await spider.start(item)

async def districts_zhaobiao():
    await delay()
    arr = parameters.create_cities(Channel.zhaobiao)
    for item in arr:
        await spider.start(item)

async def provinces_zhongbiao():
    await delay()
    arr = parameters.create_provinces(Channel.zhaobiao)
    for item in arr:
        await spider.start(item)

async def cities_zhongbiao():
    await delay()
    arr = parameters.create_cities(Channel.zhaobiao)
    for item in arr:
        await spider.start(item)

async def districts_zhongbiao():
    await delay()
    arr = parameters.create_cities(Channel.zhaobiao)
    for item in arr:
        await spider.start(item)

# 招标队列 
# tasks = [provinces_zhaobbiao(), cities_zhaobiao(), districts_zhaobiao()]
# 中标队列
# tasks1 = [provinces_zhongbiao(), cities_zhongbiao(), districts_zhongbiao()]


loop = asyncio.get_event_loop()
loop.run_until_complete(init_sql(loop))
# loop.run_until_complete(asyncio.wait(tasks))
# loop.run_until_complete(asyncio.wait(tasks1))
loop.run_until_complete(re_request())

loop.close()