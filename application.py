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

async def init(loop):
    await orm.create_pool(loop, **config.configs.db)

    # while True:
        # await spider.request_content('/showNotice/id/40288ba94f409de6014f4a07ca5916d4.html', 'fdsf')

        # params = {'purchaserOrgName': '', 'operateDateTo': '', 'channelCode': '0008', 'title': '教育', 'stockTypes': '', 'stockIndexName': '', 'operateDateFrom': '2015-01-01', 'stockNum': '', 'sitewebId': '297e6a6a49176e840149184f0a590e9c', 'performOrgName': ''}
        # await spider.start(params)

    arr = parameters.create_all_search_List_params()

    for item in arr:
        await spider.start(item)

async def re_request():
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


# async def search():
#     model = await models.Failure_requests.find('7')
#     params_dict = ast.literal_eval(model.params)
#     await spider.start(params_dict)
    # await spider.main_spider(params_dict, model.district)



loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
# loop.run_until_complete(search())
loop.run_until_complete(re_request())
loop.close()