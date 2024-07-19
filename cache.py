import requests
import xml.etree.ElementTree as ET
import json
import datetime
import os
import re
from bs4 import BeautifulSoup

def _get_category(url):
    #print("GET for " + str(url))

    data = requests.get(url, cookies = {'CONSENT' : 'YES+'})

    items = []

    myroot = ET.fromstring(data.content)
    for x in myroot.findall('channel/item'):
        title = x.find('title').text
        link = x.find('link').text
        date = x.find('pubDate').text
        items.append({
            "title" : title, 
            "link" : link, 
            "pubDate" : date, 
            "image": "https://picsum.photos/200/300?grayscale", 
            "logo" : "https://picsum.photos/32/32?grayscale",
            "site_name" : "",
            "url" : "",
            "description" : ""
        })

    for x in items:
        try:
            html = requests.get(x["link"], cookies = {'CONSENT' : 'YES+'}).content
            doc = BeautifulSoup(html, features="lxml")
            ogs = doc.html.head.findAll(property=re.compile(r'^og'))

            meta = {}
            for og in ogs:
                if og.has_attr('content'):
                    meta[og['property'][3:]]=og['content']

            x["image"] = meta["image"]
            x["site_name"] = meta["site_name"]
            x["url"] = meta["url"]
            x["link"] = meta["url"]
            x["description"] = meta["description"]
        except Exception as err:
            print(err)
            
    return items

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def _printcache(name, url):
    result=_get_category(url)

    objectJson = {"content": result}
    objectJson['timestamp'] = datetime.datetime.now()

    path = 'cache/'+name+'.json'
    json.dump(objectJson, open(os.path.join(os.path.dirname(__file__), path), 'w'), indent='\t', default = myconverter)

### main ###

_printcache('une',      'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtWnlHZ0pHVWlnQVAB?hl=fr&gl=FR&ceid=FR%3Afr')
_printcache('france',   'https://news.google.com/rss/topics/CAAqIggKIhxDQkFTRHdvSkwyMHZNR1k0YkRsakVnSm1jaWdBUAE?hl=fr&gl=FR&ceid=FR%3Afr')
_printcache('sciences', 'https://news.google.com/rss/search?q=sciences&hl=fr&gl=FR&ceid=FR%3Afr')
_printcache('sport',    'https://news.google.com/rss/search?q=sport&hl=fr&gl=FR&ceid=FR%3Afr')

print("DONE")
