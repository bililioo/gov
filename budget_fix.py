 #!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Ben'

import logging; logging.basicConfig(level=logging.INFO)

from urllib import parse
from urllib import request
import asyncio
import urllib
from bs4 import BeautifulSoup
import time
import ssl
import models
import parameters
from functools import reduce
import convert

ssl._create_default_https_context = ssl._create_unverified_context



headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'zh-CN,zh;q=0.9',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Content-Length':'203',
'Content-Type':'application/x-www-form-urlencoded',
'Cookie':'ManageSystemCookie=rfOZNOv5LwDB2fnK6MYf7RVMzCGB5eC6zvsUbV34CkxnyscMSqSX!1881410054; clickedFolderroot_region_id_01=21%5E2%5E; highlightedTreeviewLinkroot_region_id_01=2; PortalCookie=H3qbTk0AdyUyYXq5n7aooycKSTQ9ulV9WAP_-Q7yUpt4vrttUjfU!-1215113840',
'Host':'www.gdgpo.gov.cn',
'If-Modified-Since':'Fri, 06 Apr 2018 11:41:21 GMT',
'Origin':'http://www.gdgpo.gov.cn',
'Referer':'http://www.gdgpo.gov.cn/queryMoreCityCountyInfoList2.do',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'
}

base_URL = 'http://www.gdgpo.gov.cn'

replace_text = [
    '一、采购项目编号：',
    '二、采购项目名称：',
    '三、采购项目预算金额（元）：',
    '发布日期：',
    '采购人：',
    '代理机构：',
]


async def fix_model(model):
    url = model.url
    logging.info('==============================')
    logging.info('url = %s' % url)
    
    try:
        html = request.urlopen(url, timeout=10)
        # await content_spider(html, url, district, announcement_type)
        await reset_budget(html, model)

    except urllib.error.HTTPError as error:
        logging.info('******request content http error : %s' % error)
        m = models.Failure_ann(announcement_type=model.announcement_type,                                  publish_time=model.publish_time, 
                                pro_num=model.pro_num, 
                                title=model.title,
                                pro_title=model.pro_title,
                                content=model.content,
                                district=model.district,
                                purchaser=model.purchaser,
                                agent=model.agent,
                                supplier=model.supplier,
                                budget=model.budget,
                                trade_price=model.trade_price,
                                url=model.url,
                                )
        logging.info(m)
        await m.save()

    except urllib.error.URLError as error:
        logging.info('******request content url error : %s' % error)

    except Exception as error:
        logging.info('******other Exception: %s', error)
        m = models.Failure_ann(announcement_type=model.announcement_type,                                  publish_time=model.publish_time, 
                                pro_num=model.pro_num, 
                                title=model.title,
                                pro_title=model.pro_title,
                                content=model.content,
                                district=model.district,
                                purchaser=model.purchaser,
                                agent=model.agent,
                                supplier=model.supplier,
                                budget=model.budget,
                                trade_price=model.trade_price,
                                url=model.url,
                                )
        logging.info(m)
        await m.save()


async def reset_budget(html, model):
    
    bs_obj = BeautifulSoup(html, 'lxml')

    budget = ''

    div = bs_obj.body.div.find_all(attrs={"class": 'zw_c_c_cont'})
    if len(div) > 0:
        
        p_nodes = div[0].find_all('p')
        for p in p_nodes:
            if p.text.count('预算金额'):
                budget = ''.join(filter(lambda ch: ch in '0123456789.', p.text))
                logging.info('预算金额： %s' % budget)

    header_nodes = bs_obj.body.div.find_all(attrs={"class": 'zw_c_c_qx'})
    header_span_nodes = header_nodes[0].find_all('span')
    for span in header_span_nodes:
        if '预算金额：' in span.text and budget == '':
            budget = ''.join(filter(lambda ch: ch in '0123456789.', span.text))
            logging.info('预算金额： %s' % budget)

    span_nodes = bs_obj.body.find_all('span')
    for span_node in span_nodes:
        if '三、采购项目预算金额（元）：' in span_node.text and budget == '':
            budget = span_node.text.replace('三、采购项目预算金额（元）：', '')
            budget = budget.replace(',', '')
            budget = ''.join(filter(lambda ch: ch in '0123456789.', budget))
            logging.info('%s %s' % ('三、采购项目预算金额（元）：', budget))

    if str(model.budget) != budget:
        model.budget = budget
        logging.info(model)
        await models.Announcement.update(model)
    else:
        logging.info('budget is equal')

# async def request_content(href, district, announcement_type):
#     logging.info('==============================')

