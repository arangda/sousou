import asyncio
import json
from multiprocessing import Pool  #引入多进程

import aiohttp
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
        self.sou_process = [0]

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

    def handle_word_sou(self,content):
        sou_list = []
        soup = BeautifulSoup(content, 'html.parser')
        res = soup.find_all(class_="ec-tuiguang-color-change")
        n = 1
        for i in res:
            ret = i.find_parent().contents[0].contents[0].get_text()
            sou_list.append(str(n) + ret)
            n = n+1
        return sou_list
    async def handle_fetch(self,session,word):
        url = "http://m.baidu.com/s?word=" + word
        async with session.get(url,ssl=False) as response:
            return await response.text()
        '''
        这是requests爬取
        first_request_url = "http://m.baidu.com/s"
        try:
            kv = {'word': word}
            con = self.handle_request(method="GET", url=first_request_url, info=kv)
            return con
        except:
            print("爬取失败")
        '''
    # requests处理函数
    def handle_request(self, method, url, data=None, info=None):
        response = ""
        while True:
            if method == "GET":
                response = requests.get(url, headers=self.header, params=info, verify=False)
            elif method == "POST":
                response = requests.post(url, headers=self.header, params=info, verify=False)
            response.encoding = 'utf-8'
            return response.text

    async def main(self,words):
        tasks = []
        async with aiohttp.ClientSession() as session:
            for w in words:
                #tasks.append(self.handle_fetch(session,w))
                #加回调函数
                task = asyncio.ensure_future(self.handle_fetch(session,w))
                task.add_done_callback(self.get_it)
                tasks.append(task)
            return await asyncio.gather(*tasks)
    # task中的回调函数
    def get_it(self,future):
        #ret = future.result()
        #yy = self.handle_word_sou(ret)
        self.sou_process.append(1)

    def return_result(self,nickname,word):
        rest = []
        tb = time.time()
        if word is None:
            words = self.handle_words(nickname)
        else:
            words = []
            words.append(word)
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        loop = asyncio.get_event_loop()
        htmls = loop.run_until_complete(self.main(words))
        for hm in htmls:
            gt = self.handle_word_sou(hm)
            rest.append(gt)
        te = time.time()
        rest.append(str(te-tb))
        return rest

