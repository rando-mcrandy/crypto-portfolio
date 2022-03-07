from pycoingecko import CoinGeckoAPI

class CoinData:

    def __init__(self):
        self.cg = CoinGeckoAPI()
        coin_list = self.cg.get_coins_list()

        self.symbol_to_id = {}
        for d in coin_list:
            symbol = d['symbol'].upper()
            id = d['id']
            if symbol not in self.symbol_to_id:
                self.symbol_to_id[symbol] = id

        self.id_to_symbol_name = {}
        for d in coin_list:
            symbol = d['symbol'].upper()
            id = d['id']
            name = d['name']
            if id not in self.id_to_symbol_name:
                self.id_to_symbol_name[id] = {'symbol': symbol, 'name': name}

        # hardcoded coin data (multiple coins with same symbol)
        if 'ADA' in self.symbol_to_id:
            self.symbol_to_id['ADA'] = 'cardano'
            self.id_to_symbol_name['cardano'] = {'symbol': 'ADA', 'name': 'Cardano'}
        if 'ETH' in self.symbol_to_id:
            self.symbol_to_id['ETH'] = 'ethereum'
            self.id_to_symbol_name['ethereum'] = {'symbol': 'ETH', 'name': 'Ethereum'}
        if 'LTC' in self.symbol_to_id:
            self.symbol_to_id['LTC'] = 'litecoin'
            self.id_to_symbol_name['litecoin'] = {'symbol': 'LTC', 'name': 'Litecoin'}
        if 'FIL' in self.symbol_to_id:
            self.symbol_to_id['FIL'] = 'filecoin'
            self.id_to_symbol_name['filecoin'] = {'symbol': 'FIL', 'name': 'Filecoin'}
        if 'COMP' in self.symbol_to_id:
            self.symbol_to_id['COMP'] = 'compound-governance-token'
            self.id_to_symbol_name['compound-governance-token'] = {'symbol': 'COMP', 'name': 'Compound'}
        if 'UNI' in self.symbol_to_id:
            self.symbol_to_id['UNI'] = 'uniswap'
            self.id_to_symbol_name['uniswap'] = {'symbol': 'UNI', 'name': 'Uniswap'}

    def get_price_data(self, symbols):
        vs_currencies='usd'
        removed = self._filter_symbols(symbols)

        # get price data (passed in symbols, need ids)
        prices = self.cg.get_price(ids=[self.symbol_to_id[symbol] for symbol in symbols if symbol in self.symbol_to_id], vs_currencies=vs_currencies)
        # reformat returned price data (need symbols)
        prices = {self.id_to_symbol_name[k]['symbol']: v[vs_currencies] for k, v in prices.items()}

        if 'USD' in prices:
            prices['USD'] = 1.0
        
        for r in removed:
            prices[r] = 0.0

        return prices

    def get_names(self, symbols):
        removed = self._filter_symbols(symbols)
        names = {symbol: self.id_to_symbol_name[self.symbol_to_id[symbol]]['name'] if symbol in self.symbol_to_id else symbol for symbol in symbols}
        if 'USD' in names:
            names['USD'] = 'US Dollar'

        for r in removed:
            names[r] = r
    
        return names

    def _filter_symbols(self, symbols):
        # TODO: Not supported symbols
        NOT_SUPPORTED = {'MILK', 'PAVIA', 'sNMS', 'MNEP', 'am3CRV-gauge', 't.me/maticroll', 'wPGX.app'}
        removed = set()
        for ns in NOT_SUPPORTED:
            if ns in symbols:
                symbols.remove(ns)
                removed.add(ns)
        return removed