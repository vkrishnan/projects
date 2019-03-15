# -*- coding: utf-8 -*-
'''
This module used to Install SPP with GUI on offline mode.
'''
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.action_chains import ActionChains
import unittest
import sys
import time
import os
import subprocess
import logging
import shutil

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s  %(levelname)-8s %(message)s',
                    filename='/tmp/spp_offline_install.log',
                    filemode='w')

# click on something, like a monkey :)
def monkey_click_by_id( driver, theid ):
    time.sleep(2)
    driver.find_element_by_id(theid).click()

# Click element based on xpath
def monkey_click_by_xpath( driver, xpath ):
    time.sleep(2)
    driver.find_element_by_xpath(xpath).click()

# Enter a text based on id
def monkey_type_by_id( driver, theid, text ):
    time.sleep(2)
    driver.find_element_by_id(theid).send_keys(text)

    '''
    Created on Oct 13, 2015
    @author: Sriram Chowdary
    '''
def wait_until_inventory_completes( driver , timeout ):
    """
    Wait till inventory complete with in a given time and return True or False.

    driver - Webdriver driver.

    timeout - Wait time for come out if inventory doesn't complete given timeout.

    Example:
    | wait_until_inventory_completes | driver | 1800 |
    """
    for i in range(timeout):
        time.sleep(10)
        try:
            ele = driver.find_elements_by_xpath(".//*[@id='hpsum-otu-inventory-node']/tbody/tr/td[3]")[0]
            print 'Inventory status is : ',ele.text
            logging.info("Inventory status is : " + ele.text )
        except IndexError:
            print " \n Inventory not started \n "
            logging.error(" \n Inventory not started \n " )
            return False

        if 'failed' in str(ele.text):
            print driver.find_elements_by_xpath(".//*[@id='hpsum-otu-inventory-node']/tbody/tr/td[5]").text
            return False
        if 'Inventory completed' not in str(ele.text):
            continue
        else:
            return True
    return False

    '''
    Created on Oct 13, 2015
    @author: Sriram Chowdary
    '''
def wait_until_deployment_completes( driver , timeout ):
    """
    Wait till deployment complete with in a given time and return True or False.

    driver - Webdriver driver.

    timeout - Wait time for come out if deployment doesn't complete given timeout.

    Example:
    | wait_until_deployment_completes | driver | 1800 |
    """
    for i in range(timeout):
        time.sleep(10)
        try:
            ele = driver.find_elements_by_xpath(".//*[@id='hpsum-otu-install-progress']/tbody/tr/td[3]")[0]
            print 'Deployment status is : ',ele.text
            logging.info("Deployment status is : " + ele.text )
        except IndexError:
            print " \n Deployment not started \n"
            logging.error("Deployment not started ")
            return False

        if 'Deployment error' in str(ele.text):
            Text = driver.find_elements_by_xpath(".//*[@id='hpsum-otu-install-progress']/tbody/tr/td[5]")[0]
            print "Deployment error was ::  " , Text.text
            logging.error("Deployment error was ::  " + Text.text)
            return False

        if 'failed' in str(ele.text):
            print driver.find_elements_by_xpath(".//*[@id='hpsum-otu-install-progress']/tbody/tr/td[5]").text
            return False
        if str(ele.text) not in ["Deployment completed","Install done with error(s)"]:
            continue
        else:
            return True
    return False

