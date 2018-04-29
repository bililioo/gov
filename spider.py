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
'Content-Length':'233',
'Content-Type':'application/x-www-form-urlencoded',
'Cookie':'highlightedMoreroot_region_id_01=itemTextLink16; highlightedTreeviewLinkroot_region_id_01=; clickedFolderroot_region_id_01=1%5E2%5E14%5E; PortalCookie=4FX_1rD3eU_c6WanSHg9HEvV9rrN_N-5L3VrINiOIUyf65Bn9G-E!2016076279; highlightedTreeviewLinkroot_region_id_01=2; PortalCookie=H3qbTk0AdyUyYXq5n7aooycKSTQ9ulV9WAP_-Q7yUpt4vrttUjfU!-1215113840',
'Host':'www.gdgpo.gov.cn',
'If-Modified-Since':'Fri, 06 Apr 2018 11:41:21 GMT',
'Origin':'http://www.gdgpo.gov.cn',
'Referer':'http://www.gdgpo.gov.cn/queryMoreInfoList/channelCode/0005.html',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15'
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

def create_data(channel, index, title, sitewebId):
    data = dict()
    data['pageIndex'] = str(index)
    data['pageSize'] = '15'
    data['stockTypes'] = ''	
    data['channelCode'] = str(channel)
    data['sitewebId'] = sitewebId
    data['title'] =	title
    data['stockNum'] = ''
    data['purchaserOrgName'] = ''
    data['performOrgName'] = ''
    data['stockIndexName'] = ''
    data['operateDateFrom'] = '2015-01-01'
    data['operateDateTo'] = ''
    return data

async def start(params):

    arr = None
    
    try:
        arr = get_page_count(params)
    except Exception as error:
        logging.info('>>>>>>>>>>>>查页数error：%s' % error)

        model = models.Failure_requests(params=str(params), 
                                        url='http://www.gdgpo.gov.cn/queryMoreCityCountyInfoList2.do', 
                                        failure_type=0, 
                                        district='',
                                        error_msg=str(error))
        await model.save()
    
    if arr == None:
        return    

    if int(arr[0]) == 1:
        params_data = arr[1]

        data = create_data(params.get('channelCode'),'1', params_data.get('title'), params_data.get('sitewebId'))
        district = parameters.all_district.get(params_data.get('sitewebId'))
        await main_spider(data, district)
    else:
        for index in range(1, int(arr[0])):
            params_data = arr[1]

            data = create_data(params.get('channelCode'), index, params_data.get('title'), params_data.get('sitewebId'))
            district = parameters.all_district.get(params_data.get('sitewebId'))
            await main_spider(data, district)


def get_page_count(params):
    logging.info(params)

    time.sleep(1)

    url = 'http://www.gdgpo.gov.cn/queryMoreCityCountyInfoList2.do'
    b_params = bytes(parse.urlencode(params), 'utf-8')

    re = request.Request(url, data=b_params, headers=headers)
    html = urllib.request.urlopen(re, timeout=10)
    # html = request.urlopen(url, data=b_params, timeout=10)
    bs_obj = BeautifulSoup(html, 'lxml')   

    ul_nodes = bs_obj.body.div.find_all('ul')
    for ul in ul_nodes:
        if ul.get('class') == ['m_m_c_list']:
            if '没有数据' in ul.text:
                logging.info('检索列表没有数据')
                return None

    div = bs_obj.body.div.find_all(attrs={"class": 'm_m_c_page'})
    a_node_href = div[0].find_all('a')[-2]['href']
    page_count = ''.join(filter(lambda ch: ch in '0123456789.', a_node_href))

    if page_count == '':
        page_count = '1'
    #     page_count = div[0].span.find_all(attrs={"class": 'aspan1'}).text
        

    return (page_count, params)


