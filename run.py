import os
from dotenv import load_dotenv
from script.exchange.binance_us import BinanceUSApi
# from script.exchange.celsius import CelsiusApi
from script.exchange.gemini import GeminiApi
from script.exchange.coinbase import CoinbaseApi
from script.wallet.bsc import BSCWallet
from script.wallet.cardano import CardanoWallet
from script.wallet.polygon import PolygonWallet
from script.coin_data import CoinData
import pandas as pd
from script.util import prices_dict_to_df, names_dict_to_df
pd.options.display.float_format = '{:,.6f}'.format


load_dotenv()

def get_balances():
    '''
    Get balances from exchanges and wallets
    '''
    balances = []
    if os.getenv('GEMINI_API_KEY') and os.getenv('GEMINI_API_SECRET'):
        balances.append(GeminiApi(os.getenv('GEMINI_API_KEY'), os.getenv('GEMINI_API_SECRET')).run())
    if os.getenv('BINANCEUS_API_KEY') and os.getenv('BINANCEUS_API_SECRET'):
        balances.append(BinanceUSApi(os.getenv('BINANCEUS_API_KEY'), os.getenv('BINANCEUS_API_SECRET')).run())
    if os.getenv('COINBASE_API_KEY') and os.getenv('COINBASE_API_SECRET'):
        balances.append(CoinbaseApi(os.getenv('COINBASE_API_KEY'), os.getenv('COINBASE_API_SECRET')).run())
    if os.getenv('BSC_WALLETS'):
        balances.append(BSCWallet(os.getenv('BSC_WALLETS').split(';')).run())
    if os.getenv('CARDANO_WALLETS'):
        balances.append(CardanoWallet(os.getenv('CARDANO_WALLETS').split(';')).run())
    if os.getenv('POLYGON_WALLETS'):
        balances.append(PolygonWallet(os.getenv('POLYGON_WALLETS').split(';')).run())

    if len(balances) == 0:
        print('lmao no accounts, poor loser')
        return None
    elif len(balances) == 1:
        return balances[0]
    else:
        return pd.concat(balances, ignore_index=True)

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
    price_data = get_price_data(coin_data, total_balances['asset'].to_list())
    names = get_names(coin_data, total_balances['asset'].to_list())

    # combine balances and price data
    df = pd.merge(total_balances, price_data, on='asset', how='left')

    # compute portfolio value
    df['value (usd)'] = df['amount'] * df['price (usd)']

    # compute totals
    df_sum = df.groupby('asset').sum().drop(columns='price (usd)').sort_values(by="value (usd)", ascending=False)
    df_sum = pd.merge(df_sum, price_data, on='asset', how='left')
    df_sum = pd.merge(df_sum, names, on='asset', how='left')
    df_sum = df_sum[['name', 'asset', 'price (usd)', 'amount', 'value (usd)']]
    price_data.fillna(0)

    print(f"Total Value (USD): {df['value (usd)'].sum()}")
    print(df_sum)
 