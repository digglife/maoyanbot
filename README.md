## 猫眼爬虫

基于 Scrapy 框架的猫眼爬虫，主要用于爬取电影的 **评分** 和 **票房**。

### 用法

```bash
$ pip install -r requirements

# 抓取可用代理。
# 如不用代理，可以注释 settings.py 中的如下内容

# DOWNLOADER_MIDDLEWARES = {
#     'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
#     'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
# }

$ scrapy crawl proxy

# 抓取猫眼电影评分和票房数据，保存为JsonLine文件。
$ scrapy crawl movie
```

### 解释

#### 1. 网络字体反爬的破解方法

猫眼为了保护重要数据，对评分和票房数据采用了 网络字体反爬机制。概括而言，就是 HTML 中的数据返回无对应字符的 UNICODE 代码（UNICODE 私人使用区），
然后使用网络字体在浏览器中渲染出代码对应的数字。

每次请求电影页面，下载的 woff 都不同，每个 woff 中的代码对应的数字也都不同。比如，网络字体 A 中，`\uE851` 对应的是 数字 0， 网络字体 B 中 数字0 对应的代码可能是 `\uE748`，没有规律。
但是字体的字形数据 (glyphs) 是不变的，我们只要获取猫眼的任一 woff，找出字形和数字的对应关系，保存为字典，然后每次抓取时，解析出新字体中的字形，在字典中查询即可获取真正的数字。

以上的 Python 实现在 [`font.py`](maoyan/font.py) 中。

#### 2. 使用代理轮询避免 IP 屏蔽

猫眼对同一 IP 的频繁请求会采取屏蔽措施，所以可以用代理在一定程度上避免。[`proxy.py`](maoyan/spiders/proxy.py)是一个用来爬取有效代理的爬虫， 生成的爬虫会保存在 [proxies.txt](proxies.txt) 里。

注意，本爬虫会在爬取之后会测试代理的可用性，阻塞性请求。

如不用代理，可以注释 [`settings.py`](maoyan/settings.py) 中的如下内容：

```python
DOWNLOADER_MIDDLEWARES = {
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
}
```

#### 3. JSON Pipeline

爬取的数据自动保存为 [`jsonline`](movie.jsonline) 文件，为此配置了一个 [pipeline](maoyan/pipelines.py)。



