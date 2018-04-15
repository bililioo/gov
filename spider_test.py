 #!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Ben'

import spider
import asyncio
import os
import convert
from functools import reduce

async def init(loop):

    # await spider.request_content('test', '/showNotice/id/40288ba96079352601609c3e44b02017.html')

    # params.filter_district()
    # print(params.create_params())

    def add(a, b):
        return a + b

    prices = ['1', '2', '3', '4', '5']
    total_price = reduce(lambda x, y: int(x) + int(y), prices)
    print(total_price)
    await spider.start()


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.close()