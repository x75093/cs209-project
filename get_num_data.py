__author__ = 'Akhil'

import pandas as pd
import lxml.html as lh
from datetime import datetime as dt

def getNumbersData():
    url = "http://www.the-numbers.com/movie/budgets/all"
    doc = lh.parse(url)
    trs = doc.iter("tr")

    l = []
    i = 0
    for tr in trs:
        cont = tr.text_content()
        lst = cont.splitlines()
        if len(lst) < 5: continue
        l.append(lst)
        i += 1

    data = pd.DataFrame(l)
    data.columns = ["Rank","ReleaseDate","Name","Budget","Domestic","Worldwide","Del"]
    newCols = list(data.columns)
    newCols.remove("Del")
    data = data[newCols]

    data["ReleaseDate"] = data["ReleaseDate"].apply(lambda x: dt.strptime(x,"%m/%d/%Y"))
    data["Budget"] = data["Budget"].apply(lambda x: x.replace("$","").replace(",",""))
    data["Domestic"] = data["Domestic"].apply(lambda x: x.replace("$","").replace(",",""))
    data["Worldwide"] = data["Worldwide"].apply(lambda x: x.replace("$","").replace(",",""))

    data.Budget = data.Budget.convert_objects(convert_numeric=True)
    data.Domestic = data.Domestic.convert_objects(convert_numeric=True)
    data.Worldwide = data.Worldwide.convert_objects(convert_numeric=True)

    data["ReleaseDate"] = data["ReleaseDate"].apply(lambda x: x.date())
    data["Year"] = data["ReleaseDate"].apply(lambda x: x.year)
    return data

# Get numbers data
data = getNumbersData()
data.to_csv("movieBudgets.csv",encoding="utf8",header=True,index=False)
