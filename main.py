__author__ = 'Akhil'

import numpy as np
import matplotlib.pyplot as plt
import json
import urllib2
import bs4
import pandas as pd
import lxml.html as lh
from datetime import datetime as dt
import time
import sklearn.linear_model
import statsmodels.api as sm
from patsy import dmatrices
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews

apiKey = "u8j7q6zesvbf2mb44abmhfdp"
apiSuffix = "?apikey=" + apiKey
pageLimitSuffix = "&page_limit="
querySuffix ="&q="

def getRTData():
    movieListUrl = "http://api.rottentomatoes.com/api/public/v1.0/lists/movies.json"
    dvdListUrl = "http://api.rottentomatoes.com/api/public/v1.0/lists/dvds.json"

    movieDict = {}

    # get list of movie lists
    # top_rentals, current_releases, upcomning etc
    response = urllib2.urlopen(movieListUrl+apiSuffix)
    jsonText = response.read()
    data = json.loads(jsonText)
    links = data["links"]

    for linkTitle,linkUrl in links.items():
        response = urllib2.urlopen(linkUrl+apiSuffix+pageLimitSuffix+str(50))
        movies = json.loads(response.read())["movies"]

        # loop over movies
        for movie in movies:
            title = movie["title"]
            revUrl = movie["links"]["reviews"]

            movieDict[title] = revUrl
            # reviews = json.loads(urllib2.urlopen(revUrl+apiSuffix+pageLimitSuffix+str(50)).read())["reviews"]

            # loop over the reviews for each movie
            # for r in reviews:
            #     print (title,r["critic"],r["publication"],r["freshness"])

    # get list of dvd lists
    # top_rentals, current_releases, upcomning etc
    response = urllib2.urlopen(dvdListUrl+apiSuffix)
    jsonText = response.read()
    data = json.loads(jsonText)
    links = data["links"]

    for linkTitle,linkUrl in links.items():
        response = urllib2.urlopen(linkUrl+apiSuffix+pageLimitSuffix+str(50))
        movies = json.loads(response.read())["movies"]

        # loop over movies
        for movie in movies:
            title = movie["title"]
            revUrl = movie["links"]["reviews"]

            movieDict[title] = revUrl

    print movieDict.keys()

def word_feats(words):
    return dict([(word, True) for word in words])

def trainClassifer():
    negids = movie_reviews.fileids('neg')
    posids = movie_reviews.fileids('pos')

    negfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'neg') for f in negids]
    posfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'pos') for f in posids]

    negcutoff = len(negfeats)*3/4
    poscutoff = len(posfeats)*3/4

    trainfeats = negfeats[:negcutoff] + posfeats[:poscutoff]
    testfeats = negfeats[negcutoff:] + posfeats[poscutoff:]
    print 'train on %d instances, test on %d instances' % (len(trainfeats), len(testfeats))

    classifier = NaiveBayesClassifier.train(trainfeats)
    print 'accuracy:', nltk.classify.util.accuracy(classifier, testfeats)
    classifier.show_most_informative_features()
    return classifier

def regressionAnalysis():
    # load data for 2013
    data3 = pd.read_csv("movieRTAndBudgetData.csv")
    data3 = data3.dropna()
    data3 = data3[(data3["Worldwide"] > 0 ) & (data3["CriticsScore"] > 0)]
    data3["PR"] = data3["Worldwide"] / data3["Budget"]
    data3["lW"] = np.log(data3["Worldwide"])
    data3["lB"] = np.log(data3["Budget"])


    # Use sklearn
    # model = sklearn.linear_model.LinearRegression()
    # model.fit(data3[["Budget","AudScore","CriticsScore"]].as_matrix(),data3[["Worldwide"]].as_matrix())
    # print model.intercept_,model.coef_

    minBudgetIndie = 0
    y, X = dmatrices("lW ~ lB + AudScore", data=data3[data3["Budget"]> minBudgetIndie], return_type="dataframe")
    model = sm.OLS(y, X)
    res = model.fit()
    print res.summary()

if __name__ == "__main__":

    classifier = trainClassifer()

    words = ["great","good","bad","john","sarcastic"]
    probs = classifier.prob_classify_many([word_feats(w) for w in words])
    for p,w in zip(probs,words):
        print w,p.prob("pos")




