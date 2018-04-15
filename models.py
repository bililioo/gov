#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Ben'

import orm
from orm import Model, StringField, BooleanField, FloatField, TextField, IntegerField

class Announcement(Model):
    __table__ = 'announcements'

    announcement_type = IntegerField()
    publish_time = StringField(ddl='text(50)')
    pro_num = StringField(ddl='text(100)')
    title = StringField(ddl='text(500)')
    pro_title = StringField(ddl='text(500)')
    content = StringField(ddl='text(500)')
    district = StringField(ddl='text(100)')
    purchaser = StringField(ddl='text(200)')
    agent = StringField(ddl='text(200)')
    supplier = StringField(ddl='text(200)')
    budget = StringField(ddl='text(100)')
    trade_price = StringField(ddl='text(200)')
    url = StringField(ddl='text(200)')
    id = StringField(primary_key=True ,ddl='Int')


    # `type` Int not null,  -- 公告类型
	# `publish_time` char, -- 发布时间
    # `pro_num` text(100), -- 项目编号
	# `title` text(500), -- 公告标题
    # `pro_title` text(500), -- 项目名称
	# `content` text(500), -- 项目内容
	# `district` text(100), -- 地区
    # `purchaser` text(200), -- 采购人
    # `agent` text(200), -- 代理商
    # `supplier` text(200), -- 中标人
    # `budget` text(100), -- 预算
    # `trade_price` text(200), -- 中标价格
    # `url` text(200), -- 原文链接
	# `id` Int not null auto_increment,

class Failure_requests(Model):
    __table__ = 'failure_requests'

    failure_type = IntegerField()
    url = StringField(ddl='text(500)')
    params = StringField(ddl='text(500)')
    district = StringField(ddl='text(50)')
    id = StringField(primary_key=True ,ddl='Int')

