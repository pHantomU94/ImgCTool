
import urllib
import requests
import os
import re
import sys
import time
import threading
from datetime import datetime as dt
from multiprocessing.dummy import Pool
from multiprocessing import Queue
from Image import Image

class ImgsDownloader(object):
    
    def __init__(self, word, dirpath = None, processNum = 30):
        if " " in word:
            pass
        self.word = word
        if not dirpath:
            dirpath = os.path.join(os.path.dirname(os.getcwd()), 'results')
        self.dirpath = dirpath 
        self.logDir = os.path.join(os.path.dirname(os.getcwd()), 'logs')
        self.logFile = os.path.join(self.logDir,"logInfo")
        self.errorFile = os.path.join(self.logDir,"errorUrl")
        if os.path.exists(self.errorFile):
            os.remove(self.errorFile)       
        self.session = requests.Session()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, sdch",
            }
        self.re_url = re.compile("")
        self.delay = 1.5    # Add a delay to prevent being banned due to frequent requests
        self.index = 0
        self.queue = Queue()
        self.messageQueue = Queue()
        self.lock = threading.Lock()
        self.prefix = "**"
    def _resolveUrl(self, url):
        """
        Resolve the urls of images from the specified link
        Input:
            url. The specified link
        """
        time.sleep(self.delay)
        html = self.session.get(url, timeout = 15)
        datas = self.re_url(html)
        imgs = [Image(x, x.split(".")[-1]) for x in datas]
        info = self.prefix + "%s image urls has been resolved."%len(imgs)
        self.messageQueue.put(info)
        self.queue.put(imgs)

    def _downImg(self, img):
        """
        Download the img according to the img_url and save img as img_type
        Input:
            img. The image info as type Image.
        """
        imgUrl = img.url
        msg = None
        try:
            time.sleep(self.delay)
            img_res = self.session.get(imgUrl,timeout = 15)
            if str(img_res.status_code)[0] == "4":
                msg = "\nDownload failed.%s : %s"%(imgUrl, img_res.status_code)
            elif "text/html" in img_res.headers["Content-Type"]:
                msg = "\nCan not open image.%s"%imgUrl       
        except Exception as e:
            msg = "\nException: %s.%s"%(str(e),imgUrl)
        finally:
            if msg:
                self.messageQueue.put(msg)
                self._saveError(msg)
            else:
                index = self._getIndex()
                info = "Downloading: %sth images.Url:%s."%(index + 1, imgUrl)
                self.messageQueue.put(info)
                filename = os.path.join(self.dirpath, self.word + str(index) + '.' + img.type)
                with open(filename, "wb") as f:
                    f.write(img_res.content)
    
    def _getIndex(self):
        """
        Get current index 
        """
        self.lock.acquire()
        try:
            return self.index
        finally:
            self.index += 1
            self.lock.release()
    
    def _saveError(self, msg):
        """
        Record the error message in errorfile
        Input: 
            msg. The error message 
        """
        self.lock.acquire()
        try:
            with open(self.errorFile, "a", encoding="utf-8") as f:
                f.write(msg)
        finally: 
            self.lock.release()
        
if __name__ == "__main__":

    pass

