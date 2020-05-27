# ImgCTool 
This is an image download tool for research only, which is used to obtain the image set needed for training.
ImgCTool implements a dynamic crawler. It can download images according to keywords from some search engines that dynamically load images through Ajex. 

这是一个用于科研的图片爬取工具，可以帮助你获取所需的图片数据集。
目前实现了一个动态爬虫，可以从通过Ajex动态加载图片的搜索引擎与图片站中根据关键词下载图片。
# Usage

# Extension
You can continue to add other websites as sources on this basis. At present, the base class of dynamic crawler is implemented. For other websites which use dynamic images loading, you can implement the extension by imitating the subclasses in the `src/api/` directory. Generally speaking, all you need to do is parse and build the jsonurl interface link containing the image source URLs(to implement the abstract method$\_Buildurls$), the rest of the work can be done by ImgCTool. In some websites, the image source URLs are encoded. In this case, you need to override the decoding method(`_Decode`) to decode the image URLs (refer to `/src/api/baiduDL.py`）。

你可以在此基础上继续添加其他网站作为爬取源。目前实现了动态爬虫的基类。对于同样采用动态图片加载方式的其他网站，你可以仿照`src/api/`目录下的子类实现扩展。一般来说你只需要做的是解析并构造含有图片源url的jsonurl接口链接（实现抽象函数$\_buildUrls$），其余的工作都可以由ImgCTool来完成。有些网站的图片源url是经过加密处理的，这种情况下，你还需要重写解码函数（`_decode函数`），实现图片url的解码（参照`/src/api/baiduDL.py`）。