async def main_spider(data, district):
    await asyncio.sleep(2)

    logging.info(data)

    if str(data.get('channelCode')) == '0005':
        announcement_type = 1
    else:
        announcement_type = 0

    url = 'http://www.gdgpo.gov.cn/queryMoreCityCountyInfoList2.do'
    params = bytes(parse.urlencode(data), 'utf-8')
    # req = request.Request('http://www.gdgpo.gov.cn/queryMoreCityCountyInfoList2.do')
    # req.headers = headers

    try:
        html = request.urlopen(url, data=params, timeout=15)
        bs_obj = BeautifulSoup(html, 'lxml')        

        a_nodes = bs_obj.body.find_all(attrs={"target": "_blank"})
        for a_node in a_nodes:
            href = a_node.attrs.get('href')
            # title = a_node.attrs.get('title')
            # logging.info(title)
            # logging.info(href)
            if href.count('showNotice/id/') == 1:
                # 开始采集公告内容网页
                await request_content(href, district, announcement_type)
    except Exception as error:
        logging.info('<<<<<<<<<<<请求列表error: %s' % error)
        model = models.Failure_requests(params=str(data), url=url, failure_type=1, district=district, error_msg=str(error))
        await model.save()
        

async def request_content(href, district, announcement_type):
    logging.info('==============================')

    url = base_URL + href
    # url = 'http://www.gdgpo.gov.cn/showNotice/id/40288ba96269beb201626be8ab54496e.html' # 3个中标供应商测试url
    # url = 'http://www.gdgpo.gov.cn/showNotice/id/40288ba95debddc9015df356a76c3088.html' # 项目分包成交金额测试url

    logging.info('url = %s' % url)
    
    try:
        html = request.urlopen(url, timeout=10)
        await content_spider(html, url, district, announcement_type)

    except urllib.error.HTTPError as error:
        logging.info('******request content http error : %s' % error)

        model = models.Failure_requests(params='', url=href, failure_type=2, district=district, error_msg=str(error), announcement_type=announcement_type)
        await model.save()

    except urllib.error.URLError as error:
        logging.info('******request content url error : %s' % error)

    except Exception as error:
        logging.info('******other Exception: %s', error)

        model = models.Failure_requests(params='', url=href, failure_type=2, district=district, error_msg=str(error), announcement_type=announcement_type)
        await model.save()

