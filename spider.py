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

def create_data(index, title, sitewebId):
    data = dict()
    data['pageIndex'] = str(index)
    data['pageSize'] = '15'
    data['stockTypes'] = ''	
    data['channelCode'] = '0008'
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

        data = create_data('1', params_data.get('title'), params_data.get('sitewebId'))
        district = parameters.all_district.get(params_data.get('sitewebId'))
        await main_spider(data, district)
    else:
        for index in range(1, int(arr[0])):
            params_data = arr[1]

            data = create_data(index, params_data.get('title'), params_data.get('sitewebId'))
            district = parameters.all_district.get(params_data.get('sitewebId'))
            await main_spider(data, district)


def get_page_count(params):
    logging.info(params)

    time.sleep(1)

    url = 'http://www.gdgpo.gov.cn/queryMoreCityCountyInfoList2.do'
    b_params = bytes(parse.urlencode(params), 'utf-8')

    html = request.urlopen(url, data=b_params, timeout=10)
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
    asyncio.sleep(1)

    logging.info(data)

    # params = b'stockTypes=&channelCode=0008&sitewebId=4028889705bebb510105bec068b00003&title=%E5%A4%A7%E5%AD%A6&stockNum=&purchaserOrgName=&performOrgName=&stockIndexName=&operateDateFrom=2015-01-01&operateDateTo='

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
            if href.count('showNotice/id/') == 1:
                # 开始采集公告内容网页
                await request_content(href, district)
    except Exception as error:
        logging.info('<<<<<<<<<<<请求列表error: %s' % error)
        model = models.Failure_requests(params=str(data), url=url, failure_type=1, district=district, error_msg=str(error))
        await model.save()
        

async def request_content(href, district):
    logging.info('==============================')

    url = base_URL + href
    # url = 'http://www.gdgpo.gov.cn/showNotice/id/40288ba96269beb201626be8ab54496e.html' # 3个中标供应商测试url
    # url = 'http://www.gdgpo.gov.cn/showNotice/id/40288ba95debddc9015df356a76c3088.html' # 项目分包成交金额测试url
    # url = 'http://www.gdgpo.gov.cn/showNotice/id/40288ba96079352601609c3e44b02017.html'
    # url = 'http://www.gdgpo.gov.cn/showNotice/id/40288ba95113b8ce015113f349d9020e.html'
    # url = 'http://www.gdgpo.gov.cn/showNotice/id/297e55e84c5f33d6014c6e2afd513871.html' # 15年样式的url
    # url = 'http://www.gdgpo.gov.cn/showNotice/id/40288ba94f1d14e6014f29dc40d03e99.html'
    # url = 'http://www.gdgpo.gov.cn/showNotice/id/40288ba95e1ebb6a015e27d63e9573e8.html'
    # url = 'http://www.gdgpo.gov.cn/showNotice/id/297e55e84ebb3b8e014ece6e09f86a7f.html'
    # url = 'http://www.gdgpo.gov.cn/showNotice/id/40288ba94f5ff01f014f67cfbc92630b.html'
    # url = 'http://www.gdgpo.gov.cn/showNotice/id/297e55e84ebb3b8e014ece70c9226b1d.html'
    # url = 'http://www.gdgpo.gov.cn/showNotice/id/40288ba962b4fd6d0162b88ae0da2db3.html'
    logging.info('url = %s' % url)
    
    try:
        html = request.urlopen(url, timeout=10)
        await content_spider(html, url, district)

    except urllib.error.HTTPError as error:
        logging.info('******request content http error : %s' % error)

        model = models.Failure_requests(params='', url=href, failure_type=2, district=district, error_msg=str(error))
        await model.save()

    except urllib.error.URLError as error:
        logging.info('******request content url error : %s' % error)

    except Exception as error:
        logging.info('******other Exception: %s', error)

        model = models.Failure_requests(params='', url=href, failure_type=2, district=district, error_msg=str(error))
        await model.save()

