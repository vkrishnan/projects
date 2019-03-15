import sys
import time
import logging
from selenium.common.exceptions import *
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

timeout = 180

#Reference variables that will be updated from SeleniumApi.py file when object
#is created for SPPGuidedInstallation class
logger = None
SppAssertionError = None
launch_browser_and_open_URL = None
set_chrome_profile = None
set_firefox_profile = None
confirm_page_load = None
monkeysleep = None
monkey_type_by_id = None
monkey_click_by_id = None
monkey_click_by_xpath = None

def set_local_logger():
    """
    Create a logger for logging purpose and return the reference
    """
    logger = logging.getLogger('GuidedApi')
    fh = logging.FileHandler('GuidedApi.log')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

class SPPGuidedInstallation(object):

    """
    Class contains functions for guided installation that is used by SPP automation via Selenium.
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, hpsum_version, function_references = None):
        """
        SeleniumApi constructor
        """

        global logger,SppAssertionError,launch_browser_and_open_URL,set_chrome_profile,set_firefox_profile
        global confirm_page_load,monkeysleep,monkey_type_by_id,monkey_click_by_id,monkey_click_by_xpath

        self.driver = None
        self.xpath = None
        self.hpsum_version = None
        self.HPSUM_page_name = None
        self.run_count = 0  #Indicates no of times guided installation is run
        self.deploy_count = 0  #Used for deployment count
        self.no_installable_components = False
        #Components to be selected by default for installation -- Value 0 is for unchecked: 1 or more is for checked
        self.default_components = {
                                    "SNMP Agents":0,
                                    "smh-templates":0,
                                    "Insight Management Agents":0,
                                    "WBEM":0,
                                  }
        self.wait = None
        self.wait_for_min = None

        if function_references:
            logger = function_references['logger']
            SppAssertionError = function_references['SppAssertionError']
            launch_browser_and_open_URL = function_references['launch_browser_and_open_URL']
            set_chrome_profile = function_references['set_chrome_profile']
            set_firefox_profile = function_references['set_firefox_profile']
            confirm_page_load = function_references['confirm_page_load']
            monkeysleep = function_references['monkeysleep']
            monkey_type_by_id = function_references['monkey_type_by_id']
            monkey_click_by_id = function_references['monkey_click_by_id']
            monkey_click_by_xpath = function_references['monkey_click_by_xpath']
        else:
            # This is done just in case if this file is run directly witout importing,
            # so initialize required variables
            import SeleniumApi
            logger = SeleniumApi.logger
            SppAssertionError = SeleniumApi.SppAssertionError
            launch_browser_and_open_URL = SeleniumApi.launch_browser_and_open_URL
            set_chrome_profile = SeleniumApi.set_chrome_profile
            set_firefox_profile = SeleniumApi.set_firefox_profile
            confirm_page_load = SeleniumApi.confirm_page_load
            monkeysleep = SeleniumApi.monkeysleep
            monkey_type_by_id = SeleniumApi.monkey_type_by_id
            monkey_click_by_id = SeleniumApi.monkey_click_by_id
            monkey_click_by_xpath = SeleniumApi.monkey_click_by_xpath

        #Import HPSUM specific xpaths
        if '7' == hpsum_version:
            from SppLibrary.config import HPSUM_7_xpath as xpath7
            self.xpath = xpath7
            self.hpsum_version = 7
            self.HPSUM_page_name = "HP Smart Update Manager"
        elif '8' == hpsum_version:
            from SppLibrary.config import HPSUM_8_xpath as xpath8
            self.xpath = xpath8
            self.hpsum_version = 8
            self.HPSUM_page_name = "Smart Update Manager"
        else:
            raise SppAssertionError("Recieved hpsum version %s. Unable to find xpaths for this version"%(hpsum_version))

    def _login(self, user, password, lpath, run_count, url):
        """
        Launch HPSUM page and login
        """
        #sets browser profile to chrome
        self.driver = set_chrome_profile()
        self.driver.implicitly_wait(5)
        self.wait = WebDriverWait(self.driver, 300)
        self.wait_for_min = WebDriverWait(self.driver, 60)
        driver = self.driver
        self.run_count += 1
        self.deploy_count = 0
        self.no_installable_components = False
        self.user = user
        self.password = password
        self.home_page = url
        self.lpath = lpath

        launch_browser_and_open_URL(driver, url, self.HPSUM_page_name, lpath )
        logger.info("Login in progress")
        # Enter Username
        monkey_type_by_id( driver, "hp-login-user",user )
        # Enter Password
        monkey_type_by_id( driver, "hp-login-password",password )
        # Click on Login button
        monkey_click_by_id( driver, "hp-login-button" )

        monkeysleep(2)
        try:
            element = self.wait.until(
                          lambda driver: driver.find_element_by_id("hp-session-control")
                        )
        except:
            raise SppAssertionError("Timed Out. Login error ",
                                    "LoginError", lpath, driver)
        logger.info('Logged In')
        monkeysleep(10)
        logger.info('Title is : %s' %(driver.title))
        return True

    def _click_localhost_guided_update(self, run_count):
        """
        Clicks on localhost huided update button and verify that page is loaded
        """
        driver = self.driver
        logger.info('Selecting Localhost Guided Update')
        try:
            monkey_click_by_xpath( driver, self.xpath.LOCALHOST_GUIDED_BUTTON)
            logger.info('Localhost guided update selected')
        except:
            logger.debug(sys.exc_info())
            raise SppAssertionError("Problem on clicking Localhost Guided Update.",
                                    "%s_guided_local_host_unclickable"%(run_count), self.lpath
                                    ,driver)

        logger.info("Waiting for Interactive mode selection page...")
        try:
            element = self.wait.until(
                          lambda driver: driver.find_element_by_id("hpsum-action-ok-button")
                        )
        except:
            logger.debug(sys.exc_info())
            raise SppAssertionError("Timed Out. Unable to find Interactive mode selection page.",
                                    "InteractiveModeSelectionPageError", self.lpath, driver)

        monkeysleep(60)
        return True

    def _click_interactive_mode(self, run_count):
        """
        Check interactive mode radio button for guided update
        """
        driver = self.driver
        # Click "Interactive Mode" radio button
        try:
            element = self.wait.until(
                          lambda driver: driver.find_element_by_id("interactive-mode")
                        )
            monkeysleep(2)
            logger.info("Selecting interactive mode")
            monkey_click_by_id( driver, "interactive-mode" )
        except:
            logger.debug(sys.exc_info())
            raise SppAssertionError("Unable to select interactive mode." ,
                                    "InteractiveModeRadioButtonUnclickable", self.lpath
                                    ,driver)

        monkeysleep(5)
        # Click "OK" button
        logger.info("Clicking interactive OK button")
        try:
            monkey_click_by_id( driver, "hpsum-action-ok-button" )
        except:
            logger.debug(sys.exc_info())
            raise SppAssertionError("Problem on clicking inetractive OK button." ,
                                    "%s_interactive_mode_OK_unclickable"%(run_count), self.lpath
                                    ,driver)
        logger.info("Interactive OK button clicked")
        return True

    def _check_inventory_status(self, run_count):
        """
        Verify inventory page for baseline and node inventory process
        """
        driver = self.driver
        # Conforming inventory page loaded. Look for localhost in the review page
        logger.info("Checking if node is localhost")
        try:
            element = self.wait.until(
                            lambda driver: driver.find_element_by_xpath(self.xpath.LOCALHOST_AS_NODE_NAME_INVENTORY_TEXT)
                        )
        except:
            logger.debug(sys.exc_info())
            raise SppAssertionError('Error In Reading Inventory Page Data.' ,
                                    "%s_inventory_page_load_error"%(run_count), self.lpath
                                    ,driver)
        logger.info("Node is localhost")

        # Take Screenshot of inventory page before Inventory Start
        driver.save_screenshot('%s\\ScreenShots\\%s_Guided_Inventory_info_1.png'%(self.lpath,run_count))

        monkeysleep(2)
        logger.info("Waitiing for baseline inventory to start...")
        try:
            element = self.wait.until(
                            lambda driver: driver.find_element_by_xpath(self.xpath.BASELINE_INVENTORY_TEXT)
                        )
        except:
            logger.debug(sys.exc_info())
            raise SppAssertionError('Baseline Inventory not started. Timed out' ,
                                    "%s_baseline_inventory_not_started_error"%(run_count), self.lpath
                                    ,driver)

        monkeysleep(2)
        logger.info("Baseline inventory in progress")
        # Reads the baseline inventory status and notify its status
        for i in xrange(timeout+1):
            monkeysleep(10)
            try:
                ele = driver.find_elements_by_xpath(self.xpath.BASELINE_INVENTORY_TEXT)[0]
                logger.info("Baseline Inventory status is : " + ele.text )
            except IndexError:
                logger.debug(sys.exc_info())
                raise SppAssertionError("Baseline Inventory info not available" ,
                                    "%s_baseline_inventory_info_not_available_error"%(run_count), self.lpath
                                    ,driver)

            if ('fail' in ele.text.lower()) or ('error' in ele.text.lower()):
                logger.debug(ele.text.lower())
                Text = driver.find_elements_by_xpath(self.xpath.BASELINE_INVENTORY_RESULT)[0]
                raise SppAssertionError("Baseline Inventory error is: " + Text.text ,
                                    "%s_Guided_Inventory_failed_1"%(run_count), self.lpath
                                    ,driver)
            elif i >= (timeout - 1):
                raise SppAssertionError("Problem in Baseline inventory",
                                    "%s_guided_inventory_timeout"%(run_count), self.lpath
                                    ,driver)
            elif ('Inventory completed' in str(ele.text)) or ('Baseline successfully added' in str(ele.text)):
                Text = driver.find_elements_by_xpath(self.xpath.BASELINE_INVENTORY_RESULT)[0]
                logger.info("Baseline Inventory status: %s"%(Text.text))
                break
            else:
                continue

        logger.info("Node inventory in progress")
        # Reads the node inventory status and notify its status
        for i in xrange(timeout+1):
            monkeysleep(10)
            try:
                ele = driver.find_elements_by_xpath(self.xpath.NODE_INVENTORY_TEXT)[0]
                logger.info("Node inventory status is : " + ele.text )
            except IndexError:
                logger.debug(sys.exc_info())
                raise SppAssertionError("Node inventory not started",
                                    "%s_node_inventory_not started"%(run_count), self.lpath
                                    ,driver)

            if ('fail' in ele.text.lower()) or ('error' in ele.text.lower()):
                logger.debug(ele.text.lower())
                Text = driver.find_elements_by_xpath(self.xpath.NODE_INVENTORY_RESULT)[0]
                raise SppAssertionError("Node inventory error was :: " + Text.text,
                                    "%s_node_inventory_failed"%(run_count), self.lpath
                                    ,driver)
            elif i >= (timeout - 1):
                raise SppAssertionError("Problem on Node Complete Inventory. Timed out",
                                    "%s_node_inventory_completion_failed"%(run_count), self.lpath
                                    ,driver)
            elif ('Inventory completed' in str(ele.text)) or ('Baseline successfully added' in str(ele.text)):
                Text1 = driver.find_elements_by_xpath(self.xpath.NODE_INVENTORY_RESULT)[0].text
                logger.info("Node inventory status: %s"%(Text1))
                break
            else:
                continue
        return True

    '''
    Created on 15 Nov, 2016
    @author: Abhishek
    '''
    def start_interactive_installation(self,user,password, lpath, run_count, url):
        """
        Start Localhost Guided Update , then select interactive installation mode
        """

        logger.info("Starting interactive guided installation")
        #login
        self._login(user, password, lpath, run_count, url)
        #click guided update
        self._click_localhost_guided_update(run_count)
        #click interactive mode
        self._click_interactive_mode(run_count)
        #verify inventory status
        self._check_inventory_status(run_count)
        return True

    '''
    Created on 15 Nov, 2016
    @author: Abhishek
    '''
    def verify_review_page_and_deploy(self,lpath,run_count):
        """ Verify the Review page, select all the
            required Component and take screenshot"""
        driver = self.driver
        menu = driver.find_element_by_xpath(self.xpath.INVENTORY_NEXT_BUTTON)
        hover = ActionChains(driver).move_to_element(menu)
        hover.perform();monkeysleep(5)
        driver.save_screenshot('%s\\ScreenShots\\%s_Guided_Inventory_info_2.png'%(lpath,run_count))
        try:
            monkey_click_by_id(driver,"step0Next")
            logger.info("Next button in inventory page clicked.")
        except:
            logger.debug(sys.exc_info())
            raise SppAssertionError("Error in clicking Next button. Unable to move forward to component selection page",
                                    "%s_NextButtonUnclickable"%(run_count), lpath
                                    ,driver)

        # Wait until Review completes
        monkeysleep(25)

        driver.save_screenshot('%s\\ScreenShots\\%s_Guided_Review_info.png'%(lpath,run_count))
        # Count the no of elements avalable in the table
        count = int(driver.find_element_by_xpath(self.xpath.TOTAL_AVAILABLE_COMPONENTS_TEXT).text)
        if count == 0:
            raise SppAssertionError("No components available in page for selection.",
                                    "%s_NoComponentsAvailableForSelection"%(run_count), lpath
                                    ,driver)
        logger.info("Selecting optional components if not selected already")

        #Find selected components
        components_selected = driver.find_elements_by_xpath(self.xpath.COMPONENTS_SELECTED)
        components_selected_text = []
        for component in components_selected:
            components_selected_text.append(component.text)
            for key in self.default_components.keys():
                if key in component.text:
                    self.default_components[key] += 1

        components_available = driver.find_elements_by_xpath(self.xpath.COMPONENT_TABLE)
        #Select optional components SNMP Agents, smh-templates for linux and WBEM, Insight Management Agents for windows if not selected
        for component in components_available:
            for key in self.default_components.keys():
                if (key in component.text) and (not self.default_components[key] ):
                    component.click()
                    self.default_components[key] += 1

        monkeysleep(3)

        logger.info("Capturing screenshots for available components")
        # Take Screenshot of review page
        scount = 0
        for i in range(1, count+1):
            element = self.xpath.COMPONENT_TEXT.format(i)
            menu = driver.find_element_by_xpath(element)
            hover = ActionChains(driver).move_to_element(menu)
            # Take the ScreenShot at proper interval
            if i == 3 or i == 8 or i == 13 or i == 18 or i == 23:
                scount += 1
                hover.perform();monkeysleep(3)
                driver.save_screenshot('%s\\ScreenShots\\%s_Guided_Review_info_%s.png'%(lpath,run_count,scount))

        menu = driver.find_element_by_xpath(self.xpath.COMPONENTS_PAGE_COMMANDS);monkeysleep(3)
        hover = ActionChains(driver).move_to_element(menu);hover.perform()
        driver.save_screenshot('%s\\ScreenShots\\%s_Guided_Review_info_%s.png'%(lpath,run_count,scount+1))
        # if total component to install is 0 then give error message 'No Components To Install'
        total = str(driver.find_elements_by_xpath(self.xpath.TOTAL_SELECTED_COMPONENTS_TEXT)[0].text)
        if total == '0':
            if 1 == self.run_count:
                raise SppAssertionError('No Components To Install',
                                    "%s_NoComponentsAvailableForInstall"%(run_count), lpath
                                    ,driver)
            else:
                #Bypass deploy as no components available for install
                logger.warn('No components to install')
                self.no_installable_components = True
                return True

        monkeysleep(10)

        logger.info("Review completed successfully. Deploying now.")
        status = self.deploy_and_take_screenshot(lpath, run_count)
        return status

    '''
    Created on 15 Nov, 2016
    @author: Abhishek
    '''
    def remove_dependency_components(self,cp_ids):
        """ This Function Will take the cp_id and
        uncheck the component to stop it from being deployed"""
        driver = self.driver
        #Find selected components
        for cp_id_exe in cp_ids:
            components_selected = driver.find_elements_by_xpath(self.xpath.COMPONENTS_SELECTED)
            cp_id = cp_id_exe.strip('.exe')
            logger.warning("Unchecking %s due to dependency in components"%(cp_id))
            for component in components_selected:
                if cp_id in component.text:
                    component.click()

        monkeysleep(10)
        return True

    def _click_deploy_button(self,lpath,run_count):
        """
        Clicks deploy button
        """
        driver = self.driver
        try:
            menu = driver.find_element_by_id("step1Next")
            hover = ActionChains(driver).move_to_element(menu);hover.perform()
            monkey_click_by_id( driver, "step1Next" )
            logger.info("Deploy button clicked...")
        except:
            logger.debug(sys.exc_info())
            menu = driver.find_element_by_id("step1Next")
            hover = ActionChains(driver).move_to_element(menu);hover.perform()
            dependency_elements = driver.find_elements_by_class_name("hp-status-error")
            if dependency_elements:
                logger.info("There are still  dependency components")
            raise SppAssertionError("Unable to click deploy button and move to deploy page",
                                    "DeployError", lpath, driver)
        return True

    '''
    Created on 15 Nov, 2016
    @author: Abhishek
    '''
    def deploy_and_take_screenshot(self,lpath,run_count):
        """
        This function checks for dependency components, unselects components 
        from installation if any and continue deploying
        """
        driver = self.driver
        status = None
        self.deploy_count += 1

        # if total component to install is 0 then give error message 'No Components To Install'
        total = str(driver.find_elements_by_xpath(self.xpath.TOTAL_SELECTED_COMPONENTS_TEXT)[0].text)
        if total == '0':
            if 1 == self.run_count:
                raise SppAssertionError('No Components To Install',
                                    "%s_NoComponentsAvailableForInstall"%(run_count), lpath
                                    ,driver)
            else:
                self.no_installable_components = True
                logger.info("No installable components")
                return True

        #Find if there are any dependency components and uncheck those components
        dependency_elements = driver.find_elements_by_class_name("hp-status-error")
        if dependency_elements:
            logger.info("Unchecking dependency components")
            for dep_elem in dependency_elements:
                #Find parent element i.e row of current dependency element and click
                dep_elem.find_element_by_xpath("./../../..").click()
            logger.info("Done unchecking")


        self._click_deploy_button(lpath,run_count)
        monkeysleep(10)

        #Check if deploy page is loaded, if not there will be dependent components try 
        #unchecking dependency components and click deploy button
        try:
            logger.info("Checking if deploy page is loaded")
            element = self.wait_for_min.until(
                          lambda driver: driver.find_element_by_xpath(self.xpath.DEPLOYMENT_PAGE_REBOOT)
                        )
        except:
            logger.info("In review page.")
            dependency_elements = driver.find_elements_by_class_name("hp-status-error")
            if dependency_elements:
                logger.info("Unchecking dependency components again")
                for dep_elem in dependency_elements:
                    #Find parent element i.e row of current dependency element and click
                    dep_elem.find_element_by_xpath("./../../..").click()
                logger.info("Done unchecking")
            self._click_deploy_button(lpath,run_count)

        monkeysleep(10)

        #Now check if deploy page is loaded
        try:
            element = self.wait_for_min.until(
                          lambda driver: driver.find_element_by_xpath(self.xpath.DEPLOYMENT_PAGE_REBOOT)
                        )
        except:
            logger.debug(sys.exc_info())
            menu = driver.find_element_by_id("step1Next")
            hover = ActionChains(driver).move_to_element(menu);hover.perform()
            raise SppAssertionError("Unable to move to deploy page",
                                    "DeployError", lpath, driver)
        #Check if the name of node being deployed is localhost
        driver.save_screenshot('%s\\ScreenShots\\%s_Guided_Deployment_info.png'%(lpath,run_count))
        ele = driver.find_element_by_xpath(self.xpath.LOCALHOST_AS_NODE_NAME_DEPLOY_TEXT).text
        if 'localhost' not in ele:
            raise SppAssertionError ('Node not localhost',
                                    "%s_NodeNotLocalhostError"%(run_count), lpath
                                    ,driver)
        scount = 0
        for i in xrange((timeout*2)+1):
            monkeysleep(10)
            try:
                ele = driver.find_elements_by_xpath(self.xpath.DEPLOYMENT_STATUS_TEXT)[0]
                logger.info("Deployment status is : " + ele.text )
            except IndexError:
                logger.debug(sys.exc_info())
                raise SppAssertionError("Deployment not started ",
                                    "%s_deployment_not_started"%(run_count), lpath
                                    ,driver)

            if 'Deployment error' in str(ele.text) or 'failed' in str(ele.text) or  "Install done with error(s)" in str(ele.text):
                logger.warn("Error in deploying components in %s"%(run_count))
                scount += 1
                Text = driver.find_elements_by_xpath(self.xpath.DEPLOYMENT_RESULT_TEXT)[0]
                menu = driver.find_element_by_xpath(self.xpath.DEPLOYMENT_RESULT_TEXT)
                hover = ActionChains(driver).move_to_element(menu);hover.perform()
                driver.save_screenshot('%s\\Failure_ScreenShots\\%s_DeploymentError1.png'%(lpath,run_count))
                menu = driver.find_element_by_xpath(self.xpath.DEPLOYMENT_PAGE_REBOOT)
                hover = ActionChains(driver).move_to_element(menu);hover.perform()
                driver.save_screenshot('%s\\Failure_ScreenShots\\%s_DeploymentError2.png'%(lpath,run_count))
                break
            elif i >= (timeout - 1):
                raise SppAssertionError("Timeout occured for finishing deployment",
                                    "%s_deployment_timeout"%(run_count), lpath
                                    ,driver)
            elif "Deployment completed" in str(ele.text):
                break
            else:
                continue

        monkeysleep(1)
        driver.save_screenshot('%s\\ScreenShots\\%s_Guided_Deployed_info.png'%(lpath,run_count))
        # Count the no of elements avalable in the table
        count = len(driver.find_elements_by_xpath(self.xpath.DEPLOYED_COMPONENTS))
        scount = 0
        for i in range(1, count+1):
            element = self.xpath.DEPLOYED_COMPONENT_NAME_TEXT.format(i)
            menu = driver.find_element_by_xpath(element)
            hover = ActionChains(driver).move_to_element(menu)
            if i == 3 or i == 8 or i == 13 or i == 18 or i == 23:
                scount += 1
                hover.perform();monkeysleep(2)
                driver.save_screenshot('%s\\ScreenShots\\%s_Guided_Deployment_info_%s.png'%(lpath,run_count,scount))

        menu = driver.find_element_by_xpath(self.xpath.DEPLOYMENT_PAGE_COMMANDS);
        hover = ActionChains(driver).move_to_element(menu);hover.perform()
        driver.save_screenshot('%s\\ScreenShots\\%s_Guided_Deployment_info_%s.png'%(lpath,run_count,scount+1))
        monkeysleep(3)

        return True

    '''
    Created on 15 Nov, 2016
    @author: Abhishek
    '''
    def reboot_system(self,run_count,lpath):
        driver = self.driver
        try:
            element = driver.find_element_by_xpath(self.xpath.DEPLOYMENT_PAGE_REBOOT)
            element.click()
            logger.info("Successfully clicked on Reboot button")
        except:
            logger.debug(sys.exc_info())
            if 'Second_Run' in run_count and self.no_installable_components:
                logger.info("Not rebooting system as no components available for installation in %s"%(run_count))
                return False
            else:
                raise SppAssertionError("Unable to click Reboot button",
                                    "%s_reboot_error"%(run_count), lpath
                                    ,driver)

        monkeysleep(5)

        try:
            #driver.find_element_by_xpath(self.xpath.DEPLOYMENT_PAGE_REBOOT_CONFIRM).click()
            menu = driver.find_element_by_xpath(self.xpath.DEPLOYMENT_PAGE_REBOOT_CONFIRM);
            hover = ActionChains(driver).move_to_element(menu).click(menu);hover.perform()
            logger.info("Successfully confirmed system reboot")
            monkeysleep(5)
        except:
            logger.debug(sys.exc_info())
            logger.info("Trying to click button with updated xpath")
            try:
                menu = driver.find_element_by_xpath(self.xpath.DEPLOYMENT_PAGE_REBOOT_CONFIRM_UPDATED);
                hover = ActionChains(driver).move_to_element(menu).click(menu);hover.perform()
                logger.info("Successfully confirmed system reboot")
                monkeysleep(5)
            except:
                logger.debug(sys.exc_info())
                raise SppAssertionError("Unable to click OK button to confirm reboot",
                                        "%s_reboot_error"%(run_count), lpath
                                        ,driver)

        return True

    def close_browser(self):
        driver = self.driver
        try:
            logger.info("Closing browser")
            driver.quit()
        except:
            logger.debug(sys.exc_info())
            logger.info("Unable to close browser.")

    '''
    Created on 15 Nov, 2016
    @author: Abhishek
    '''
    def close_firefox_browser(self):
        driver = self.driver
        try:
            logger.info("Closing browser")
            driver.quit()
        except:
            logger.debug(sys.exc_info())
            logger.debug("Unable to close browser.")
