import requests
import xml.etree.ElementTree as ET
import json
import datetime
import opengraph_py3
import os

def _get_category(url):
    #print("GET for " + str(url))

    data = requests.get(url)

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
            "site_name" = "",
            "url" = "",
            "description" = ""
        })

    for x in items:
        try:
            og = opengraph_py3.OpenGraph(url=x["link"])
            x["image"] = og["image"]
            x["site_name"] = og["site_name"]
            x["url"] = og["url"]
            x["description"] = og["description"]
            x["logo"] = og["logo"]
        except Exception as err:
            print("error")
            
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
