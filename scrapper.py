from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import xmltodict
import json
from bs4 import BeautifulSoup
import os
import website
import requests
import shutil

# Get initial Page and data
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.get(website.website)
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'lxml')


parent_dir = os.path.abspath(os.getcwd())

# Get title
tit = ((soup.find('h1', class_="tit")).find(text=True))
title = tit.replace(" ", "_")
path = os.path.join(parent_dir, title)
try:
    os.mkdir(path)
except: 
    pass

file_name = title + '/' + title + "_cover"

# Download Cover picture and save to folder
cover = soup.find('div', class_="pic")
res = requests.get(cover.img['src'], stream = True)
if res.status_code == 200:
    with open(file_name,'wb') as f:
        shutil.copyfileobj(res.raw, f)
    print('Image sucessfully Downloaded: ',file_name)
else:
    print('Image Couldn\'t be retrieved')

chapter = website.host + ((soup.find("div", class_="btn")).findChildren("a"))[1]['href']

driver.get(chapter)
soup = BeautifulSoup(driver.page_source, 'lxml')

amount_chapter = input("How many chapters does the lightnovel have?: ")
chapterList = []

numbering = 1
while (True):
    print("Working on chapter " + str(numbering))
    if(numbering == amount_chapter):
        next_chap = website.website
    else:
        next_chap = website.host + (soup.find("a", {"title": "Read Next chapter"}))['href']
    chap_tit = (soup.find("span", class_="chapter")).find(text=True)
    chap_txt = (soup.find("div", class_="txt")).extract()
    chap_num = numbering
    for script in chap_txt("div"):
        script.decompose()
    for script in chap_txt("sub"):
        script.decompose()
    for script in chap_txt("h4"):
        script.decompose()
    for script in chap_txt("strong"):
        script.decompose()
    test = xmltodict.parse(str(chap_txt))
    chapter = {
        "title": str(chap_tit),
        "id": chap_num,
        "content": xmltodict.parse(str(chap_txt))
    }
    if(next_chap == website.website):
        break
    chapterList.append(chapter)
    driver.get(next_chap)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    numbering = numbering + 1


# save content and file
ln = {
    "title": str(tit),
    "cover": "/" + title + "_cover.jpeg",
    "chapters": chapterList
}
bytes_object = ln
json_object = json.dumps(bytes_object, indent= 4)

with open(title + '/' + title + ".json", "w") as outfile:
    outfile.write(json_object)