async def content_spider(html, url='', district='', announcement_type=0):

    time.sleep(2)
    # await asyncio.time.sleep(2)

    publish_time = ''
    pro_num = ''
    pro_title = ''
    pro_content = ''
    purchaser = ''
    agent = ''
    budget = ''
    title = ''
    total_price = 0

    bs_obj = BeautifulSoup(html, 'lxml')

    title_node = bs_obj.body.div.find_all(attrs={"class": 'zw_c_c_title'})
    if len(title_node) > 0:
        title = title_node[0].text
        logging.info('title = %s' % title)

    # if '中标金额：' in span_node.text and announcement_type == 0 and total_price == 0:
    #         total_price = ''.join(filter(lambda ch: ch in '0123456789.', span_node.text))

    header_nodes = bs_obj.body.div.find_all(attrs={"class": 'zw_c_c_qx'})
    header_span_nodes = header_nodes[0].find_all('span')
    for span in header_span_nodes:
        if '中标金额：' in span.text and announcement_type == 0:
            total_price = ''.join(filter(lambda ch: ch in '0123456789.', span.text))
            if total_price == '' or total_price == '00.00':
                total_price = 0
            logging.info('中标金额： %s' % total_price)

        if '预算金额：' in span.text and budget == '':
            budget = ''.join(filter(lambda ch: ch in '0123456789.', span.text))
            logging.info('预算金额： %s' % budget)


    div = bs_obj.body.div.find_all(attrs={"class": 'zw_c_c_cont'})
    if len(div) > 0:
        # 采购人
        purchaser = div[0].text
        purchaser = purchaser[purchaser.find('受') + 1:purchaser.find('的委托')]
        logging.info('%s %s' % (replace_text[4], purchaser))

        
        p_nodes = div[0].find_all('p')
        # 2015的采购项目名
        for p in p_nodes:
            if p.text.count('采购项目名称：') == 1: 
                pro_title = p.text[p.text.find('：') + 1:]
                logging.info('%s %s' % (replace_text[1], pro_title))

            elif p.text.count('内容：') == 1 and pro_content == '':
                pro_content = p.text[p.text.find('：') + 1:]
                logging.info('项目内容：%s' % pro_content)

            elif p.text.count('预算金额') == 1:
                budget = ''.join(filter(lambda ch: ch in '0123456789.', p.text))
                logging.info('预算金额： %s' % budget)
    
    tr_nodes = []
    if bs_obj != None and bs_obj.body != None and bs_obj.body.tbody != None:
        tr_nodes = bs_obj.body.tbody.find_all('tr')

    prices = []
    if len(tr_nodes) == 2 and total_price == 0:
        tr = tr_nodes[0]
        td = tr.find_all('td')[-1].text
        if td.count('成交金额（元）') == 1:
            tr1 = tr_nodes[1]
            trade_price = tr1.find_all('td')[-1].text
            trade_price = ''.join(filter(lambda ch: ch in '0123456789.', trade_price))
            prices.append(trade_price)
            logging.info('中标、成交金额（元） %s' % trade_price)
    elif len(tr_nodes) > 2 and total_price == 0:
        tr0 = tr_nodes[0]
        if tr0.find_all('td')[-1].text.count('成交金额（元）') == 1: 
            
            for i, tr_node in enumerate(tr_nodes[1:]):
                trade_price = tr_node.find_all('td')[-1].text
                trade_price = ''.join(filter(lambda ch: ch in '0123456789.', trade_price))
                if trade_price == None or trade_price == '':
                    trade_price = 0
                prices.append(trade_price)
                logging.info('中标、成交金额（元） %s' % trade_price)
                
    p_nodes = bs_obj.body.find_all('p')
    suppliers = []
    supplier = ''
    for p_node in p_nodes:
        if p_node.text.count('中标供应商名称') or p_node.text.count('中标（成交）供应商名称：') == 1:
            if p_node.u != None:
                if supplier != p_node.u.text:
                    supplier = p_node.u.text
                    suppliers.append(supplier)
                    logging.info('中标供应商名称 %s' % supplier)
            else:
                index = p_node.text.find('名称')
                temp_supplier = p_node.text[index + 2:]
                temp_supplier.replace('：', '')
                if supplier != temp_supplier:
                    supplier = temp_supplier
                    suppliers.append(supplier)
                    logging.info('中标供应商名称 %s' % supplier)


        if p_node.text.count('中标（成交）金额：') == 1:
            u_node = p_node.u
            if u_node == None:
                trade_price = p_node.text
            else:
                trade_price = p_node.u.text
            trade_price = trade_price[trade_price.find('：') + 1:]
            trade_price = ''.join(filter(lambda ch: ch in '0123456789.', trade_price))
            prices.append(trade_price)
            logging.info('中标、成交金额（元） %s' % trade_price)
    
    if len(prices) > 1 and (total_price == 0 or total_price == '') :
        try:
            total_price = reduce(lambda x, y: float(x) + float(y), prices)
        except:
            total_price = prices[0]

    span_nodes = bs_obj.body.find_all('span')
    for span_node in span_nodes:

        if '三、项目编号：' in span_node.text:
            pro_num = span_node.text.replace('三、项目编号：', '')
            logging.info('%s %s' % ('三、项目编号：', pro_num))

        if replace_text[0] in span_node.text:
            pro_num = span_node.text.replace(replace_text[0], '')
            logging.info('%s %s' % (replace_text[0], pro_num))

        if replace_text[1] in span_node.text:
            pro_title = span_node.text.replace(replace_text[1], '')
            logging.info('%s %s' % (replace_text[1], pro_title))

        # if replace_text[2] in span_node.text and announcement_type == 0:
        #     budget = span_node.text.replace(replace_text[2], '')
        #     budget = budget.replace(',', '')
        #     budget = ''.join(filter(lambda ch: ch in '0123456789.', budget))
        #     logging.info('%s %s' % (replace_text[2], budget))

        if '三、采购项目预算金额（元）：' in span_node.text and budget == '':
            budget = span_node.text.replace('三、采购项目预算金额（元）：', '')
            budget = budget.replace(',', '')
            budget = ''.join(filter(lambda ch: ch in '0123456789.', budget))
            logging.info('%s %s' % ('三、采购项目预算金额（元）：', budget))

        if replace_text[3] in span_node.text:
            publish_time = span_node.text.replace(replace_text[3], '')
            logging.info('%s %s' % (replace_text[3], publish_time))

        if replace_text[5] in span_node.text:
            agent = span_node.text.replace(replace_text[5], '')
            logging.info('%s %s' % (replace_text[5], agent))
        
        if '中标、成交金额人民币：' in span_node.text and announcement_type == 0 and total_price == 0: 
            cut_text = span_node.text[span_node.text.find('：') + 1:]
            total_price = ''.join(filter(lambda ch: ch in '0123456789.', cut_text))
            if total_price == '':
                total_price = convert.chinese_to_arabic(cut_text)
                # total_price = ''.join(filter(lambda ch: ch in '0123456789.', total_price))
    
        if '中标金额：人民币' in span_node.text and announcement_type == 0 and total_price == 0:
            cut_text = span_node.text[span_node.text.find('：') + 1:]
            total_price = ''.join(filter(lambda ch: ch in '0123456789.', cut_text))
            if total_price == '':
                total_price = 0
        
        
        # if '中标金额：' in span_node.text and announcement_type == 0 and total_price == 0:
        #     total_price = ''.join(filter(lambda ch: ch in '0123456789.', span_node.text))
        
    if len(suppliers) == 0:
        suppliers.append('')
    supplier = ','.join(str(i) for i in suppliers)
    # if len(suppliers) == 0:
    #     suppliers.append('')
    #     supplier = ','.join((str(i) for i in suppliers)

    if title == '':
        model = models.Failure_requests(params='', url=href, failure_type=2, district=district, error_msg='title is null', announcement_type=announcement_type)
        await model.save()
        return 


    model = models.Announcement(announcement_type=announcement_type,                    publish_time=publish_time, 
    pro_num=pro_num, 
    title=title,
    pro_title=pro_title,
    content=pro_content,
    district=district,
    purchaser=purchaser,
    agent=agent,
    supplier=supplier,
    budget=budget,
    trade_price=total_price,
    url=url,
    )
    logging.info(model)
    await model.save()

    # model = models.Announcement(announcement_type=announcement_type, publish_time=publish_time, pro_num=pro_num, title=title, pro_title=pro_title, content=pro_content, district=district, purchaser=purchaser, agent=agent, supplier=supplier, budget=budget, trade_price=total_price, url=url)

    # model = models.Announcement()

    # logging.info(model)
    # await model.save()

    # 一个中标供应商 或没找到供应商
    # if len(suppliers) == 1 or len(suppliers) == 0:
    #     total_price = 0 
    #     if len(prices) == 1:
    #         total_price = prices[0]
    #     elif len(prices) > 1:
    #         total_price = reduce(lambda x, y: float(x) + float(y), prices)
        
    #     if len(suppliers) == 0:
    #         suppliers.append('')

    #     model = models.Announcement(announcement_type=announcement_type, 
    #                                 publish_time=publish_time, 
    #                                 pro_num=pro_num, 
    #                                 title=title,
    #                                 pro_title=pro_title,
    #                                 content=pro_content,
    #                                 district=district,
    #                                 purchaser=purchaser,
    #                                 agent=agent,
    #                                 supplier=suppliers[0],
    #                                 budget=budget,
    #                                 trade_price=total_price,
    #                                 url=url,
    #                                 )
    #     logging.info(model)
    #     await model.save()
    # else:
    #     # suppliers 有多个的原因是中标分包
    #     for i, supplier in enumerate(suppliers):

    #         p = 0
    #         if len(prices) >= len(suppliers):
    #             p = prices[i]

    #         model = models.Announcement(announcement_type=announcement_type, 
    #                                     publish_time=publish_time, 
    #                                     pro_num=pro_num, 
    #                                     title=title,
    #                                     pro_title=pro_title,
    #                                     content=pro_content,
    #                                     district=district,
    #                                     purchaser=purchaser,
    #                                     agent=agent,
    #                                     supplier=supplier,
    #                                     budget=budget,
    #                                     trade_price=p,
    #                                     url=url,
    #                                     )
    #         logging.info(model)
    #         await model.save()



# if __name__ == '__main__':
#     datas = create_data(30)
#     main_spider(datas[0])