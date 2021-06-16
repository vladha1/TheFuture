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
from newscatcher import Newscatcher
from newscatcher import urls
from datetime import datetime
import datefinder
from operator import itemgetter
import feedparser
from io import StringIO
import io
import base64
import urllib
import numpy as np
from pyowm.owm import OWM


def home(request):
    newslist=[]
    searchcriteria=None
    IndianURLs = urls(country = 'IN')
    
    searchcriteria = request.GET.get('search')
    #print("criteria:",searchcriteria)

    det=[]
    counter=0
    for IndianURL in IndianURLs:
         
        nc = Newscatcher(website = IndianURL)
        results = nc.get_news()
        
        if results is not None and results['articles'] is not None:
            articles = results['articles']

            for article in articles:
               datesfound=datefinder.find_dates(article.published)
               dateresult="x"
               for match in datesfound:
                
                dateresult=match.strftime("%Y-%m-%d %H:%M")

                txt=list(article.summary_detail.values())[3]
                detailtext = BeautifulSoup(txt, "html.parser").get_text()                
                
                counter=counter+1
                newslist=newslist+[{'Source':IndianURL,'Title':article.title,'Published':dateresult,'Summary_Detail':detailtext,'link':article.link,'id':"head_"+str(counter)}]

    newslist=newslist+rssfeeds()
    newsdf=pd.DataFrame(newslist)
    #if searchcriteria!=None:
    #    newsdf=newsdf[(newsdf['Summary_Detail'].str.contains(searchcriteria))|(newsdf['Title'].str.contains(searchcriteria))|(newsdf['Source'].str.contains(searchcriteria))]

    #print("type",type(newsdf))
    newsdf=newsdf.sort_values(by=['Published'],ascending=False)
    newslist=newsdf.to_dict('records')

    #newslist_sorted=sorted(newslist, key= lambda i: i['Published'],reverse=True)

                #newslist_sorted=newslist_sorted[newslist_sorted['Summary_Detail'].str.contains("Hwang")]
    
        
    txt=str(newsdf['Title'])
    
    #wordcloud = wordcloudplot(txt)

    #print("responding")
    return render(request, 'home.html', {'newslist':newslist,'weather':weather()})
        #return newslist

def rssfeeds():

    feedsources=['https://www.indiainfoline.com/rss/news.xml','http://feeds.feedburner.com/nseindia/results','https://www.reutersagency.com/feed/?best-regions=asia&post_type=best','https://www.investing.com/rss/news.rss','https://www.cnbc.com/id/19746125/device/rss/rss.xml','https://www.financialexpress.com/market/indian-markets/feed/','https://www.livemint.com/rss/news','https://www.financialexpress.com/feed/','https://www.news18.com/rss/business.xml','https://www.business-standard.com/rss/markets-106.rss','https://economictimes.indiatimes.com/rssfeedsdefault.cms','https://www.moneycontrol.com/rss/MCtopnews.xml','https://www.thehindu.com/business/feeder/default.rss']
    news=[]
    counter=0
    for feedsource in feedsources:
        
        NewsFeed = feedparser.parse(feedsource)
        for items in NewsFeed.entries:
            newsitem={}
            counter=counter+1
            newsitem['id']="head1_"+str(counter)
            newsitem['Source']=NewsFeed.feed.title
            if NewsFeed.feed.title=="Latest News":
                newsitem['Source']="Business Standard"
            elif NewsFeed.feed.title=="Top News and Analysis (pro)":
                newsitem['Source']="CNBC"
            elif NewsFeed.feed.title=="All News":
                newsitem['Source']="Investing.com"

            newsitem['Title']=items.get('title')

            if NewsFeed.feed.title=="All News":
                newsitem['Summary_Detail']=items.get('title')
            else:
                newsitem['Summary_Detail']=items.get('summary')
            
            
            newsitem['link']=items.get('link')
            datesfound=datefinder.find_dates(items.get('published'))
            dateresult="x"
            for match in datesfound:
                dateresult=match.strftime("%Y-%m-%d %H:%M")
            
            #dateresult="2021-04-18"
            newsitem['Published']=dateresult
            news=news+[newsitem]

            
    return news
    
def weather():
    owm = OWM('e1b22fd351f070c4e79fd931bbb6fa60')
    mgr = owm.weather_manager()
    weather = mgr.weather_at_place('Bangalore,IN').weather
    return(weather.temperature('celsius'))
