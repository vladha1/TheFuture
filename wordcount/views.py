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

def home(request):
    newslist=[]
    searchcriteria=None
    IndianURLs = urls(country = 'IN')
    
    searchcriteria = request.GET.get('search')
    print("criteria:",searchcriteria)

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
                
            if searchcriteria==None or searchcriteria in detailtext or searchcriteria in article.title:               
                counter=counter+1
                newslist=newslist+[{'Source':IndianURL,'Title':article.title,'Published':dateresult,'Summary_Detail':detailtext,'link':article.link,'id':"head_"+str(counter)}]

    newslist=newslist+rssfeeds(searchcriteria)
    newslist_sorted=sorted(newslist, key= lambda i: i['Published'],reverse=True)
                #newslist_sorted=newslist_sorted[newslist_sorted['Summary_Detail'].str.contains("Hwang")]
    
    print("responding")
    return render(request, 'home.html', {'newslist':newslist_sorted})
        #return newslist

def rssfeeds(searchcriteria):

    feedsources=['https://www.livemint.com/rss/news','https://www.financialexpress.com/feed/','https://www.news18.com/rss/business.xml','https://www.business-standard.com/rss/latest.rss','https://economictimes.indiatimes.com/rssfeedsdefault.cms','https://www.moneycontrol.com/rss/MCtopnews.xml','https://www.thehindu.com/business/feeder/default.rss']
    news=[]
    counter=0
    for feedsource in feedsources:
        
        NewsFeed = feedparser.parse(feedsource)
        for items in NewsFeed.entries:
            newsitem={}
            if searchcriteria==None or searchcriteria in items.summary or searchcriteria in items.title:               
                counter=counter+1
                newsitem['id']="head1_"+str(counter)
                newsitem['Source']=NewsFeed.feed.title
                if NewsFeed.feed.title=="Latest News":
                    newsitem['Source']="Business Standard"
                newsitem['Title']=items.title
                newsitem['Summary_Detail']=items.summary
                newsitem['link']=items.link
                datesfound=datefinder.find_dates(items.published)
                dateresult="x"
                for match in datesfound:
                    dateresult=match.strftime("%Y-%m-%d %H:%M")
                
                #dateresult="2021-04-18"
                newsitem['Published']=dateresult
                news=news+[newsitem]

            
    #print(NewsFeed.feed.title)
            
    return news

