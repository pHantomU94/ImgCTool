from src.dynamicDL import DynamicImgsDownloader
import re
import time
import urllib

class BaiduImgsDownloader(DynamicImgsDownloader):

    # URL decoding table
    str_table = {
        '_z2C$q': ':',
        '_z&e3B': '.',
        'AzdH3F': '/'
    }

    trans_table = str.maketrans("wkv1ju2it3hs4g5rq6fp7eo8dn9cm0bla","abcdefghijklmnopqrstuvw1234567890")

    def __init__(self, word, dirpath = None, processNum = 16):
        super(BaiduImgsDownloader,self).__init__(word)
        self._identify = "BD"
        self._encode = "utf-8"
        self._re_url = re.compile(r'"objURL":"(.*?)"')

    def _decode(self, url):
        """解码图片URL
        解码前：
        ippr_z2C$qAzdH3FAzdH3Ffl_z&e3Bftgwt42_z&e3BvgAzdH3F4omlaAzdH3Faa8W3ZyEpymRmx3Y1p7bb&mla
        解码后：
        http://s9.sinaimg.cn/mw690/001WjZyEty6R6xjYdtu88&690
        """
        # 先替换字符串
        for key, value in self.str_table.items():
            url = url.replace(key, value)
        # 再替换剩下的字符
        return url.translate(self.trans_table)
    
    def _buildUrls(self):
        word = urllib.parse.quote(self._word)
        baseurl = r"http://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&fp=result&queryWord={word}&cl=2&lm=-1&ie=utf-8&oe=utf-8&st=-1&ic=0&word={word}&face=0&istype=2nc=1&pn={pn}&rn=60"
        time.sleep(self._delay)
        html = self._session.get(baseurl.format(
            word=word, pn=0), timeout=15).content.decode(self._encode)
        results = re.findall(r'"listNum":(\d+),', html)
        maxNum = int(results[0]) if results else 0
        urls = [baseurl.format(word=word, pn=x)
                for x in range(0, maxNum + 1, 60)]
        with open(self._srcUrlFile, "w+", encoding=self._encode) as f:
            for url in urls:
                f.write(url + "\n")
        return urls
            

# if __name__ == "__main__":
#     word_list = ["无人机"]
#     for word in word_list:
#         down = BaiduImgsDownloader(word)
#         down.start()

