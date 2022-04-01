#!/usr/bin/env python
# coding: utf-8

# In[ ]:


pip install tzlocal


# In[ ]:


from pycoingecko import CoinGeckoAPI
import json
import csv
from datetime import datetime
import tzlocal

cg = CoinGeckoAPI()
coin_dictionary = {}
prices_dictionary = {}
total_volumes_dictionary = {}
market_caps_dictionary = {}

#limit of 50 calls per minute sets maximum list size for data pull
#cosmos ecosystem coins
coin_list = ['akash-network', 'band-protocol', 'bitcanna', 'bitsong','bostrom', 'cerberus-2', 'certik', 'cheqd-network',            'chihuahua-token', 'comdex', 'cosmos', 'crypto-com-chain', 'cryptyk','darcmatter-coin', 'decentr','desmos',            'dig-chain', 'e-money', 'e-money-eur', 'hope-galaxy', 'ion','iris-network', 'ixo','juno-network','ki',            'likecoin','lum-network','medibloc','microtick','neta','osmosis','persistence','pstake-finance','regen',            'secret','sentinel','sommelier','stargaze','starname','terra-krw','terra-luna','terrausd','umee','vidulum']

#Each coin comes with 3 separate dictionaries (prices, total_volumes, market_caps)
#The dictionary values are a list of lists; [Unix date, attribute] 
for coin in coin_list:
    coin_dictionary[coin] = cg.get_coin_market_chart_by_id(id=coin,vs_currency = 'usd', days=365, interval='daily')


# In[ ]:


#Breaking apart the dictionary into specific attributes for easier manipulation
for coin in coin_list:
    prices_dictionary[coin] = coin_dictionary[coin]['prices']
    total_volumes_dictionary[coin] = coin_dictionary[coin]['total_volumes']
    market_caps_dictionary = coin_dictionary[coin]['market_caps']
    
#Converting Unix Timestamp from CoinGecko API to desired format
date_conversion_list = []
local_timezone = tzlocal.get_localzone()
for date in prices_dictionary['cosmos']:
    unix_timestamp = float(date[0]/1000)
    local_time_unformatted = datetime.fromtimestamp(unix_timestamp, local_timezone)
    local_time = local_time_unformatted.strftime("%m/%d/%y")
    date_conversion_list.append((date[0], local_time))

#Now I am going to use the dateconversion list to rerack the dictionary so that things can be found by date
#We will need this to link in the market data for betas and correlation
time_series_prices = {}

for coin in coin_list:
    daily_coin_prices = []
    coin_dates = []
    for entry in prices_dictionary[coin]:
        coin_dates.append(entry[0])
    
    for date in date_conversion_list:
        #see if the date exists for the coin
        if date[0] in coin_dates:
            for entry in prices_dictionary[coin]:
                if date[0]==entry[0]:
                    daily_coin_prices.append((date[1], entry[1]))
        else:
            daily_coin_prices.append((date[1],0))
            
    time_series_prices[coin] = daily_coin_prices
       
                
        
       
time_series_prices 
 


# In[ ]:


time_series_prices_json = json.dumps(time_series_prices)


# In[ ]:


with open('time_series_prices.json','w') as outfile:
    outfile.write(time_series_prices_json)


# In[ ]:




