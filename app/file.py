import os
import re
import time

from flask import request
import numpy as np

from app import app
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER


class file(object):

    def __init__(self):
        self.date = time.strftime("%Y-%m-%d",time.localtime())

    def allowed_file(self,filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    def upload(self, dirs):
        for dr in dirs:
            newdir = os.path.join(app.config['UPLOAD_FOLDER'], dr+'/')
            if os.path.isdir(newdir):
                file = request.files.get(dr)
                if file and self.allowed_file(file.filename):
                    filename = dr + '_' + self.date + '.' + file.filename.rsplit('.', 1)[1]
                    file.save(os.path.join(newdir, filename))
            else:
                os.mkdir(newdir)

    def walk(self, dirs):
        dt = {}
        for dr in dirs:
            newdir = os.path.join(app.config['UPLOAD_FOLDER'], dr+'/')
            if os.path.isdir(newdir):
                dt[dr] = os.listdir(newdir)
            else:
                os.mkdir(newdir)
        return dt

    def read(self):
        oldfile = UPLOAD_FOLDER + 'swt/' + 'swt_2019-07-22.xls'
        import pandas as pd
        xlsx = pd.ExcelFile(oldfile)
        df = pd.read_excel(xlsx, 'sheet1', usecols="D,E,F,G", skiprows=[0, 1, 2], names=['D', 'E', 'F', 'G'])
        df['engine'] = df.apply(self.what_engine, axis=1)
        df['zhuan'] = df.apply(self.is_zhuan, axis=1)
        newdf = df.groupby('engine').agg({'D':'size','zhuan':'sum'})
        print(newdf)

    def is_zhuan(self,data):
        zc = str(data['G'])
        if '转' in zc:
            return 1
    def what_engine(self, data):
        eg = str(data['D'])
        if 'ada.baidu.com' in eg:
            return '百度'
        elif 'sg5g.' in eg or 'sogou.com' in eg:
            return '搜狗'
        elif 'smfuke.' in eg:
            return '神马'
        elif 'A360' in eg or 'B360' in eg:
            return '360'
        elif 'meiyou' in eg:
            return '美柚'
        else:
            return 'nan'

    def read_baidu(self):
        oldfile = UPLOAD_FOLDER + 'baidu/' + 'baidu_2019-07-23.csv'
        import pandas as pd
        #xlsx = pd.ExcelFile(oldfile)
        df = pd.read_csv(oldfile, encoding="GB2312", skiprows=7, usecols=[0,2,3,4,5])
        df['展现'] = pd.to_numeric(df['展现'], errors='coerce')
        df['点击'] = pd.to_numeric(df['点击'], errors='coerce')
        df['消费'] = pd.to_numeric(df['消费'], errors='coerce')
        print("****百度****")
        print(df.groupby('账户').agg({'展现':np.sum,'点击':np.sum,'消费':np.sum}))

    def read_sogou(self):
        oldfile = UPLOAD_FOLDER + 'sogou/' + 'sogou_2019-07-23.csv'
        import pandas as pd
        df = pd.read_csv(oldfile, encoding="GB2312", skiprows=[1], usecols=[2,3,4,5,6])
        df['展示数'] = pd.to_numeric(df['展示数'], errors='coerce')
        df['点击数'] = pd.to_numeric(df['点击数'], errors='coerce')
        df['消耗'] = pd.to_numeric(df['消耗'], errors='coerce')
        print("****搜狗****")
        print(df.groupby('账户').agg({'展示数':np.sum,'点击数':np.sum,'消耗':np.sum}))

    def read_shenma(self):
        oldfile = UPLOAD_FOLDER + 'shenma/' + 'shenma_2019-07-23.csv'
        import pandas as pd
        df = pd.read_csv(oldfile, encoding="GB2312", skiprows=0, usecols=[1,2,3,4,5])
        df['展现量'] = pd.to_numeric(df['展现量'], errors='coerce')
        df['点击量'] = pd.to_numeric(df['点击量'], errors='coerce')
        df['消费'] = pd.to_numeric(df['消费'], errors='coerce')
        print("****神马****")
        print(df.groupby('账户').agg({'展现量':np.sum,'点击量':np.sum,'消费':np.sum}))

    def read_360(self):
        oldfile = UPLOAD_FOLDER + '360/' + '360_2019-07-23.csv'
        import pandas as pd
        df = pd.read_csv(oldfile, encoding="GB2312", skiprows=0, usecols=[1,3,4,5,7])
        df['展示次数'] = pd.to_numeric(df['展示次数'], errors='coerce')
        df['点击次数'] = pd.to_numeric(df['点击次数'], errors='coerce')
        df['总费用'] = pd.to_numeric(df['总费用'], errors='coerce')
        print("****360****")
        newdf = df.groupby('推广账户').agg({'展示次数': np.sum, '点击次数': np.sum, '总费用': np.sum})
        newdf.loc['汇总'] = newdf.apply(lambda x:x.sum())
        print(newdf)


if __name__ == '__main__':
    f = file()
    f.read()
    f.read_baidu()
    f.read_sogou()
    f.read_shenma()
    f.read_360()
