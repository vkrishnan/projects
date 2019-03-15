"""
This module contains utility functions for selenium that is used by SPP automation.
"""

ROBOT_LIBRARY_VERSION = '0.1'
__version__ = ROBOT_LIBRARY_VERSION

import time
import os
import sys
import logging
from selenium import webdriver

logger = logging.getLogger('SeleniumApi')
fh = logging.FileHandler('Selenium_Api.log')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

timeout = 180

def monkeysleep(seconds ):
    while( seconds > 0 ):
        time.sleep( 1 );
        seconds = seconds - 1;

def monkey_click_by_id(driver,theid ):
    # click on something, like a monkey :)
    monkeysleep(2);
    driver.find_element_by_id(theid).click()

def monkey_click_by_xpath(driver, xpath ):
    # Click element based on xpath
    monkeysleep(2)
    driver.find_element_by_xpath(xpath).click()

def monkey_type_by_id(driver, theid, text ):
    # Enter a text based on id
    monkeysleep(2)
    driver.find_element_by_id(theid).send_keys(text)

def confirm_page_load(driver, expected_title, lpath):
    """ Check for the title to load otherwise relode the page"""

    logger.info("Checking if " + expected_title + " page is loaded")
    title = driver.title
    count = 0
    while expected_title not in title:
        monkeysleep(5)
        title = driver.title
        count += 5
        if count >= 300:
            raise SppAssertionError("Problem in loading %s page" %(expected_title),
                                    "PageLoadFailed",lpath,driver)
        if count%60 == 0:
            driver.refresh()

    logger.info(expected_title + " page is loaded")

'''
Created on 15 Nov, 2016
@author: Abhishek
'''
def set_firefox_profile():
    """
    Sets browser to firefox for testing
    """
    fp = webdriver.FirefoxProfile()
    fp.set_preference("network.proxy.type", 0 )
    driver = webdriver.Firefox()
    return driver

def set_chrome_profile():
    """
    Sets browser to chrome for testing
    """
    driver = webdriver.Chrome()
    return driver

'''
Created on 15 Nov, 2016
@author: Abhishek
'''
def launch_browser_and_open_URL(driver, page_url, expected_title, lpath):
    """ Launch browser and open provided page"""

    logger.info("Launching browser and redirecting to URL: %s"%(page_url))
    driver.get(page_url)
    driver.maximize_window()
    time.sleep(5)
    confirm_page_load(driver, expected_title, lpath)


class SppAssertionError(AssertionError):
    """
    Raise assertion error and log the error. Take a screnshot of page if necessary.
    """
    def __init__(self, msg, screenshot_name = None, log_path = None, driver = None):
        logger.error(msg)
        if screenshot_name != None:
            driver.save_screenshot('%s\\Failure_ScreenShots\\%s.png'%(log_path,screenshot_name))
        AssertionError.__init__(self,msg)

class SeleniumApi(object):
    """
    Class contains functions that is used by SPP automation via Selenium.
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        """
        SeleniumApi constructor
        """
        self.local_references= {}
        self.local_references['logger'] = logger
        self.local_references['SppAssertionError'] = SppAssertionError
        self.local_references['launch_browser_and_open_URL'] = launch_browser_and_open_URL
        self.local_references['set_chrome_profile'] = set_chrome_profile
        self.local_references['set_firefox_profile'] = set_firefox_profile
        self.local_references['confirm_page_load'] = confirm_page_load
        self.local_references['monkeysleep'] = monkeysleep
        self.local_references['monkey_type_by_id'] = monkey_type_by_id
        self.local_references['monkey_click_by_id'] = monkey_click_by_id
        self.local_references['monkey_click_by_xpath'] = monkey_click_by_xpath

        self.guidedObj = None
        self.PIVobj = None

    '''
    Created on 15 Nov, 2016
    @author: Abhishek
    '''
    def start_interactive_installation(self, hpsum_version, user,password, lpath, run_count, url):
        """
        Start Localhost Guided Update , then select interactive installation mode
        """
        
        #Singleton object for guided installation class
        if not self.guidedObj:
            import Selenium_Guided
            self.guidedObj = Selenium_Guided.SPPGuidedInstallation(hpsum_version, self.local_references)

        status = self.guidedObj.start_interactive_installation(user, password, lpath, run_count, url)
        return status

    '''
    Created on 15 Nov, 2016
    @author: Abhishek
    '''
    def verify_review_page_and_deploy(self,lpath,run_count):
        """ Verify the Review page, select all the
            required Component and take screenshot"""
        status = self.guidedObj.verify_review_page_and_deploy(lpath,run_count)
        return status

    '''
    Created on 15 Nov, 2016
    @author: Abhishek
    '''
    def remove_dependency_components(self,cp_ids):
        """ This Function Will take the cp_id and
        uncheck the component to stop from being deployed"""
        status = self.guidedObj.remove_dependency_components(cp_ids)
        return status

    '''
    Created on 15 Nov, 2016
    @author: Abhishek
    '''
    def deploy_and_take_screenshot(self,lpath,run_count):
        """ Deploy and take screenshots """
        status = self.guidedObj.deploy_and_take_screenshot(lpath,run_count)
        return status

    '''
    Created on 15 Nov, 2016
    @author: Abhishek
    '''
    def reboot_system(self,run_count,lpath):
        """ Reboot the system by clicking reboot button on the page"""
        status = self.guidedObj.reboot_system(run_count,lpath)
        return status

    def close_browser(self):
        """
        Closes the browser
        """
        self.guidedObj.close_browser()
        return True

    '''
    Created on 15 Nov, 2016
    @author: Abhishek
    '''
    def close_firefox_browser(self):
        """
        Close firefox browser
        """
        self.guidedObj.close_firefox_browser()
        return True

    '''
    Created on Feb 1,2017
    @author: Abhishek
    '''
    def smh_piv_check(self, url, user, password, lpath, os_platform , server):
        """
        Verify PIV
        """
        import Selenium_PIV
        self.PIVobj = Selenium_PIV.SMH_PIV(self.local_references,)
        if 'synergy' == server:
            status = self.PIVobj.check_only_webapp(url, user, password, lpath, os_platform)
        else:
            status = self.PIVobj.start_piv_check(url, user, password, lpath, os_platform)
        return status

    def smh_piv_wrapup(self,):
        """
        Wrapup PIV
        """
        self.PIVobj.wrap_up()
        return True

