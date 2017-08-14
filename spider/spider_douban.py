# -*- coding: utf-8 -*-
import re
import urllib2

class DoubanSpider(object):
	def __init__(self):

		self.page=1
		self.num=0
		self.url="https://movie.douban.com/top250?start={num}&filter="
		self._top_num=1
		self.data=[]
		self.critic=[]


	def get_page(self,page):
		"""
		抓取数据
		"""
		url = self.url
		page_data=urllib2.urlopen(url.format(num=(page - 1)*25)).read().decode("utf-8")
		return page_data

	def get_title(self,page_data):
		"""
		根据抓取页面内容提取电影名,及影评
		"""
		title=re.findall(r'<span\s+class="title">(.*?)</span>',page_data,re.S)
		critics=re.findall(r'<span\s+class="inq">(.*?)</span>',page_data,re.S)
		for item in title:
			if item.find("&nbsp") == -1:
				#self.data.append("Top"+str(self._top_num)+" "+item)
				self.data.append(item)
				self._top_num += 1

		for critic in critics:
			self.critic.append(critic)

	def start_spider(self):
		while self.page <= 4:
			page_data=self.get_page(self.page)
			title=self.get_title(page_data)
			self.page += 1

def main():
	douban=DoubanSpider()
	douban.start_spider()


	for i in range(100):
		print "Top %d, %s" % (i+1,douban.data[i])
		print u"   影评：%s" % douban.critic[i]



if __name__ == '__main__':
	main()


