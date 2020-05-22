from src.dynamicDL import DynamicImgsDownloader
import re
import time
import urllib

class SoImgsDownloader(DynamicImgsDownloader):

    def __init__(self, word, dirpath = None, processNum = 16):
        super(SoImgsDownloader,self).__init__(word,dirpath=dirpath,processNum=processNum)
        self._identify = "SO"
        self._encode = "utf-8"
        self._re_url = re.compile(r'"img":"(.*?)"')
    
    def _decode(self, url):
        url = url.replace('\\','')
        return url 

    def _buildUrls(self):
        word = urllib.parse.quote(self._word)
        step = 60
        baseurl = r"https://image.so.com/j?q={word}&pd=1&pn=60&correct={word}&sn={pn}"
        time.sleep(self._delay)
        html = self._session.get(baseurl.format(
            word=word, pn=0), timeout=15).content.decode(self._encode)
        results = re.findall(r'"total":(\d+),', html)
        maxNum = int(results[0]) if results else 0
        urls = [baseurl.format(word=word, pn=x)
                for x in range(0, maxNum + 1, step)]

        with open(self._srcUrlFile, "w+", encoding=self._encode) as f:
            for url in urls:
                f.write(url + "\n")
        return urls