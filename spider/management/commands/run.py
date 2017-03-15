import re
import pickle
import urllib.request
from xml.dom import minidom
from pymemcache.client.base import Client as MemClient

mem_client = MemClient(('localhost', 11211))

def get_urls():
    url = 'http://api.biglion.ru/api.php?method=get_torg_price&type=xml&ctype=all'
    cache = mem_client.get(url)
    if cache is not None:
        print('Loading from cache...')
        return pickle.loads(cache)
    print('Loading from net...')
    request = urllib.request.Request(url)
    with urllib.request.urlopen(request) as f:
            print('Parsing...')
            xml_str = f.read().decode('utf-8')
            xmldoc = minidom.parseString(xml_str)
            urls_nodels_list = xmldoc.getElementsByTagName('url')
            print('Received', len(urls_nodels_list), 'items')
            urls_str = []
            for url_node in urls_nodels_list:
                urls_str.append(url_node.firstChild.nodeValue.strip())
            cache = mem_client.set(url,  pickle.dumps(urls_str))
            return urls_str


get_urls()
