from ImgDL import ImgsDownloader, re, time, urllib, Image

class BaiduImgsDownloader(ImgsDownloader):

    # URL decoding table
    str_table = {
        '_z2C$q': ':',
        '_z&e3B': '.',
        'AzdH3F': '/'
    }

    char_table = {
        'w': 'a',
        'k': 'b',
        'v': 'c',
        '1': 'd',
        'j': 'e',
        'u': 'f',
        '2': 'g',
        'i': 'h',
        't': 'i',
        '3': 'j',
        'h': 'k',
        's': 'l',
        '4': 'm',
        'g': 'n',
        '5': 'o',
        'r': 'p',
        'q': 'q',
        '6': 'r',
        'f': 's',
        'p': 't',
        '7': 'u',
        'e': 'v',
        'o': 'w',
        '8': '1',
        'd': '2',
        'n': '3',
        '9': '4',
        'c': '5',
        'm': '6',
        '0': '7',
        'b': '8',
        'l': '9',
        'a': '0'
    }

    def __init__(self, word, dirpath = None, processNum = 16):
        super(BaiduImgsDownloader,self).__init__(word)
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
        return url.translate(self.char_table)
    
    def _buildUrls(self):
        word = urllib.parse.quote(self._word)
        url = r"http://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&fp=result&queryWord={word}&cl=2&lm=-1&ie=utf-8&oe=utf-8&st=-1&ic=0&word={word}&face=0&istype=2nc=1&pn={pn}&rn=60"
        time.sleep(self._delay)
        html = self._session.get(url.format(
            word=word, pn=0), timeout=15).content.decode('utf-8')
        results = re.findall(r'"listNum":(\d+),', html)
        maxNum = int(results[0]) if results else 0
        urls = [url.format(word=word, pn=x)
                for x in range(0, maxNum + 1, 60)]
        with open(self._srcUrlFile, "w+", encoding="utf-8") as f:
            for url in urls:
                f.write(url + "\n")
        return urls
            

if __name__ == "__main__":
    word_list = ["无人机"]
    for word in word_list:
        down = BaiduImgsDownloader(word)
        down.start()