class Test(unittest.TestCase):
    '''
    Created on Oct 13, 2015
    @author: Sriram Chowdary
    '''
    def setUp(self):
        """
        Setup variables,web driver and create log folder.

        """
        print '\n Setup Started '
        logging.info(" Setup Started ")
        os.system( '/opt/hp/hpsum/x64/hpsum_bin_x64 --mode offline_interactive &')
        logging.info("Ran offline_interactive command")
        time.sleep(80)
        os.system('killall firefox')
        fp = webdriver.FirefoxProfile()
        fp.set_preference("network.proxy.type", 0 );
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        self.base_url = "localhost:63001/index.html#/guided.update/show"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.username = 'root'
        self.password = 'hpinvent'
        self.ret = False
        self.total = 0
        self.log_dir = 'Log_{{iloip}}'
        self.log_path = '/tmp/{0}'.format(self.log_dir)
        if not os.path.exists(self.log_path):
            logging.info("log_path is   " +  str(self.log_path))
            os.makedirs(self.log_path)

    '''
    Created on Oct 13, 2015
    @author: Sriram Chowdary
    '''
    def test_(self):
        """
        Install SPP with GUI on offline mode.

        """
        print ' \n Test case Started \n'
        logging.info("Test case Started ")
        os.system( 'hpblob -d -k SMARTSTART_SELENIUM -f /tmp/selenium')
        logging.info("Removed Selenium file ")
        driver = self.driver
        os.system('start_sshd.sh')
        #######     OPEN MAIN PAGE      ########
        driver.get(self.base_url)
        time.sleep(5)
        driver.maximize_window()
        for i in range(0,20):
            time.sleep(10)
            title = driver.title
            logging.info("Title is   :: " +  str(title))
            if 'Smart Update Manager' in title: break
            if 'Smart Update Manager' not in title: driver.refresh()

        if 'Smart Update Manager' not in title:
             print "\n  Problem in Loading HP Smart Update Manager page "
             logging.error("  Problem in Loading HP Smart Update Manager page " )
             return False
        logging.info("Opened HP Smart Update Manager Page")

        # Enter Username
        monkey_type_by_id( driver, "hp-login-user",self.username )

        # Enter Password
        monkey_type_by_id( driver, "hp-login-password",self.password )

        # Click on Login button
        monkey_click_by_id( driver, "hp-login-button" )
        time.sleep(10)

        # Click on hpsum-menu-guide-close
        try:
            monkey_click_by_id( driver, "hpsum-menu-guide-close" )
            time.sleep(2)
        except:
            pass

        # Click on HP Smart Update Manager dropdown
        try:
            monkey_click_by_xpath( driver, "//*[@id='hp-main-menu-control']/div[3]" )
        except:
               pass
        time.sleep(2)

        # Click on Localhost Guided Update
        try:
            monkey_click_by_xpath( driver, ".//*[@id='hp-main-menu']/ul/li[2]/ul/li[1]/a")
        except:
               logging.error("Problem on Click Local host Guided Update  ")
        time.sleep(2)

        # Click "Interactive Mode" radio button
        try:
             monkey_click_by_id( driver, "interactive-mode" )
        except:
             logging.error("Problem on Clicking Interactive Mode  ")

        time.sleep(2)

        # Click "OK" button
        try:
            monkey_click_by_id( driver, "hpsum-action-ok-button" )
        except:
             logging.error("Problem on Clicking OK button  ")

        # Wait until inventory completes
        time.sleep(5)
        driver.save_screenshot('{0}/Inventory.png'.format(self.log_path))
        self.ret = wait_until_inventory_completes( driver , 400 )
        logging.info("Inventory ret is ::  " + str(self.ret))
        menu = driver.find_element_by_xpath("//*[@id='step0commands']")
        hover = ActionChains(driver).move_to_element(menu)
        hover.perform();time.sleep(3)
        driver.save_screenshot('{0}/Inventory_1.png'.format(self.log_path))
        if not self.ret:
            print '\n Inventory not completed successfully \n'
            return False

        time.sleep(2)
        print 'Inventory Completed successfully '
        logging.info("Inventory Completed successfully " )
        # Click on Next button after inventory  completes
        monkey_click_by_id( driver, "step0Next" )
        time.sleep(2)

        # Wait until Review completes and take screen-shots
        time.sleep(5)
        self.total = str(driver.find_elements_by_xpath(".//*[@id='selected-component-number-N1localhost']")[0].text)
        logging.info("Selected review components are  " +  str(self.total))
        driver.save_screenshot('{0}/Review.png'.format(self.log_path))
        count = len(driver.find_elements_by_xpath("//*[@id='hpsum-otu-installables-N1localhost-table']/tbody/tr"))
        print 'Total review elements are  ',  count
        logging.info("Total review components are  " +  str(count))
        menu = driver.find_element_by_xpath("//*[@id='step1commands']")
        hover = ActionChains(driver).move_to_element(menu);hover.perform()
        for i in range(1, count):
            try:
                 element = "//*[@id='hpsum-otu-installables-N1localhost-table']/tbody/tr[{0}]/td[2]".format(i)
                 menu = driver.find_element_by_xpath(element)
                 hover = ActionChains(driver).move_to_element(menu)
            except:
                 pass
            if i == 3 :
                hover.perform();time.sleep(3)
                driver.save_screenshot('{0}/Review_1.png'.format(self.log_path))
                menu = driver.find_element_by_xpath("//*[@id='hpsum-step3']")
                hover = ActionChains(driver).move_to_element(menu);hover.perform()
            if i == 10 :
                hover.perform();time.sleep(3)
                driver.save_screenshot('{0}/Review_2.png'.format(self.log_path))
                menu = driver.find_element_by_xpath("//*[@id='hpsum-step3']")
                hover = ActionChains(driver).move_to_element(menu);hover.perform()
            if i == 17 :
                hover.perform();time.sleep(3)
                driver.save_screenshot('{0}/Review_3.png'.format(self.log_path))
                menu = driver.find_element_by_xpath("//*[@id='hpsum-step3']")
                hover = ActionChains(driver).move_to_element(menu);hover.perform()
            if i == 25 :
                hover.perform();time.sleep(3)
                driver.save_screenshot('{0}/Review_4.png'.format(self.log_path))
                menu = driver.find_element_by_xpath("//*[@id='hpsum-step3']")
                hover = ActionChains(driver).move_to_element(menu);hover.perform()
        menu = driver.find_element_by_xpath("//*[@id='step1commands']");time.sleep(3)
        hover = ActionChains(driver).move_to_element(menu);hover.perform()
        driver.save_screenshot('{0}/Review_5.png'.format(self.log_path))
        if self.total == '0':
            print "  No Components To Install in review page"
            logging.error("No Components To Install in review page ")
            return False

        # Click on Deploy button after Review completes
        try:
            monkey_click_by_id( driver, "step1Next" )
            print "Review completed successfully  "
            logging.info("Review completed successfully  ")
        except:
            logging.error("Problem on clicking Deploy button ")
        time.sleep(15)

        # Wait until Deployment completes
        driver.save_screenshot('{0}/Deployment.png'.format(self.log_path))
        self.ret = wait_until_deployment_completes( driver , 400 )
        print ' Deploy ret is :',self.ret
        logging.error("Deploy ret is ::  " + str(self.ret))
        time.sleep(10)
        menu = driver.find_element_by_xpath("//*[@id='step2commands']")
        hover = ActionChains(driver).move_to_element(menu);hover.perform()
        driver.save_screenshot('{0}/Deployment_1.png'.format(self.log_path))

        if not self.ret:
            print ' Deployment not completed successfully '
            logging.error("Problem on complete Deployment successfully ")
            return False
        print 'Deployment Completed successfully '
        logging.info("Deployment Completed successfully ")
        time.sleep(3600)
        logging.info("Completed test case execution successfully ")


if __name__ == "__main__":
    unittest.main()
