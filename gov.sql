-- schema.sql
-- 如果存在先删除库
drop database if exists gov;
-- 建库
create database gov;

use gov;

grant select, insert, update, delete on gov.* to 'www-data'@'localhost' identified by 'www-data';

-- 建表
create table announcements (
    `announcement_type` Int not null,  -- 公告类型
	`publish_time` text(50), -- 发布时间
    `pro_num` text(100), -- 项目编号
	`title` text(500), -- 公告标题
    `pro_title` text(500), -- 项目名称
	`content` text(500), -- 项目内容
	`district` text(100), -- 地区
    `purchaser` text(200), -- 采购人
    `agent` text(200), -- 代理商
    `supplier` text(200), -- 中标人
    `budget` text(100), -- 预算
    `trade_price` text(200), -- 中标价格
    `url` text(200), -- 原文链接
	`id` Int not null auto_increment,
   	primary key (`id`)
) engine=innodb default charset=utf8;


create table failure_requests (
    `failure_type` Int not null, -- 0=页码失败，1=列表失败，2=内容页失败
    `url` text(500), -- url
    `params` text(500),
    `district` text(50), -- 所属地区
    `id` Int not null auto_increment,
    primary key (`id`)
) engine=innodb default charset=utf8;
