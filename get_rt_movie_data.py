__author__ = 'Akhil'

import json
import urllib2
import pandas as pd
from datetime import datetime as dt
import time

apiKey = "u8j7q6zesvbf2mb44abmhfdp"
apiSuffix = "?apikey=" + apiKey
pageLimitSuffix = "&page_limit="
querySuffix ="&q="

def getRTDataForMovie(row):
    max_results = 50
    symbolsToReplace = ["&",":"]
    queryUrl = "http://api.rottentomatoes.com/api/public/v1.0/movies.json"

    strNameToUse = row.Name.replace(" ","+")
    for s in symbolsToReplace:
        strNameToUse = strNameToUse.replace(s,"")

    finalUrl = queryUrl+apiSuffix+querySuffix+strNameToUse+pageLimitSuffix+str(50)

    time.sleep(1.)
    try:
        response = urllib2.urlopen(finalUrl)
    except urllib2.HTTPError, e:
        print e.fp.read()

    jasonText = json.loads(response.read())
    numResults = jasonText["total"]
    outSeries = {"Name":row.Name,"Rank":row.Rank,"RTID":None,"RTData":None,"Ratings":None,\
                 "AudScore":None,"CriticsScore":None,"Cast":None,"RevLink":None}
    foundFlag = 0

    for i in range(min(numResults,max_results)):
        movie = jasonText["movies"][i]
        if movie["year"] == row.Year:
            print "Found", movie["title"],"as",row.Name
            foundFlag = 1
            outSeries["RTID"] = movie["id"]
            outSeries["RTData"] = json.dumps(movie)
            outSeries["Ratings"] = json.dumps(movie["ratings"])
            outSeries["AudScore"] = movie["ratings"]["audience_score"]
            outSeries["CriticsScore"] = movie["ratings"]["critics_score"]
            outSeries["Cast"] = json.dumps(movie["abridged_cast"])
            outSeries["RevLink"] = movie["links"]["reviews"]
            break

    if foundFlag == 0:
        print "No match found for ",row.Name

    return pd.Series(outSeries)

# Load list of movies and get RT data for them
min_year = 2009
month = 13
data = pd.read_csv("movieBudgets.csv")
data["ReleaseDate"] = data["ReleaseDate"].apply(lambda x: dt.strptime(x,"%Y-%m-%d").date())
data["Year"] = data["ReleaseDate"].apply(lambda x: x.year)
data["Month"] = data["ReleaseDate"].apply(lambda x: x.month)

# subset data and query Rotten Tomatoes
data2 = data[(data["Year"] > min_year) & (data["Month"] < month)]
data3 = data2.apply(getRTDataForMovie,1)

# merge with numbers data and save
data4 = pd.merge(data3,data)
data4.to_csv("movieRTAndBudgetData.csv",encoding="utf-8",index=False)
