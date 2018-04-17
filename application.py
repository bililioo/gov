#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Ben'

import logging; logging.basicConfig(level=logging.INFO)

import orm
import spider
import asyncio
import os
import config
import parameters
import models
import ast
from parameters import Channel
import random

async def init_sql(loop):
    await orm.create_pool(loop, **config.configs.db)

async def re_request():
    logging.info('开始循环失败请求')

    request_models = await models.Failure_requests.findAll()
    for re in request_models:
        if re.failure_type == 0:
            params_dict = ast.literal_eval(re.params)
            await spider.start(params_dict)
            models.Failure_requests.remove(re.id)

        elif re.failure_type == 1:
            params_dict = ast.literal_eval(re.params)
            await spider.main_spider(params_dict, re.district)
            models.Failure_requests.remove(re.id)

        elif re.failure_type == 2:
            params_dict = ast.literal_eval(re.params)
            await spider.request_content(re.url, re.district)
            models.Failure_requests.remove(re.id)


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


tasks = [provinces_zhaobbiao(), cities_zhaobiao(), districts_zhaobiao()]

loop = asyncio.get_event_loop()
loop.run_until_complete(init_sql(loop))
loop.run_until_complete(asyncio.wait(tasks))
loop.run_until_complete(re_request())

loop.close()