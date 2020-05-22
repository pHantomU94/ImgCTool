from src.dynamicDL import DynamicImgsDownloader
import re
import time
import urllib

class BingImgsDownloader(DynamicImgsDownloader):

    def __init__(self, word, dirpath = None, processNum = 16):
        super(BingImgsDownloader,self).__init__(word,dirpath=dirpath,processNum=processNum)
        self._identify = "Bing"
        self._encode = "utf-8"
        self._re_url = re.compile(r'"contentUrl":"(.*?)"')

    def _buildUrls(self):
        word = urllib.parse.quote(self._word)
        step = 25
        baseurl = r"https://cn.bing.com/images/api/custom/search?q={word}&count=25&offset={pn}&skey=_nNvmSzcI9YZ8urB3e7umKHYcL-15-HDoEXKS-FTyo8"
        time.sleep(self._delay)
        html = self._session.get(baseurl.format(
            word=word, pn=0), timeout=15).content.decode(self._encode)
        print(html)
        results = re.findall(r'"totalEstimatedMatches":(\d+),', html)
        maxNum = int(results[0]) if results else 0
        urls = [baseurl.format(word=word, pn=x)
                for x in range(0, maxNum + 1, step)]

        with open(self._srcUrlFile, "w+", encoding=self._encode) as f:
            for url in urls:
                f.write(url + "\n")
        return urls