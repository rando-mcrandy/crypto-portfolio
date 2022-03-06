import os
from dotenv import load_dotenv
from script.exchange.binance_us import BinanceUSApi
from script.exchange.celsius import CelsiusApi
from script.exchange.gemini import GeminiApi
from script.exchange.coinbase import CoinbaseApi
from script.wallet.bsc import BSCWallet
from script.coin_data import CoinData
import pandas as pd
from script.util import prices_dict_to_df, names_dict_to_df

load_dotenv()

def get_balances():
    '''
    Get balances from exchanges and wallets
    '''
    gemini_balances = GeminiApi(os.getenv('GEMINI_API_KEY'), os.getenv('GEMINI_API_SECRET')).run()
    binance_us_balances = BinanceUSApi(os.getenv('BINANCEUS_API_KEY'), os.getenv('BINANCEUS_API_SECRET')).run()
    coinbase_balances = CoinbaseApi(os.getenv('COINBASE_API_KEY'), os.getenv('COINBASE_API_SECRET')).run()
    bsc_balances = BSCWallet(os.getenv('BSC_WALLETS').split(';')).run()

    return pd.concat([gemini_balances, binance_us_balances, coinbase_balances, bsc_balances], ignore_index=True)

def get_price_data(coin_data, asset_symbols):
    '''
    Get price data from CoinGecko
    '''
    price_data = prices_dict_to_df(coin_data.get_price_data(asset_symbols))
    return price_data

def get_names(coin_data, asset_symbols):
    '''
    Get names from CoinGecko
    '''
    names = names_dict_to_df(coin_data.get_names(asset_symbols))
    return names

if __name__ == "__main__":
    # get balances
    total_balances = get_balances()

    # get price data
    coin_data = CoinData()
    price_data = get_price_data(coin_data, total_balances['asset'])
    names = get_names(coin_data, total_balances['asset'])

    # combine balances and price data
    df = pd.merge(total_balances, price_data, on='asset', how='left')

    # compute portfolio value
    df['value (usd)'] = df['amount'] * df['price (usd)']
    df = pd.merge(df, names, on='asset')

    # compute totals
    df_sum = df.groupby('name').sum().sort_values(by="value (usd)", ascending=False)
    print(f"Total Value (USD): {df['value (usd)'].sum()}")
    print(df_sum)
 


    

