from bs4 import BeautifulSoup
import urllib3, shutil
import re
import requests

def download_json(traceid):
    json_url = 'http://155.98.38.140:30232/jaeger/api/traces/' + traceid+ '?prettyPrint=true'
    print(json_url)
    session = requests.Session()  # Create a session to persist cookies
    response = session.get(json_url)
    print(response.text)
    
    # print(json_url)
    # http = urllib3.PoolManager()

    # path = "jaeger_logs/"+traceid + '.json'
    # r = http.request('GET', json_url, preload_content=False)
    # # print(r)
    # with http.request('GET', json_url, preload_content=False) as r, open(path, 'wb') as out_file:
    #     shutil.copyfileobj(r, out_file)
        
# Passing the source code to BeautifulSoup to create a BeautifulSoup object for it.
soup = BeautifulSoup(open("./Jaeger_UI.html"), "html.parser")  # I assume that you save the page source of your Jaeger search result here as `Jaeger_UI.html`. 

# Extracting all the <a> tags into a list.
tags = str(soup.find_all('a', {'class': 'ResultItemTitle--item ub-flex-auto'}))

pattern = r'href="/jaeger/trace/([a-fA-F0-9]+)"'
traces = re.findall(pattern, tags)

# print(traces)
for trace in traces[:2]:
    print(trace)
    download_json(trace)
