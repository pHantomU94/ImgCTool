

class Image(object):
    """
    Class Image
    Save the url of image and file type of this image
    """
    def __init__(self,img_url,type):
        super(Image,self).__init__()
        self.url = img_url
        self.type = type