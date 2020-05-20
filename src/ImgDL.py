import urllib
import requests
import os
import re
import sys
import time
import threading
from datetime import datetime
from multiprocessing.dummy import Pool
from multiprocessing import Queue
from Image import Image
from abc import ABC, abstractmethod

class ImgsDownloader(ABC):
    
    def __init__(self, word, dirpath = None, processNum = 16):
        if " " in word:
            pass
        self._word = word
        if not dirpath:
            # dirpath = os.path.join(os.path.dirname(os.getcwd()), 'results')
            dirpath = os.path.join(os.getcwd(), 'results')
        self._dirpath = dirpath 
        self._logDir = os.path.join(os.getcwd(), 'logs')
        self._srcUrlFile = os.path.join(self._logDir, 'srcUrl')
        self._logFile = os.path.join(self._logDir,"logInfo")
        self._errorFile = os.path.join(self._logDir,"errorUrl")
        if os.path.exists(self._errorFile):
            os.remove(self._errorFile)       
        self._session = requests.Session()
        self._session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, sdch",
            }
        self._re_url = re.compile("")   
        self._delay = 1.5   # Add a delay to prevent being banned due to frequent requests
        self._index = 0     # image file index for save 
        self._pool = Pool(processNum)
        self._queue = Queue()   # to save and read image src url
        self._messageQueue = Queue()    # message queue for log info
        self._lock = threading.Lock()   # Synchrolock
        self._prefix = "**"
        self._QUIT = "QUIT"

    def start(self):
        t = threading.Thread(target=self._log)
        t.setDaemon(True)
        t.start()
        self._messageQueue.put(self._prefix + "New job start")
        start_time = datetime.now()
        urls = self._buildUrls()
        self._messageQueue.put(self._prefix + "Total %s source urls"%(len(urls)))
        self._pool.map(self._resolveUrl, urls[0:5])
        while self._queue.qsize():
            imgs = self._queue.get()
            self._pool.map_async(self._downImg, imgs)
        self._pool.close()
        self._pool.join()
        self._messageQueue.put(self._prefix + "Job completed. Total %s images. Duration: %s"%(self._index, datetime.now() - start_time))
        self._messageQueue.put(self._prefix + "The images are saved in %s."%self._dirpath)
        self._messageQueue.put(self._prefix + "Logs are saved in %s"%self._logFile)
        self._messageQueue.put(self._prefix + "Errors are saved in %s"%self._errorFile)
        self._messageQueue.put(self._QUIT)

    def _log(self):
        """
        Print log in consloe and log file
        """
        with open(self._logFile, "w+", encoding="utf-8") as f:
            while True:
                msg = self._messageQueue.get()
                if msg == self._QUIT:
                    break
                msg = str(datetime.now()) + " " + msg
                if self._prefix in msg:
                    print(msg)
                elif "Downloading" in msg:
                    pass
                f.write(msg + '\n')
                f.flush()

    @abstractmethod
    def _buildUrls(self):
        """
        A abstract method to build the src url for acquiring image urls.
        This method must be implemented in subclasses.
        This method should be designed according to the specified website.
        """
    @abstractmethod
    def _decode(self, url):
        """
        """

    def _resolveUrl(self, url):
        """
        Resolve the urls of images from the specified link
        Input:
            url. The specified link
        """
        time.sleep(self._delay)
        html = self._session.get(url, timeout = 15).content.decode('utf-8')
        datas = self._re_url.findall(html)
        imgs = [Image(self._decode(x), self._decode(x).split(".")[-1]) for x in datas]
        info = self._prefix + "%s image urls has been resolved."%len(imgs)
        self._messageQueue.put(info)
        self._queue.put(imgs)

    def _downImg(self, img):
        """
        Download the img according to the img_url and save img as img_type
        Input:
            img. The image info as type Image.
        """
        imgUrl = img.url
        msg = None
        try:
            time.sleep(self._delay)
            img_res = self._session.get(imgUrl,timeout = 15)
            if str(img_res.status_code)[0] == "4":
                msg = "\nDownload failed.%s : %s"%(imgUrl, img_res.status_code)
            elif "text/html" in img_res.headers["Content-Type"]:
                msg = "\nCan not open image.%s"%imgUrl       
        except Exception as e:
            msg = "\nException: %s.%s"%(str(e),imgUrl)
        finally:
            if msg:
                self._messageQueue.put(msg)
                self._saveError(msg)
            else:
                index = self._getIndex()
                info = "Downloading: %s th images. Url: %s."%(index + 1, imgUrl)
                self._messageQueue.put(info)
                filename = os.path.join(self._dirpath, self._word + str(index) + '.' + img.type)
                with open(filename, "wb") as f:
                    f.write(img_res.content)
    
    def _getIndex(self):
        """
        Get current index 
        """
        self._lock.acquire()
        try:
            return self._index
        finally:
            self._index += 1
            self._lock.release()
    
    def _saveError(self, msg):
        """
        Record the error message in errorfile
        Input: 
            msg. The error message 
        """
        self._lock.acquire()
        try:
            with open(self._errorFile, "a+", encoding="utf-8") as f:
                f.write(msg)
        finally: 
            self._lock.release()
        
if __name__ == "__main__":

    pass

