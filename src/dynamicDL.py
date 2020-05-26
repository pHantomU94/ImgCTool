import urllib
import requests
import re
import sys
import time
import threading
from datetime import datetime
from multiprocessing.dummy import Pool
from multiprocessing import Queue
from .Image import Image
from abc import ABC, abstractmethod
from pathlib import Path

class DynamicImgsDownloader(ABC):
    
    def __init__(self, word, processNum = 16, dirpath = None):
        if " " in word:
            raise("Multi keyword joint search is not supported temporarily.")
        """
        These member variables need to be reset in the subclass.
        """
        self._identify = "Baseclass"    # The search engine identify
        self._encode = "utf-8"          # The encode method of engine
        self._re_url = re.compile("")   # Regular matching rules of image source URL
        """
        end
        """
        self._word = word   # Image keyword
        root_path = Path.cwd()  # Project root path
        result_path = root_path / "download"    # The download result folder
        # Make default download path when folder is not specified
        if not dirpath:
            dirpath = result_path / self._word
        self._dirpath = dirpath 
        # Make related folder
        if not Path.exists(result_path):
            Path.mkdir(result_path)
        if not Path.exists(self._dirpath):
            Path.mkdir(self._dirpath)
        self._logDir = root_path / "logs"   # log files folder path
        if not Path.exists(self._logDir):   # 
            Path.mkdir(self._logDir)
        self._srcUrlFile =self._logDir / "srcUrl"
        self._logFile = self._logDir / "logInfo"
        self._errorFile = self._logDir / "errorUrl"
        if Path.exists(self._errorFile):
            Path.unlink(self._errorFile)       
        self._session = requests.Session()
        self._session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, sdch",
            }
        self._delay = 1.5   # Add a delay to prevent being banned due to frequent requests
        self._index = 0     # image file index for save 
        self._pool = Pool(processNum)
        self._queue = Queue()   # to save and read image src url
        self._messageQueue = Queue()    # message queue for log info
        self._lock = threading.Lock()   # Synchrolock
        self._prefix = "** "
        self._QUIT = "QUIT"

    def start(self):
        # start the log monitor
        t = threading.Thread(target=self._log)
        t.setDaemon(True)
        t.start()
        # create job
        self._messageQueue.put(self._prefix + "New job start. Keyword: %s, Search engine: %s"%(self._word, self._identify))
        start_time = datetime.now()
        # step 1: create all the jsonurl according to the specified engine
        urls = self._buildUrls()
        self._messageQueue.put(self._prefix + "Total %s source urls"%(len(urls)))
        # step 2: resolve all the jsonurls to accquire the images url 
        self._pool.map(self._resolveUrl, urls[0:1])
        # step 3: download the image according to image url
        while self._queue.qsize():
            imgs = self._queue.get()
            self._pool.map_async(self._downImg, imgs)
        self._pool.close()
        self._pool.join()
        # end 
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
                # end
                if msg == self._QUIT:
                    break
                msg = str(datetime.now()) + " " + msg
                # resolve info and others 
                if self._prefix in msg:
                    print(msg)
                # downlog info
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
    
    def _decode(self, url):
        """
        This method work for decode image url if necessary.
        This method is not set to abstract because some engines do not need to decode. 
        You can override this function in a subclass if you need to decode the image url.
        """
        return url

    def _resolveUrl(self, url):
        """
        Resolve the urls of images from the specified link
        Input:
            url. The specified link
        """
        # sleep
        time.sleep(self._delay)
        # get html page from jsonurl
        html = self._session.get(url, timeout = 15).content.decode(self._encode)
        # resolve image URL according to regular rules
        datas = self._re_url.findall(html)
        # make image objects containing url and type
        imgs = [Image(self._decode(x), self._decode(x).split(".")[-1]) for x in datas]
        # generate log info
        info = self._prefix + "%s image urls has been resolved."%len(imgs)
        # save in Queue 
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
            # sleep
            time.sleep(self._delay)
            # get image
            img_res = self._session.get(imgUrl,timeout = 15)
            if str(img_res.status_code)[0] == "4":
                msg = "\nDownload failed.%s : %s"%(imgUrl, img_res.status_code)
            elif "text/html" in img_res.headers["Content-Type"]:
                msg = "\nCan not open image.%s"%imgUrl       
        except Exception as e:
            msg = "\nException: %s.%s"%(str(e),imgUrl)
        finally:
            # download failed
            if msg:
                self._messageQueue.put(msg)
                self._saveError(msg)
            # download success
            else:
                # get image index
                index = self._getIndex()
                # downloading and save
                info = "Downloading: %s th images. Url: %s."%(index + 1, imgUrl)
                self._messageQueue.put(info)
                filename = self._dirpath / (self._identify + "_" + self._word + "_" + str(index) + "." + img.type)
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

