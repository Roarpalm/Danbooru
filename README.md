[https://danbooru.donmai.us](https://danbooru.donmai.us) 爬虫，批量下载排行榜

## Danbooru.py
更改 ```self.page``` 即为页数

使用 ```requests``` 库

## ids.txt
保存已爬取的图片id，避免重复

- - - -

#### 2020年5月5日第一次更新：
![zhenxiang](imgs/wangjingze.gif?raw=true)

#### 2020年5月6日第二次更新：
这个网站的服务器简直不设防，开更多线程更暴力地爬取，速度很快

#### 2020年5月6日第三次更新：
加了个 ```month_list``` 函数，输入开始月份和结束月份生成月份列表，```Spider``` 里默认爬100页，这样爬取就更暴力了