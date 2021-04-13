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



def home(request):
    newslist=[]

    IndianURLs = urls(country = 'IN')
    
    det=[]
    counter=0
    for IndianURL in IndianURLs:
         
        nc = Newscatcher(website = IndianURL)
        results = nc.get_news()
        #print(nc)
        try:
            articles = results['articles']
        
            for article in articles:
                txt=list(article.summary_detail.values())[3]
                detailtext = BeautifulSoup(txt, "html.parser").get_text()                
                counter=counter+1
                newslist=newslist+[{'Source':IndianURL,'Title':article.title,'Published':article.published,'Summary_Detail':detailtext,'link':article.link,'id':"head_"+str(counter)}]
                
        except:
            a=1
    print("responding")
    return render(request, 'home.html', {'newslist':newslist})
        #return newslist

