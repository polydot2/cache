import requests
import xml.etree.ElementTree as ET
import json
import datetime
import os
from bs4 import BeautifulSoup
import base64
from urllib.parse import quote, urlparse

def get_decoding_params(gn_art_id):
    response = requests.get(f"https://news.google.com/rss/articles/{gn_art_id}")
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    div = soup.select_one("c-wiz > div")
    return {
        "signature": div.get("data-n-a-sg"),
        "timestamp": div.get("data-n-a-ts"),
        "gn_art_id": gn_art_id,
    }

def decode_urls(articles):
    articles_reqs = [
        [
            "Fbv4je",
            f'["garturlreq",[["X","X",["X","X"],null,null,1,1,"US:en",null,1,null,null,null,null,null,0,1],"X","X",1,[1,1,1],1,1,null,0,0,null,0],"{art["gn_art_id"]}",{art["timestamp"]},"{art["signature"]}"]',
        ]
        for art in articles
    ]
    payload = f"f.req={quote(json.dumps([articles_reqs]))}"
    headers = {"content-type": "application/x-www-form-urlencoded;charset=UTF-8"}
    response = requests.post(
        url="https://news.google.com/_/DotsSplashUi/data/batchexecute",
        headers=headers,
        data=payload,
    )
    response.raise_for_status()
    return [json.loads(res[2])[1] for res in json.loads(response.text.split("\n\n")[1])[:-2]]

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
        
        # decode URL google
        encoded_urls = [x.find('link').text]
        articles_params = [get_decoding_params(urlparse(url).path.split("/")[-1]) for url in encoded_urls]
        link = decode_urls(articles_params)[0]

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

def _printcache(name, url, max_entries=100):
    # Obtenir les nouvelles entrées
    result = _get_category(url)
    
    # Chemin du fichier JSON
    path = os.path.join(os.path.dirname(__file__), 'cache', f'{name}.json')
    
    # Lire le contenu existant du fichier JSON (s'il existe)
    existing_data = {"content": [], "timestamp": None}
    try:
        with open(path, 'r') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Si le fichier n'existe pas ou est corrompu, on commence avec une liste vide
        pass
    
    # Fusionner les nouvelles entrées avec les anciennes, en évitant les doublons
    existing_links = {item["link"] for item in existing_data["content"]}
    new_items = [item for item in result if item["link"] not in existing_links]
    combined_content = existing_data["content"] + new_items
    
    # Limiter le nombre total d'entrées (les plus récentes en premier)
    combined_content = sorted(
        combined_content,
        key=lambda x: x.get("pubDate", ""),
        reverse=True
    )[:max_entries]
    
    # Créer l'objet JSON à sauvegarder
    objectJson = {
        "content": combined_content,
        "timestamp": datetime.datetime.now()
    }
    
    # Écrire dans le fichier JSON
    with open(path, 'w') as f:
        json.dump(objectJson, f, indent='\t', default=myconverter)
        
### main ###
_printcache('une',      'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtWnlHZ0pHVWlnQVAB?hl=fr&gl=FR&ceid=FR%3Afr')
_printcache('france',   'https://news.google.com/rss/topics/CAAqIggKIhxDQkFTRHdvSkwyMHZNR1k0YkRsakVnSm1jaWdBUAE?hl=fr&gl=FR&ceid=FR%3Afr')
_printcache('sciences', 'https://news.google.com/rss/search?q=sciences&hl=fr&gl=FR&ceid=FR%3Afr')
_printcache('sport',    'https://news.google.com/rss/search?q=sport&hl=fr&gl=FR&ceid=FR%3Afr')

## test
# encoded_urls = "https://news.google.com/rss/articles/CBMipgFBVV95cUxPWV9fTEI4cjh1RndwanpzNVliMUh6czg2X1RjeEN0YUctUmlZb0FyeV9oT3RWM1JrMGRodGtqTk1zV3pkNEpmdGNxc2lfd0c4LVpGVENvUDFMOEJqc0FCVVExSlRrQmI3TWZ2NUc4dy1EVXF4YnBLaGZ4cTFMQXFFM2JpanhDR3hoRmthUjVjdm1najZsaFh4a3lBbDladDZtVS1FMHFn?oc=5",
# articles_params = [get_decoding_params(urlparse(url).path.split("/")[-1]) for url in encoded_urls]
# decoded_urls = decode_urls(articles_params)
# print(decoded_urls)

print("DONE")