#     url = base_URL + href
#     # url = 'http://www.gdgpo.gov.cn/showNotice/id/40288ba96269beb201626be8ab54496e.html' # 3个中标供应商测试url
#     # url = 'http://www.gdgpo.gov.cn/showNotice/id/40288ba95debddc9015df356a76c3088.html' # 项目分包成交金额测试url

#     logging.info('url = %s' % url)
    
#     try:
#         html = request.urlopen(url, timeout=10)
#         await content_spider(html, url, district, announcement_type)

#     except urllib.error.HTTPError as error:
#         logging.info('******request content http error : %s' % error)

#         model = models.Failure_requests(params='', url=href, failure_type=2, district=district, error_msg=str(error), announcement_type=announcement_type)
#         await model.save()

#     except urllib.error.URLError as error:
#         logging.info('******request content url error : %s' % error)

#     except Exception as error:
#         logging.info('******other Exception: %s', error)

#         model = models.Failure_requests(params='', url=href, failure_type=2, district=district, error_msg=str(error), announcement_type=announcement_type)
#         await model.save()

# async def content_spider(html, url='', district='', announcement_type=0):

#     time.sleep(2)
#     # await asyncio.time.sleep(2)

#     publish_time = ''
#     pro_num = ''
#     pro_title = ''
#     pro_content = ''
#     purchaser = ''
#     agent = ''
#     budget = '0'
#     title = ''
#     total_price = 0

#     bs_obj = BeautifulSoup(html, 'lxml')

#     title_node = bs_obj.body.div.find_all(attrs={"class": 'zw_c_c_title'})
#     if len(title_node) > 0:
#         title = title_node[0].text
#         logging.info('title = %s' % title)

#     # if '中标金额：' in span_node.text and announcement_type == 0 and total_price == 0:
#     #         total_price = ''.join(filter(lambda ch: ch in '0123456789.', span_node.text))

#     header_nodes = bs_obj.body.div.find_all(attrs={"class": 'zw_c_c_qx'})
#     header_span_nodes = header_nodes[0].find_all('span')
#     for span in header_span_nodes:
#         if '中标金额：' in span.text and announcement_type == 0:
#             total_price = ''.join(filter(lambda ch: ch in '0123456789.', span.text))
#             if total_price == '':
#                 total_price = 0
#             logging.info('中标金额： %s' % total_price)

#         if '预算金额：' in span.text and announcement_type == 1:
#             budget = ''.join(filter(lambda ch: ch in '0123456789.', span.text))
#             if budget == '':
#                 budget = 0
#             logging.info('预算金额： %s' % budget)


#     div = bs_obj.body.div.find_all(attrs={"class": 'zw_c_c_cont'})
#     if len(div) > 0:
#         # 采购人
#         purchaser = div[0].text
#         purchaser = purchaser[purchaser.find('受') + 1:purchaser.find('的委托')]
#         logging.info('%s %s' % (replace_text[4], purchaser))

        
#         p_nodes = div[0].find_all('p')
#         # 2015的采购项目名
#         for p in p_nodes:
#             if p.text.count('采购项目名称：') == 1: 
#                 pro_title = p.text[p.text.find('：') + 1:]
#                 logging.info('%s %s' % (replace_text[1], pro_title))

#             elif p.text.count('内容：') == 1 and pro_content == '':
#                 pro_content = p.text[p.text.find('：') + 1:]
#                 logging.info('项目内容：%s' % pro_content)
            
#             elif p.text.count('预算金额') and budget == '0':
#                 budget = ''.join(filter(lambda ch: ch in '0123456789.', p.text ))
#                 logging.info('预算金额： %s' % budget)
    
#     tr_nodes = []
#     if bs_obj != None and bs_obj.body != None and bs_obj.body.tbody != None:
#         tr_nodes = bs_obj.body.tbody.find_all('tr')

#     prices = []
#     if len(tr_nodes) == 2 and total_price == 0:
#         tr = tr_nodes[0]
#         td = tr.find_all('td')[-1].text
#         if td.count('成交金额（元）') == 1:
#             tr1 = tr_nodes[1]
#             trade_price = tr1.find_all('td')[-1].text
#             trade_price = ''.join(filter(lambda ch: ch in '0123456789.', trade_price))
#             prices.append(trade_price)
#             logging.info('中标、成交金额（元） %s' % trade_price)
#     elif len(tr_nodes) > 2 and total_price == 0:
#         tr0 = tr_nodes[0]
#         if tr0.find_all('td')[-1].text.count('成交金额（元）') == 1: 
            
#             for i, tr_node in enumerate(tr_nodes[1:]):
#                 trade_price = tr_node.find_all('td')[-1].text
#                 trade_price = ''.join(filter(lambda ch: ch in '0123456789.', trade_price))
#                 if trade_price == None or trade_price == '':
#                     trade_price = 0
#                 prices.append(trade_price)
#                 logging.info('中标、成交金额（元） %s' % trade_price)
                
