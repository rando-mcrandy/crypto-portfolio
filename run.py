import os
from dotenv import load_dotenv
from script.exchange.binance_us import BinanceUSApi
from script.exchange.gemini import GeminiApi
import pandas as pd

load_dotenv()

def balances_dict_to_df(balances):

    temp = {'asset': [], 'amount': [], 'source': []}

    for k, v in balances.items():
        temp['asset'].append(k)
        temp['amount'].append(v['amount'])
        temp['source'].append(v['source'])
    
    return pd.DataFrame(temp)


gemini_balances = GeminiApi(os.getenv('GEMINI_API_KEY'), os.getenv('GEMINI_API_SECRET')).run()
binance_us_balances = BinanceUSApi(os.getenv('BINANCEUS_API_KEY'), os.getenv('BINANCEUS_API_SECRET')).run()

gemini_balances = balances_dict_to_df(gemini_balances)
binance_us_balances = balances_dict_to_df(binance_us_balances)

total_balances = pd.concat([gemini_balances, binance_us_balances], ignore_index=True)
print(total_balances)
print(total_balances.groupby('asset').sum())



    

