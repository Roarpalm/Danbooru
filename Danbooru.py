import requests, os, threading
from time import time, sleep
from lxml import etree
from tqdm import tqdm
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

class Spider():
    def __init__(self):
        self.header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}
        self.ids = []
        self.good_ids = []
        self.srcs = []
        self.page = range(1, 31) # 页数
        self.date = '2020-03' # 月份
        self.dir_path = os.path.abspath('.') + os.sep + self.date + '_' + str(self.page[0]) + '~' + (str(self.page[-1])) + os.sep
        self.n = 0
        self.run()

    def get_id(self):
        '''爬取id'''
        for i in self.page:
            print('正在爬取第' + str(i) + '页')
            if i == 1:
                url = f'https://danbooru.donmai.us/explore/posts/popular?date={self.date}-29&scale=month'
            else:
                url = f'https://danbooru.donmai.us/explore/posts/popular?date={self.date}-29&page={i}&scale=month'

            response = requests.get(url, headers=self.header)
            html = response.content.decode()
            bf = BeautifulSoup(html, 'lxml')
            alt = bf.find_all('img', {'class':'has-cropped-true'})
            for i in alt:
                id_ = i.get('alt')
                id_ = id_.split('#')[-1]
                self.ids.append(id_)

    def get_src(self):
        '''解析'''
        def main(id_):
            url = 'https://danbooru.donmai.us/posts/' + id_
            print('正在解析：' + url)
            response = requests.get(url, headers=self.header)
            html = response.content.decode()
            tree = etree.HTML(html)
            src = tree.xpath('//*[@id="image"]/@src')[-1]
            self.srcs.append(src)

        with ThreadPoolExecutor(max_workers=4) as e:
            [e.submit(main, id_) for id_ in self.good_ids]

    def new_dir(self):
        '''新建文件夹'''
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)

    def save(self):
        with open('ids.txt', 'r+') as f:
            old = f.read().splitlines()
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
                
            response = requests.get(src, headers=self.header, stream=True)
            with open(file_name, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            print(f'第{str(a)}张图片下载完成')

        with ThreadPoolExecutor(max_workers=4) as e:
            [e.submit(main, src) for src in self.srcs]
            
    def run(self):
        start = time()
        self.get_id()
        self.save()
        self.get_src()
        self.new_dir()
        self.download()
        print(f'用时{int((time()-start) // 60)}分{int((time()-start) % 60)}秒')


if __name__ == "__main__":
    Spider()