async def content_spider(html, url='', district=''):

    time.sleep(2)

    announcement_type = 0
    publish_time = ''
    pro_num = ''
    pro_title = ''
    content = ''
    purchaser = ''
    agent = ''
    budget = '0'

    bs_obj = BeautifulSoup(html, 'lxml')

    title_node = bs_obj.body.div.find_all(attrs={"class": 'zw_c_c_title'})
    if len(title_node) > 0:
        title = title_node[0].text
        logging.info('title = %s' % title)

    div = bs_obj.body.div.find_all(attrs={"class": 'zw_c_c_cont'})
    if len(div) > 0:
        # 采购人
        purchaser = div[0].text
        purchaser = purchaser[purchaser.find('受') + 1:purchaser.find('的委托')]
        logging.info('%s %s' % (replace_text[4], purchaser))

        # 2015的采购项目名
        temp_title = div[0].text
        index = div[0].text.find('采购项目名称：')
        temp_title = temp_title[index + 7:]
        temp_title = temp_title[:temp_title.find('。')] 
        pro_title = temp_title
        logging.info('%s %s' % (replace_text[1], pro_title))


    tr_nodes = bs_obj.body.tbody.find_all('tr')
    prices = []
    if len(tr_nodes) == 2:
        tr = tr_nodes[0]
        td = tr.find_all('td')[-1].text
        if td.count('成交金额（元）') == 1:
            tr1 = tr_nodes[1]
            trade_price = tr1.find_all('td')[-1].text
            trade_price = ''.join(filter(lambda ch: ch in '0123456789.', trade_price))
            prices.append(trade_price)
            logging.info('中标、成交金额（元） %s' % trade_price)
    elif len(tr_nodes) > 2:
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
            trade_price = p_node.u.text
            trade_price = ''.join(filter(lambda ch: ch in '0123456789.', trade_price))
            prices.append(trade_price)
            logging.info('中标、成交金额（元） %s' % trade_price)

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

        if replace_text[2] in span_node.text:
            budget = span_node.text.replace(replace_text[2], '')
            budget = budget.replace(',', '')
            logging.info('%s %s' % (replace_text[2], budget))

        if replace_text[3] in span_node.text:
            publish_time = span_node.text.replace(replace_text[3], '')
            logging.info('%s %s' % (replace_text[3], publish_time))

        if replace_text[5] in span_node.text:
            agent = span_node.text.replace(replace_text[5], '')
            logging.info('%s %s' % (replace_text[5], agent))
        
    # 一个中标供应商
    if len(suppliers) == 1 or len(suppliers) == 0:
        total_price = 0
        if len(prices) == 1:
            total_price = prices[0]
        elif len(prices) > 1:
            total_price = reduce(lambda x, y: float(x) + float(y), prices)
        
        if len(suppliers) == 0:
            suppliers.append('')

        model = models.Announcement(announcement_type=0, 
                                    publish_time=publish_time, 
                                    pro_num=pro_num, 
                                    title=title,
                                    pro_title=pro_title,
                                    content=content,
                                    district=district,
                                    purchaser=purchaser,
                                    agent=agent,
                                    supplier=suppliers[0],
                                    budget=budget,
                                    trade_price=total_price,
                                    url=url,
                                    )
        logging.info(model)
        await model.save()
    else:
        # suppliers 有多个的原因是中标分包
        for i, supplier in enumerate(suppliers):
            model = models.Announcement(announcement_type=0, 
                                        publish_time=publish_time, 
                                        pro_num=pro_num, 
                                        title=title,
                                        pro_title=pro_title,
                                        content=content,
                                        district=district,
                                        purchaser=purchaser,
                                        agent=agent,
                                        supplier=supplier,
                                        budget=budget,
                                        trade_price=prices[i],
                                        url=url,
                                        )
            logging.info(model)
            await model.save()



# if __name__ == '__main__':
#     datas = create_data(30)
#     main_spider(datas[0])