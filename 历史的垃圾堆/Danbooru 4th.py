import requests, os, threading, datetime
from requests import adapters
from time import time
from lxml import etree
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from dateutil.relativedelta import relativedelta

class Spider():
    def __init__(self, x):
        self.header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}
        self.session = requests.Session()
        self.session.mount('https://danbooru.donmai.us', adapters.HTTPAdapter(pool_connections=1, pool_maxsize=8))
        self.ids = []
        self.good_ids = []
        self.srcs = []
        self.page = range(1, 101) # 页数
        self.date = x # 月份
        self.dir_path = os.path.abspath('.') + os.sep + self.date + '_' + str(self.page[0]) + '~' + str(self.page[-1]) + os.sep
        self.n = 0
        self.run()

    def get_id(self):
        '''爬取'''
        def main(i):
            print('正在爬取第' + str(i) + '页')
            if i == 1:
                url = f'https://danbooru.donmai.us/explore/posts/popular?date={self.date}-01&scale=month'
            else:
                url = f'https://danbooru.donmai.us/explore/posts/popular?date={self.date}-01&page={i}&scale=month'

            response = self.session.get(url, headers=self.header)
            html = response.content.decode()
            bf = BeautifulSoup(html, 'lxml')
            alt = bf.find_all('img', {'class':'has-cropped-true'})
            for i in alt:
                id_ = i.get('alt')
                id_ = id_.split('#')[-1]
                self.ids.append(id_)
        
        with ThreadPoolExecutor(max_workers=8) as e:
            [e.submit(main, i) for i in self.page]

    def get_src(self):
        '''解析'''
        def main(id_):
            url = 'https://danbooru.donmai.us/posts/' + id_
            print('正在解析：' + url)
            response = self.session.get(url, headers=self.header)
            html = response.content.decode()
            tree = etree.HTML(html)
            src = tree.xpath('//*[@id="image"]/@src')[-1]
            self.srcs.append(src)

        with ThreadPoolExecutor(max_workers=8) as e:
            [e.submit(main, id_) for id_ in self.good_ids]

    def new_dir(self):
        '''新建文件夹'''
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)

    def save(self):
        '''保存'''
        if not os.path.exists('ids.txt'):
            e = open('ids.txt', 'a')
            e.close()
        with open('ids.txt', 'r+') as f:
            old = f.read().splitlines()
            f.write(self.date + '_' + str(self.page[0]) + '~' + str(self.page[-1]) + '\n')
            for i in self.ids:
                if i not in old:
                    f.write(i + '\n')
                    self.good_ids.append(i)
            print(f'新增{len(self.good_ids)}张图片')

    def download(self):
        '''下载'''
        def main(src):
            self.n += 1
            a = self.n
            if src.split('.')[-1] == 'jpg':
                file_name = self.dir_path + str(self.n) + '.jpg'
            if src.split('.')[-1] == 'mp4':
                file_name = self.dir_path + str(self.n) + '.mp4'
            if src.split('.')[-1] == 'webm':
                file_name = self.dir_path + str(self.n) + '.webm'
            response = self.session.get(src, headers=self.header)
            with open(file_name, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            print(f'第{str(a)}张图片下载完成')

        with ThreadPoolExecutor(max_workers=8) as e:
            [e.submit(main, src) for src in self.srcs]
            
    def run(self):
        start = time()
        self.get_id()
        self.save()
        self.get_src()
        self.new_dir()
        self.download()
        print(f'用时{int((time()-start) // 60)}分{int((time()-start) % 60)}秒')

def month_list(begin_date, end_date):
    date_list = []
    begin_date = datetime.datetime.strptime(begin_date, "%Y-%m")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m")
        date_list.append(date_str)
        begin_date += relativedelta(months=1)
    
    for x in date_list:
        Spider(x)

if __name__ == "__main__":
    month_list('2020-04', '2020-04')