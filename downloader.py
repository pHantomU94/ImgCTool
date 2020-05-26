from src.api import Baidu
from src.api import Sougou
from src.api import SO360
from src.api import Bing
from src.api import VCG
import configparser

def parser():
    args = []
    cp = configparser.ConfigParser()
    cp.read("config.ini", encoding="utf-8-sig")
    if cp.has_section("search"):
        if cp.has_option("search","engine"):
            args.append(cp.get("search","engine"))
        else:
            raise("Config.ini error: can not find search engine.")
        if cp.has_option("search","keyword"):
            args.append(cp.get("search","keyword"))
        else:
            raise("Config.ini error: can not find search keyword.")
    else:
        raise("Config.ini error: can not find section 'search'.")
    if cp.has_section("path"):
        if cp.has_option("path","dirpath"):
            args.append(cp.get("path","dirpath"))
    if cp.has_section("system"):
        if cp.has_option("system","processnum"):
            args.append(cp.get("system","processnum"))
    return args
        

def main():
    args = parser()
    print("Bing and VCG are unavailable now.")
    if args[0] == "Baidu":
        dl = Baidu(args[1])
        dl.start()
    elif args[0] == "Sougou":
        dl = Sougou(args[1])
        dl.start()
    elif args[0] == "SO360":
        dl = SO360(args[1])
        dl.start()
    # elif args[0] == "VCG":
    #     dl = VCG(args[1])
    #     dl.start()
    elif args[0] == "ALL":
        dl = Baidu(args[1])
        dl.start()
        dl = Sougou(args[1])
        dl.start()
        dl = SO360(args[1])
        dl.start()
        # dl = VCG(args[1])
        # dl.start()
    else:
        print("Unavailable search engine: %s"%args[0])
        return
    

    

if __name__ == "__main__":
    main()