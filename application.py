#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Ben'

import logging; logging.basicConfig(level=logging.INFO)

import orm
import spider
import asyncio
import os
from config import configs
import models
import ast
import random
import budget_fix

'''
    把队列放进loop中会以协程的方式执行队列中的任务，一个队列过多任务，可能会导致访问站点失败。
'''

async def init_sql(loop):
    logging.info(configs)
    await orm.create_pool(loop, **configs.db)

async def delay():
    s = random.randint(1, 5)
    await asyncio.sleep(s)

async def update(models_begin, models_end):
    nil_models = await models.Announcement.findAll(where='budget = \'\'')
    zero_models = await models.Announcement.findAll(where='budget = 0')
    budget_models = nil_models + zero_models

    for item in budget_models[int(models_begin):int(models_end)]:
        await delay()
        await budget_fix.fix_model(item)

async def re_failure_ann():
    logging.info('开始循环失败请求')

    cycle_type = True
    while cycle_type:
        request_models = await models.Failure_ann.findAll()
        if len(request_models) > 0:
            for item in request_models:
                await delay()
                await budget_fix.fix_model(item)
                await models.Failure_ann.remove(item)
        else:
            cycle_type = False

tasks = [update(20831, 30000), update(30000, 40000), update(40000, -1)]

loop = asyncio.get_event_loop()
loop.run_until_complete(init_sql(loop))
loop.run_until_complete(asyncio.wait(tasks)) 
loop.run_until_complete(re_failure_ann()) 


loop.close()