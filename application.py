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

async def init(loop):

    await orm.create_pool(loop, **config.configs.db)
    
    arr = parameters.create_all_search_List_params()
    for item in arr:
        await spider.start(item)


loop = asyncio.get_event_loop()
loop.loop = 4
loop.run_until_complete(init(loop))
loop.close()