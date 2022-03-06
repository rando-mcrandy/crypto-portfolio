import urllib.parse
import hashlib
import hmac
import requests
import time
import json

class BinanceUSApi:
    '''
    Interact with BinanceUS Api to retrieve balances.
    https://docs.binance.us/?python#rest-api
    '''

    def __init__(self, api_key, api_secret):
        self._api_key = api_key
        self._api_secret = api_secret

    def run(self):
        '''
        Execute retrieval of balances. 

        Return Example:
        {
            'ETH' : {'amount': 4.2315164152', 'source': 'BinanceUS'},
            'BTC' : {'amount': 0.5423431145', 'source': 'BinanceUS'}
        }
        '''
        return self._get_balances()
        
    def _get_balances(self):
        '''
        Get balances via API call then format data
        '''
        data = {
            'timestamp': int(round(time.time() * 1000)),
        }
        uri_path = '/api/v3/account'
        unformated_balances = self._send_request(data, uri_path)
        
        balances = {}
        for b in unformated_balances:
            amount = float(b['free']) + float(b['locked'])
            if amount > 0.0:
                balances[b['asset']] = {'amount': amount, 'source': 'BinanceUS'}
        
        return balances

    def _get_binanceus_signature(self, data, secret):
        '''
        Get binanceus signature
        ''' 
        postdata = urllib.parse.urlencode(data)
        message = postdata.encode()
        byte_key = bytes(secret, 'UTF-8')
        mac = hmac.new(byte_key, message, hashlib.sha256).hexdigest()
        return mac

    def _send_request(self, data, uri_path):
        url = 'https://api.binance.us'
        headers = {}
        headers['X-MBX-APIKEY'] = self._api_key
        signature = self._get_binanceus_signature(data, self._api_secret) 
        params={
            **data,
            'signature': signature,
            }           
        req = requests.get((url + uri_path), params=params, headers=headers)
        return json.loads(req.text)['balances']
