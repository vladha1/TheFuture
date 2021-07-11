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
import datefinder
from operator import itemgetter
import feedparser
from io import StringIO
import io
import base64
import urllib
import numpy as np
from pyowm.owm import OWM
import tweepy
import pytz


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

    newslist=newslist+rssfeeds()+twitter()
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

    
    return render(request, 'home.html', {'newslist':newslist})
    

def rssfeeds():

    feedsources=['https://www.indiainfoline.com/rss/news.xml','http://feeds.feedburner.com/nseindia/results','https://www.reutersagency.com/feed/?best-regions=asia&post_type=best','https://www.investing.com/rss/news.rss','https://www.cnbc.com/id/19746125/device/rss/rss.xml','https://www.financialexpress.com/market/indian-markets/feed/','https://www.financialexpress.com/feed/','https://www.news18.com/rss/business.xml','https://www.business-standard.com/rss/markets-106.rss','https://economictimes.indiatimes.com/rssfeedsdefault.cms','https://www.moneycontrol.com/rss/MCtopnews.xml','https://www.thehindu.com/business/feeder/default.rss']
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
            
            newsitem['Published']=dateresult
            news=news+[newsitem]
    return news
    


def twitter():
    tweetnews=[]

    auth = tweepy.OAuthHandler("")
    auth.set_access_token("x" )



    api = tweepy.API(auth)
    handles=['CNBCTV18Live','ReutersIndia','EconomicTimes','NDTVProfit','forbes_india','moneycontrolcom','ETNOWlive','ETmarkets','ETmarkets','BloombergTV','CNBCTV18Live','BT_India','ZeeBusiness','FinancialXpress','NSEIndia','TOIBusiness','IIFL_Live','FinancialTimes','BloombergQuint','WSJMarkets']

    tweets=[]
    for handle in handles:

        tweets = tweets + api.user_timeline(screen_name=handle, 
                            # 200 is the maximum allowed count
                            
                            include_rts = False,
                            # Necessary to keep full_text 
                            exclude_replies = True,
                            # otherwise only the first 140 words are extracted
                            tweet_mode = 'extended'
                            )

    utctz=pytz.timezone('UTC')
    intz = pytz.timezone('Asia/Calcutta')

    for info in tweets:

        source="Twitter-"+info.user.name
        id=info.id
        created_at=utctz.localize(info.created_at)
        created_at_local=created_at.astimezone(intz)
        published=created_at_local.strftime("%Y-%m-%d %H:%M")
        fulltextlist=info.full_text.split("http")
        Title=fulltextlist[0]
        if len(fulltextlist)>1:
            url="http"+fulltextlist[1]
        else:
            url=""
        
        tweetnews=tweetnews+[{'Source':source,'Title':Title,'Published':published,'Summary_Detail':"",'link':url,'id':id}]
    return tweetnews