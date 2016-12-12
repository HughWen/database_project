# Database project 2016

## 需求分析
该项目设计了一个热点监控系统，其能够动态地抓取定量的媒体报告话题分析并把数据存入数据库中。另外还设置了用户注册和登录系统。从数据库需求上来分析，该系统需要数据库储存用户信息，需要数据库储存抓取到的话题信息。从整个系统来讲，该系统是基于flask搭建的网站。其主体设计可分为三块：数据库模块设计，网站模块设计，爬虫模块设计。

## 数据库设计
该项目总共使用了三个数据库：sqlite, mongodb, redis。其中sqlite 用于储存用户信息，mongodb用于储存爬取的标签信息，redis用于完成爬虫的并发请求。
其中数据库设计如下：
sqlite 包含两张表：User 和 Role。其中User 用于储存用户的具体信息，Role用于储存role信息（即各个role之间的。两者之间以User中的role_id作为外键来连接。
mongodb 属于Nosql, 没有严谨的数据结构，其适合储存json格式的数据。
redis 也属于Nosql，没有严禁的数据结构。其因为在启动的过程中会把所有数据读入内存，故数据操作极快，常用与作爬虫并发控制处理。

## 数据字典
sqlite
User 表：
|id	|username	|role\_id	|email	|password_hash	|confirmed	|about_me	|last_seen	|location	|member\_since	|name	|avatar_hash|
|-----	|:------:	|:-----:	|:------:	|:--------:	|:----------:	|:--------:	|:--------:	|:-----:	|:----:	|:-------:	|	---------:|
|1	|ww0	|2	|11@qq.com	|******	|1	|good boy	|12-12	|sustc	|12-10	|zengxiaoxian	|ef23	|
