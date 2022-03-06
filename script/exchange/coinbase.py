from coinbase.wallet.client import Client
from ..util import balances_dict_to_df

class CoinbaseApi:
    '''
    Interact with Coinbase Api to retrieve balances.
    https://developers.coinbase.com/api/v2
    '''

    def __init__(self, api_key, api_secret):
        self._api_key = api_key
        self._api_secret = api_secret
        self._client = Client(api_key, api_secret)

    def run(self):
        '''
        Execute retrieval of balances. 

        Return Example (dataframe):
          asset        amount     source
        0   BNB  5.4545454545   Coinbase
        1  USDC  44254.003133   Coinbase
        '''
        return self._get_balances()

    def _get_balances(self):
        '''
        Get balances via API call then format.
        Coinbase has "accounts" and a "primary account". Must make separate calls for each. 
        Must also make call for cash in account.
        '''
        unformated_balances = self._client.get_accounts()
        unformated_balances = unformated_balances['data']
        unformated_balances.append(self._client.get_primary_account())
        unformated_balances.append(self._client.get_account('USD'))
        
        balances = {}
        for b in unformated_balances:
            asset = b['balance']['currency']
            amount = float(b['balance']['amount'])
            if asset == 'CGLD': # coinbase calls it cgld for some reason...
                asset = 'CELO'
            if amount > 0.0:
                balances[asset] = {'amount': amount, 'source': 'coinbase'}

        return balances_dict_to_df(balances)
        

        