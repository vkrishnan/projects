# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.action_chains import ActionChains
import unittest
import sys
import time
import os
import subprocess
import logging
import glob
import win32gui

logger = logging.getLogger('Create_spp_image')
fh = logging.FileHandler('C:\\dev\\spp\\tests\\spp\\testsuite\\create_spp_image.log',mode='w')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter);logger.addHandler(fh)
logger.setLevel(logging.DEBUG)

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

def monkey_type_by_xpath( driver, theid, text ):
    time.sleep(2)
    driver.find_element_by_xpath(theid).send_keys(text)

# Wait until complete inventory
def wait_until_inventory_completes( driver , timeout):
    for i in range(timeout):
        time.sleep(20)
        try:
            ele = driver.find_elements_by_xpath(".//*[@id='hpsum-otu-inventory-node']/tbody/tr/td[3]")[0]
            logger.info("Inventory status is : " + ele.text )
        except IndexError:
            print " \n Inventory not started \n "
            logger.error("Inventory not started " )
            return False

        if 'failed' in str(ele.text):
            Text = driver.find_elements_by_xpath(".//*[@id='hpsum-otu-install-progress']/tbody/tr/td[5]")[0]
            logger.error("Deployment error was ::  " + Text.text)
            return False
        if 'Inventory completed' not in str(ele.text):
            continue
        else:
            return True
    logger.error("Problem on Complete Inventory ")
    return False



