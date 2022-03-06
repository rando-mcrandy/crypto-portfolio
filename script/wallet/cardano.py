from math import comb
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..util import balances_dict_to_df
import pandas as pd

class CardanoWallet:
    '''
    Interact with CardanoScan using Selenium.
    '''

    def __init__(self, wallets):
        '''
        Init driver and wallets
        '''
        s=Service(ChromeDriverManager().install())
        options = Options()
        options.headless = True
        options.add_argument("--window-size=1920,1200")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self._driver = webdriver.Chrome(options=options, service=s)
        self._wallets = wallets

    def __del__(self):
        self._driver.quit()

    def run(self):
        '''
        Execute retrieval of balances.

        Return Example (dataframe):
          asset        amount          source
        0   ADA  5.4545454545   Cardano-722F5
        1  MILK  44254.003133   Cardano-722F5
        '''

        combined_balances = None
        # get balances for each wallet and combine
        for wallet in self._wallets:
            balances = self._get_balances(wallet)
            if combined_balances is None:
                combined_balances = balances
            else:
                combined_balances = pd.concat([combined_balances, balances], ignore_index=True)
        
        return combined_balances
    
    def _close_driver(self):
        self._driver.quit()

    def _get_balances(self, wallet):
        ada_amount, tokens_data = self._get_data(wallet)
        balances = {}

        if ada_amount > 0.0:
            balances['ADA'] = {'amount': ada_amount, 'source': 'Cardano-' + wallet[-5:]}

        # parse tokens from table
        if tokens_data is not None:
            rows = tokens_data.find_elements(By.TAG_NAME, 'tr')
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                asset = cols[1].text
                amount = float(cols[3].text)
            
                balances[asset] = {'amount': amount, 'source': 'Cardano-' + wallet[-5:]}
        
        return balances_dict_to_df(balances)

    def _get_data(self, wallet):
        try:
            self._driver.get(f'https://cardanoscan.io/address/{wallet}')

            # go to address page to fetch ada amount and check if wallet has tokens
            ada_amount = WebDriverWait(self._driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="addressDetailsPage"]/div/div/div[3]/div/div[2]/div[3]/div[2]/div[2]/span[1]/span'))
            )
            has_tokens = "NO TOKENS" not in self._driver.find_element(By.XPATH, '//*[@id="addressDetailsPage"]/div/div/div[1]/div/div[3]/div').text
            ada_amount = float(ada_amount.text.replace(',', ''))
            
            # fetch token amounts (if applicable)
            tokens_data = None
            if has_tokens:
                self._driver.get(f'https://cardanoscan.io/tokenholdings/{wallet}')
                WebDriverWait(self._driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="tokenHoldings"]/div/div/div/div/div[4]/div[1]/div[2]/div/div/div/table/tbody/tr[1]/td[1]'))
                )
                tokens_data = self._driver.find_element(By.XPATH, '//*[@id="tokenHoldings"]/div/div/div/div/div[4]/div[1]/div[2]/div/div/div/table/tbody')
            
            return ada_amount, tokens_data
            
        except:
            print("Something went wrong in bscscan webdriverwait.")
