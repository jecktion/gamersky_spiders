# -*- coding: utf-8 -*-
# 此程序用来抓取 的数据
import hashlib
import os

import requests
import time
import random
import re
from multiprocessing.dummy import Pool
import csv
import json
import sys
from fake_useragent import UserAgent, FakeUserAgentError


class Spider(object):
	def __init__(self):
		try:
			self.ua = UserAgent(use_cache_server=False).random
		except FakeUserAgentError:
			pass
		# self.date = '2000-01-01'
	
	def get_headers(self):
		user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0',
		               'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0',
		               'IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)',
		               'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
		               'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
		               'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)',
		               'Opera/9.52 (Windows NT 5.0; U; en)',
		               'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.2pre) Gecko/2008071405 GranParadiso/3.0.2pre',
		               'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.458.0 Safari/534.3',
		               'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.211.4 Safari/532.0',
		               'Opera/9.80 (Windows NT 5.1; U; ru) Presto/2.7.39 Version/11.00']
		user_agent = random.choice(user_agents)
		headers = {'host': "shouyou.gamersky.com",
		           'connection': "keep-alive",
		           'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
		           'accept': "*/*",
		           'referer': "http://ku.gamersky.com/2015/pal6/",
		           'accept-encoding': "gzip, deflate",
		           'accept-language': "zh-CN,zh;q=0.9"
		           }
		return headers
	
	def p_time(self, stmp):  # 将时间戳转化为时间
		stmp = float(str(stmp)[:10])
		timeArray = time.localtime(stmp)
		otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
		return otherStyleTime
	
	def replace(self, x):
		x = re.sub(re.compile('<.*?>', re.S), '', x)
		x = re.sub(re.compile('\n'), ' ', x)
		x = re.sub(re.compile('\r'), ' ', x)
		x = re.sub(re.compile('\r\n'), ' ', x)
		x = re.sub(re.compile('[\r\n]'), ' ', x)
		x = re.sub(re.compile('\s{2,}'), ' ', x)
		return x.strip()
	
	def GetProxies(self):
		# 代理服务器
		proxyHost = "http-dyn.abuyun.com"
		proxyPort = "9020"
		# 代理隧道验证信息
		proxyUser = "HI18001I69T86X6D"
		proxyPass = "D74721661025B57D"
		proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
			"host": proxyHost,
			"port": proxyPort,
			"user": proxyUser,
			"pass": proxyPass,
		}
		proxies = {
			"http": proxyMeta,
			"https": proxyMeta,
		}
		return proxies
	
	def get_comments(self, ss):  # 获取某一页游戏评论
		game_id, game_url, product_number, plat_number, page = ss
		print 'page:',page
		url = "http://cm.gamersky.com/api/getnewestcomment2"
		querystring = {
			"jsondata": "{\"pageIndex\":%d,\"pageSize\":15,\"articleId\":\"%s\",\"count\":1000}" % (page, game_id)}
		retry = 5
		while 1:
			try:
				user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0',
							   'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0',
							   'IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)',
							   'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
							   'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
							   'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)',
							   'Opera/9.52 (Windows NT 5.0; U; en)',
							   'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.2pre) Gecko/2008071405 GranParadiso/3.0.2pre',
							   'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.458.0 Safari/534.3',
							   'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.211.4 Safari/532.0',
							   'Opera/9.80 (Windows NT 5.1; U; ru) Presto/2.7.39 Version/11.00']
				user_agent = random.choice(user_agents)
				headers = {'host': "cm.gamersky.com",
				           'connection': "keep-alive",
				           'user-agent': user_agent,
				           'accept': "*/*",
				           'referer': "http://shouyou.gamersky.com/z/yys/",
				           'accept-encoding': "gzip, deflate"}
				text = requests.get(url, timeout=10, headers=headers, proxies=self.GetProxies(),
				                    params=querystring).text
				# print 'text:',text
				p = re.compile('({.*})', re.S)
				text = re.findall(p, text)[0]
				text = json.loads(text)['body']
				# print 'text 1:',text
				text = json.loads(text)['NewComment']
				# print 'text 2:',text
				p0 = re.compile(
					u'<div class="cmt-list-cont" cmtid=.*?<span class="user-time">(.*?)</span>.*?<.*? class="user-name".*?>(.*?)</.*?>.*?<.*?<p>(.*?)</p>.*?>顶\[<i>(.*?)</i>\]</a>',
					re.S|re.M)
				items = re.findall(p0, text)
				# print 'items:',items
				results = []
				for item in items:
					nick_name = item[1]
					cmt_date = '2018-' + item[0].split()[0]
					# if cmt_date < self.date:
					# 	continue
					cmt_time = '2018-' + item[0] + ':00'
					comments = self.replace(item[2])
					like_cnt = item[3]
					if like_cnt == '':
						like_cnt = '0'
					cmt_reply_cnt = '0'
					long_comment = '0'
					last_modify_date = self.p_time(time.time())
					src_url = game_url
					tmp = [product_number, plat_number, nick_name, cmt_date, cmt_time, comments, like_cnt,
					       cmt_reply_cnt, long_comment, last_modify_date, src_url]
					print '|'.join(tmp)
					results.append([x.encode('gbk', 'ignore') for x in tmp])
				if len(results) > 0:
					return results
				else:
					return None
			except Exception as e:
				retry -= 1
				if retry == 0:
					print e
					return None
				else:
					continue
	
	def get_total_page(self, game_id):  # 获取网址的总页数
		url = "http://cm.gamersky.com/api/getnewestcomment2"
		querystring = {"jsondata": "{\"pageIndex\":1,\"pageSize\":15,\"articleId\":\"%s\",\"count\":1000}" % game_id}
		retry = 5
		while 1:
			try:
				user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0',
							   'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0',
							   'IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)',
							   'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
							   'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
							   'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)',
							   'Opera/9.52 (Windows NT 5.0; U; en)',
							   'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.2pre) Gecko/2008071405 GranParadiso/3.0.2pre',
							   'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.458.0 Safari/534.3',
							   'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.211.4 Safari/532.0',
							   'Opera/9.80 (Windows NT 5.1; U; ru) Presto/2.7.39 Version/11.00']
				user_agent = random.choice(user_agents)
				headers = {'host': "cm.gamersky.com",
				           'connection': "keep-alive",
				           'user-agent': user_agent,
				           'accept': "*/*",
				           'referer': "http://shouyou.gamersky.com/z/yys/",
				           'accept-encoding': "gzip, deflate"}
				text = requests.get(url, timeout=10, headers=headers, params=querystring).text
				p = re.compile('({.*})', re.S)
				text = re.findall(p, text)[0]
				text = json.loads(text)['body']
				text = json.loads(text)['Login']
				p0 = re.compile('<em class="join-num2">(\d+?)</em>')
				total = int(re.findall(p0, text)[0])
				if total == 0:
					return None
				if total % 15 == 0:
					pagenums = total / 15
				else:
					pagenums = total / 15 + 1
				return pagenums
			except Exception as e:
				retry -= 1
				if retry == 0:
					print e
					return None
				else:
					continue
	
	def get_game_id(self, game_url):  # 获取game_id
		retry = 5
		while 1:
			try:
				text = requests.get(game_url, timeout=10).content.decode('utf-8', 'ignore')
				p0 = re.compile(u'<div id="SOHUCS" sid="(\d+?)"></div>')
				game_id = re.findall(p0, text)[0]
				return game_id
			except:
				retry -= 1
				if retry == 0:
					return None
				else:
					continue
	
	def get_all_review(self, game_url, product_number, plat_number):
		game_id = self.get_game_id(game_url)
		if game_id is None:
			print u'%s 抓取无结果' % product_number
			return None
		total_page = self.get_total_page(game_id)
		if total_page is None:
			print u'%s 无评论' % product_number
			return None
		else:
			print u'%s 共有 %d 页评价' % (product_number, total_page)
			ss = []
			for page in range(1, total_page + 1):
				ss.append([game_id, game_url, product_number, plat_number, page])
			pool = Pool(5)
			items = pool.map(self.get_comments, ss)
			pool.close()
			pool.join()
			mm = []
			for item in items:
				if item is not None:
					mm.extend(item)
			with open('data_comments_5.csv', 'a') as f:
				writer = csv.writer(f, lineterminator='\n')
				writer.writerows(mm)


if __name__ == "__main__":
	spider = Spider()
	s1 = []
	with open('data.csv') as f:
		tmp = csv.reader(f)
		for i in tmp:
			if 'http' in i[2]:
				s1.append([i[2], i[0], 'P29'])
	for s in s1:
		print s[1], s[0]
		if s[1] in ['F0000143']:
			spider.get_all_review(s[0], s[1], s[2])
