# -*- coding: utf-8 -*-
"""
Created on Mon Sep 12 17:10:32 2022

@author: kknow
"""

import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import SessionNotCreatedException

# TODO Consider where to put the default logger for dev_util
from dev_util.app_util import logger

# TODO Move this to browser_util
class BaseChromeDriver():
    """
    Base class for chrome driver for selenium-based web requests.  This is an
    attempt to refactor the driver into a reusable base class, so that 
    specialized implementations do not have to reimplement the driver
    capability each time.
    
    This class uses the selenium python api (https://www.scrapingbee.com/blog/selenium-python/)
    and chrome driver.  The main method for getting the authorization key opens a 
    chrome browser, prompts the user for a password if needed, and extracts the 
    target authorization key from the request headers within the message logs.
    
    Check selenium.dev site for additional API documentation
    
    This implementation is based on an adaption of the original 
    dev.market.market.MarketKeyFinder class from the mktstats-dash project
    
    """
    
    def __init__(self, headless=True):
        
        # Check https://sites.google.com/chromium.org/driver/ for updates
        # TODO This will need to be generalized for Heroku
        # This link may help: https://medium.com/@mikelcbrowne/running-chromedriver-with-python-selenium-on-heroku-acc1566d161c
        # self.DRIVER_PATH = 'C:/Users/kknow/Downloads/chromedriver_win32_v100/chromedriver.exe'
        self.DRIVER_PATH = 'C:/Users/kknow/Downloads/chromedriver_win32_v101/chromedriver.exe'
        self.headless = headless
        
        # Cache for performance enhancements
        self.enable_driver_cache = True # Flag for enabling/disabling driver caching
        self._driver = None
        self._driver_wait_secs = 5 # wait time for driver requests to prevent timeouts

        # Example        
        # market_id = 7001
        # contract_id = 24517
        
        return None

    def __init_chrome_driver__(self):
        """
        Creates a default instance of the chrome driver

        Returns
        -------
        driver : TYPE
            DESCRIPTION.

        """
        
        driver_path = self.DRIVER_PATH
    
        # Enable performance logging
        # https://stackoverflow.com/questions/27644615/getting-chrome-performance-and-tracing-logs
        caps = DesiredCapabilities.CHROME.copy()
        # as per latest docs
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}
        caps['goog:perfLoggingPrefs'] = {'enableNetwork': True}
        
        # TODO Generalize options and add support for derived class customization
        # These settings are useful for testing.
        # chrome_options = Options()
        chrome_options = webdriver.ChromeOptions()
        if self.headless:
            chrome_options.add_argument("--headless") # hide the browser window
        # chrome_options.add_argument("--window-size=1920x1080") # show the browser window with the specified dimensions
        # chrome_options.page_load_strategy = 'eager'
        # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # chrome_options.add_experimental_option("useAutomationExtension", False)

        # KK 10/27/21: Added error checking for mismatch between chrome driver and chrome
        # Previously, error message appeared in debug but not run mode    
        try:
            
            service = ChromeService(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options, desired_capabilities=caps)
            
            
            # driver = webdriver.Chrome(executable_path=driver_path, desired_capabilities=caps, options=chrome_options)
            # driver.fullscreen_window()
        except SessionNotCreatedException as e:
            logger.error('ChromeDriver version mismatch.')
            print(str(e))
            return None
        
        if self.enable_driver_cache:
            self._driver = driver
        # driver = webdriver.Chrome(executable_path=DRIVER_PATH, desired_capabilities=caps)
        
        return driver
    
    def __get_chrome_driver__(self):
        
        if self._driver is None:
            driver = self.__init_chrome_driver__()
        else:
            driver = self._driver
            
        return driver
    
    def get_item(self, key_type, key_val, parent_item, timeout_secs=None):
        
        timeout_secs = self._driver_wait_secs if timeout_secs is None else timeout_secs
        
        try:
            item = WebDriverWait(parent_item, timeout=timeout_secs).until(lambda d: d.find_element(by=key_type, value=key_val))
            logger.info("Found item by key type: {} with key value: {}".format(key_type, key_val))
            return item
        except:
            logger.info("Timeout waiting for key type: {} with key value {}".format(key_type, key_val))
            return None
            
        return 

    def get_item_by_id(self, item_id, parent_item, timeout_secs=None):        
        return self.get_item(key_type=By.ID, key_val=item_id, parent_item=parent_item, timeout_secs=timeout_secs)

    def get_item_by_tag_name(self, tag_name, parent_item, timeout_secs=None):
        return self.get_item(key_type=By.TAG_NAME, key_val=tag_name, parent_item=parent_item, timeout_secs=timeout_secs)
    
    def get_and_click_item(self, key_type, key_val, parent_item, timeout_secs=None):        
        
        timeout_secs = self._driver_wait_secs if timeout_secs is None else timeout_secs

        try:
            # https://www.selenium.dev/documentation/webdriver/waits/
            wait = WebDriverWait(parent_item, timeout=timeout_secs)
            # item = self.get_item_by_id(item_id, parent_item, timeout_secs)
            # item = wait.until(EC.element_to_be_clickable(item))
            item = wait.until(EC.element_to_be_clickable((key_type, key_val)))
            item.click()            
            logger.info("Found and clicked item for key type: {} with key value: {}".format(key_type, key_val))
            # return item
        except:
            logger.info("Timeout waiting for clickable item for key type {} with key value: {}".format(key_type, key_val))
            return None

        return None        

    def get_and_click_item_by_id(self, item_id, parent_item, timeout_secs=None):
        return self.get_and_click_item(key_type=By.ID, key_val=item_id, parent_item=parent_item)

    def get_webdriver(self):
        return self.__get_chrome_driver__()
        
    def open_url(self, url):
        
        driver = self.__get_chrome_driver__()
        
        if driver is None:
            logger.error("Unable to initialize chromedriver.")

        driver.get(url)

        return driver
    
    def get_table_header(self, tbl):
        
        # tbl_header = tbl.find_element_by_tag_name('thead')
        # tbl_header = tbl.findElements(By.tagName("thead"))
        tbl_header = self.get_item_by_tag_name('thead', tbl)

        if tbl_header is None:
            logger.error("Unable to find table header")
        
        return tbl_header
        
    def get_table_body(self, tbl):
        
        # tbl_body = tbl.find_element_by_tag_name('tbody')
        tbl_body = self.get_item_by_tag_name('tbody', tbl)

        if tbl_body is None:
            logger.error("Unable to find table body")
        
        return tbl_body
    
    def get_table_data_as_df(self, tbl_id, parent_item, timeout_secs=5):
        
        # tbl_id = 'tblDailyYieldCurve'
        
        # tbl = driver.find_element_by_id(tbl_id)
        tbl = self.get_item_by_id(tbl_id, parent_item)        

        if tbl is None:
            logger.error("Unable to find table data for id: {}".format(tbl_id))
            return None
    
        thead = self.get_table_header(tbl)
        col_names = [th.text for th in thead.find_elements(By.TAG_NAME, 'th')]
        
        tbody = self.get_table_body(tbl)
        row_data = [ [td.text for td in trow.find_elements(By.TAG_NAME, 'td')] for trow in tbody.find_elements(By.TAG_NAME, "tr")] 

        df = pd.DataFrame(data=row_data, columns=col_names)
        
        # https://anaasher.medium.com/web-scraping-how-to-use-python-selenium-to-extract-data-from-html-table-7e6e3bcaebd6
        # Read and Convert Web table into data frame
        # webtable_df = pd.read_html(driver.find_element_by_xpath("//table[@id='dtTbl']").get_attribute('outerHTML'))[0]
        
        # WebDriverWait(tbl, timeout=timeout_secs).until(lambda t: EC.visibility_of_all_elements_located(t))
        
        # tbl_html = tbl.get_attribute('outerHTML')
        # df = pd.read_html(tbl_html)[0]

        return df

