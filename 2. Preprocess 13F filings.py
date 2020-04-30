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

# New test

# Idea: loop over text files: order by folder
# merge new filing in extra column on cusip and compute increase etc
# add ticker
# add market cap, industry etc.
hedge_funds = pd.read_excel('C:/Users/ppijls/Documents/R/Projects/Trading systems/13F/Fund_Information/CIK_codes.xlsx')
hedge_funds['CIK'] = [cik.replace('#','') for cik in hedge_funds.CIK.values] 
cik_codes = hedge_funds.CIK.values

fund_history = []
cusip_names    = []

for fund in list(cik_codes):
    print(fund)

    fundID = fund
    positions_list = []
    
    # Read in text files  
    mypath = 'C:/Users/ppijls/Documents/R/Projects/Trading systems/13F/13f/'+fundID+'/'
    from os import listdir
    from os.path import isfile, join
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    onlyfiles = [s for s in onlyfiles if "ASCII" not in s]
    onlyfiles = [s for s in onlyfiles if "ghostdriver" not in s]
    
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
     
         
    fund_pos = pd.concat(positions_list)
    quarters = fund_pos['Period'].unique()
    cusip = fund_pos[['cusip', '\nnameOfIssuer']] # save cik names
    fund_pos.rename(columns={'value':'amount', 'sshPrnamt':'Nshares'}, inplace=True)
    
    fund_pos = pd.melt(fund_pos, id_vars=['cusip', 'Period'], value_vars=['amount','Nshares'])
    fund_pos = pd.pivot_table(fund_pos, columns = ['Period','variable'], index = ['cusip'])
    fund_pos = fund_pos[fund_pos.columns[::-1]]
    
    cols = ['_'.join(col) for col in fund_pos.columns]
    cols = [col.replace('value_','') for col in cols] 
    fund_pos.columns = cols
    
    # Add deltas
    Nshares_cols = [col for col in fund_pos.columns if 'Nshares' in col]
    Amount_cols  = [col for col in fund_pos.columns if 'amount' in col]
    
    delta_nshares = fund_pos[Nshares_cols[::-1]].pct_change(axis=1)
    delta_amount  = fund_pos[Amount_cols[::-1]].pct_change(axis=1)
    
    delta = pd.merge(delta_nshares,delta_amount, left_index=True, right_index=True)
    cols = [col+'_delta' for col in delta.columns] 
    delta.columns = cols
    
    # add average share price
    for quarter in list(quarters):
        tmp = fund_pos[[col for col in fund_pos.columns if quarter in col]]
        avg_price =  (tmp.iloc[:,0]/tmp.iloc[:,1])*1000
        fund_pos[quarter+'_AvgPrice'] = avg_price

    # add position in fund per period
    fund_position = fund_pos[[col for col in fund_pos.columns if 'amount' in col]].apply(lambda x: x/x.sum())
    fund_position.columns = [col+'Pos%' for col in fund_position.columns] 
    
    
    
    # merge delta and fund_pos
    fund_pos = pd.merge(fund_pos,delta, left_index=True, right_index=True)
    fund_pos = pd.merge(fund_pos,fund_position, left_index=True, right_index=True)
    fund_pos = fund_pos.reindex(sorted(fund_pos.columns)[::-1], axis=1)
    fund_pos['CIK'] = fundID
    fund_pos['cusip']  = fund_pos.index
    
    # Add to list
    fund_history.append(fund_pos)
    cusip_names.append(cusip)


# Combine Funds
hedge_funds_pos = pd.concat(fund_history)
hedge_funds_pos = hedge_funds_pos.reindex(sorted(hedge_funds_pos.columns)[::-1], axis=1)
hedge_funds_pos = hedge_funds_pos.reset_index(drop=True)


# Add cusip Names
cusip_df = pd.concat(cusip_names)
cusip_df['\nnameOfIssuer'] = [col.replace('\n','') for col in cusip_df['\nnameOfIssuer']] 
cusip_df = cusip_df.drop_duplicates(subset=['cusip'])

hedge_funds_pos = hedge_funds_pos.merge(cusip_df, left_on='cusip', right_on='cusip')
hedge_funds_pos.rename(columns={'\nnameOfIssuer':'Stock'}, inplace=True)

# Add Fund Name
hedge_funds_pos = hedge_funds_pos.merge(hedge_funds, left_on='CIK', right_on='CIK')
hedge_funds_pos = hedge_funds_pos.reindex(sorted(hedge_funds_pos.columns)[::-1], axis=1)

# Order by delta => what about new positions
new_positions = hedge_funds_pos[hedge_funds_pos['2019-09-30_Nshares'].isnull() & hedge_funds_pos['2019-12-31_Nshares'].notna()]
hedge_funds_pos = hedge_funds_pos.sort_values(by=['2019-12-31_Nshares_delta'], ascending=False)


# write to excel
from datetime import date
today = date.today()
d1 = today.strftime("%d-%m-%Y")

#hedge_funds_pos.to_excel('C:/Users/ppijls/Documents/R/Projects/Trading systems/13F/hedge_fund_positions'+d1+ '.xlsx')


# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('C:/Users/ppijls/Documents/R/Projects/Trading systems/13F/hedge_fund_positions'+d1+ '.xlsx', engine='xlsxwriter')

# Write each dataframe to a different worksheet.
hedge_funds_pos.to_excel(writer, sheet_name='all_data')
new_positions.to_excel(writer, sheet_name='new_positions')

# Close the Pandas Excel writer and output the Excel file.
writer.save()


















# Find ticker symbol
#cusip_ids = hedge_funds_pos.cusip.unique()
#
#tickers = []
#ticker_dic = {c:"" for c in cusip_ids}
#for c in list(ticker_dic.keys()):
#    c = str(c)
#    url = "http://quotes.fidelity.com/mmnet/SymLookup.phtml?reqforlookup=REQUESTFORLOOKUP&productid=mmnet&isLoggedIn=mmnet&rows=50&for=stock&by=cusip&criteria="+c+"&submit=Search"
#    html = requests.get(url).text
#    soup = BeautifulSoup(html, 'lxml')
#    ticker_elem = soup.find('tr', attrs={"bgcolor":"#666666"})
#    ticker = ""
#    try:
#        ticker = ticker_elem.next_sibling.next_sibling.find('a').text
#        ticker_dic[c] = ticker
#        tickers.append(ticker)
#    except:
#        pass
#
#tickers = pd.DataFrame.from_dict(ticker_dic, orient='index')
#tickers.columns = ["Ticker"]
#tickers['cusip'] = tickers.index
#
#positions = positions.merge(tickers, left_on="cusip", right_on = "cusip")


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