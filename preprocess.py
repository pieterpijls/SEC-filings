# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 16:57:16 2020

@author: ppijls
"""

import os
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from urllib.request import urlopen
import matplotlib.pyplot as plt
import requests
import pandas as pd
import numpy as np

# Idea: loop over text files: order by folder
# merge new filing in extra column on cusip and compute increase etc
# add ticker
# add market cap, industry etc.

cik_codes = pd.read_excel('C:/Users/ppijls/Documents/R/Projects/Trading systems/13F/Fund_Information/CIK_codes.xlsx')
cik_codes = cik_codes.CIK.values


ticker = '0001418814'#'0000908551'

# Read in text files  
mypath = 'C:/Users/ppijls/Documents/R/Projects/Trading systems/13F/13f/'+ticker+'/'
from os import listdir
from os.path import isfile, join
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]


positions_list = []

for file in list(onlyfiles):
    positions =     pd.read_csv(mypath+ file, sep='\t', lineterminator='\r',
                                    skiprows = 3, error_bad_lines=False)
    
    positions = positions.drop(['sshPrnamtType', 'investmentDiscretion', 'votingAuthoritySole',
                                'votingAuthorityShared', 'votingAuthorityNone'], axis=1)
    info =  pd.read_csv(mypath+ file, sep='\t', lineterminator='\r',
                          error_bad_lines=False, nrows=2)
    
    positions['Fund']        = info.columns.values[0].replace('Ticker: ','')
    positions['FilingDate']  = info.iloc[0].values[0].replace('\nFiling Date: ','')
    positions['Period']      = info.iloc[1].values[0].replace('\nPeriod of Report: ','')

    positions_list.append(positions)
    
   
    
df = pd.concat(positions_list)
df = df.set_index(['Period'])
    
    
    
df = positions_list[1]
df = df.set_index(['Period'])
df = df([''])
check = df.unstack(level = 1)













# Find ticker symbol
cusip_nums = positions['cusip'].values

tickers = []
ticker_dic = {c:"" for c in cusip_nums}
for c in list(ticker_dic.keys()):
    url = "http://quotes.fidelity.com/mmnet/SymLookup.phtml?reqforlookup=REQUESTFORLOOKUP&productid=mmnet&isLoggedIn=mmnet&rows=50&for=stock&by=cusip&criteria="+c+"&submit=Search"
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    ticker_elem = soup.find('tr', attrs={"bgcolor":"#666666"})
    ticker = ""
    try:
        ticker = ticker_elem.next_sibling.next_sibling.find('a').text
        ticker_dic[c] = ticker
        tickers.append(ticker)
    except:
        pass

tickers = pd.DataFrame.from_dict(ticker_dic, orient='index')
tickers.columns = ["Ticker"]
tickers['cusip'] = tickers.index
positions = positions.merge(tickers, left_on="cusip", right_on = "cusip")


# Add Previous Period







# Hedge Funds

#AWM INVESTMENT COMPANY, INC.
#BAUPOST GROUP LLC
#BLUE HARBOUR GROUP, L.P.
#CORVEX MANAGEMENT LP
#ELLIOTT MANAGEMENT CORP
#FARALLON CAPITAL MANAGEMENT LLC
#FRONTFOUR CAPITAL GROUP LLC
#GREENLIGHT CAPITAL INC
#ICAHN CARL C
#JANA PARTNERS LLC
#LUXOR CAPITAL GROUP, LP
#MARCATO CAPITAL MANAGEMENT LP
#NORTHERN RIGHT CAPITAL MANAGEMENT, L.P.
#PAR CAPITAL MANAGEMENT INC
#QVT FINANCIAL LP
#RAGING CAPITAL MANAGEMENT, LLC
#SACHEM HEAD CAPITAL MANAGEMENT LP
#SANDELL ASSET MANAGEMENT CORP.
#SARISSA CAPITAL MANAGEMENT LP
#SEIDMAN LAWRENCE B
#SPRINGOWL ASSOCIATES LLC
#STARBOARD VALUE LP
#TCI FUND MANAGEMENT LTD
#THIRD POINT LLC
#VALUEACT HOLDINGS, L.P.