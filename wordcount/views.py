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
from nsepython import *
import yfinance as yf


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

    newslist=newslist+rssfeeds()#+twitter()
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
    rendering={'indiamarkets':indiamarkets(),'newslist':newslist,'SPX':globalstocks('^SPX'),'SPXF':globalstocks('ES=F'),'NQF':globalstocks('NQ=F'),'DOWF':globalstocks('YM=F'),'CRDF':globalstocks('CL=F'),'GLD':globalstocks('GLD'),'GLDF':globalstocks('GC=F'),'BTC':globalstocks('BTC-USD'),'INR':globalstocks('USDINR=X'),'N225':globalstocks('^N225'),'SGXN':globalstocks('IN-N21.SI'),'RUT':globalstocks('^RUT'),'DJI':globalstocks('^DJI'),'VIX':globalstocks('^VIX'),'NDAQ':globalstocks('^IXIC'),'KOSPI':globalstocks('^KS11'),'FTSE':globalstocks('^FTSE'),'DAX':globalstocks('^GDAXI'),'CAC':globalstocks('^FCHI'),'TNX':globalstocks('^TNX'),'BSESN':globalstocks('^BSESN'),'SHCOMP':globalstocks('000001.SS'),'HSI':globalstocks('^HSI')}
    
    return render(request, 'newhome.html',rendering)
    

def globalstocks(ticker):

    # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
    #url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol='+ticker+'&interval=5min&apikey=LGMS48PFLKLHONKB'
    #r = requests.get(url).json().get('Global Quote')
    #print(type(r))
    #print(r)
    #print(r.keys())

    stock = yf.Ticker(ticker)
    data1= stock.info
    price=data1.get('regularMarketPrice')
    prevPrice=data1.get('previousClose')
    #print("price:",price)
    #print("prev:",prevPrice)
    try:
        percChange=str(round((price/data1.get('previousClose')-1)*100,1))
    except:
        percChange=0
    response=str(round(price,1))+" ("+percChange+"%)"
    return response

def globalmarkets():
        
        indexcols1=[]
        #print(indexcols1)
        tickers=set(['GLD','QQQ','^N225','000001.SS','^HSI','^TNX','^GDAXI','^FTSE','^FCHI','^SPX','USDINR=X'])

        for ticker in tickers:
            indexcol1=indexcols1.append(globalstocks(ticker))
        return indexcols1

def niftyrename(row):
    if row['indexName']=='NIFTY 50':
        return "NIFTY"
    else:
        return row['indexName'].replace('NIFTY ',"")

def indiamarkets():

    #['NIFTY 50', 'NIFTY MIDCAP 50', 'NIFTY MIDCAP 100', 'NIFTY BANK', 'NIFTY FMCG', 'NIFTY FIN SERVICE', 'NIFTY COMMODITIES', 'NIFTY CONSUMPTION', 'NIFTY IT', 'NIFTY AUTO', 'NIFTY PHARMA', 'NIFTY INFRA', 'NIFTY ENERGY', 'NIFTY METAL', 'NIFTY REALTY', 'NIFTY MEDIA', 'NIFTY GS 10YR']
        indices=['NIFTY 50', 'NIFTY MIDCAP 50', 'NIFTY MIDCAP 100', 'NIFTY BANK', 'NIFTY FMCG', 'NIFTY FIN SERVICE', 'NIFTY COMMODITIES', 'NIFTY CONSUMPTION', 'NIFTY IT', 'NIFTY AUTO', 'NIFTY PHARMA', 'NIFTY INFRA', 'NIFTY ENERGY', 'NIFTY METAL', 'NIFTY REALTY', 'NIFTY MEDIA', 'NIFTY GS 10YR']
        
        
        indexcols=nse_index()[['indexName','last','percChange']]

        #indexcols1=indexcols[indexcols['indexName']].to_dict('r')
        indexcols1=indexcols[indexcols['indexName'].isin(indices)]
        indexcols1['indexName']=indexcols1.apply(niftyrename,axis=1)
        indexcols1=indexcols1.to_dict('r')
        #print(indexcols1)
       
        return indexcols1


    


def rssfeeds():

    feedsources=['https://www.indiainfoline.com/rss/news.xml','http://feeds.feedburner.com/nseindia/results','https://www.reutersagency.com/feed/?best-regions=asia&post_type=best','https://www.investing.com/rss/news.rss','https://www.cnbc.com/id/19746125/device/rss/rss.xml','https://www.financialexpress.com/market/feed/','https://www.news18.com/rss/business.xml','https://www.business-standard.com/rss/markets-106.rss','https://economictimes.indiatimes.com/rssfeedsdefault.cms','https://www.moneycontrol.com/rss/MCtopnews.xml','https://www.thehindu.com/business/feeder/default.rss']
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
    
    
    api = tweepy.API(auth)
    handles=set(['CNBCTV18Live','ReutersIndia','NDTVProfit','forbes_india','moneycontrolcom','ETNOWlive','ETmarkets','ReutersIndia','EconomicTimes','NDTVProfit','forbes_india','moneycontrolcom','ETNOWlive','BloombergTV','CNBCTV18Live','@BT_India','NSEIndia','TOIBusiness','IIFL_Live','FinancialTimes','BloombergQuint','WSJMarkets'])

    tweets=[]
    for handle in handles:
        try:
            tweets = tweets + api.user_timeline(screen_name=handle, 
                                # 200 is the maximum allowed count
                                
                                include_rts = False,
                                # Necessary to keep full_text 
                                exclude_replies = True,
                                # otherwise only the first 140 words are extracted
                                tweet_mode = 'extended'
                                )
        except:
            print(handle," not valid")

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