from src.dynamicDL import DynamicImgsDownloader
import re
import time
import urllib
import base64

class VCGImgsDownloader(DynamicImgsDownloader):

    def __init__(self, word, dirpath = None, processNum = 16):
        super(VCGImgsDownloader,self).__init__(word,dirpath=dirpath,processNum=processNum)
        self._identify = "VCG"
        self._encode = "utf-8"
        self._re_url = re.compile(r'"url800":"(.*?)"')
    
    def _decode(self, url):
        url = "http:" + url
        return url 

    def _word_encode(self, word):
        encode_url = urllib.parse.quote(word)
        bytes_url = encode_url.encode("utf-8")
        str_url = base64.b64encode(bytes_url)
        str_url = str_url.decode("utf-8")
        str_url = urllib.parse.quote(str_url)
        return str_url


    def _buildUrls(self):

        baseurl = r"https://www.vcg.com/api/common/searchAllImage?params={word}&sec=%242a%2408%24AqEGKuBo5ODqOec1BUyiP.t89RqJlTFSuU%2FkQWsCp34Gmnl9gvPRq"
        maxNum = 200
        words = ["{\"phrase\":\"%s\",\"page\":\"%s\",\"uuid\":\"GH8S9D_162d8de72a3f044007b7169ad0ffab94\"}"%(self._word, x) for x in range(1,maxNum+2)]
        urls = [baseurl.format(word=self._word_encode(word)) for word in words]

        with open(self._srcUrlFile, "w+", encoding=self._encode) as f:
            for url in urls:
                f.write(url + "\n")
        return urls