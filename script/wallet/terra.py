from ast import Pass
from lib2to3.pgen2 import token
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

class TerraWallet:
    '''
    Interact with finder.terra.money using Selenium.
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
        0  Luna  5.4545454545     Terra-kszan
        1  UST   44254.003133     Terra-kszan
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
        coin_data, token_data = self._get_data(wallet)
        balances = {}

        coin_and_token_articles = []
        if coin_data:
            coin_and_token_articles += coin_data.find_elements(by=By.CLASS_NAME, value='card')
        if token_data:
            coin_and_token_articles += token_data.find_elements(by=By.CLASS_NAME, value='card')
        
        for article in coin_and_token_articles:
            coin_amount_pair = (article.text).split()[:2]
            balances[coin_amount_pair[0]] = {'amount': float((coin_amount_pair[1]).replace(',', '')), 'source': 'Terra-' + wallet[-5:]}
        
        return balances_dict_to_df(balances)

    def _get_data(self, wallet):

        coin_data, token_data = None, None
        try:
            self._driver.get(f'https://finder.terra.money/mainnet/address/{wallet}')

            # go to address page to fetch coins
            coin_data = WebDriverWait(self._driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/section/section/article[2]/section/div'))
            )
        except:
            print("Something went wrong in terra webdriverwait.")
            return None, None

        try:
            # check to see if there are tokens (tokens are the 3rd article out of 4 total iff wallet has tokens)
            WebDriverWait(self._driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/section/section/article[4]/section/div'))
            )
            token_data = WebDriverWait(self._driver, 3).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/section/section/article[3]/section/div'))
        )
        except:
            # print("no tokens")
            pass
                
        return coin_data, token_data

        
        
