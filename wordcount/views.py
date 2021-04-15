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
import dateparser


def home(request):
    newslist=[]

    IndianURLs = urls(country = 'IN')
    
    det=[]
    counter=0
    for IndianURL in IndianURLs:
         
        nc = Newscatcher(website = IndianURL)
        results = nc.get_news()
        #print(nc)
        

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
               
               newslist_sorted=sorted(newslist, key= lambda i: i['Published'],reverse=True)

    
def otherfeeds():
    newsfeeds = ["https://www.livemint.com/rss/markets.xml","https://economictimes.indiatimes.com/rssfeedsdefault.cms","https://www.business-standard.com/rss/home_page_top_stories.rss"]

    for items in newsfeed:
        items_parse = feedparser.parse(items).entries
        return items_parse


    print("responding")
    return render(request, 'home.html', {'newslist':newslist_sorted})
        #return newslist

