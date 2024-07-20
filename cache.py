import requests
import xml.etree.ElementTree as ET
import json
import datetime
import os
import re
from bs4 import BeautifulSoup
import base64
import base64
from urllib.parse import urlparse
import re 

def decode_google_news_url(source_url):
    url = urlparse(source_url)
    path = url.path.split('/')
    # print(path)
    if (
        url.hostname == "news.google.com" and
        len(path) > 1 and
        path[len(path) - 2] == "articles"
    ):
        base64_str = path[len(path) - 1]
        decoded_bytes = base64.urlsafe_b64decode(base64_str + '==')
        decoded_str = decoded_bytes.decode('latin1')
        # print(decoded_str)
        
        prefix = bytes([0x08, 0x13, 0x22]).decode('latin1')
        if decoded_str.startswith(prefix):
            decoded_str = decoded_str[len(prefix):]

        suffix = bytes([0xd2,0x01,0x00]).decode('latin1')
        if decoded_str.endswith(suffix):
            decoded_str = decoded_str[:-len(suffix)]
            
        # bytes_array = bytearray(decoded_str, 'latin1')
        # length = bytes_array[0]
        # if length >= 0x80:
        #     decoded_str = decoded_str[2:length+1]
        # else:
        #     decoded_str = decoded_str[1:length+1]
        
        match = re.search(r'https?://.*', decoded_str) 
        if match: 
            decoded_str = match.group(0) 
             
        # print(decoded_str)
        return decoded_str
    else:
        return source_url

################################################################
    
def _get_category(url):
    #print("GET for " + str(url))
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
    cookies = {'CONSENT': 'YES+cb.20220419-08-p0.cs+FX+111'}
    data = requests.get(url, headers=headers, cookies=cookies)

    items = []

    myroot = ET.fromstring(data.content)
    for x in myroot.findall('channel/item'):
        title = x.find('title').text
        link = decode_google_news_url(x.find('link').text)
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
        
    # print(decode_google_news_url(link))
    for x in items:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
            cookies = {'CONSENT': 'YES+cb.20220419-08-p0.cs+FX+111'}
            html = requests.get(x["link"], headers=headers, cookies=cookies).content
            doc = BeautifulSoup(html, features="lxml")

            image = doc.find("meta", property="og:image")
            site_name = doc.find("meta", property="og:site_name", content=True)
            url = doc.find("meta", property="og:url", content=True)
            description = doc.find("meta", property="og:description", content=True)
            
            # print(image)

            x["image"] = image["content"] if image else ""
            x["site_name"] = site_name["content"] if site_name else ""
            x["url"] = url["content"]  if url else ""
            x["description"] = description["content"] if description else ""
            
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

## test
# https://www.lefigaro.fr/international/couvre-feu-centaine-de-morts-tirs-a-balles-reelles-de-l-armee-la-tension-atteint-son-paroxysme-au-bangladesh-20240720
# google_url = "https://news.google.com/rss/articles/CBMimwFodHRwczovL3d3dy5sZWZpZ2Fyby5mci9pbnRlcm5hdGlvbmFsL2NvdXZyZS1mZXUtY2VudGFpbmUtZGUtbW9ydHMtdGlycy1hLWJhbGxlcy1yZWVsbGVzLWRlLWwtYXJtZWUtbGEtdGVuc2lvbi1hdHRlaW50LXNvbi1wYXJveHlzbWUtYXUtYmFuZ2xhZGVzaC0yMDI0MDcyMNIBAA?oc=5"
# print(decode_google_news_url(google_url))

print("DONE")
