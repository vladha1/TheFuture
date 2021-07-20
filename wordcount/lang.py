import spacy

nlp = spacy.load("en_core_web_md")  # make sure to use larger package!

import spacy
#nlp = spacy.load('en_core_web_sm')
doc1 = nlp('@AdaniOnline takes over #Mumbai International Airport. "We are delighted to take over management of the world-class Mumbai International Airport. We promise to make Mumbai proud," #GautamAdani said')
doc2 = nlp('Adani Group takes over Mumbai International Airport Gautam Adani: Delighted to take over management of the world class Mumbai Intl Airport... Will build an airport ecosystem of future for biz, leisure &amp; entertainment Will create thousands of new local jobs')
doc3 = nlp('I love pizza and pasta')

print (doc1.similarity(doc2))
print (doc2.similarity(doc3))
print (doc1.similarity(doc3))