#     p_nodes = bs_obj.body.find_all('p')
#     suppliers = []
#     supplier = ''
#     for p_node in p_nodes:
#         if p_node.text.count('中标供应商名称') or p_node.text.count('中标（成交）供应商名称：') == 1:
#             if p_node.u != None:
#                 if supplier != p_node.u.text:
#                     supplier = p_node.u.text
#                     suppliers.append(supplier)
#                     logging.info('中标供应商名称 %s' % supplier)
#             else:
#                 index = p_node.text.find('名称')
#                 temp_supplier = p_node.text[index + 2:]
#                 temp_supplier.replace('：', '')
#                 if supplier != temp_supplier:
#                     supplier = temp_supplier
#                     suppliers.append(supplier)
#                     logging.info('中标供应商名称 %s' % supplier)


#         if p_node.text.count('中标（成交）金额：') == 1:
#             u_node = p_node.u
#             if u_node == None:
#                 trade_price = p_node.text
#             else:
#                 trade_price = p_node.u.text
#             trade_price = trade_price[trade_price.find('：') + 1:]
#             trade_price = ''.join(filter(lambda ch: ch in '0123456789.', trade_price))
#             prices.append(trade_price)
#             logging.info('中标、成交金额（元） %s' % trade_price)
    
#     if len(prices) > 0:
#         total_price = reduce(lambda x, y: float(x) + float(y), prices)

#     span_nodes = bs_obj.body.find_all('span')
#     for span_node in span_nodes:

#         if '三、项目编号：' in span_node.text:
#             pro_num = span_node.text.replace('三、项目编号：', '')
#             logging.info('%s %s' % ('三、项目编号：', pro_num))

#         if replace_text[0] in span_node.text:
#             pro_num = span_node.text.replace(replace_text[0], '')
#             logging.info('%s %s' % (replace_text[0], pro_num))

#         if replace_text[1] in span_node.text:
#             pro_title = span_node.text.replace(replace_text[1], '')
#             logging.info('%s %s' % (replace_text[1], pro_title))

#         if replace_text[2] in span_node.text and announcement_type == 0 and budget == '0':
#             budget = span_node.text.replace(replace_text[2], '')
#             budget = budget.replace(',', '')
#             budget = ''.join(filter(lambda ch: ch in '0123456789.', budget))
#             logging.info('%s %s' % (replace_text[2], budget))

#         if replace_text[3] in span_node.text:
#             publish_time = span_node.text.replace(replace_text[3], '')
#             logging.info('%s %s' % (replace_text[3], publish_time))

#         if replace_text[5] in span_node.text:
#             agent = span_node.text.replace(replace_text[5], '')
#             logging.info('%s %s' % (replace_text[5], agent))
        
#         if '中标、成交金额人民币：' in span_node.text and announcement_type == 0 and total_price == 0: 
#             cut_text = span_node.text[span_node.text.find('：') + 1:]
#             total_price = ''.join(filter(lambda ch: ch in '0123456789.', cut_text))
#             if total_price == '':
#                 total_price = convert.chinese_to_arabic(cut_text)
#                 # total_price = ''.join(filter(lambda ch: ch in '0123456789.', total_price))
    
#         if '中标金额：人民币' in span_node.text and announcement_type == 0 and total_price == 0:
#             cut_text = span_node.text[span_node.text.find('：') + 1:]
#             total_price = ''.join(filter(lambda ch: ch in '0123456789.', cut_text))
#             if total_price == '':
#                 total_price = 0
        
        
#         # if '中标金额：' in span_node.text and announcement_type == 0 and total_price == 0:
#         #     total_price = ''.join(filter(lambda ch: ch in '0123456789.', span_node.text))
        
#     if len(suppliers) == 0:
#         suppliers.append('')
#     supplier = ','.join(str(i) for i in suppliers)
#     # if len(suppliers) == 0:
#     #     suppliers.append('')
#     #     supplier = ','.join((str(i) for i in suppliers)

#     if title == '':
#         model = models.Failure_requests(params='', url=href, failure_type=2, district=district, error_msg='title is null', announcement_type=announcement_type)
#         await model.save()
#         return 

    # models.Announcement.update()


    # model = models.Announcement(announcement_type=announcement_type,                    publish_time=publish_time, 
    # pro_num=pro_num, 
    # title=title,
    # pro_title=pro_title,
    # content=pro_content,
    # district=district,
    # purchaser=purchaser,
    # agent=agent,
    # supplier=supplier,
    # budget=budget,
    # trade_price=total_price,
    # url=url,
    # )
    # logging.info(model)
    # await model.save()