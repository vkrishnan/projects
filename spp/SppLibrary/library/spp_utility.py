import os
import codecs
import traceback
import sys
import subprocess
import glob
import logging
import time
import datetime
import re
import wmi
import paramiko
import threading
from pythoncom import CoInitialize

logger = logging.getLogger('SppLibrary.library')
logger.setLevel(logging.DEBUG)

class Utility(object):

    """
    This Contains all the common Keywords which are used by both Windows and Unix test cases.
    """

    def __init__(self):
        pass

    '''
    @author: Prasanna Sahoo
    '''
    def get_hpsum_preinstall_status(self, log_name, log_time):
        """
        This function will check the Inventory , Deployment and Analysis status.

        Example:
        | Get Hpsum  Preinstall Status | log_name | log_time |
        """
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

    '''
    @author: Vinay Krishnan
    '''
    def generate_event_logs(self, logfile, event_logs, log_path):
        """
        Get the event logs from the specified machine according to the
        log type (Example: Application) and save it to the appropriately
        named log file.

        Example:
        | Generate Event Logs | logfile | event_logs | log_path |
        """
        log_path = os.path.join(log_path, "%s.html" % (logfile))
        log = codecs.open(log_path, encoding='utf-8', mode='w')
        log.write("<html>\n")

        filter_components = ["Winlogon", "MsiInstaller", "Security-SPP", "SNMP", "WBEM", "HpCISSs2", "HpCISSs3", "HpSAMD", "HP Ethernet", "HP Smart Update Manager System Log and NIC agents", "User32"]
        try:
            for component in event_logs:
                the_time = str(component.TimeGenerated)
                evt_type = component.EventType
                msg = component.Message
                source = str(component.SourceName)
                logger.info('Found componets' + source)
                if any([component in source for component in filter_components]):
                    log.write("<b>Event Date/Time</b><time>: %s</time></br>" % the_time)
                    log.write("<b>Source</b><name>: %s</name></br>" % source)
                    log.write("<b>Message</b><message>: %s</message></br>" % msg)
        except:
            log.write("</html>")
            raise AssertionError(traceback.print_exc(sys.exc_info()))
        log.write("</html>")

    '''
    @author: Prasanna Sahoo
    '''
    def check_permission_of_files(self, output):
        """
        Added For checking Permission Of Files - Log files should not
        have writable permission by group and other.

        Example:
        | Check Permission Of Files | output |
        """
        filename = str(output.split()[-1])
        group = output[5]
        other = output[8]
        # print group , Other
        if group == 'w' or other == 'w':
            raise AssertionError('%s: Group or others have write permission' % (filename,))

    '''
    Created on Aug 24, 2015
    @author: Vinay Krishnan
    '''
    def install_prerequisites_batch(self, batch_file, arg):
        """
        Starts a process to execute the batch file provided as
        argument and returns the stdout and stderr.

        Example:

        | Install Prerequisites Batch | batch_file | arg |
        """
        logger.info(batch_file)
        logger.info(arg)
        try:
            process = subprocess.Popen([batch_file, arg], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except:
            raise AssertionError('Error executing batch file %s' % (batch_file))

        output, error = process.communicate()

        logger.info(output)        
        if 'All tests successful' not in output or 'is not recognized' in output:
            logger.info(output)
            raise AssertionError('Error installing: refer log file for more details')

    '''
    Created on Mar 5, 2015 @author: girish devappa
    '''
    def hpsum_log_file_check(self, file_info, file_types_list):
        """ 
        This function will verify HPSUM logs by doing a check for files 'node', 'inventory', 'deploy', 'hpsum_log',
        'hpsum_detail_log' on the file system of the host machine. Result would be logged to the file piv_connect_windows.log

        Example:
        | Hpsum Log File Check | file_info |
        """
        test_flag = True
        zero_size_files = []
        files_not_found = []

        for (file_name, file_size) in file_info:
            if file_name in file_types_list:
                if file_size == 0:
                    test_flag = False
                    zero_size_files.append(file_name)
                    logger.info(file_name + " size is zero ")

        files_list = [item[0] for item in file_info]

        for sub_list_name in file_types_list:
            if sub_list_name not in files_list:
                test_flag = False
                files_not_found.append(sub_list_name)

        if not test_flag:
            logger.info(" PIV Failed")
            error_string = 'Files with zero size: ' + ';'.join(zero_size_files) + '\n'
            error_string += 'Files not found: ' + ';'.join(files_not_found)
            raise AssertionError(error_string)

    '''
    Created on Mar 9, 2015
    @author: girish devappa
    Modified on Dec 22, 2015
    @author: Vinay Krishnan
    Modified on Mar 31, 2016
    @author: Chinmaya kumar Dash
    '''
    def PIV_hpservice_check(self,server_type, services):
        """ The function will check if the services HP AMS Storage Service ,HP Insight Event Notifier,
            HP Insight Foundation Agents,HP Insight NIC Agents,HP Insight Server Agents,HP Insight Storage Agents,
            HP ProLiant Agentless Management Service,HP ProLiant Health Monitor Service,
            HP ProLiant System Shutdown Service,HP Smart Array SAS/SATA Event Notification Service,
            HP Smart Update Tools,HP System Management Homepage ,HP WMI Storage Providers
            are running or not in Proliant server

            And check if the services HP Insight Event Notifier,
            HP Insight Foundation Agents,HP Insight NIC Agents,HP Insight Server Agents,HP Insight Storage Agents,
            HP ProLiant Agentless Management Service, HP ProLiant System Shutdown Service,
            HP Smart Update Tools,HP System Management Homepage 
            are running or not in Proliant server.

            Result would be logged to the file piv_connect_windows.log

            Example:
            | PIV Hpservice Check | server_type | services |
        """
        service_dict_proliant = {'Insight Foundation Agents': 0,
                        'Insight Server Agents': 0,
                        'Insight Storage Agents': 0,
                        'Insight NIC Agents': 0,
                        'System Management Homepage': 0,
                        'ProLiant System Shutdown Service': 0,
                        'ProLiant Agentless Management Service': 0,
                        'ProLiant Monitor Service': 0,
                        'Smart Array SAS/SATA Event Notification Service': 0,
                        #'Smart Update Tools': 0,
                        'AMS Storage Service': 0,
                        'Insight Event Notifier': 0,
                        'WMI Storage Providers': 0
                        }
        service_dict_synergy = {'Insight Foundation Agents': 0,
                        'Insight Server Agents': 0,
                        'Insight Storage Agents': 0,
                        'Insight NIC Agents': 0,
                        'System Management Homepage': 0,
                        'ProLiant System Shutdown Service': 0,
                        'ProLiant Agentless Management Service': 0,
                        #'Smart Update Tools':0,
                        'Insight Event Notifier':0
                        }
        service_dict = {}
        if server_type == 'synergy':
            service_dict = service_dict_synergy
        elif server_type == 'proliant':
            service_dict = service_dict_proliant

        service_list = service_dict.keys()

        for item in services:
            flag = 0
            service_name = ''
            for service in service_list:
                if not len(set(service.split()) - set(item[0].split())):
                    flag = 1
                    service_name = service
                    break

            if flag and item[1] == 'Running':
                service_dict[service_name] = 1
            elif (service in item[0]) and (item[1] == 'Stopped' or item[1] == 'Disabled' or item[1] == 'Paused'):
                service_dict[service_name] = 2

        logger.debug('service_dict' + str(service_dict))
        return service_dict

    def wbem_check(self, services):
        service_name = 'WMI Storage Providers'
        for service in services:
            if not len(set(service_name.split()) - set(service[0].split())) and service[1] == 'Running':
                return 1
        return 0

    '''
    Created on Mar 20, 2015 @author: girish devappa
    Modified on Mar 31, 2016
    @author: Chinmaya kumar Dash
    '''
    def PIV_uninstall_programs_check(self, installed_programs):
        """
        This function will uninstall the progarms HP Lights-Out Online Configuration Utility,
        HP ProLiant Integrated Management Log Viewer, HP Smart Storage Administrator CLI,
        log data is appended to piv_connect_windows.log

        Example:
        | PIV Uninstall Programs Check | installed_programs |
        """
        uninstall_programs_list = ["Lights-Out Online Configuration Utility", 
                                    "Integrated Management Log Viewer", 
                                    "Smart Storage Administrator CLI"]
        installed_programs_list = []

        for program in installed_programs:
            installed_programs_list.append(program.Name.strip())

        common_products = []

        for product in uninstall_programs_list:
            for sys_product in installed_programs_list:
                if product in sys_product:
                    common_products.append(product)
        missing_products = list(set(uninstall_programs_list) - set(common_products))
        logger.debug('common_products' + str(common_products))
        logger.debug('missing_products' + str(missing_products))

        for installed_program in installed_programs:
            try:
                for program in common_products:
                    if program in installed_program.Name:
                        logger.info("uninstalling " + str(installed_program.Name))
                        installed_program.Uninstall()
                        break
            except:
                raise AssertionError("Failed to uninstall " + str(installed_program.Name))

        if len(common_products) != len(uninstall_programs_list):
            raise AssertionError("Programs Not Found: " + "\n".join(list(missing_products)))

    def parse_device_manager_info(self, resultset):
        """ 
        Detects if there are any yellow bang in the Device manager of
        remote computer.

        Example:

        | Parse Device Manager Info | resultset |
        """
        yellowbanglst = []
        for objItem in resultset:
            desc = str(objItem.Description)
            if desc not in yellowbanglst and 'Mouse' not in desc and 'Keyboard' not in desc:
                yellowbanglst.append(objItem.Description)
                logger.info('Yellow bang item: ' + desc)
        if len(yellowbanglst) > 0:
            raise AssertionError(" Yellow bang items:   " + ','.join([i for i in yellowbanglst if i]))

    def _split_files(self, inputFile, chunk_size, prefix):
        """
        This function divides the files into chunks of chunk_size
        and returns their file names as a list.

        Used in send_script_to_blob_wrapper.
        """
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

        logger.debug('segment names ' + str(chunkNames))
        return chunkNames

    def send_script_to_blob_wrapper(self, ilo, ilo_uname, ilo_pword, blob, script_path, perl_path, locfg_path, ribcl_xml_template):
        """
        This function is used to move python code into ILO blob.

        Example:
        | Send Script To Blob Wrapper | ilo | ilo_uname | ilo_pword | blob | script_path | perl_path | locfg_path | ribcl_xml_template |
        """
        datalen = os.path.getsize(script_path)
        pid = os.getpid()
        totalsegments = datalen / 2048
        logger.info('segments ' + str(totalsegments))
        isappend = 'n'
        isfinal = 'n'

        segments = self._split_files(script_path, 2048, str(pid))

        for segment_no, segment_name in enumerate(segments):
            logger.debug('Processing segment ' + str(segment_name))
            segment_len = os.path.getsize(segment_name)
            segment_data = open(segment_name).read().encode('base64')
            if segment_no:
                isappend = 'y'
            if segment_no >= totalsegments:
                isfinal = 'y'

            ribcl = ribcl_xml_template % (isappend, isfinal, segment_len, blob, segment_data)

            os.remove(segment_name)

            try:
                open(str(pid), 'w').write(ribcl)
            except:
                raise AssertionError("Could not open temporary file for writing")

            command = r'%s %s -v -u %s -p %s -s %s -l %s.out -f %s' % (perl_path, locfg_path, ilo_uname, ilo_pword, ilo, pid, pid)
            logger.info(command)
            out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            file_out = open('%s.out' % (pid)).read()
            logger.debug(file_out)
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
    Created on 20 July, 2016
    @author: Chinmaya Kumar Dash
    '''
    def mount_image(self,*disks):
        """
        Mount the iso image in system.

        Example:
        | Mount Image | ${LEFT_IMAGE_PATH} | ${RIGHT_IMAGE_PATH} |
        """
        for disk in disks:
            subprocess.Popen('batchmnt %s /wait'%(disk),stdout = subprocess.PIPE)
            time.sleep(5)

    '''
    Created on 20 July, 2016
    @author: Chinmaya Kumar Dash
    '''
    def get_build_mount_point(self,left_disk,right_disk):
        """
        Get the iso image mount point.

        Example:
        | Get Spp Mount Point | ${LEFT_IMAGE_PATH} | ${RIGHT_IMAGE_PATH} |
        """
        cmd_out = subprocess.Popen('batchmnt /list',stdout = subprocess.PIPE)
        cmd_out1 =  cmd_out.communicate()[0].split('\n')
        drives = []
        for i in cmd_out1:
            if left_disk.split('\\')[-1].strip('"') in i or right_disk.split('\\')[-1].strip('"') in i:
                drives.append(i.split(' ')[0])
        return drives

    '''
    Created on 20 July, 2016
    @author: Chinmaya Kumar Dash
    '''
    def unmount_image(self,drives):
        """
        Unmount the Drive

        Example:
        | Unmount Image | E: |
        """
        for disk in drives:
            time.sleep(10)
            try:
                subprocess.Popen('batchmnt /unmount %s'%(disk),stdout = subprocess.PIPE)
            except:
                raise AssertionError("Unable to unmount")

    '''
    Created on 25 Oct, 2016
    @author: Abhishek
    '''
    def reboot_servers(self, server_info):
        """
        Reboots the servers provided in the argument.
        Creates a thread for each host identified, starts the thread and
        waits for completion of all started threads.
        Returns list of failed servers if any
        """

        reboot_threads = []
        failed_servers = []

        #logging needed for paramiko module
        paramiko.util.log_to_file("paramiko.log")

        for server in server_info:
            thread_args = {}
            thread_args['host'] = server_info[server]['SYSIP']
            thread_args['username'] = server_info[server]['UID']
            thread_args['password'] = server_info[server]['PWD']
            thread_args['type'] = server_info[server]['TYPE']

            try:
                reboot_thread = threading.Thread(target = Utility._reboot_server, args = (thread_args, failed_servers), name=thread_args['host'])
                reboot_threads.append(reboot_thread)
                reboot_thread.start()
            except:
                logger.debug("Unable to start reboot process thread for %s"%(server))
                failed_servers.append(server)

        for reboot_thread in reboot_threads:
            reboot_thread.join()
            if reboot_thread.name not in failed_servers:
                print reboot_thread.name," is rebooted"

        if failed_servers:
            logger.debug("Following are servers that failed to reboot:")
            for failed_server in failed_servers:
                logger.debug(failed_server)

        #Wait for all servers to be up and running with all internal tasks
        time.sleep(30)

        temp = set(failed_servers)
        failed_servers = list(failed_servers)
        return failed_servers

    '''
    Created on 25 Oct, 2016
    @author: Abhishek
    '''

    @staticmethod
    def _reboot_server(system_info, failed_servers):

        """
        This function is executed by each thread which is created by parent thread "reboot_servers".
        Based on type of host opens connection to host and executes reboot command on each.
        Then waits for the server to shutdown and come up again.
        """

        logger.debug("rebooting_server:%s"%(system_info['host']))

        if system_info['type'] in ('LINUX', 'VMWARE'):
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(system_info['host'], username=system_info['username'], password=system_info['password'])
                stdin, stdout, stderr = client.exec_command('reboot')
                client.close()
            except:
                print "unable to reboot %s"%(system_info['host'])
                failed_servers.append(system_info['host'])
                return  -1

        elif system_info['type'] in ('WINDOWS'):
            try:
                CoInitialize()  #Needs to be called when making multiple windows connections from a thread using wmi module
                connection = wmi.WMI(system_info['host'], user=system_info['username'], password=system_info['password'])
                (pid, status) = connection.Win32_Process.Create(CommandLine="shutdown -r", CurrentDirectory='.')
                print pid,status," from %s"%(system_info['host'])
            except Exception as ex:
                if ex.com_error:
                    failed_servers.append(system_info['host'])
                print "Unable to reboot %s"%(system_info['host'])
            except wmi.x_wmi:
                failed_servers.append(system_info['host'])
                print "Your Username and Password for %s are wrong."%(system_info['host'])
                return  -1
            except:
                failed_servers.append(system_info['host'])
                print "Unable to reboot %s"%(system_info['host'])
                return  -1

        # Wait for server to be down
        timeout = 300
        while True:
            timeout -= 1
            response = os.system("ping -n 1 %s > nul 2>&1" %(system_info['host']) )
            if response == 0:
                if timeout <= 0:
                    failed_servers.append(system_info['host'])
                    logger.debug("%s failed to reboot after issuing reboot command"%(system_info['host']))
                    return -1
            else:
                break
            time.sleep(1)

        timeout = 600
        # Wait for server to be up
        while True:
            timeout -= 1
            response = os.system("ping -n 1 %s > nul 2>&1" %(system_info['host']) )
            if response != 0:
                if timeout <= 0:
                    failed_servers.append(system_info['host'])
                    logger.debug("%s failed to come up after reboot"%(system_info['host']))
                    return -1
            else:
                break
            time.sleep(1)
        return 0
