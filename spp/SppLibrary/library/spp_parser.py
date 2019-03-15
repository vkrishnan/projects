import re
import csv
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import zipfile
import urllib2
import os
import logging
import subprocess
import time
from filecmp import dircmp
from os import listdir
from os.path import isfile, join
import difflib
import sys

logger = logging.getLogger('SppLibrary.library')
logger.setLevel(logging.DEBUG)

class SppParser(object):

    """
    This contains all Keywords required for file operations.
    """

    def __init__(self):
        pass

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
                logger.debug('New Version: ' + new_version)
                if not line.split(':')[-1].strip():
                    flag = 1
                    error_messages.append('New Version not found; line number: %s' % (str(num + 1)))
            if 'Component Version to be Installed:' in line:
                component_version = line.split(':')[-1].strip()
                logger.debug('Component Version is:' + component_version)
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
    Created on June 1, 2015
    @author: Sriram
    '''
    def unzip_files(self, server, username, password, dest, source):
        """
        Unzip .zip files in SUT server.

        Example:
        | Unzip Files | ${SYSTEM_IP} | ${SYSTEM_USERNAME} | ${SYSTEM_PASSWORD} | ${destination} | ${source} |
        """
        logger.debug(str(source))
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
        """
        This function will read the following parameter "bypass_vib_sig_check" in "hpsum.ini" file.
        If value of "bypass_vib_sig_check=true" then it will be changed to false by this function.

        Example:
        | Read Hpsum Config File | path |
        """

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
    Modified on 22 December, 2016
    @author: Rahul Verma
    '''
    def windows_signature_validation(self, resultset, report_file_path):
        """
        This function will initially check for all the unsigned items in SUT and do a comparison
        with content.html.

        Further it does compare with HPSUM_deploy_preview.xml and
        logs the common entry.

        Example:
        | Windows Signature Validation | resultset | windows_component_list | report_file_path |
        """

        logger.info("report_file_path " + report_file_path)
        other_unsigned_comp = []
        unsigned_dictionary = {}
        xml_list = []
        # obtain the list of unsigned drivers
        for result in resultset:
            if result.IsSigned == False:
                unsigned_dictionary[str(result.DriverVersion)] = [str(result.DriverProviderName)]

        # unsigned_list will contain list of list  where in inner list will have two items each of FriendlyName and DriverVersion
        logger.info("unsigned items from sut")
        for key, val in unsigned_dictionary.iteritems():
            logger.info(str(key) + " : " + str(val))

        # Create a list having a dictionary containing version, name and filename from Install_details_XML
        final_unsigned_dict = {}
        tree = ET.parse(report_file_path)
        root = tree.getroot()
        for child in root.iter("Component"):
            xml_list.append({'version':str(child[5].text), 'name':str(child[1].text), 'filename':str(child[0].text)})

        for key,value in unsigned_dictionary.iteritems():
            try:
                ind = [i['version'] for i in xml_list].index(key)
            except:
                other_unsigned_comp.append(str(value)) 
            else:
                found_dict = xml_list[ind]
                final_unsigned_dict[found_dict['filename']] = found_dict['name']

        for key, val in final_unsigned_dict.iteritems():
            logger.warning("Unsigned Component :" + str(key) + "  " + str(val))

        if other_unsigned_comp:
            logger.warning("Other unsigned Component(s) not matching version with Install_details_XML:" + str(other_unsigned_comp))

        unsigned_keys = final_unsigned_dict.keys()
        if unsigned_keys:
            logger.info(" unsigned components  ")
            raise AssertionError("Unsigned Components: " + str(unsigned_keys))

    '''
    Created on Aug 6, 2015
    @author: James Pigott and prasanna sahoo
    Modified on Feb 22, 2017
    @author: Rahul Verma
    '''
    def build_signature_list(self, path):
        """
        This function will take the contents.html file from a specific SPP and build the component
        list to use for checking signatures.

        Example:
        | Build Signature List | contents.html |
        """
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
                if contents_field[0] == "Product Category" and "Firmware" not in contents_field[1]:
                    if contents_dataset[4][1].endswith("zip"):
                        components_list.append(contents_dataset[4][1])
        print str(os).capitalize() + " Components\n".join([str(i) for i in components_list])
        return components_list

    '''
    Created on 29 December 2015
    Modified on 11 April 2017
    @author: Rahul Verma
    '''
    def check_dependency(self,fpath):
        """
        This function will parse hpsum_log and check for components having dependency and will return a dictionary
        having block number as key and a dictionary as value of the key which has key as component name and the reason for dependency as value.

        Example:
        | Check Dependency | hspum_log.txt |
        """

        cmp = {'1':None, '2':None, '3':None}
        try:
            f = open(fpath, "r")
        except:
            raise AssertionError('Log file not found: %s' %(fpath))

        c = 0
        r = re.compile(r".*Smart Update Manager .* Started.*")
        d = re.compile(".*Dependency fail.*")
        # Search for Smart update Manager in log to count no. of runs
        for line in f:
            m = r.search(line)
            dep = d.search(line)
            # If string found increase couter and proceed
            if m:
                components = {}
                c += 1
                continue
            if  c <= 3:
                # Get component filename in comp
                if 'Component Filename' in line:
                    comp = line.split(':')[1].strip()
                # Search for Dependency Fail message in log and if found store in ser
                if dep:
                    ser = []
                    if "installation requires one or more" in line:
                        ser.append(line.strip())
                        for line in f:
                            if line.startswith('    -'):
                                s = line.split('-')[1].strip()
                                ser.append(s)
                            else:
                                break 
                    else:
                        ser = line
                    # update dictionary with component name as key and dependency failure message as value
                    components.update({comp:ser})
                    # update dictionary with run count as value and dictionary having component name and dependency failure as value.
                    cmp.update({str(c):components})
            else:
                break
        return cmp

    '''
    Created on 2. March, 2016
    @author: Rahul Verma
    '''
    def tpm_check(self, fpath):
        """
        This fucntion will parse hpsum_log to check for TPM module,
        if present it will give a warning in the running test case

        Example:
        | Tpm Check | hpsum_log.txt |
        """
        flag = 0
        f = open(fpath,"r")
        for line in f:
            if "Trusted Platform Module (TPM)" in line:
                flag = 1
                break
        return flag

    def hpsign_cpid(self, path, version):
        """
        This function will parse contents.html and will return
        component id of HPVSA, HPDSA and net-mst kernel
        according to vmware version.

        Example:
        | Hpsign Cpid | path | version |
        """
        with open(path) as contents_file:
            contents_html = contents_file.read()

        # Contents.html uses an html feature that doesn't require tags to explicitly be opened
        # This adds the opening tags so we can convert the html table to a dataset
        contents_html = contents_html.replace("</tr>\n", "</tr>\n<tr>")
        soup = BeautifulSoup(contents_html, "html5lib")

        # Find the table in contents.html
        contents_table = soup.find("table", attrs={"id": "content"})
        contents_table_headings = [th.get_text() for th in contents_table.find("tr").find_all("th")]
        list = {}
        c = []

        # Creating dataset fron Contents.html
        contents_datasets = []
        for row in contents_table.find_all("tr")[1:]:
            contents_dataset = zip(contents_table_headings, (td.get_text() for td in row.find_all("td")))
            contents_datasets.append(contents_dataset)

        # Creating RE to fing HPDSA, HPVSA and net-mst component from the dataset
        a = re.compile(r".*Dynamic Smart Array B140i Controller Driver for VMware.* |net-mst kernel module driver component for VMware.* |.*Dynamic Smart Array B120i/B320i Controller Driver for VMware.*")
        for content_field in contents_datasets:
            for content in content_field:
                if content[0] == "Description":
                    m = a.search(content[1])
                    if m:
                        cp_id = content_field[4]
                        list.update({content[1]:cp_id[1]})

        # Matching the VMWARE version with the found components in list and return the component id
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
        """
        This function will take the path of the .zip folder and
        will reuturn the path and name of .vib file in that folder.

        Example:
        | Get File Path | cp027548.zip |
        """
        vibfile = zipfile.ZipFile(fpath)
        content = vibfile.namelist()
        for val in content:
            if 'vib' in val:
                return (val,os.path.basename(val))

    '''
    Created on 10 May, 2016
    @author: Rahul Verma
    '''
    def HPSUM_deploy_report_check(self, report):
        """
        Parses the deploy preview report and check
        if there is any install neended component in the report or not.

        Example:
        | HPSUM Deploy Report Check | First_run_deploy_preview_report.html |
        """
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
        """
        This function will parse hpsum_detail_log and
        check if something is intalled or the node was already upto date.

        Example:
        |Check Hpsum Detail Log | hpsum_detail_log.txt |
        """
        f = open(fpath,"r")
        flag = 0
        r = re.compile(r".*Node .* is up to date, no updates were needed.*")
        for line in f:
            m = r.search(line)
            if m:
                flag = 1

        return flag

    def get_node_type(self):
        """
        This Function is use to detect the node type of the remote.

        Example:
        | Get Node Type |
        """
        for line in open('scouting.log','r'):
            if "with error code 0" in line or "with return code 0" in line:
                val = re.findall('is \w+',line)[0].strip('is ')
        return (val.lower())

    '''
    Created on 20 July, 2016
    @author: Chinmaya Kumar Dash
    '''
    def check_files(self,mount_drives):
        """
        Check difference between two Drives

        Example:
        | Check Files | E: |
        """
        dcmp = dircmp(mount_drives[0],mount_drives[1])
        self.create_files(dcmp)

    '''
    Created on 20 July, 2016
    @author: Chinmaya Kumar Dash
    '''
    def create_files(self,dcmp):
        """
        Create comparison files.
        used in check_file.

        Example:
        | Create Files | dcmp |
        """
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
        """
        Generate build difference report.

        Example:
        | Generate Report | E: G: | Logs/Build Verification/BuildVerification_2016_07_20_12_44_07 |
        """
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
        self.create_diff_html_file(diffrentfile,drives,log_path)

    '''
    Created on 20 July, 2016
    @author: Chinmaya Kumar Dash
    '''
    def create_diff_html_file(self,diffrentfile,drives,log_path):
        """
        Creates Html file for readable different files.
        used in generate_report.

        Example:
        | Create_html_file | diffrentfile | drives | log_path |
        """
        left_diff_file = []
        right_diff_file = []
        time.sleep(10)
        for strings in diffrentfile:
            if '.txt' in strings or '.bat' in strings or '.json' in strings:
                strings = strings.strip('\n')
                left_diff_file.append(strings)
                right_diff_file.append(strings.replace(drives[0],drives[1]))
        for lfiles in left_diff_file:
            logger.debug(str(lfiles))
            fromlines = open('%s'%(lfiles), 'U').readlines()
            rfiles = lfiles.replace(drives[0],drives[1])
            tolines = open('%s'%(rfiles), 'U').readlines()
            diff = difflib.HtmlDiff().make_file(fromlines,tolines,context=False)
            fname = lfiles.split('\\')[-1].split('.')[0]
            logger.debug(str(fname))
            x = open('%s\\%s.html'%(log_path,fname),'w')
            x.writelines(diff)
            x.close()

    '''
    Created on 26 October, 2016
    @author: Chinmaya Kumar Dash
    '''
    def get_gatherlog_location(self,lfile):
        """
        This function will get the log location of gather log.

        Example:
        | Get Gatherlog Location | lfile |
        """
        lpath = None
        for line in open(lfile,'r'):
            if "logs are now in" in line:
                lpath = (re.findall(r'in .*',line)[0].strip('in ')).rstrip('\\')
        return lpath

    '''
    Created on 10 October, 2016
    @author: Rahul Verma
    '''
    def reboot_message_check(self, system_log):
        """
        Parses the system log and check if the reboot message given as a parameter is present in it or not.

        Example:
        | Reboot Message Check | system_log |
        """
        soup = BeautifulSoup(open(system_log).read(), "html5lib")
        table = soup.findAll("message")
        r = re.compile(r".*Checking Reboot Message.*")
        flag = 0
        for rows in table:
            m = r.search(str(rows))
            if m:
                flag = 1
        return flag

    '''
    Created on 12 October, 2016
    @author: Rahul Verma
    '''
    def get_ilo_component_filename(self,fpath):
        """
        This function will parse hpsum_log and will return file name for iLO component.

        Example:
        | Get Ilo Component Filename | hpsum_log.txt |
        """
        try:
            f = open(fpath, "r")
        except:
            raise AssertionError('Log file not found: %s' %(fpath))
        r = re.compile(r"Component Name: Online ROM Flash Component .*Integrated Lights-Out.*")
        for line in f:
            m = r.match(line)
            if 'Component Filename' in line:
                comp = line.split(':')[1].strip()
            if m:
                return comp

    '''
    Created on 24 Oct, 2016
    @author: Abhishek
    '''
    def parse_CSV_input_file(self, rg_root, parse_count):
        """
        Parses the csv file and populates HPSUM execution and report
        files according to the options provided.
        Returns a dictionary containing host ip as key and its related
        information as values
        """

        csv_file_dir = '\\tools\\'
        file_existence_path = rg_root + csv_file_dir
        print file_existence_path
        readFileOb = open(file_existence_path+'system_info.csv','r')
        hpsum_execute_file = open(file_existence_path+'hpsum_execute_%s.ini'%(parse_count,),'w')
        hpsum_report_file = open(file_existence_path+'hpsum_report_%s.ini'%(parse_count,),'w')
        csvOb = csv.reader(readFileOb, delimiter=',')
        header_info = next(csvOb)

        host_info = {}
        for row in csvOb:
            if parse_count == 2:
                if "VMWARE" in row[0].upper():
                    logger.debug("%s excluded from second parsing as sut type is Vmware"%(row[1],))
                    continue
                if any(["YES" in row[4].upper(), "YES" in row[5].upper(), "YES" in row[6].upper(), "YES" in row[7].upper()]):
                    logger.debug("%s excluded from second parsing as its installation is not auto"%(row[1],))
                    continue
            if row[1].strip() not in (None, '') and row[1] in host_info.keys(): #Check if SUT IP is provided multiple times and warn
                logger.warn("Details for %s already included in input file"%(row[1],))
                continue
            host_info[row[1]] = {header_info[i]:row[i] for i in range(len(header_info))}
            host_info[row[1]]['configured'] = 0
            try:
                host_info[row[1]]['TYPE'] = host_info[row[1]]['TYPE'].upper()
                if host_info[row[1]]['TYPE'].upper() not in ("LINUX", "WINDOWS", "VMWARE"):
                    logger.debug("Type is %s"%(host_info[row[1]]['TYPE'],))
                    raise Exception("TYPE is not one of WINDOWS or LINUX or VMWARE")
            except:
                logger.debug(sys.exc_info())
                logger.info("Error while parsing csv file. Value in TYPE is not windows or linux")
                raise Exception("Error while parsing csv file. Value in one of TYPE column's row is not windows or linux or vmware")
            logger.debug(repr(row))
            self.populate_input_file(row, hpsum_execute_file, hpsum_report_file)

        hpsum_execute_file.close()
        hpsum_report_file.close()
        readFileOb.close()

        #Validate system details file
        if parse_count == 1 and not host_info.keys():
            logger.debug("%s"%(host_info,))
            raise Exception("System details file is empty.")
        for host in host_info:
            if host_info[host]['SYSIP'].strip() in (None,''):
                raise Exception("SYSIP column must not be empty")
            if host_info[host]['UID'].strip() in (None,''):
                raise Exception("UID column must not be empty")
            if host_info[host]['PWD'].strip() in (None,''):
                raise Exception("PWD column must not be empty")
        return host_info

    '''
    Created on 24 Oct, 2016
    @author: Abhishek
    '''
    def populate_input_file(self,row, hpsum_execute_file, hpsum_report_file):
        """
        Populates the HPSUM execution and report input files
        according to the values fetched from each row of CSV file
        """
        exec_default_options = '\nSILENT = YES \nUSEAMS = YES \nUSEWMI = YES \nUSESNMP = YES \nONFAILEDDEPENDENCY = OmitComponent \
                                \nIGNOREERRORS = "ServerNotFound,BadPassword,FailedDependencies" \nSKIPTARGET = NO \nIGNOREWARNINGS=YES\n'

        report_default_options = '\nSILENT = YES\nREPORT = YES\nREPORTDIR = "C:\\cpqsystem"\nIGNOREERRORS = "ServerNotFound,BadPassword,FailedDependencies" \
                                  \nSKIPTARGET = NO \nIGNOREWARNINGS=YES\n'

        execution_commands = {
                            'default':exec_default_options,
                            'forceall': exec_default_options+"FORCEALL = YES \n",
                            'rewrite' : exec_default_options+"REWRITE = YES \n",
                            'downgrade' : exec_default_options+"DOWNGRADE = YES \n",
                            'force_romonly' : exec_default_options+"FORCEROM = YES \n"
                           }

        if row[4] and row[4].upper() == "YES":#Check force option
            hpsum_execute_file.write(execution_commands['forceall'])
        elif row[5] and row[5].upper() == "YES":#Check rewrite option
            hpsum_execute_file.write(execution_commands['rewrite'])
        elif row[6] and row[6].upper() == "YES":#Check downgrade option
            hpsum_execute_file.write(execution_commands['downgrade'])
        elif row[7] and row[7].upper() == "YES":#Check force_romonly option
            hpsum_execute_file.write(execution_commands['force_romonly'])
        elif row[8] and row[8].upper() == "YES":#Check auto option
            hpsum_execute_file.write(execution_commands['default'])
        else:#No option is given, default to auto script
            if row[1]:
                logger.warn("No installation type specified for %s. Will be defaulted with auto installation"%(row[1],))
            hpsum_execute_file.write(execution_commands['default'])

        if row[0].upper() in ("LINUX", "WINDOWS"):
            hpsum_execute_file.write("TARGETTYPE = %s\n"%(row[0].capitalize()))
        elif row[0].upper() in ("VMWARE"):
            hpsum_execute_file.write("TARGETTYPE = VMware\n")
        hpsum_execute_file.write("[TARGETS]\n")
        hpsum_execute_file.write("HOST = "+row[1]+"\n")
        hpsum_execute_file.write("UID = "+row[2]+"\n")
        hpsum_execute_file.write("PWD = "+row[3]+"\n")
        hpsum_execute_file.write("[END]\n")

        hpsum_report_file.write(report_default_options)
        if row[0].upper() in ("LINUX", "WINDOWS"):
            hpsum_report_file.write("TARGETTYPE = %s\n"%(row[0].capitalize()))
        elif row[0].upper() in ("VMWARE"):
            hpsum_report_file.write("TARGETTYPE = VMware\n")
        hpsum_report_file.write("[TARGETS]\n")
        hpsum_report_file.write("HOST = "+row[1]+"\n")
        hpsum_report_file.write("UID = "+row[2]+"\n")
        hpsum_report_file.write("PWD = "+row[3]+"\n")
        hpsum_report_file.write("[END]\n")

    '''
    Created on 24 Oct, 2016
    @author: Abhishek
    '''
    def parse_HPSUM_log_status_file(self, file_path):
        '''Parses the HPSUM log file of HPSUM deploy preview report OR
           HPSUM installation to check whether HPSUM process is started
           or failed and returns the status.
           status = 1   hpsum failed
           status = 0   hpsum executed
        '''
        hpsum_log_file = open(file_path,'r')
        status = 0
        errors = ('Scouting failed, node type:UNKNOWN'
                , 'Error occurred during operation')
        for line in hpsum_log_file:
            if  errors[0] in  line or errors[1] in line:
                status = 1
                break

        return status

    def HPSUM_multi_node_deploy_report_check(self, report, parse_count):
        """
        This function is used to parse deploy report containing multiple nodes
        Returns a tuple containing a flag and list of nodes information for which
        the search in report succeeds.
        ex for return values: (1,[172.20.56.20,]) or (0,[])
        """
        soup = BeautifulSoup(open(report).read(), "html5lib")
        #Find all nodes in report
        nodes = soup.findAll("a",{"name":re.compile('update*')})
        #Find all tables in report
        tables = soup.findAll("table",{"class":"custom"})
        #Remove an additional table which dosen't have useful information
        for i in tables:
            if "Server Details" in i.previous_element:
                tables.remove(i)

        r = re.compile(r"No install needed components found.*")
        flag = 0
        index = 0
        deploy_info = []
        flag = 0
        for i in nodes:
            found = r.search(str(tables[index]))
            if found and parse_count == 1:
                flag = 1
                deploy_info.append(i.text)
            elif not found and parse_count > 1:
                deploy_info.append(i.text)
            index += 1

        print deploy_info
        if parse_count > 1 and not deploy_info and flag == 0:
            flag = 2
        return (flag,deploy_info)