def create_spp_image(source_location, output_location, username, password):
    logger.info("Test case Started ")
    fp = webdriver.FirefoxProfile()
    fp.set_preference("network.proxy.type", 0 )
    driver = webdriver.Firefox()
    driver.implicitly_wait(60)
    base_url = "http://localhost:63001/index.html"
    verificationErrors = []
    accept_next_alert = True
    ret = False
    total = 0

    ##  OPEN MAIN PAGE
    driver.get(base_url)
    time.sleep(10)
    driver.maximize_window()
    for i in range(0,120):
        title = driver.title
        logging.info("Title is    " +  str(title))
        if 'Smart Update Manager' in title: break
        driver.refresh()
        time.sleep(5)

    logger.info("Opened HP Smart Update Manager Page")
    # Enter Username
    monkey_type_by_id( driver, "hp-login-user",username )

    # Enter Password
    monkey_type_by_id( driver, "hp-login-password",password )

    # Click on Login button
    monkey_click_by_id( driver, "hp-login-button" )
    time.sleep(10)

    # Clic on hpsum-menu-guide-close
    try:
        monkey_click_by_id( driver, "hpsum-menu-guide-close" )
        time.sleep(2)
    except:
        pass

    # Click on HP Smart Update Manager dropdown
    try:
        monkey_click_by_xpath( driver, ".//*[@id='hp-main-menu-control']/div[3]")
    except:
        pass
    time.sleep(2)

    # Click on Local host Guided Update
    try:
        monkey_click_by_xpath( driver, ".//*[@id='hp-main-menu']/ul/li[2]/ul/li[1]/a")
    except:
        monkey_click_by_xpath( driver, ".//*[@id='hp-main-menu-control']/div[3]")
        monkey_click_by_xpath( driver, ".//*[@id='hp-main-menu']/ul/li[2]/ul/li[1]/a")
    time.sleep(2)

    # Click "Interactive Mode" radio button
    try:
         monkey_click_by_id( driver, "interactive-mode" )
    except:
        logger.error("Problem on Clicking Interactive Mode  ")
        raise AssertionError("Problem on Clicking Interactive Mode ")
    time.sleep(2)

    # Click "OK" button
    try:
        monkey_click_by_id( driver, "hpsum-action-ok-button" )
    except:
        logger.error("Problem on Clicking OK button  ")

    # Wait until inventory completes
    ret = wait_until_inventory_completes( driver , 400)
    time.sleep(5)

    if not ret:
        print '\n Inventory not completed successfully \n'
        logger.error("Problem on complete Inventory successfully ")
        driver.close()
        return   False

    time.sleep(10)

    # Click on Next button after inventory  completes
    try:
        monkey_click_by_id( driver, "step0Next" )
    except:
        logger.error("Problem on clicking next button ")
    time.sleep(15)

    # Click on HP Smart Update Manager drop down
    monkey_click_by_xpath( driver, "//*[@id='hp-main-menu-control']/div[3]" )
    logger.info("Clicked on HP Smart Update Manager drop down ")
    time.sleep(3)

    # Click on Baseline Library
    monkey_click_by_xpath( driver, "//*[@id='hp-main-menu']/ul/li[2]/ul/li[3]/a" )
    logger.info("Clicked on Baseline Library ")
    time.sleep(3)

    # Click on Actions dropdown
    monkey_click_by_xpath( driver, "//*[@id='hpsum-baselines-actions']/label" )
    time.sleep(3)
    logger.info("Clicked on Actions dropdown ")

    # Click on Create custom
    monkey_click_by_xpath( driver, "//*[@id='hpsum-baselines-actions']/ol/li[2]/a" )
    logger.info("Clicked on Create custom ")
    time.sleep(10)

    # Enter Description on Description box
    monkey_type_by_xpath( driver, "//*[@id='hpsum-custom-baselines-descr']", 'updated_spp_build')
    logger.info("Entered Description ")
    time.sleep(3)

    # Enter Version on version box
    try:
        driver.find_element_by_xpath("//*[@id='hpsum-custom-baselines-version2']").clear()
        time.sleep(3)
        monkey_type_by_xpath( driver, "//*[@id='hpsum-custom-baselines-version2']", '1A' )
        logger.info("Entered version ")
        time.sleep(2)
    except:
        pass

    # Enter output location path
    driver.find_element_by_xpath("//*[@id='hpsum-custom-baselines-targetloc-hpsumBrowse-input-text']").clear()
    time.sleep(3)
    monkey_type_by_xpath( driver, "//*[@id='hpsum-custom-baselines-targetloc-hpsumBrowse-input-text']", output_location)
    logger.info("Entered output location path ")
    time.sleep(5)

    # Click on make bootable iso file check box
    monkey_click_by_xpath( driver, "//*[@id='chkbox-bootableiso']")
    time.sleep(5)
    logger.info("Clicked on make bootable iso file check box ")

    # Enter HPSUM source location path
    driver.find_element_by_xpath(".//*[@id='hpsum-custom-baselines-isoloc-hpsumBrowse-input-text']").clear()
    time.sleep(10)
    monkey_type_by_xpath( driver, ".//*[@id='hpsum-custom-baselines-isoloc-hpsumBrowse-input-text']", source_location)
    logger.info("Entered source location path ")
    time.sleep(50)

    # Click on applay filter button
    for i in range(60):
        time.sleep(30)
        create_status = driver.find_element_by_xpath(".//*[@id='hp-form-message']/div[1]/span").text
        if 'Retrieving components' in create_status: break
        if not create_status:
             monkey_click_by_xpath( driver, "//*[@id='hpsum-cbl-add-baseline-button']")
             logger.info("Clicked on applay filter button in loop ")

    # Click on Create ISO and save Baseline button
    for i in range(60):
        time.sleep(60)
        create_status = driver.find_element_by_xpath(".//*[@id='hp-form-message']/div[1]/span").text
        logger.info("Applying Filter Status : " + create_status )
        if 'Completed retrieving components' in create_status: break
    monkey_click_by_xpath( driver, "//*[@id='hpsum-custom-baselines-create']")

    #  Get iso image creation status
    for i in range(50):
        time.sleep(100)
        create_status = driver.find_element_by_xpath(".//*[@id='hp-form-message']/div[1]/span").text
        logger.info("Create ISO image status : " + create_status )
        if 'Baseline has been saved successfully' in create_status:
            driver.close(); return   True
        if not create_status:
            driver.close(); return   False
        if 'Failed' in create_status:
            driver.close(); return   False
    driver.close()
    return   False

