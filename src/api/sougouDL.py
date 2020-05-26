from src.dynamicDL import DynamicImgsDownloader
import re
import time
import urllib

class SougouImgsDownloader(DynamicImgsDownloader):

    def __init__(self, word, dirpath = None, processNum = 16):
        super(SougouImgsDownloader,self).__init__(word,dirpath=dirpath,processNum=processNum)
        self._identify = "Sougou"
        self._encode = "GBK"
        self._re_url = re.compile(r'"ori_pic_url":"(.*?)"')
    
    def _buildUrls(self):
        word = urllib.parse.quote(self._word)
        step = 48
        baseurl = r"https://pic.sogou.com/pics?query={word}&start={pn}&reqType=ajax"
        time.sleep(self._delay)
        html = self._session.get(baseurl.format(
            word=word, pn=0), timeout=15).content.decode(self._encode)
        results = re.findall(r'"maxEnd":(\d+),', html)
        maxNum = int(results[0]) if results else 0
        while(True):
            checkurl = baseurl.format(word=word,pn = maxNum)
            checkhtml = self._session.get(checkurl, timeout=15).content.decode(self._encode)
            checkres = re.findall(r'"maxEnd":(\d+),', checkhtml)
            if checkres:
                if int(checkres[0]) > maxNum:
                    maxNum = int(checkres[0])
                else:
                    break
            else:
                break
    
        urls = [baseurl.format(word=word, pn=x)
                for x in range(0, maxNum + 1, step)]

        with open(self._srcUrlFile, "w+", encoding=self._encode) as f:
            for url in urls:
                f.write(url + "\n")
        return urls