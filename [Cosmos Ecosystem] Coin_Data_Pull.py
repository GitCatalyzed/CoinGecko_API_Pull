from pycoingecko import CoinGeckoAPI
import json
import csv
import pandas
from datetime import datetime
import tzlocal
import math
import numpy as np

#____________________________________________________________________________________________________________________#
#_____________________________________________CLASSES________________________________________________________________#
#____________________________________________________________________________________________________________________#
class StakingCoin():
    
    #CLASS OBJECT FOR STANDALONE STAKING COINS
    
    def __init__(self, coin_id, historical_prices):
        
        self.coin_id = coin_id
        self.historical_prices = historical_prices
    
    def assign_volatility(self, thirty_day_volatility, sixty_day_volatility, ninety_day_volatility):
        self.thirty_day_volatility = thirty_day_volatility
        self.sixty_day_volatility = sixty_day_volatility
        self.ninety_day_volatility = ninety_day_volatility
#____________________________________________________________________________________________________________________#
#_____________________________________________FUNCTIONS______________________________________________________________#
#____________________________________________________________________________________________________________________#        
def coin_gecko_api_pull(coins):
    
    #RETURNS A DICTIONARY OF EACH COIN (KEY) AND A LIST OF [(DATES, PRICES)] (VALUE)
    
    cg = CoinGeckoAPI()
    coin_dictionary = {}
    prices_dictionary = {}
    total_volumes_dictionary = {}
    market_caps_dictionary = {}
    
    #Each coin comes with 3 separate dictionaries (prices, total_volumes, market_caps)
    #The dictionary values are a list of lists; [Unix date, attribute] 
    for coin in coins:
        coin_dictionary[coin] = cg.get_coin_market_chart_by_id(id=coin,vs_currency = 'usd', days=1095, interval='daily')

    #Breaking apart the dictionary into specific attributes for easier manipulation
    for coin in coins:
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
        
    return time_series_prices


def calculate_volatility(historical_prices, time_horizon):
    
    #CALCULATES VOLATILITY FOR A USER INPUT TIME HORIZON (# OF DAYS BEFORE MOST RECENT DATA POINT)
    
    daily_price_returns = []
    daily_price_returns_squared = []
    missing_recent_date = False
    
    for day in range(1,time_horizon + 1):
         
        if historical_prices[-day][1] == 0 or historical_prices[-day-1][1] == 0:
            
            missing_recent_date = True
            pass
        
        else:
        
            daily_return =  math.log(historical_prices[-day][1]/historical_prices[-day-1][1])
            daily_price_returns.append(daily_return)
        
    sum_of_squared_returns = 0
    daily_price_returns_squared = []
    
    for daily_value in daily_price_returns:
        
        squared_return = daily_value**2
       
        daily_price_returns_squared.append(squared_return)
        
        sum_of_squared_returns = sum_of_squared_returns + squared_return
    
    daily_variance = 0
    
    if missing_recent_date:
        
        daily_variance = sum_of_squared_returns / (time_horizon - 2)
    
    else:
        
        daily_variance = sum_of_squared_returns / (time_horizon - 1)
        
    annual_variance = daily_variance * 365
    
    annual_volatility = math.sqrt(annual_variance)
    
    return annual_volatility
    

#____________________________________________________________________________________________________________________#
#_____________________________________________CODE BLOCK_____________________________________________________________#
#____________________________________________________________________________________________________________________# 

coin_list = ['akash-network', 'band-protocol', 'bitcanna', 'bitsong','bostrom', 'cerberus-2', 'certik', 'cheqd-network',\
            'chihuahua-token', 'comdex', 'cosmos', 'crypto-com-chain', 'cryptyk','darcmatter-coin', 'decentr','desmos',\
            'dig-chain', 'e-money', 'e-money-eur', 'hope-galaxy', 'ion','iris-network', 'ixo','juno-network','ki',\
            'likecoin','lum-network','medibloc','microtick','neta','osmosis','persistence','pstake-finance','regen',\
            'secret','sentinel','sommelier','stargaze','starname','terra-krw','terra-luna','terrausd','umee','vidulum','bitcoin']


historical_prices = coin_gecko_api_pull(coin_list)

staking_coins = []

for coin in coin_list:

    staking_coin = StakingCoin(coin, historical_prices[coin])
    
    thirty_day_volatility = calculate_volatility(staking_coin.historical_prices, 30)
    sixty_day_volatility = calculate_volatility(staking_coin.historical_prices, 60)
    ninety_day_volatility = calculate_volatility(staking_coin.historical_prices, 90)
    
    staking_coin.assign_volatility(thirty_day_volatility, sixty_day_volatility, ninety_day_volatility)
    staking_coins.append(staking_coin)
    

for coin in staking_coins:
    print(coin.coin_id)
    print(f'30 day vol: {coin.thirty_day_volatility}, 60 day vol: {coin.sixty_day_volatility}, 90 day vol: {coin.ninety_day_volatility}')
    
    
