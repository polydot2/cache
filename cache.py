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

import requests
import base64

def fetch_decoded_batch_execute(id):
    s = (
        '[[["Fbv4je","[\\"garturlreq\\",[[\\"en-US\\",\\"US\\",[\\"FINANCE_TOP_INDICES\\",\\"WEB_TEST_1_0_0\\"],'
        'null,null,1,1,\\"US:en\\",null,180,null,null,null,null,null,0,null,null,[1608992183,723341000]],'
        '\\"en-US\\",\\"US\\",1,[2,3,4,8],1,0,\\"655000234\\",0,0,null,0],\\"'
        + id
        + '\\"]",null,"generic"]]]'
    )

    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        "Referer": "https://news.google.com/",
    }

    response = requests.post(
        "https://news.google.com/_/DotsSplashUi/data/batchexecute?rpcids=Fbv4je",
        headers=headers,
        data={"f.req": s},
    )

    if response.status_code != 200:
        raise Exception("Failed to fetch data from Google.")

    text = response.text
    header = '[\\"garturlres\\",\\"'
    footer = '\\",'
    if header not in text:
        raise Exception(f"Header not found in response: {text}")
    start = text.split(header, 1)[1]
    if footer not in start:
        raise Exception("Footer not found in response.")
    url = start.split(footer, 1)[0]
    return url


def decode_google_news_url(source_url):
    url = requests.utils.urlparse(source_url)
    path = url.path.split("/")
    if url.hostname == "news.google.com" and len(path) > 1 and path[-2] == "articles":
        base64_str = path[-1]
        decoded_bytes = base64.urlsafe_b64decode(base64_str + "==")
        decoded_str = decoded_bytes.decode("latin1")

        prefix = b"\x08\x13\x22".decode("latin1")
        if decoded_str.startswith(prefix):
            decoded_str = decoded_str[len(prefix) :]

        suffix = b"\xd2\x01\x00".decode("latin1")
        if decoded_str.endswith(suffix):
            decoded_str = decoded_str[: -len(suffix)]

        bytes_array = bytearray(decoded_str, "latin1")
        length = bytes_array[0]
        if length >= 0x80:
            decoded_str = decoded_str[2 : length + 1]
        else:
            decoded_str = decoded_str[1 : length + 1]

        if decoded_str.startswith("AU_yqL"):
            return fetch_decoded_batch_execute(base64_str)

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
    
    # print("try << " + x.find('link').text + "\t")   
    
    # print("decode >> "+ decode_google_news_url(link)+ "\t")
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
# google_url = "https://news.google.com/rss/articles/CBMiqAJBVV95cUxPQWZySFRYbElNVVA3RzdFSEhqU01LOUR6S1JFUHVGVVJvS0p4QWphUEVWQ0dlcTNSUTc1WF9xQUJaZDhpdDZwNklqRmNuenJWbE9RRC1VMTlrcjM0NkRhSFVsUFVIb1B2a2M2STZla1BSNGdpaDhSaG5rLTMtVjJRY0xHQ3NZaUFPOHdGbFhEckFySnloVXlWUnQwWDNDVG1xVXRSWTBCSElUbUlCYXYzc09wN1djVkFTeFFHZ25xSGEySGVpeWdHQnBLRjF2cXFPUVRRUEc3dEdpOGFHTFcxYktLbjgyWVBJT2tJTElaSGFGVk5oYW1UakpTZDNteDczX3MyRlduZm5BQXZCNGFRMkJkT1RXaHZ0ZExES19wTC1PZXVzeVNPbA?oc=5"
# https://www.lefigaro.fr/international/couvre-feu-centaine-de-morts-tirs-a-balles-reelles-de-l-armee-la-tension-atteint-son-paroxysme-au-bangladesh-20240720
# google_url = "https://news.google.com/rss/articles/CBMimwFodHRwczovL3d3dy5sZWZpZ2Fyby5mci9pbnRlcm5hdGlvbmFsL2NvdXZyZS1mZXUtY2VudGFpbmUtZGUtbW9ydHMtdGlycy1hLWJhbGxlcy1yZWVsbGVzLWRlLWwtYXJtZWUtbGEtdGVuc2lvbi1hdHRlaW50LXNvbi1wYXJveHlzbWUtYXUtYmFuZ2xhZGVzaC0yMDI0MDcyMNIBAA?oc=5"
# print("FINAL >> " + decode_google_news_url(google_url))

print("DONE")
