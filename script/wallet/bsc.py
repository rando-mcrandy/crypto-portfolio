from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..util import balances_dict_to_df
import pandas as pd

class BSCWallet:
    '''
    Interact with BscScan using Selenium.
    Need PRO API to get tokens... sad
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
          asset        amount     source
        0   BNB  5.4545454545  BSC-722F5
        1  USDC  44254.003133  BSC-722F5
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
        data = self._get_data(wallet)
        balances = {}

        # parse table for balances
        rows = data.find_elements(By.TAG_NAME, 'tr')
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, 'td')
            asset = cols[2].text
            # sometimes asset is too long, need to get it from the tooltip
            if '...' in asset:
                asset = cols[2].find_element(By.TAG_NAME, 'span').get_attribute("data-original-title")
            # sometimes asset has BSC- in front, need to get rid of it
            if 'BSC-' in asset:
                asset = asset.replace('BSC-', '')
            amount = float(cols[3].text)
            
            balances[asset] = {'amount': amount, 'source': 'BSC-' + wallet[-5:]}
        
        return balances_dict_to_df(balances)

    def _get_data(self, wallet):
        self._driver.get(f'https://bscscan.com/tokenholdings?a={wallet}')
        try:
            WebDriverWait(self._driver, 10).until(
                EC.presence_of_element_located((By.ID, "td-0.1"))
            )
            return self._driver.find_element(By.XPATH, '//*[@id="tb1"]')
            
        except:
            print("Something went wrong in bscscan webdriverwait.")