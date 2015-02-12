# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 10:51:43 2015

@author: leo_cdo_intern


Telechar

"""

from os.path import join, isfile
import requests
import json

def download_file(url, download_path):
    
    local_filename = url.split('/')[-1]
    if not isfile(join(download_path, local_filename)):
        # NOTE the stream=True parameter
        r = requests.get(url, stream=True)
        with open(join(download_path, local_filename), 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        print local_filename


download_path = '/home/debian/Documents/data/test_csv_detector'

list_url = 'https://www.data.gouv.fr:443/api/1/datasets/?sort=created&format=csv&page_size=20'


max_pages = 100
while max_pages > 0:
    max_pages -= 1
    page = requests.get(list_url).json()
    list_url = page['next_page']
    data = page['data']
    
    for i in range(20):
        download_url = data[i]['resources'][0]['url']
        download_file(download_url, download_path)





