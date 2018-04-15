#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Ben'

import logging; logging.basicConfig(level=logging.INFO)

# import orm
# import spider
import asyncio
import os
import config
import parameters
import models
import ast
import test

async def init(loop):
    # await spider.request_content('', '广州市')
    await orm.create_pool(loop, **config.configs.db)

    arr = parameters.create_all_search_List_params()
    # for item in arr:
    #     await spider.start(item)

# async def re_request():
#     re = await models.Failure_requests.findAll()
#     for re in requests:
#         if re.failure_type == 0:
#             params_dict = ast.literal_eval(re.params)
#             await spider.start(params_dict)

#         elif re.failure_type == 1:
#             params_dict = ast.literal_eval(re.params)
#             await spider.main_spider(params_dict, re.district)

#         elif re.failure_type == 2:
#             params_dict = ast.literal_eval(re.params)
#             await spider.request_content(re.url, re.district)



loop = asyncio.get_event_loop()
# loop.run_until_complete(init_orm(loop))
loop.run_until_complete(init(loop))
# loop.run_until_complete(re_request())
loop.close()