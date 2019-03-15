'''
This module contains utility functions that is used by SPP automation.
'''

ROBOT_LIBRARY_VERSION = '0.1'
__version__ = ROBOT_LIBRARY_VERSION

import os
import os.path
import shutil
import glob
import sys
import win32wnet
import time
import datetime
import re
import getpass
import logging
import codecs
import traceback
import wmi
import subprocess
import fileinput
import xlrd
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import zipfile
import urllib2
import platform
from filecmp import dircmp
from os import listdir
from os.path import isfile, join
import difflib


logger = logging.getLogger('SppAPIKeywords')
fh = logging.FileHandler('spp_api.log')
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

fh.setFormatter(formatter)

logger.addHandler(fh)
logger.setLevel(logging.INFO)


class SppAPIKeywords(object):

    '''
    Class contains functions that is used by SPP automation.
    '''
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        """
        Constructor
        """
        pass

    def Validate_Var(self, custom, default):
        """
        keywords Validate_Var func
        | spp |
        """

        if custom == "":
            custom = default

        return custom

    def get_firefox_profile(self, profile_template):
        """
        Fetches the firefox profile from the template path provided in profile_template.

        profile_template - Defined in variables.py

        Example:
        | Get Firefox Profile | C:\Users\%s\AppData\Roaming\Mozilla\Firefox\Profiles |
        """
        user = os.popen(r'whoami').read().strip().split('\\')[1].capitalize()
        logger.info('username:' + user)
        logger.info('profile_template:' + profile_template)
        profile_dir = profile_template % (user)
        logger.info('profile dir:' + profile_dir)

        try:
            os.chdir(profile_dir)
            profile_name = glob.glob('*.default')[0]
        except:
            raise AssertionError("Could not fetch the firefox profile, path might be wrong")

        complete_path = profile_dir + '\\' + profile_name
        return complete_path

    '''
    @author: Prasanna Sahoo
    '''

    def get_hpsum_preinstall_status(self, log_name, log_time):
        '''
        This function will check the Inventory , Deployment and Analysis Status.
        '''
        t_ref = datetime.datetime.strptime(log_time, "%Y-%m-%d %H:%M:%S")
        inventory_tag = "Inventory"
        analysis_tag = "Analysis"
        deployment_tag = "Deployment"
        data_list = []
        hpsum_start_tag = "HP Smart Update Manager for Node localhost Started"
        hpsum_end_tag = "HP Smart Update Manager for Node localhost Finished"
        details_dict = {'Inventory': 'ERROR', 'Analysis': 'ERROR', 'Deployment': 'ERROR'}
        # Open the file with read only permit
        f = open(log_name, 'r')
        flag = False
        for line in f:
            if hpsum_start_tag in line:
                begin_time = line.split('Started:')[1]
                begin_time = begin_time.strip()
                first_time = str(begin_time)
                t_log = datetime.datetime.strptime(first_time, "%a %b %d %Y %H:%M:%S")
                if t_log > t_ref:
                    flag = True
                    continue
            if hpsum_end_tag in line:
                if flag:
                    data_list.append(details_dict)
                    details_dict = {'Inventory': 'ERROR', 'Analysis': 'ERROR', 'Deployment': 'ERROR'}
                flag = False
                continue

            if flag:
                if inventory_tag in line:
                    status = line.strip().split()[1]
                    details_dict['Inventory'] = status.upper()
                    continue
                if analysis_tag in line:
                    status = line.strip().split()[1]
                    details_dict['Analysis'] = status.upper()
                    continue
                if deployment_tag in line:
                    status = line.strip().split()[1]
                    details_dict['Deployment'] = status.upper()
                    continue
        if flag:
            data_list.append(details_dict)
        print data_list

    def Re_Match(self, re_str, match_str):
        """
        Returns matched regular expression pattern
        """
        if not match_str:
            return match_str
        try:
            return re.match(str(re_str), match_str).group(1)
        except:
            raise AssertionError("Error in matching regular expression pattern")

    '''
    @author: Vinay Krishnan
    '''

    def Construct_Command(self, command_template, *args):
        """
        Replaces all the instances of %s in command_template with values provided
        following command_template.

        Example:
        | Construct Command | C:\Users\%s\AppData\Roaming\Mozilla\Firefox\Profiles | Administrator | Replaces %s with  Administrator |
        | Construct Command | %s\hp\swpackages\hpsum.bat /target %s /user %s /password %s /s | D: | 172.20.56.198 | root | root123 |
        """
        return command_template % (args)

    '''
    @author: Vinay Krishnan
    '''

    def getEventLogs(self, conn, logtype, logPath):
        """
        Get the event logs from the specified machine according to the
        log type (Example: Application) and save it to the appropriately
        named log file
        """
        log = codecs.open(logPath, encoding='utf-8', mode='w')
        log.write("<html>\n")

        wql = "SELECT * FROM Win32_NTLogEvent WHERE Logfile = '%s' AND Type = 'Error'" % (logtype)
        wql_r = conn.query(wql)
        wql = "SELECT * FROM Win32_NTLogEvent WHERE Logfile = '%s' AND Type = 'Critical'" % (logtype)
        wql_r += conn.query(wql)

        filter_components = ["Winlogon", "MsiInstaller", "Security-SPP", "SNMP", "WBEM", "HpCISSs2", "HpCISSs3", "HpSAMD", "HP Ethernet", "HP Smart Update Manager System Log and NIC agents"]
        try:
            for component in wql_r:
                the_time = str(component.TimeGenerated)
                evt_type = component.EventType
                msg = component.Message
                source = str(component.SourceName)
                logger.info('Found componets' + source)
                if any([component in source for component in filter_components]):
                    log.write("<b>Event Date/Time</b>: %s</br>" % the_time)
                    log.write("<b>Source</b>: %s</br>" % source)
                    log.write("<b>Message</b>:%s</br></br>" % msg)
        except:
            log.write("</html>")
            raise AssertionError(traceback.print_exc(sys.exc_info()))
        log.write("</html>")

    '''
    @author: Vinay Krishnan
    '''

    def get_all_events(self, connection, basePath):
        """
        Wrapper for getEventLogs function.
        """
        logtypes = ["System", "Application"]
        for logtype in logtypes:
            path = os.path.join(basePath, "%s.html" % (logtype))
            ret = self.getEventLogs(connection, logtype, path)

    '''
    @author: Prasanna Sahoo
    '''

    def check_permission_of_files(self, output):
        '''
        Added For checking Permission Of Files - Log files should not
        have writeable permission by group and other
        '''
        filename = str(output.split()[-1])
        group = output[5]
        other = output[8]
        # print group , Other
        if group == 'w' or other == 'w':
            raise AssertionError('%s: Group or others have write permission' % (filename,))

    '''
    @author: Prasanna Sahoo
    '''

    def get_component_status_post_installation(self, filename):
        """
        Checks for New version , Component Version, deploying Component Name in 'hpsum_detail_log.txt'.

        Example:
        | Get Component Status Post Installation | C:\\dev\\spp\\tests\\hpsum_detail_log.txt |
        """
        for num, line in enumerate(open(filename)):
            if 'Source:' in line:
                component = line.split(':')[-1].strip()
                if not component:
                    raise AssertionError('Component not found; line number: ', num + 1)
            if 'Installing:' in line:
                component = line.split(':')[-1].strip()
                if not component:
                    raise AssertionError('Component not found; line number: ', num + 1)
            if 'Version:' in line:
                if not line.split(':')[-1].strip():
                    raise AssertionError('Component Version not found for %s line number: %d' % (component, num + 1))
            if 'Description:' in line:
                if not line.split(':')[-1].strip():
                    raise AssertionError('Component Description not found for %s line number: %d' % (component, num + 1))
            if 'Return code:' in line:
                if not line.split(':')[-1].strip():
                    raise AssertionError('Return Code is not found for %s line number: %d' % (component, num + 1))

    '''
    @author: Prasanna Sahoo
    '''

    def get_component_status_post_installation_for_vmware_remote_node(self, filename):
        """
        Checks for New version , Component Version, deploying Component Name in 'hpsum_detail_log.txt'.

        Example:
        | Get Component Status Post Installation For Vmware Remote Node | C:\\dev\\spp\\tests\\hpsum_detail_log.txt |
        """
        flag = 0
        error_messages = []
        for num, line in enumerate(open(filename)):
            if 'New Version:' in line:
                new_version = line.split(':')[-1].strip()
                logger.info('New Version: ' + new_version)
                if not line.split(':')[-1].strip():
                    flag = 1
                    error_messages.append('New Version not found; line number: %s' % (str(num + 1)))
            if 'Component Version to be Installed:' in line:
                component_version = line.split(':')[-1].strip()
                logger.info('Component Version is:' + component_version)
                if not line.split(':')[-1].strip():
                    flag = 1
                    error_messages.append('Component Version to be installed not found; line number: %s' % (str(num + 1)))
            if 'Deploying component ...' in line:
                flag = 1
                error_messages.append('Deploying Component not found; line number: %s' % (str(num + 1)))

        if flag:
            raise AssertionError(str(error_messages))

    '''
    Created on Apr 2, 2015
    @author: Girish Devappa
    '''

    def get_component_status_post_installation_windows(self, filename):
        """
        Checks 'hpsum_detail_log.txt' if any of  Source, Version ,
        Component Name or Component Return Code is empty.

        Example:
        | Get Component Status Post Installation Windows | hpsum_detail_log.txt |
        """
        reg_exp_source = r'(Source:)( (\w+.exe))*'
        reg_exp_version = r'(Version:)( (\d+(\.\d+)*$))*'
        reg_exp_name = r'(Name:)(.*)'
        reg_exp_code = r'(Return Code)(( \(\d\))*)'

        pattern_Source = re.compile(reg_exp_source)
        pattern_Version = re.compile(reg_exp_version)
        pattern_Name = re.compile(reg_exp_name)
        pattern_Code = re.compile(reg_exp_code)

        error_msg = ""
        test_flag = True
        source_string = ""

        for num, line in enumerate(open(filename, 'r')):
            line = " ".join(line.split())
            m = pattern_Source.match(line)

            if m:
                if m.group(2) is None:
                    error_msg += "Source not found; line number:" + str(num + 1) + "\n"
                    test_flag = False
                else:
                    source_string = ""
                    source_string = m.group(2)
                    continue

            m = pattern_Version.match(line)
            if m:
                if m.group(2) is None:
                    error_msg += "For Source" + source_string + "\n"
                    error_msg += "Version not found for line number:" + str(num + 1) + "\n"
                    test_flag = False

            m = pattern_Name.match(line)
            if m:
                if m.group(2) == "":
                    error_msg += "For Source" + source_string + "\n"
                    error_msg += "Name not found for line number:" + str(num + 1) + "\n"
                    test_flag = False

            m = pattern_Code.match(line)
            if m:
                if m.group(2) == "":
                    error_msg += "For Source" + source_string + "\n"
                    error_msg += "Return Code is not found for line number:" + str(num + 1) + "\n"
                    test_flag = False

            m = pattern_Code.match(line)
            if m:
                if m.group(2) == "":
                    error_msg += "For Source" + source_string + "\n"
                    error_msg += "Return Code is not found for line number:" + str(num + 1) + "\n"
                    test_flag = False

        if not test_flag:
            raise AssertionError("PIV failed: " + error_msg)

    '''
    Created on May 18, 2015
    @author: Girish Devappa
    Modified on Dec 22, 2015
    @author: Vinay Krishnan
    '''

    def load_utilities(self, server, username, password, dirname):
        """
        This function loads the utilities on SUT and calls screenshot() to capture the screenshot. The required files need to placed at
        the RG server location $workingdirectory\resource\screenshot eg: C:\dev\spp\tests\spp\resource\screenshot.
        The screenshots would be placed at the location as specified in the LOG_PATH\Screenshots
        """

        utilities = {r'HP Smart Storage Administrator': r'C:\Program Files\HP\hpssa\bin\hpssaclient.exe',
                     r'HP ProLiant Integrated Management Log Viewer': r'C:\Program Files\Compaq\Cpqimlv\cpqimlv.exe',
                     r'HP Lights-Out Online Configuration Utility': r'C:\Program Files\HP\hponcfg\hponcfg_gui.exe',
                     r'hpssacli': r'C:\Program Files\HP\hpssacli\bin\hpssacli.exe'
                     }
        utility_names = []

        for utility in utilities:
            cmd = ['psexec.exe ', r'\\' + server, '-u', username.strip(), '-p', password.strip(), '-d', '-i', 'cmd', r'/c', utilities[utility]]
            logger.info(str(cmd))
            subprocess.call(cmd, stdout=subprocess.PIPE, shell=True)
            time.sleep(20)
            screenshot_name = self.screenshot(utility, server, username, password, dirname)
            time.sleep(15)
            utility_names.append(screenshot_name)
        return utility_names

    '''
    Created on May 18, 2015
    @author: Girish Devappa
    '''

    def screenshot(self, utility, server, username, password, dirname):
        """
        Captures the screenshot of the utility and returns the filename of the screenshot.

        utility - Complete path to the utility of which the screenshot has to be captured.

        server - IP Address of the server where the screenshot has to be captured.

        username - User name of the remote server

        password - Password of remote server

        dirname - Directory where the take_screenshot.bat utility is present

        Example:
        | Screenshot | C:\Program Files\HP\hpssa\bin\hpssaclient.exe | 172.20.56.150 | Administrator | Compaq123 | C:\take_screenshot\ |
        """

        cmd = ['psexec.exe ', r'\\' + server, '-u', username, '-p', password, '-d', '-i', 'cmd', r'/c', str(dirname) + r"\take_screenshot.bat", utility, '_'.join(utility.split()) + '.png']
        logger.info(str(cmd))
        subprocess.call(cmd, stdout=subprocess.PIPE, shell=True)
        return '_'.join(utility.split()) + '.png'

    def combine_files(self, destination, *source_files):
        """
        Appends the contents of files in source_files to destination file.

        Example:
        | Combine Files | .\\${LOG_PATH}\\hpsum_detail_log.txt | .\\${LOG_PATH}\\hpsum_detail_log_1.txt | .\\${LOG_PATH}\\hpsum_detail_log_2.txt |
        """

        if len(source_files) < 1:
            raise AssertionError("No files to combine")

        try:
            f_write = open(destination, 'w')
        except:
            raise AssertionError("Could not open file: " + destination)
        for files in source_files:
            try:
                f_read = open(files)
            except:
                raise AssertionError("Could not open file: " + files)
            for line in f_read:
                f_write.write(line)
            f_read.close()
        f_write.close()

    '''
    @author: Prasanna Sahoo
    '''

    def check_for_os_architecture(self):
        """
        Parses the scouting.log and returns the OS of the remote node.
        Returns either LINUX or VMWARE.
        """
        for line in open("scouting.log", 'r'):
            if "with error code 0" in line or "with return code 0" in line:
                if 'LINUX' in line:
                    return 'LINUX'
                if 'VMWARE' in line:
                    return 'VMWARE'

    '''
    Created on June 1, 2015
    @author: Sriram Chaudary
    '''

    def Parse_Excel_File(self, Excel_File_Path):
        '''
        Get all Components from Excel file and return list with all components.

        Example:
        | Parse Excel File | ${Excel_Path} |
        '''

        workbook = xlrd.open_workbook(Excel_File_Path)
        try:
            worksheet = workbook.sheet_by_name('vmware')
        except:
            raise AssertionError("\n\n Could not contain vmware sheet ")
        comp_list = []
        no = 0
        for x in range(0, 4):
            row = worksheet.row(x)
            if no > 2:
                break
            indices = [i for i, s in enumerate(row) if 'name' in s.value]
            if indices:
                no = indices[0]
        for row_idx in range(0, worksheet.nrows):       # Iterate through rows
            for col_idx in range(0, 1):                 # Iterate through columns
                cell_obj = worksheet.cell(row_idx, no)  # Get cell object by row, col
                comp_list.append(cell_obj.value)
        for i in comp_list:
            print 'zip files are:', i
            pass
        return comp_list

    def Get_File_Names(self, path, drive, file_type):
        path = str(path)
        type = str(file_type)
        query_string = "Select * from CIM_DataFile WHERE Path = '%s' AND Drive = '%s' AND Extension = '%s'" % (path, drive, file_type)
        logger.info(query_string)
        output = self.connection.query(query_string)
        files = []
        for item in output:
            logger.info(str(item.Name))
            files.append(item.Name)
        return files

    def unzip_files(self, server, username, password, dest, source):
        """
        Unzip .zip files in SUT server.

        Example:
        | Unzip Files | ${SYSTEM_IP} | ${SYSTEM_USERNAME} | ${SYSTEM_PASSWORD} | ${destination} | ${source} |
        """
        logger.info(str(source))
        unzip_cmd = r'C:\\spp_automation_setup\\unzip.exe -d %s %s' % (dest, source)
        cmd = ['psexec.exe ', r'\\' + server,
               '-u', username,
               '-p', password,
               '-d', '-i',
               'cmd', r'/c', unzip_cmd]
        subprocess.call(cmd, stdout=subprocess.PIPE, shell=True)
        time.sleep(5)

    '''
    Created on June 1, 2015
    Modified on 20 April 2016
    @author: Sriram
    @author: Rahul Verma
    '''

    def check_file_name(self, fname):
        """
        Check file name after unzip, Specified conditions are matching or not.

        Example:
        | Unzip Files | ${Filename} |
        """
        if re.search(r'offline[-_]bundle', fname, re.I):
            return 'VMWARE Signed'
        elif re.search(r'(MLNX-NMST|MLNX-MST)', fname, re.I):
            pass
        elif re.search(r'net-mst', fname, re.I):
            pass
        elif re.search(r'hp[vd]sa*', fname, re.I):
            pass
        else:
            return 'Unsigned'

    '''
    Created on June 1, 2015
    Modified on March 30, 2016
    @author: Kapil Chauhan
    '''

    def read_hpsum_config_file(self, path):
        '''
        This function will read the following parameter "bypass_vib_sig_check" in "hpsum.ini" file.
        If value of "bypass_vib_sig_check=true" then it will be changed to false by this function.
        '''

        f = open(path, 'r')
        filedata = f.read()
        f.close()
        if 'bypass_vib_sig_check=true' in filedata:
            newdata = filedata.replace("bypass_vib_sig_check=true", "bypass_vib_sig_check=false")
            f = open(path, 'w')
            f.write(newdata)
            f.close()
            return('bypass_vib_sig_check value = true')
        elif 'bypass_vib_sig_check=false' in filedata:
            return('bypass_vib_sig_check value is already false')
        else:
            return("String bypass_vib_sig_check not found")

    '''
    Created on July 6, 2015
    Modified on Dec 12, 2015
    @author: devappa
    Modified on 28 July, 2016
    @author: Rahul Verma
    '''

    def windows_signature_validation(self, windows_component_list, report_file_path):
        '''
        This function will initially check for all the unsigned items in SUT and do a comparison
        with content.html. Further it does compare with HPSUM_deploy_preview.xml and
        logs the common entry
        '''

        logger.info("report_file_path " + report_file_path)

        unsigned_dictionary = {}
        querystring = "SELECT * FROM Win32_PnPSignedDriver"
        resultset = self.connection.query(querystring)
        # obtain the list of unsigned drivers
        for result in resultset:
            if result.IsSigned == False:
                unsigned_dictionary[str(result.DriverVersion)] = [str(result.DriverProviderName)]

        # unsigned_list will contain list of list  where in inner list will have two items each of FriendlyName and DriverVersion
        logger.info("unsigned items from sut")
        for key, val in unsigned_dictionary.iteritems():
            logger.info(key)
            logger.info(str(key) + " : " + str(val))

        for list_item in windows_component_list:
            for item in unsigned_dictionary:
                if list_item == item:
                    unsigned_dictionary[item].append(str(list_item))

        logger.info("unsigned items updated from consolidated from contents.html")
        for key, val in unsigned_dictionary.iteritems():
            logger.info(str(key) + " : " + str(val))

        # obtain from contents.html list of unsigned items and do a comparison with REPORT_XML
        final_unsigned_list = {}

        tree = ET.parse(report_file_path)
        root = tree.getroot()

        for child in root.iter("component"):
            if (str(child[0].text) in unsigned_dictionary):
                final_unsigned_list[str(child[6].text)] = [child[0].text, child[5].text]

        for key, val in final_unsigned_list.iteritems():
            logger.warning("Unsigned Component :" + str(key) + "  " + str(val[1]))

        unsigned_keys = final_unsigned_list.keys()
        if unsigned_keys:
            logger.info(" unsigned components  ")
            raise AssertionError("Unsigned Components: " + str(unsigned_keys))

    '''
    Created on Oct 13, 2015
    @author: Vinay Krishnan
    '''

    def split_files(self, inputFile, chunk_size, prefix):
        '''
        This function divides the files into chunks of chunk_size
        and returns their file names as a list.
        '''
        # read the contents of the file
        f = open(inputFile, 'rb')
        data = f.read()  # read the entire content of the file
        f.close()

        # get the length of data, ie size of the input file in bytes
        bytes = len(data)

        # calculate the number of chunks to be created
        noOfChunks = bytes / chunk_size
        if(bytes % chunk_size):
            noOfChunks += 1

        chunkNames = []
        for i in range(0, bytes + 1, chunk_size):
            fn1 = "%s_segment_%s" % (prefix, i)
            chunkNames.append(fn1)
            f = open(fn1, 'wb')
            f.write(data[i:i + chunk_size])
            f.close()

        logger.info('segment names ' + str(chunkNames))
        return chunkNames

    '''
    Created on Oct 13, 2015
    @author: Vinay Krishnan
    '''

    def execute_locfg_utility_wrapper(self, ilo, ilo_uname, ilo_pword, blob, script_path, perl_path, locfg_path):
        '''
        This function is used to move python code into ILO blob
        '''
        datalen = os.path.getsize(script_path)
        pid = os.getpid()
        totalsegments = datalen / 2048
        logger.info('segments ' + str(totalsegments))
        isappend = 'n'
        isfinal = 'n'

        segments = self.split_files(script_path, 2048, str(pid))

        for segment_no, segment_name in enumerate(segments):
            logger.info('Processing segment ' + str(segment_name))
            segment_len = os.path.getsize(segment_name)
            segment_data = open(segment_name).read().encode('base64')
            if segment_no:
                isappend = 'y'
            if segment_no >= totalsegments:
                isfinal = 'y'

            ribcl = '''<RIBCL VERSION="2.0">
                        <LOGIN USER_LOGIN="Administrator" PASSWORD="Rootpwd123!">
                        <RIB_INFO MODE="write">
                        <BLOB_WRITE>
                            <BLOB_NAMESPACE VALUE="perm"/>
                            <BLOBSTORE_TYPE VALUE="text/plain" />
                            <BLOB_APPEND VALUE="%s" />
                            <BLOB_FINAL VALUE="%s" />
                            <BLOB_TOTAL_SIZE VALUE="%s" />
                            <BLOB_NAME VALUE="%s" />
                            <BLOB_DATA>
                                -----BEGIN BLOB-----
                                %s
                                -----END BLOB-----
                            </BLOB_DATA>
                        </BLOB_WRITE>
                        </RIB_INFO>
                        </LOGIN>
                    </RIBCL>''' % (isappend, isfinal, segment_len, blob, segment_data)

            os.remove(segment_name)

            try:
                open(str(pid), 'w').write(ribcl)
            except:
                raise AssertionError("Could not open temporary file for writing")

            command = r'%s %s -v -u %s -p %s -s %s -l %s.out -f %s' % (perl_path, locfg_path, ilo_uname, ilo_pword, ilo, pid, pid)
            logger.info(command)
            out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            file_out = open('%s.out' % (pid)).read()
            logger.info(file_out)
            if len(file_out) <= 0:
                raise AssertionError('Error: executing ribcl command')
            if 'Script Succeeded' not in file_out:
                filelist = glob.glob(str(pid) + '*')
                for f in filelist:
                    logger.info(f)
                    os.remove(f)
                raise AssertionError('Error: Selenium script not sent to ilo blob')
            os.remove(str(pid))
            os.remove('%s.out' % (pid))

    '''
    Created on Oct 13, 2015
    @author: Vinay Krishnan
    '''

    def write_by_ribcl(self, ilo, uname, pword, xml_name, perl_path, locfg_path):
        '''
        This function is used to execute various XML scripts on remote server, like Set_One_Time_Boot_Order_To_HDD.xml
        '''
        command = r'%s %s -v -u %s -p %s -s %s -f %s' % (perl_path, locfg_path, uname, pword, ilo, xml_name)
        logger.info(command)
        out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        logger.info(str(out))
        if len(out[1]) > 0:
            raise AssertionError('Error: executing ribcl command')
        if 'Script Succeeded' not in out[0]:
            raise AssertionError('Error: script not sent to blob')

    '''
    Created on Aug 6, 2015
    @author: James Pigott and prasanna sahoo
    '''

    def build_signature_list(self, path, os):
        '''
        This function will take the contents.html file from a specific SPP and build the component
        list to use for checking signatures.
        '''
        with open(path) as contents_file:
            contents_html = contents_file.read()

        # Contents.html uses an html feature that doesn't require tags to explicitly be opened
        # This adds the opening tags so we can convert the html table to a dataset
        contents_html = contents_html.replace("</tr>\n", "</tr>\n<tr>")

        contents_stream = BeautifulSoup(contents_html, "html5lib")

        # Find the table in contents.html
        contents_table = contents_stream.find("table", attrs={"id": "content"})

        # The first tr contains the headings
        contents_table_headings = [th.get_text() for th in contents_table.find("tr").find_all("th")]

        contents_datasets = []
        for row in contents_table.find_all("tr")[1:]:
            contents_dataset = zip(contents_table_headings, (td.get_text() for td in row.find_all("td")))

            contents_datasets.append(contents_dataset)

        components_list = []

        for contents_dataset in contents_datasets:
            for contents_field in contents_dataset:
                if contents_field[0] == "Filename":
                    if contents_field[1].endswith("zip") and os == "vmware":
                        components_list.append(contents_field[1])
                    elif contents_field[1].endswith("exe") and os == "windows":
                        reg_tok = re.split('\.', contents_field[1])
                        if reg_tok[1] == "exe":
                            components_list.append(contents_field[1])
                    elif ((contents_field[1].endswith("rpm") or contents_field[1].endswith("scexe")) and os == "linux"):
                        components_list.append(contents_field[1])
        print str(os).capitalize() + " Components\n".join([str(i) for i in components_list])
        return components_list

    '''
    Created on Nov 27, 2015
    @author: Vinay Krishnan
    '''

    def get_RG_root(self):
        ''' Returns the RG root Path '''
        path = os.path.realpath(__file__)
        return "\\".join(path.split("\\")[0:3])

    '''
    Created on Aug 24, 2015
    @author: Vinay Krishnan
    '''

    def install_prerequisites_batch(self, batch_file, arg):
        ''' Starts a process to execute the batch file provided as argument and returns the stdout and stderr '''
        logger.info(batch_file)
        logger.info(arg)
        try:
            process = subprocess.Popen([batch_file, arg], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except:
            raise AssertionError('Error executing batch file %s' % (batch_file))

        output, error = process.communicate()
        return output

    '''
    Created on Aug 24, 2015
    @author: Vinay Krishnan
    '''

    def analyze_prerequisites_log(self, output):
        ''' Searches for errors in output string and raises an Assertion accordingly '''
        if 'All tests successful' not in output or 'is not recognized' in output:
            logger.info(output)
            raise AssertionError('Error installing: refer log file for more details')

    '''
    Created on 29 December 2015
    Modified on 26 February 2016
    @author: Rahul Verma
    '''
    def check_dependency(self,fpath):
        '''
        This function will parse hpsum_log and check for components having dependency and will return a dictionary
        having block number as key and component names as value of the key which is a list.
        '''

        cmp = {'1':None, '2':None, '3':None}
        try:
            f = open(fpath, "r")
        except:
            raise AssertionError('Log file not found: %s' %(fpath))

        c = 0
        r = re.compile(r".*HP Smart Update Manager .* Started.*")
        for line in f:
            m = r.search(line)
            if m:
                components = []
                c += 1
                continue
            if  c <= 3:
                if 'Component Filename' in line:
                    comp = line.split(':')[1].strip()
                if 'Dependency failed' in line:
                    components.append(comp)
                    component_name = list(set(components))
                    cmp.update({str(c):component_name})
            else:
                break

        return cmp

    '''
    Created on Jan 7, 2016
    @author: Sriram Chowdary
    '''
    def replace_string_in_file_return_filename(self, file_path, replace_dict):
        ''' Finds and replaces key in dictionary with value.
            file_path - file name of the file whose macro substitution has to be done
            replace_dict - dictionary whose keys have to replaced with values in file_path.
        '''

        # Converting keys from unicode to str as robot sends unicode
        replace_dict = dict((str(key).strip(), str(replace_dict[key]).strip()) for key in replace_dict)
        logger.info('Replace dict' + str(replace_dict))

        # Creating a temporary file with name preprended with '_temp'
        path, script_name = os.path.split(file_path)
        filename, ext = os.path.splitext(script_name)
        temp_file = os.path.join(path, filename + '_temp' + ext)
        logger.info('Temp file is ' + temp_file)

        # Needed to handle issue with decoding special characters in file
        reload(sys)
        sys.setdefaultencoding('utf8')

        with open(temp_file, 'w') as fwrite, open(file_path) as fread:
            for line in fread:
                match_list = [method for method in replace_dict.keys() if method in line]
                for item in match_list:
                    line = line.replace(item, replace_dict[item])
                fwrite.write(line)

        return temp_file

    '''
    Created on 21 Jan, 2016
    @author: Rahul Verma
    '''    
    def uncheck_dependency_comp(self, fpath):
        '''
        This functions take the source.html file of the review page and parse it to find the component having dependency. 
        It will create a list having id of the component having dependency and will return that list to the calling keyword.
        '''
        soup = BeautifulSoup(open(fpath).read(), "lxml")
        table = soup.findAll('table')
        table_rows = table[2].findAll('tr')
        c_id = []
        for row in table_rows:
            try:
                if row.span.string == 'error':
                    c = row.a['id']
                    c_id.append(c)
            except:
                continue
        return c_id

    '''
    Created on 2. March, 2016
    @author: Rahul Verma
    '''
    def tpm_check(self, fpath):
        '''
        This fucntion will parse hpsum_log to check for TPM module, if present it will give a warning in the running test case
        '''
        flag = 0
        f = open(fpath,"r")
        for line in f:
            if "Trusted Platform Module (TPM)" in line:
                flag = 1
                break
        return flag

    '''
    Created on 11 March, 2016
    @author: Rahul Verma
    '''
    def hpsign_cpid(self, path, version):
        '''
        This function will parse contents.html and will return component id of HPVSA, HPDSA and net-mst kernel according to vmware version
        '''
        with open(path) as contents_file:
            contents_html = contents_file.read()
        contents_html = contents_html.replace("</tr>\n", "</tr>\n<tr>")
        soup = BeautifulSoup(contents_html, "html5lib")
        contents_table = soup.find("table", attrs={"id": "content"})
        contents_table_headings = [th.get_text() for th in contents_table.find("tr").find_all("th")]
        list = {}
        c = []
        contents_datasets = []
        for row in contents_table.find_all("tr")[1:]:
            contents_dataset = zip(contents_table_headings, (td.get_text() for td in row.find_all("td")))
            contents_datasets.append(contents_dataset)

        a = re.compile(r"HP Dynamic Smart Array B140i Controller Driver for VMware.* |net-mst kernel module driver component for VMware.* |HP Dynamic Smart Array B120i/B320i Controller Driver for VMware.*")
        for content_field in contents_datasets:
            for content in content_field:
                if content[0] == "Description":
                    m = a.search(content[1])
                    if m:
                        cp_id = content_field[4]
                        list.update({content[1]:cp_id[1]})
        v = re.search(r"\d\.\d",version)
        b = re.compile(r".*" + v.group(0) + r".*")
        for key, value in list.iteritems():
            h = b.search(key)
            if h:
                c.append(value)
        return c
        
    '''
    Created on 15 March, 2016
    @author: Rahul Verma
    '''
    def get_file_path(self, fpath):
        '''
        This function will take the path of the .zip folder and will reuturn the path and name of .vib file in that folder.
        '''
        vibfile = zipfile.ZipFile(fpath)
        content = vibfile.namelist()
        for val in content:
            if 'vib' in val:
                return (val,os.path.basename(val))
    '''
    Created on 14 Apr, 2016
    @author: Chinmaya Kumar Dash
    '''
    def HPSUM_Check(self):
        '''
        Check whether HPSUM is running in the system
        '''
        for process in self.connection.Win32_Process():
            if 'hpsum_service' in process.caption:
                return process.ProcessId
                
    '''
    Created on 10 May, 2016
    @author: Rahul Verma
    '''
    def HPSUM_deploy_report_check(self, report):
        '''
        Parses the deploy preview report and check if there is any install neended component in the report or not.
        '''
        soup = BeautifulSoup(open(report).read(), "html5lib")
        table = soup.findAll("table", attrs={"class":"custom"})
        r = re.compile(r"No install needed components found.*")
        flag = 0
        for rows in table:
            m = r.search(str(rows))
            if m:
                flag = 1
        return flag
        
    '''
    Created on 21 May, 2016
    @author: Rahul Verma
    '''
    def check_hpsum_detail_log(self,fpath):
        '''
        This function will parse hpsum_detail_log and check if something is intalled or the node was already upto date.
        '''
        f = open(fpath,"r")
        flag = 0
        r = re.compile(r".*Node .* is up to date, no updates were needed.*")
        for line in f:
            m = r.search(line)
            if m:
                flag = 1
        return flag

    '''
    Created on 25 May, 2016
    @author: Sriram Chowdary
    '''
    def download_file_from_http_server(self, url, dow_path):
        '''
        Download ssp image from web server using http URL

        Example:
        | Download File From Http Server | ${IMAGE_LOCATION} | ${OFFLINE_SPP_PATH}\\downloaded_spp_image\\ |
        '''
        proxy_handler = urllib2.ProxyHandler({})
        opener = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener)

        filename = url.split('/')[-1].strip()
        print filename
        print dow_path + filename

        response = urllib2.urlopen(url)

        f = open(dow_path + filename, 'wb')

        while True:
            html = response.read(100)
            if not html:
                break
            f.write(html)
        f.close()
        return filename

    '''
    Created on 25 May, 2016
    @author: Sriram Chowdary
    '''
    def kill_hpsum_process_rg(self):
        '''
        Kill hpsum process on rg server

        Example:
        | Kill Hpsum Process RG|
        '''
        c = wmi.WMI ()
        for process in c.Win32_Process():
            if 'hpsum_service' in process.caption:
                return process.ProcessId

    '''
    Created on 20 July, 2016
    @author: Chinmaya Kumar Dash
    '''
    def connect_to_share_path(self,ip,user,password):
        '''
        Establish a share connection.
        
        Example:
        | Connect To Share Path | ${IMAGE_SHARE_IP} | ${IMAGE_SHARE_USERNAME} | ${IMAGE_SHARE_PASSWORD} |
        '''
        try:
            unc = unc = ''.join(['\\\\', ip])
            win32wnet.WNetAddConnection2(0, None, unc, None, user, password)
        except:
                win32wnet.WNetCancelConnection2(unc, 0, 0)
                win32wnet.WNetAddConnection2(0, None, unc, None, user, password)

    '''
    Created on 20 July, 2016
    @author: Chinmaya Kumar Dash
    '''
    def mount_image(self,disk1,disk2):
        '''
        Mount the iso image in system.
        
        Example:
        | Mount Image | ${LEFT_IMAGE_PATH} | ${RIGHT_IMAGE_PATH} |
        '''
        try:
            os.system('batchmnt %s'%(disk1))
        except:
            raise assertionerror("Unable to mount")
        time.sleep(5)
        try:
            os.system('batchmnt %s'%(disk2))
        except:
            raise assertionerror("Unable to mount")
        time.sleep(5)

    '''
    Created on 20 July, 2016
    @author: Chinmaya Kumar Dash
    '''
    def get_spp_mount_point(self,left_disk,right_disk):
        '''
        Get the iso image mount point.
        
        Example:
        | Get Spp Mount Point | ${LEFT_IMAGE_PATH} | ${RIGHT_IMAGE_PATH} |
        '''
        left_iso = re.findall('\w+\.\d+_\d+\.\d+\.iso',left_disk)[0]
        right_iso = re.findall('\w+\.\d+_\d+\.\d+\.iso',right_disk)[0]
        list2 = subprocess.check_output('batchmnt /list', stderr=subprocess.STDOUT).split('\n')
        list1 = []
        for line in list2:
            if left_iso in line or right_iso in line:
                print line
                list1.append(line)
        disk_list = []
        for i in list1:
            disk_list.append(re.findall('[A-Z]:\s',i))
        drive =[]
        for i in disk_list:
            for j in i:
                drive.append(j.strip())
        print len(drive)
        if len(drive)==2:
            return drive
        elif len(drive) > 2:
            raise IOError ('more then 2 images are mounted')
        else:
            raise IOError ('problem in mounting')

    '''
    Created on 20 July, 2016
    @author: Chinmaya Kumar Dash
    '''
    def unmount_image(self,drives):
        '''
        Unmount the Drive
        
        Example:
        | Unmount Image | E: |
        '''
        for disk in drives:
            time.sleep(10)
            try:
                os.system('batchmnt /unmount %s'%(disk))
            except:
                raise assertionerror("Unable to unmount")

    '''
    Created on 20 July, 2016
    @author: Chinmaya Kumar Dash
    '''
    def check_files(self,mount_drives):
        '''
        Check diffrenence between two Drives
        Example:
        | Check Files | E: |
        '''
        dcmp = dircmp(mount_drives[0],mount_drives[1])
        self.create_files(dcmp)

    '''
    Created on 20 July, 2016
    @author: Chinmaya Kumar Dash
    '''
    def create_files(self,dcmp):
        '''
        Cheate comparision files.
        used in check_file.
        '''
        smf = open('same_file.txt','a')
        for name in dcmp.same_files:
            smf.write('%s\%s\n'%(dcmp.left,name))
        smf.close()
        lf = open('left_file.txt','a')
        for name in dcmp.left_only:
            lf.write('%s\%s\n'%(dcmp.left,name))
        lf.close()
        rf = open('right_file.txt','a')
        for name in dcmp.right_only:
            rf.write('%s\%s\n'%(dcmp.right,name))
        rf.close()
        dif = open('differnet_file.txt','a')
        for name in dcmp.diff_files:
            dif.write('%s\%s\n'%(dcmp.left,name))
        dif.close()
        for sub_dcmp in dcmp.subdirs.values():
            self.create_files(sub_dcmp)

    '''
    Created on 20 July, 2016
    @author: Chinmaya Kumar Dash
    '''
    def generate_report(self,drives,log_path):
        '''
        Generate build difference report.
        
        Example:
        | Generate Report | E: G: | Logs/Build Verification/BuildVerification_2016_07_20_12_44_07 |
        '''
        file1_count = file2_count = 0
        folder1_count = folder2_count = 0
        for dirpath, dirnames, filenames in os.walk(drives[0]):
            file1_count += len(filenames)
            folder1_count += len(dirnames)
        for dirpath, dirnames, filenames in os.walk(drives[1]):
            file2_count += len(filenames)
            folder2_count += len(dirnames)
        samefile = []
        leftfile = []
        rightfile = []
        diffrentfile =[]
        file_list = ['same_file.txt','left_file.txt','right_file.txt','differnet_file.txt']
        for files in file_list:
            file1 = open('%s'%files,'r')    
            if 'same_file' in files:
                samefile = file1.readlines()
            if 'left_file' in files:
                leftfile = file1.readlines()
            if 'right_file' in files:
                rightfile = file1.readlines()
            if 'differnet_file' in files:
                diffrentfile = file1.readlines()
        file1.close()
        report = open('report.txt','w')
        report.writelines('Binary Comparison of <%s\> to <%s\>\n'%(drives[0],drives[1]))
        report.writelines('%s files in %s folders in drive %s\n'%(file1_count,folder1_count,drives[0]))
        report.writelines('%s files in %s folders in drive %s\n'%(file2_count,folder2_count,drives[1]))
        report.writelines("\n%s files don't match\n"%(len(diffrentfile)))
        report.writelines('-'*30+'\n')
        report.writelines(diffrentfile)
        report.writelines('\n%s files only on left\n'%(len(leftfile)))
        report.writelines('-'*30+'\n')
        report.writelines(leftfile)
        report.writelines('\n%s files only on right\n'%(len(rightfile)))
        report.writelines('-'*30+'\n')
        report.writelines(rightfile)
        report.writelines('\n%s files match exactly\n'%(len(samefile)))
        report.writelines('-'*30 + '\n')
        report.writelines(samefile)
        report.close()
        self.create_html_file(diffrentfile,drives,log_path)

    '''
    Created on 20 July, 2016
    @author: Chinmaya Kumar Dash
    '''
    def create_html_file(self,diffrentfile,drives,log_path):
        '''
        Creates Html file for readable different files.
        used in generate_report.
        '''
        left_diff_file = []
        right_diff_file = []
        time.sleep(10)
        for strings in diffrentfile:
            if '.txt' in strings or '.bat' in strings or '.json' in strings:
                strings = strings.strip('\n')
                left_diff_file.append(strings)
                right_diff_file.append(strings.replace(drives[0],drives[1]))
        for lfiles in left_diff_file:
            fromlines = open('%s'%(lfiles), 'U').readlines()
            rfiles = lfiles.replace(drives[0],drives[1])
            tolines = open('%s'%(rfiles), 'U').readlines()
            diff = difflib.HtmlDiff().make_file(fromlines,tolines,context=False)
            fname = re.findall(r'\\.*\.',lfiles)
            fname = (fname[0].strip('.')).strip('\\')
            x = open('%s\\%s.html'%(log_path,fname),'w')
            x.writelines(diff)
            x.close()

    '''
    Created on 20 July, 2016
    @author: Chinmaya Kumar Dash
    '''
    def cleanup_tool(self,log_path):
        '''
        move files to log_path.
        
        Example:
        | Cleanup Tool | Logs/Build Verification/BuildVerification_2016_07_20_12_44_07 |
        '''
        file_list = ['same_file.txt','left_file.txt','right_file.txt','differnet_file.txt','report.txt']
        for files in file_list:
             os.system('MOVE /Y %s \"%s\"'%(files,log_path))
