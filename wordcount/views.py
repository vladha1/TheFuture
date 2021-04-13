from django.http import HttpResponse
from django.shortcuts import render
import pandas as pd
import operator
import time
import uuid
from datetime import datetime
from decimal import Decimal
import requests

from newscatcher import Newscatcher
from newscatcher import urls



def home(request):
    newslist=[]

    IndianURLs = urls(country = 'IN')
    
    det=[]

    for IndianURL in IndianURLs:

        nc = Newscatcher(website = IndianURL)
        results = nc.get_news()
        print(nc)
        try:
            articles = results['articles']
        
            for article in articles:
                newslist=newslist+[{'Source':IndianURL,'Title':article.title,'Published':article.published,'Summary_Detail':list(article.summary_detail.values())[3],'link':article.link}]
        except:
            a=1
        print(newslist)
    return render(request, 'home.html', {'newslist':newslist})
        #return newslist

