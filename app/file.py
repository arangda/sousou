import os
import re
import time

from flask import request

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
        oldfile = UPLOAD_FOLDER + 'swt/' + 'swt_'+ self.date + '.xls'
        import pandas as pd
        xlsx = pd.ExcelFile(oldfile)
        df = pd.read_excel(xlsx, 'sheet1', usecols="D,E,F,G", skiprows=[0, 1, 2], names=['D', 'E', 'F', 'G'])
        zzz = 0
        from collections import defaultdict
        sss = defaultdict(list)
        for i in df['D']:
            if '&C-' in str(i):
                sss['C'].append(i)
            if '&E-' in str(i):
                sss['E'].append(i)
            if '&F-' in str(i):
                sss['F'].append(i)
            if '&A-' in str(i):
                sss['A'].append(i)

        for i in df['G']:
            if '转' in str(i):
                zzz += 1
        for kk,vv in sss.items():
            print(kk +'---' + str(len(vv)))
        print(zzz)

if __name__ == '__main__':
    f = file()
    f.read()
