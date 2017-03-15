import re
import urllib.request
from xml.dom import minidom

def get_urls():
    print('Loading...')
    url = 'http://api.biglion.ru/api.php?method=get_torg_price&type=xml&ctype=all'
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
            return urls_str


print(get_urls())
