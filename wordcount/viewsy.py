from django.http import HttpResponse
from django.shortcuts import render
import pandas as pd
import operator
import time
import uuid
from datetime import datetime
from decimal import Decimal
import requests
from bs4 import BeautifulSoup
import investpy

#import feedparser


def timesofindia():
    url = "https://timesofindia.indiatimes.com/home/headlines"
    page_request = requests.get(url)
    data = page_request.content
    soup = BeautifulSoup(data,"html.parser")

    counter = 0
    response=[]
    for divtag in soup.find_all('div', {'class': 'headlines-list'}):
        for ultag in divtag.find_all('ul', {'class': 'clearfix'}):
            if (counter <= 10):
                for litag in ultag.find_all('li'):
                    counter = counter + 1
                    #print(str(counter) + " - https://timesofindia.indiatimes.com" + litag.find('a')['href'])
                    response=response+[{'counter':str(counter),'headline':litag.text,'link': "https://timesofindia.indiatimes.com" + litag.find('a')['href']}]
    return response

def invest():
    df = investpy.get_stock_historical_data(stock='AAPL',country='United States',from_date='01/04/2021',to_date='10/04/2021')
    return df.to_html


def rbi():
    feedresults=[]
    feed = feedparser.parse('https://rbi.org.in/pressreleases_rss.xml')
    for items in feed.entries:
        feedresults=feedresults+[{'title':items.title,'published':items.published,'link':items.link}]
    feeddata=pd.DataFrame(feedresults).to_html
    return feeddata


def home1(request):
        return render(request,'home.html',{'news':timesofindia(),'tickers':invest(),'rbi':rbi()})






def home(request):
    newslist=[]

    IndianURLs = urls(country = 'IN')

    det=[]

    for IndianURL in IndianURLs:

        nc = Newscatcher(website = IndianURL)
        results = nc.get_news()
        
        try:
            articles = results['articles']
        
            for article in articles:
                txt=list(article.summary_detail.values())[3]
                detailtext = BeautifulSoup(txt, "html.parser").get_text()                
                newslist=newslist+[{'Source':IndianURL,'Title':article.title,'Published':article.published,'Summary_Detail':detailtext,'link':article.link}]
                

        except:
            a=1
        render(request, 'myapp/index.html', {'newslist':newslist})
        #return newslist

