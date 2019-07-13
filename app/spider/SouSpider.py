import json
from multiprocessing import Pool  #引入多进程
import requests
import re
import time
from bs4 import BeautifulSoup
import numpy as np

from config import UPLOAD_FOLDER


class HandleSou(object):
    def __init__(self):
        #使用session保存cookies信息
        #self.sou_session = requests.session()
        self.sou_session = requests.session()
        self.header = {
            'User-Agent': 'Mozilla / 5.0(Windows NT 6.1;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 75.0.3770.100Safari / 537.36'
        }
        self.sou_dict = {}

    #获取所有搜索词列表的方法
    def handle_words(self, nickname):
        dflist = []
        oldfile = UPLOAD_FOLDER + nickname + '.xlsx'
        import pandas as pd
        xlsx = pd.ExcelFile(oldfile)
        df = pd.read_excel(xlsx, 'Sheet1')
        df2 = df.fillna('没有值')
        cols = df2.values.tolist()
        from itertools import chain
        return list(chain.from_iterable(cols))

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
    def handle_all_sou(self,nickname):
        rest = []
        words = self.handle_words(nickname)
        #p = Pool()
        for w in words:
            #p.apply_async(self.handle_word_sou, args=(w,))
            r = self.handle_word_sou(w)
            rest.append(r.values())
        #p.close()
        #p.join()
        return rest

