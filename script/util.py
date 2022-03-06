import pandas as pd

def balances_dict_to_df(balances):
    temp = {'asset': [], 'amount': [], 'source': []}
    for k, v in balances.items():
        temp['asset'].append(k)
        temp['amount'].append(v['amount'])
        temp['source'].append(v['source'])
    return pd.DataFrame(temp)

def prices_dict_to_df(values):
    temp = {'asset': [], 'price (usd)': []}
    for k, v in values.items():
        temp['asset'].append(k)
        temp['price (usd)'].append(v)
    return pd.DataFrame(temp)

def names_dict_to_df(names):
    temp = {'asset': [], 'name': []}
    for k, v in names.items():
        temp['asset'].append(k)
        temp['name'].append(v)
    return pd.DataFrame(temp)