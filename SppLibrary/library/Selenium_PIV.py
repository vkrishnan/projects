import sys
import time
import logging
from selenium.common.exceptions import *
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

timeout = 180

#Reference variables that will be updated from SeleniumApi.py file when object
#is created for SMH_PIV class
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
    logger = logging.getLogger('Selenium_PIV')
    fh = logging.FileHandler('PIV.log')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

'''
Created on 1 Feb, 2017
@author: Abhishek
'''
class SMH_PIV(object,):
    """
    Class contains functions for PIV that is used by SPP automation via Selenium.
    """
    def __init__(self,function_references = None):
        """
        Constructor for PIV class
        """
        global logger,SppAssertionError,launch_browser_and_open_URL,set_chrome_profile,set_firefox_profile
        global confirm_page_load,monkeysleep,monkey_type_by_id,monkey_click_by_id,monkey_click_by_xpath

        self.PIV_page_name = "HPE System Management Homepage"
        self.home_page_xpath = "//*[@id='menu']/ul/li[1]/a"
        self.wait = None
        self.driver = None
        self.lpath = None
        self.os_platform = None
        self.data_source = None
        self.available_components = [] #List holding all available components
        self.imag_component_no = 9 #Imaginary constant no for total no of tables
        self.final_status = True

        self.HEADER_FRAME = "CHPHeaderFrame"
        self.DATA_FRAME = "CHPDataFrame"

        self.component_info = {}
        self.has_smart_storage_component = None #Indicate for smart storage component presence

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

        logger.info("#####################################################")
        logger.info("#                SMH PIV                            #")
        logger.info("#####################################################")

    def start_piv_check(self, url, user, password, lpath, os_platform):
        """
        Function to check PIV
        """
        self.launch_PIV_page(url, user, password, lpath, os_platform)
        self.data_source = self.get_data_source()
        #Save homepage screenshot
        self._save_homepage_screens(self.data_source or "")
        data_source = self.data_source
        if not data_source:
            logger.debug("No data source")
            self._check_data_source("SNMP")
            data_source = self.get_data_source()

        self.align_window_by_name()
        logger.info("Current data source is:%s"%(data_source,))
        if os_platform == "linux":
            logger.info("Verifying linux PIV")
            self.get_available_components_info("SNMP")
        elif os_platform == "windows":
            logger.info("Verifying windows PIV for %s"%(data_source,))
            self.get_available_components_info(data_source)
            if data_source == "SNMP":
                logger.info("Switching data source to WBEM")
                self.switch_data_source("WBEM")
                logger.info("Verifying windows PIV for WBEM")
                self.get_available_components_info("WBEM")
            else:
                logger.info("Switching data source to SNMP")
                self.switch_data_source("SNMP")
                logger.info("Verifying windows PIV for SNMP")
                self.get_available_components_info("SNMP")

        #Check Webapp info
        driver = self.driver
        self._switch_frame(self.HEADER_FRAME)
        logger.info("Checking  webapp info")
        webapps_elem = driver.find_elements_by_link_text("Webapps")
        if not webapps_elem:
            raise SppAssertionError("Webapps link not available on page","WebAppLinkUnavailable",self.lpath,driver)

        webapps_elem[0].click()
        monkeysleep(2)
        driver.save_screenshot("%s\\ScreenShots\\Webapps.png"%(self.lpath))
        monkeysleep(2)
        logger.info("Clicking Insight diagnostics link")
        self._switch_frame(self.DATA_FRAME)
        try:
            monkey_click_by_xpath(driver,'//*[@id="form"]/fieldset/div/ul/li/a')
        except:
            raise SppAssertionError("Insight Diagnostics link not available in WebApp page",
                                    "InightDiagnosticsLinkMissing",self.lpath,driver)

        driver.switch_to_default_content()
        if len(driver.window_handles) == 1:
            raise SppAssertionError("Insight Diagnostics page not opened",
                                    "InightDiagnosticsLoadError",self.lpath,driver)
        #switch to Insight diag page
        driver.switch_to_window(driver.window_handles[1])
        self._get_webapp_information(driver)
        #switch to PIV page
        driver.switch_to_window(driver.window_handles[0])
        #Check smart storage administrator element
        self._check_smart_storage()
        self.wrap_up()
        if not self.final_status:
            raise SppAssertionError("PIV for gui validation failed")
        return self.final_status

    def _check_smart_storage(self,):
        """Check smart storage administrator element"""
        driver = self.driver
        if "linux" == self.os_platform:
            if self.has_smart_storage_component:
                logger.info("Restarting hpsmhd service")
                self._restart_hpsmhd_service()
                monkeysleep(10)
                logger.info("Opening SSA page...")
                self.get_smart_storage_info()
            else:
                logger.info("Smart storage administrator not found")
        return True

    def check_only_webapp(self, url, user, password, lpath, os_platform):
        """
        Incase of synergy this function will check for webapp alone
        """
        self.url = url
        self.user = user
        self.password = password
        self.lpath = lpath
        self.os_platform = os_platform
        self._get_webapp_information()
        if not self.final_status:
            raise SppAssertionError("PIV for webapp check validation failed")
        return self.final_status

    def launch_PIV_page(self, url, user, password, lpath, os_platform):
        """
        Launch PIV home page and login and take screen shots
        """
        self.driver = set_chrome_profile()
        self.driver.implicitly_wait(10)
        driver = self.driver
        self.wait = WebDriverWait(driver, 60)

        self.url = url
        self.user = user
        self.password = password
        self.lpath = lpath
        self.os_platform = str(os_platform)
        if "windows" == os_platform:
            self.table_xpaths = {
                                'SNMP':{'NIC':'','Storage':'','System Configuration':''},
                                'WBEM':{'Network':'','Storage':'','Software':''}
                                }
        elif "linux" == os_platform:
            self.table_xpaths = {
                                'SNMP':{'Storage':'','System':'','NIC':''},
                                }
        else:
            raise SppAssertionError("Unknown os platform other than 'linux'/'windows' received. os_platform:%s"%(os_platform,))

        logger.info("Openening browser and redirecting to PIV page ")
        launch_browser_and_open_URL(driver, url, self.PIV_page_name, lpath)
        self._login()

        self._switch_frame(self.DATA_FRAME)
        #Expand all component tables
        component_info_tab_expander = driver.find_elements_by_link_text("Show All")
        for showall in component_info_tab_expander:
            try:
                showall.click()
            except:
                logger.debug(sys.exc_info())
                logger.debug("error in clicking show all links")

        return True

    def get_data_source(self, ):
        """ Check the Data Source of the page whether SNMP or WBEM """

        logger.info("Reading data source...")
        driver = self.driver
        self._switch_frame(self.HEADER_FRAME)
        data_source_elem = driver.find_elements_by_xpath("/html/body/table/tbody/tr/td[6]/div/span/nobr")
        logger.debug("%s,%s,%s"%(data_source_elem,data_source_elem[0].text,type(data_source_elem[0].text)))
        if data_source_elem and data_source_elem[0].text in ("SNMP","WBEM"):
            logger.info("Data source is "+data_source_elem[0].text)
            return data_source_elem[0].text
        else:
            logger.warn("Data source is empty")
            return False

    def _check_data_source(self,data_source ):
        """ Check the data source of the page whether SNMP or WBEM """

        driver = self.driver
        self._switch_frame(self.HEADER_FRAME)
        data_source_elem = driver.find_elements_by_xpath("/html/body/table/tbody/tr/td[6]/div/span/nobr")

        logger.info("Checking for data source to be: "+data_source)
        if data_source_elem and data_source_elem[0].text in ("SNMP","WBEM"):
            if data_source_elem[0].text != data_source:
                logger.warn("Available data source:"+data_source_elem[0].text+". Expected:"+data_source)
                raise SppAssertionError("Expected data source unavailable","WrongDatasource",self.lpath,driver)
            else:
                logger.info("Data source is as expected: "+data_source)
        else:
            raise SppAssertionError("No data source available","DatasourceEmpty",self.lpath,driver)

        return True

    def switch_data_source(self, data_source):
        """ 
        Switches between available datasources: SNMP<->WEBM
        """
        if "linux" == self.os_platform:
            self._check_data_source("SNMP")
        elif "windows" == self.os_platform:
            logger.info("Switching data source to "+ data_source)
            driver = self.driver
            self._switch_frame(self.HEADER_FRAME)
            settings = driver.find_element_by_link_text("Settings")
            settings.click()
            monkeysleep(2)
            self._switch_frame(self.DATA_FRAME)

            #Click select link under SMH data source table
            if 'WBEM' == data_source:
                monkey_click_by_xpath(driver,"/html/body/table/tbody/tr/td/div[1]/div[1]/ul/li/div/a")
            else:
                monkey_click_by_xpath(driver,"/html/body/table/tbody/tr/td/div[2]/div[1]/ul/li/div/a")
            monkeysleep(2)

            logger.info("Selecting data source")
            #Select WEBM<->SNMP
            if 'SNMP' == data_source:
                monkey_click_by_xpath(driver, '//*[@id="t1"]/tbody/tr/td/form/input[11]')
            elif 'WBEM' == data_source:
                monkey_click_by_xpath(driver, '//*[@id="t1"]/tbody/tr/td/form/input[12]')
            else:
                logger.debug("Unknown data source to switch to. Received %s"%(data_source,))
                return
            monkeysleep(1)
            logger.info("Applying changes")
            #Click select button
            monkey_click_by_xpath(driver, '//*[@id="t1"]/tbody/tr/td/form/input[15]')
            logger.info("Waiting for data source changes to be applied")
            #Wait for a time to get data source changes applied
            monkeysleep(10)
            logger.info("Will signout and relogin")
            self._signout_and_login()
            monkeysleep(2)
            self._check_data_source(data_source)
            logger.info("Data source switching finished")
            #Save home page screen after switching
            self._save_homepage_screens(data_source)         

            return True

    def _save_homepage_screens(self,data_source):
        """ Saves homepage screen shots"""
        
        driver = self.driver
        #Expand all component tables
        component_info_tab_expander = driver.find_elements_by_link_text("Show All")
        for showall in component_info_tab_expander:
            try:
                showall.click()
            except:
                logger.debug(sys.exc_info())
                logger.debug("unable to click show all links")
        #Save homepage screenshot
        self._switch_frame(self.DATA_FRAME)
        top = driver.find_element_by_xpath('//*[@id="systemStatusSummary"]/h4');
        hover = ActionChains(driver).move_to_element(top);hover.perform()
        monkeysleep(2)
        driver.save_screenshot("%s\\ScreenShots\\%sHomePage1.png"%(self.lpath,data_source))
        monkeysleep(1)

        bottom = driver.find_elements_by_xpath('/html/body/table/tbody/tr/td/div[9]/div/center/center')
        if bottom:
            hover = ActionChains(driver).move_to_element(bottom[0]);hover.perform()
            monkeysleep(2)
            driver.save_screenshot("%s\\ScreenShots\\%sHomePage2.png"%(self.lpath,data_source))

        return True

    def get_available_components_info(self,data_source):
        """
        Get all available component information
        """
        driver = self.driver
        logger.info("Gathering all available components info")
        self._switch_frame(self.DATA_FRAME)
        self.first_table_xpath = "./html/body/table/tbody/tr/td/div[1]/div"
        self.rem_table_xpath = "./html/body/table/tbody/tr/td/div[%s]"

        first_table = driver.find_elements_by_xpath(self.first_table_xpath+"/h4")
        rem_table_components = driver.find_elements_by_xpath(self.rem_table_xpath%('*')+"/h4")

        if not first_table and not rem_table_components:
            raise SppAssertionError("No components available","NoComponents", self.lpath, driver)

        self.available_components = []
        self.available_components.append(first_table[0].text)
        self.available_components.extend([component.text for component in rem_table_components])

        tab_name = driver.find_elements_by_xpath(self.first_table_xpath+"/h4")
        if tab_name and tab_name[0].text in self.table_xpaths[data_source].keys():
            elem_name = tab_name[0].text
            logger.info("Found component:%s"%(elem_name,))
            self.table_xpaths[data_source][elem_name] = self.first_table_xpath
        for i in range(2,self.imag_component_no):
            tab_name = driver.find_elements_by_xpath(self.rem_table_xpath%(i)+"/h4")
            if tab_name and tab_name[0].text in self.table_xpaths[data_source].keys():
                elem_name = tab_name[0].text
                logger.info("Found component:%s"%(elem_name,))
                self.table_xpaths[data_source][elem_name] = self.rem_table_xpath%(i)

        logger.debug(repr(self.table_xpaths))

        for elem_name in self.table_xpaths[data_source].keys():
            if not self.table_xpaths[data_source][elem_name]:
                logger.warn("No %s related components in %s %s"%(elem_name, self.os_platform, data_source))
                continue

            try:
                if elem_name in ("NIC","Network"):
                    self._get_network_info(data_source, elem_name )
                elif elem_name in ('Storage',):
                    self._get_storage_info(data_source, elem_name )
                elif elem_name in ('System','System Configuration','Software'):
                    self._get_firmware_and_software_info(data_source, elem_name )
                else:
                    logger.info("Component %s has no related component tables"%(elem_name,))
            except:
                logger.error("Error while gathering %s info"%(elem_name))
                self.final_status = False
                logger.debug(sys.exc_info())
                logger.debug("Error while gathering %s"%(elem_name))

        return True

    def _get_storage_info(self, data_source,key_name):
        """
        Get the storage driver information
        """
        logger.info("Gathering storage components info for %s"%(data_source,))
        driver = self.driver
        self._switch_frame(self.DATA_FRAME)
        if not self.component_info.has_key('Storage'):
            if "windows" == self.os_platform:
                self.component_info['Storage'] = {"WBEM":[], "SNMP":[]}
            else:
                self.component_info['Storage'] = {"SNMP":[]}

        storage_components_xpath = "%s/div[1]/ul/li"%(self.table_xpaths[data_source][key_name])
        total_components = len(driver.find_elements_by_xpath(storage_components_xpath) )
        logger.debug("Total subcomponents:%d"%(total_components,) )

        storage_components_xpath += "[%s]/div/a"
        for count in range(1,total_components+1):
            self._switch_frame(self.DATA_FRAME)
            monkeysleep(2)
            elem = driver.find_element_by_xpath( storage_components_xpath%(count,) )
            elem_name = elem.text
            logger.debug("found %s"%(elem_name, ))
            if "WBEM" == data_source:
                self.component_info['Storage']["WBEM"].append(elem_name)
            else:
                self.component_info['Storage']["SNMP"].append(elem_name)
                if 'linux' == self.os_platform and "Smart Storage" in elem_name:
                    self.has_smart_storage_component = True
                    continue

            logger.info("clicking %s"%(elem_name, ))
            elem.click()
            monkeysleep(2)
            logger.debug("Saving screens")
            driver.save_screenshot("%s\\ScreenShots\\%s_%s_1.png"%(self.lpath, data_source, elem_name ))
            monkeysleep(2)
            self._go_to_home_page()
            monkeysleep(2)
        return True

    def _get_network_info(self, data_source,key_name):
        """
        Get NIC driver related information
        """
        logger.info("Gathering network components info for %s"%(data_source,))
        driver = self.driver
        self._switch_frame(self.DATA_FRAME)
        if not self.component_info.has_key('Network'):
            if "windows" == self.os_platform:
                self.component_info['Network'] = {"WBEM":[], "SNMP":[]}
            else:
                self.component_info['Network'] = {"SNMP":[]}

        network_components_xpath = "%s/div[1]/ul/li"%(self.table_xpaths[data_source][key_name])
        total_components = len(driver.find_elements_by_xpath(network_components_xpath) )
        logger.debug("Total subcomponents:%d"%(total_components,) )

        network_components_xpath += "[%s]/div/a"
        for cnt in range(1,total_components+1):
            self._switch_frame(self.DATA_FRAME)
            elem = driver.find_element_by_xpath( network_components_xpath%(cnt,) )
            elem_name = elem.text
            logger.debug("found %s"%(elem_name, ))

            if "WBEM" == data_source:
                self.component_info['Network']["WBEM"].append(elem_name)
            else:
                self.component_info['Network']["SNMP"].append(elem_name)

            if "Virtual" in elem.text:
                continue

            logger.info("clicking %s"%(elem_name, ))

            elem.click()
            monkeysleep(2)
            logger.debug("saving screens")
            driver.save_screenshot("%s\\ScreenShots\\%s_%s_1.png"%(self.lpath, data_source, elem_name ))
            #Scroll to bottom of page
            if "WBEM" == data_source:
                menu = driver.find_element_by_xpath("/html/body/table[2]/tbody/tr/td[2]")
            else:
                menu = driver.find_element_by_xpath("/html/body/font/a")

            hover = ActionChains(driver).move_to_element(menu);hover.perform()
            driver.save_screenshot("%s\\ScreenShots\\%s_%s_2.png"%(self.lpath, data_source, elem_name ))
            monkeysleep(2)
            self._go_to_home_page()
            monkeysleep(3)
        return True

    def _get_firmware_and_software_info(self, data_source,key_name):
        """
        Get firmware and software related information
        """
        logger.info("Gathering Firmware/Software components info for %s"%(data_source,))
        driver = self.driver
        self._switch_frame(self.DATA_FRAME)
        if not self.component_info.has_key('Firmware/Software'):
            if "windows" == self.os_platform:
                self.component_info['Firmware/Software'] = {"WBEM":[], "SNMP":[]}
            else:
                self.component_info['Firmware/Software'] = {"SNMP":[]}

        fs_components_xpath = "%s/div[1]/ul/li"%(self.table_xpaths[data_source][key_name])
        total_components = len(driver.find_elements_by_xpath(fs_components_xpath) )
        logger.debug("Total subcomponents:%d"%(total_components,) )

        fs_components_xpath += "[%s]/div/a"
        for cnt in range(1,total_components+1):
            self._switch_frame(self.DATA_FRAME)
            monkeysleep(2)
            elem = driver.find_element_by_xpath( fs_components_xpath%(cnt,) )
            elem_name = elem.text

            logger.debug("found element %s"%(elem_name))
            if "WBEM" == data_source:
                self.component_info['Firmware/Software']["WBEM"].append(elem_name)
            elif "SNMP" == data_source:
                if "Software" in elem_name and "Firmware":
                    self.component_info['Firmware/Software']["SNMP"].append(elem_name)
                else:
                    continue

            logger.info("clicking element %s"%(elem_name))
            elem.click()
            monkeysleep(2)
            logger.debug("saving screens")
            driver.save_screenshot("%s\\ScreenShots\\%s_%s_1.png"%(self.lpath, data_source, elem_name ))
            #Scroll to bottom of page
            if "WBEM" == data_source:
                for i in (2,3):
                    next = driver.find_elements_by_xpath("/html/body/table[2]/tbody/tr[2]/td/div/input")
                    if next:
                        try:
                            next[0].click()
                            driver.save_screenshot("%s\\ScreenShots\\%s_%s_%d.png"%(self.lpath, data_source, elem_name, i ))
                            monkeysleep(2)
                        except:
                            logger.info("No more info available for software")
                            self._go_to_home_page()
                            monkeysleep(2)
                            continue
            if "SNMP" == data_source:
                menu = driver.find_element_by_xpath("/html/body/font/a")
                hover = ActionChains(driver).move_to_element(menu);hover.perform()
                driver.save_screenshot("%s\\ScreenShots\\%s_%s_2.png"%(self.lpath, data_source, elem_name ))

            monkeysleep(2)
            self._go_to_home_page()
            monkeysleep(2)
        return True

    def align_window_by_name(self, ):
        """ Changes the ordering of data tables in homepage by name """

        logger.info("Alligning page by name")
        driver = self.driver
        self._switch_frame(self.HEADER_FRAME)
        driver.find_element_by_link_text("Settings").click()
        self._switch_frame(self.DATA_FRAME)
        logger.debug("Selecting User preferences")
        if "windows" == self.os_platform:
            monkey_click_by_xpath(driver,"/html/body/table/tbody/tr/td/div[3]/div[1]/ul/li[3]/div/a")
        else:
            monkey_click_by_xpath(driver,"/html/body/table/tbody/tr/td/div[2]/div[1]/ul/li[3]/div/a")

        logger.debug("Changing order by name")
        box_order = Select(driver.find_element_by_name("box_order"))
        box_order.select_by_visible_text("By name")

        item_order = Select(driver.find_element_by_name("box_item_order"))
        item_order.select_by_visible_text("By name")

        monkey_click_by_id(driver,"applyButton")
        logger.info("Done")
        self._go_to_home_page()
        return True

    def _switch_frame(self, frame):
        """
        Switches to the respective frame
        frame: Name of frame to switch to
        """

        driver = self.driver
        driver.switch_to_default_content()
        driver.switch_to_frame(frame)
        return True

    def _login(self,):
        """ Login to PIV page """

        driver = self.driver
        logger.info("Login in process...")
        # Enter Username
        monkey_type_by_id( driver, "user", self.user )
        # Enter Password
        monkey_type_by_id( driver, "password", self.password )
        # Click on Login button
        monkey_click_by_id( driver, "logonButton" )

        #Wait untill logged in - Checking for homepage frame loaded
        logger.info("Waiting for homepage to load")
        try:
            element = self.wait.until(
                        EC.presence_of_element_located( (By.XPATH, '/html/body/iframe') )
                        )
        except:
            raise SppAssertionError("Unable to login","LoginError", self.lpath,driver)

        logger.info("Logged in.")

        return True

    def _go_to_home_page(self,):
        """ Redirect to home page """

        driver = self.driver
        logger.debug("Returning to home page")
        self._switch_frame(self.HEADER_FRAME)
        driver.find_elements_by_link_text("Home")[0].click()       
        monkeysleep(2)
        #Expand all component tables
        logger.debug("Clicking all show all links")
        self._switch_frame(self.DATA_FRAME)

        for i in xrange(self.imag_component_no):
            try:
                show_all_list = driver.find_elements_by_link_text("Show All")
                if show_all_list:
                    hover = ActionChains(driver).move_to_element(show_all_list[0]);hover.perform()
                    show_all_list[0].click()
                    monkeysleep(1)
                else:
                    break
            except:
                logger.debug(sys.exc_info())
        logger.debug("Home page loaded.")

        return True

    def _signout_and_login(self,):
        """ signout and relogin """
        
        driver = self.driver
        self._switch_frame(self.HEADER_FRAME)
        signout = driver.find_elements_by_link_text("Sign Out")
        signout[0].click()
        driver.refresh()
        monkeysleep(10)
        self._login()
        self._go_to_home_page()
        return True

    def _restart_hpsmhd_service(self,):
        """ restarts hpsmhd service on linux system"""

        import paramiko

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            host = self.url.replace("https://","").replace(":2381","")
            logger.debug("restarting hpsmhd service for %s"%(host,))
            client.connect(host, username=self.user, password=self.password)
            stdin, stdout, stderr = client.exec_command('hpssa -start')
            monkeysleep(2)
            stdin, stdout, stderr = client.exec_command('service hpsmhd restart')
            monkeysleep(2)
            stdin, stdout, stderr = client.exec_command('service hpsmhd status | grep "(running)" ')
            logger.debug(stdin)
            logger.debug(stdout)
            logger.debug(stderr)
            client.close()
            logger.info("Done.")
            return True
        except:
            logger.debug(sys.exc_info())
            logger.error("Unable to restart hpsmhd service")
            self.final_status = False
            return False

    def get_smart_storage_info(self,):
        """ Gets smart storage info"""

        ssaDriver = set_chrome_profile()
        ssaUrl = self.url+"/HPSSA/index.htm"
        ssaDriver.get(ssaUrl)
        ssaDriver.maximize_window()
        """ Login to SSA page """
        logger.info("Login in process...")
        # Enter Username
        monkey_type_by_id( ssaDriver, "user", self.user )
        # Enter Password
        monkey_type_by_id( ssaDriver, "password", self.password )
        # Click on Login button
        monkey_click_by_id( ssaDriver, "logonButton" )

        #Wait untill logged in - Checking for homepage frame loaded
        try:
            element = WebDriverWait(ssaDriver,timeout).until(
                        EC.title_contains( "Smart Storage" )
                        )
        except:
            logger.error("Unable to login to SSA page")
            ssaDriver.save_screenshot("%s\\Failure_ScreenShots\\SSA_login_error.png"%(self.lpath))
            self.final_status = False
            return False

        logger.info("Logged in to SSA. Saving screens")
        monkeysleep(2)
        ssaDriver.save_screenshot("%s\\ScreenShots\\SSA_page.png"%(self.lpath))
        monkeysleep(2)

        try:
            logger.info("Closing SSA browser page")
            ssaDriver.quit()
        except:
            logger.debug(sys.exc_info())
            logger.debug("Unable to close SSA browser page.")
        return True

    def _get_webapp_information(self, webappDriver = None):
        """ Get Webapp information """

        if not webappDriver:
            logger.info("Checking webapp info for synergy type server")
            webappDriver = set_chrome_profile()
            webappUrl = self.url+"/hpdiags/frontend2/startup.php?"
            webappDriver.get(webappUrl)
            webappDriver.maximize_window()
            """ Login to Webapp page """
            logger.info("Login in process...")
            # Enter Username
            monkey_type_by_id( webappDriver, "user", self.user )
            # Enter Password
            monkey_type_by_id( webappDriver, "password", self.password )
            # Click on Login button
            monkey_click_by_id( webappDriver, "logonButton" )

            #Wait untill logged in - Checking for webapp title
            try:
                element = WebDriverWait(webappDriver,timeout).until(
                            EC.title_contains( "Insight Diagnostics" )
                            )
            except:
                logger.error("Webapps Page load error")
                webappDriver.save_screenshot("%s\\Failure_ScreenShots\\WebAppsPageLoad.png"%(self.lpath))
                self.final_status = False
                return False
            logger.info("Logged in")

        logger.info("Waiting for insight diagnostics page to load")
        try:
            elem = WebDriverWait(webappDriver,timeout*2).until(
                                    EC.presence_of_element_located( (By.XPATH,"//*[@id='diagnoseTab']") )
                                    )
        except:
            logger.debug(sys.exc_info())
            logger.error("Insight Diagnostics Page load error")
            webappDriver.save_screenshot("%s\\Failure_ScreenShots\\InsightPageLoadError.png"%(self.lpath))
            self.final_status = False
            return False

        monkeysleep(2)
        logger.info("Clicking diagnose tab")
        monkey_click_by_xpath(webappDriver,"//*[@id='diagnoseTab']")
        monkeysleep(2)
        diag_elems = webappDriver.find_elements_by_xpath("//*[@id='diagnoseDeviceList']/li[*]")
        if not diag_elems or 'Not' in diag_elems[0].text:
            logger.error("No devices to diagnose")
            webappDriver.save_screenshot("%s\\Failure_ScreenShots\\NoDevicesInInsightdiagnosticsPage.png"%(self.lpath))
            self.final_status = False
            return False
        logger.info("Clicking All devices checkbox")
        webappDriver.find_elements_by_xpath("//*[@id='diagnoseDeviceList']/li[1]/input")[0].click()
        monkey_click_by_xpath(webappDriver,"//*[@id='beginDiagnosis']")
        logger.info("Running diagnose test")
        try:
            WebDriverWait(webappDriver,timeout).until(EC.text_to_be_present_in_element((By.ID,"cancelRetestButton"),"Retest"))
        except:
            logger.warn("Timeout for diagnose test")
            webappDriver.save_screenshot("%s\\Failure_ScreenShots\\DiagnoseTimeout.png"%(self.lpath))
            self.final_status = False
            return False
        logger.info("Done")
        monkeysleep(2)
        webappDriver.save_screenshot("%s\\ScreenShots\\DiagnosticsInfo_1.png"%(self.lpath) )
        monkeysleep(1)
        self._switch_frame("statusFrameB")
        webappDriver.execute_script("window.scrollTo(0,2000)")
        monkeysleep(1)
        webappDriver.save_screenshot("%s\\ScreenShots\\DiagnosticsInfo_2.png"%(self.lpath))
        monkeysleep(2)
        webappDriver.switch_to_default_content()
        logger.info("Checking logs tab")
        monkey_click_by_id(webappDriver,"logTab")
        monkeysleep(1)
        self._switch_frame("errorLogFrame")
        logElem = webappDriver.find_elements_by_xpath("//*[@id='errorLog']/tbody/tr/td")
        if logElem and "Error Log is empty" not in logElem[0].text:
            logger.warn("Errors present in device diagnose log")
        webappDriver.save_screenshot("%s\\ScreenShots\\DiagnoseErrorLog.png"%(self.lpath) )
        monkeysleep(1)
        webappDriver.switch_to_default_content()
        monkeysleep(2)
        logger.info("Finished verifying webapp info. Closing window")
        try:
            webappDriver.close()
        except:
            logger.debug(sys.exc_info())
            logger.debug("Unable to close webapp window")
        monkeysleep(1)
        return True

    def wrap_up(self,):
        """ Close browser """
        try:
            self._log_available_components()
            logger.info("Closing browser.")
            self.driver.quit()
            logger.info("Done")
        except:
            logger.debug(sys.exc_info())
            logger.debug("Unable to close browser")

    def _log_available_components(self,):
        """ Log available components """

        level_one   = "|__"
        level_two   = "|      |__"
        level_three = "|      |      |__"
        logger.info("Available components info:")
        for elem in self.component_info:
            logger.info(level_one + elem)
            for data_source in self.component_info[elem]:
                logger.info("|      |")
                logger.info(level_two + data_source)
                for sub_elem in self.component_info[elem][data_source]:
                    logger.info(level_three + sub_elem)
                if not self.component_info[elem][data_source]:
                    logger.info(level_three + "No components")
            logger.info("| ")

        return True

