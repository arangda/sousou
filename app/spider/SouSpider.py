import json
import multiprocessing  #引入多进程
import requests
import re
import time
from bs4 import BeautifulSoup

class HandleSou(object):
    def __init__(self):
        #使用session保存cookies信息
        #self.sou_session = requests.session()
        self.sou_session = requests.session()
        self.header = {
            'User-Agent': 'Mozilla / 5.0(Windows NT 6.1;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 75.0.3770.100Safari / 537.36'
        }
        self.sou_dict = {}

    #获取全国所有城市列表的方法
    def handle_city(self):
        city_search = re.compile(r'www\.lagou\.com\/.*\/">(.*?)</a>')
        city_url = 'https://www.lagou.com/jobs/allCity.html'
        city_result = self.handle_request(method='GET', url=city_url)
        #self.city_list = city_search.findall(city_result)
        #lagou.lagou_session.cookies.clear()
    def handle_word_sou(self,word):
        first_request_url = "http://m.baidu.com/s"
        try:
            kv = {'word': word}
            r = self.handle_request(method="GET", url=first_request_url, info=kv)
            soup = BeautifulSoup(r, 'html.parser')
            res = soup.find_all(class_="ec-tuiguang-color-change")
            self.sou_dict['搜索词:'] = word
            n = 1
            for i in res:
                ret = i.find_parent().contents[0].contents[0].get_text()
                self.sou_dict[n] = ret
                n = n+1
            return self.sou_dict
        except:
            print("爬取失败")
    def handle_request(self, method, url, data=None, info=None):
        response = ""
        while True:
            if method == "GET":
                response = requests.get(url, headers=self.header, params=info, verify=False)
            elif method == "POST":
                response = requests.post(url, headers=self.header, params=info, verify=False)
            response.encoding = 'utf-8'
            return response.text


