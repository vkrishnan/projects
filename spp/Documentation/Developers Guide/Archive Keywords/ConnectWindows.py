'''
This module contains functions that connects to the Windows Server
'''

ROBOT_LIBRARY_VERSION = '0.1'
__version__ = ROBOT_LIBRARY_VERSION

import wmi
import time
import logging
import sys
import string
import win32wnet
import os
import glob
import shutil

# Error codes fetched from the following location
# http://msdn.microsoft.com/en-us/library/aa389388(v=vs.85).aspx
WMI_ERROR_DEFINITION = {0: 'Successful Completion',
                        2: 'Access Denied',
                        3: 'Insufficient Privilege',
                        8: 'Unknown failure',
                        9: 'Path Not Found',
                        21: 'Invalid Parameter'}

logger = logging.getLogger('ConnectWindows')
fh = logging.FileHandler('connect_windows.log')
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

fh.setFormatter(formatter)

logger.addHandler(fh)
logger.setLevel(logging.INFO)


class ConnectWindows(object):

    '''
         Class contains functions that connects to Windows Server
    '''
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, retry=5):
        '''
             Initialize the connection retry parameter
        '''
        self.retry = retry
        logger.info('--------------------------------------------')
        logger.info('Logging started at: ' + time.ctime())
        logger.info('--------------------------------------------')

    def connect_windows(self, host, username, password):
        """ Establishes a wmi connection to the Windows computers and returns the connection object.

        Example:
        | Connect Windows | 172.20.56.42 | Administrator | Compaq123 |
        """
        self.host = host
        self.username = username
        self.password = password
        logger.info('Connecting with credentials: %s, %s, %s' % (host, username, password))
        for i in range(self.retry):
            try:
                self.connection = wmi.WMI(
                    self.host,
                    user=self.username,
                    password=self.password)
                logger.info('Connection is ' + str(self.connection))
                return self.connection
            except:
                if i == self.retry - 1:
                    raise AssertionError("Connection to remote server failed, check for host name, credentials or connection to remote computer")
                continue

    def is_image_mounted_windows(self, image_location):
        """ Checks if SPP image is mounted on the CD drive and returns its status.

        image_location - Network path to the SPP image.

        Returns True if SPP image is mounted else returns False

        Example:
        | Is Image Mounted Windows | http://172.20.59.221/Snap3/Build85/SPPGen9Snap3.2015_0403.85.iso |
        """
        drive_type = 5  # 5 -> Compact Disc
        for drive in self.connection.Win32_LogicalDisk():
            if drive.DriveType == drive_type and drive.VolumeName is not None and image_location.find(drive.VolumeName) != -1:
                logger.info('Image is mounted')
                return True
        logger.info('Image is not mounted')
        return False

    def get_mounted_drive_letter(self, timeout, image_location):
        """ Returns the mounted drive letter where SPP image is mounted.

        timeout - maximum time to wait to retrieve the drive letter.
        image_location - Network path to the SPP image.

        Returns the drive letter if image is mounted else raises an AssertionError.

        Example:
        | Get Mounted Drive Letter | http://172.20.59.221/Snap3/Build85/SPPGen9Snap3.2015_0403.85.iso |
        """
        drive_type = 5  # 5 -> Compact Disc
        timeout = int(timeout)
        time.sleep(5)
        for _ in range(timeout):
            time.sleep(1)
            for drive in self.connection.Win32_LogicalDisk():
                if drive.DriveType == drive_type and drive.VolumeName is not None and image_location.find(drive.VolumeName) != -1:
                    logger.info('Mounted drive letter is: ' + drive.Caption)
                    logger.info('Mounted drive VolumeName is: ' + drive.VolumeName)
                    time.sleep(30)
                    query_string = "Select * From CIM_Datafile Where Name = '%s\\hp\\swpackages\\hpsum.bat'" % (drive.Caption)
                    if len(self.connection.query(query_string)) > 0:
                        return drive.Caption
        raise AssertionError("Could not retrieve the mounted drive letter")

    def start_hpsum_on_windows(self, command, timeout, cwd='.'):
        """ Starts hpsum command and waits until the service is started
            on the remote computer until timeout occurs.

        Example:
        | Start Hpsum On Windows | D:\hp\swpackages\hpsum.bat /s /use_snmp /use_wmi | 60 |
        """
        logger.info('command executing is ' + command)
        pid, status = self.connection.Win32_Process.Create(CommandLine=command, CurrentDirectory=cwd)
        if not pid:
            raise AssertionError(WMI_ERROR_DEFINITION[status])

        timeout = int(timeout)

        for _ in range(timeout):
            time.sleep(1)
            for process in self.connection.Win32_Process():
                if 'hpsum_service' in process.caption:
                    return process.ProcessId
        return False

    def reboot_windows(self):
        """ Reboots a remote computer.

        Example:
        | Reboot Windows |
        """
        self.connect_windows(self.host, self.username, self.password)
        command = r'cmd.exe /c shutdown -r'
        pid, status = self.connection.Win32_Process.Create(CommandLine=command)
        if not pid:
            raise AssertionError(WMI_ERROR_DEFINITION[status])

    def kill_process_windows(self, pid=None, process_name=None):
        """Kills the process with either pid or process name.

        pid - pid of the process to be killed.
        process_name - if process must be killed using process name
                       it should be passed as a named parameter.

        Example:
        | Kill Process Windows | 2342 | Kills the process with pid = 2342 |
        | Kill Process Windows | process_name=notepad.exe | Kills the notepad.exe process |
        """
        if not pid and not process_name:
            raise AssertionError('Please specify pid or process_name to kill')
        if pid:
            command = r'taskkill /pid %s /f' % (str(pid))
        else:
            command = r'taskkill /im %s /f' % (str(process_name))
        logger.info('Kill Process with command ' + command)
        pid, status = self.connection.Win32_Process.Create(CommandLine=command)
        if not pid:
            raise AssertionError(WMI_ERROR_DEFINITION[status])

    def file_should_exist_on_remote_windows(self, filename):
        """Checks if a file exists on the remote computer.

        filename should always be the absolute path on the remote computer.
        Directories do not work.

        Example:
        | File Should Exist On Remote Windows | C:\\dev\\spp\\tests\\hpsum_log.txt |
        """
        query_string = "Select * From CIM_Datafile Where Name = '%s'" % (filename)
        logger.info('Query String: %s' % (query_string))
        if len(self.connection.query(query_string)) < 1:
            raise AssertionError('File Not Found')

    def wait_until_file_is_created(self, filename, timeout):
        """ Waits until file gets created on the remote computer until timeout seconds occurs.

        Example:
        | Wait Until File Is Created | C:\\dev\\spp\\tests\\hpsum_log.txt | 10 |
        """
        timeout = int(timeout)
        query_string = "Select * From CIM_Datafile Where Name = '%s'" % (filename)
        logger.info("File query string is " + query_string)
        for i in range(timeout):
            if len(self.connection.query(query_string)) < 1:
                time.sleep(1)
                continue
            logger.info("File %s does exist" % (filename))
            return
        raise AssertionError("File %s does not exist" % (filename))

    def execute_windows_command_and_wait(self, command, timeout, cwd='.'):
        """ Executes command on remote windows computer and waits until the command exits
            or until timeout occurs.

        Example:
        | Execute Windows Command And Wait | D:\hp\swpackages\hpsum.bat | 60 |
        """
        logger.info('command executing is ' + command)
        pid, status = self.connection.Win32_Process.Create(CommandLine=command, CurrentDirectory=cwd)
        logger.info('Process started with pid ' + str(pid))
        if not pid:
            raise AssertionError(WMI_ERROR_DEFINITION[status])

        timeout = int(timeout)

        def loop_until_process_exit():
            '''
                This function checks the processes in remote server
                and returns True if it does not exist and False if it exists
            '''
            for _ in range(self.retry):
                try:
                    for process in self.connection.Win32_Process():
                        if pid == process.ProcessId:
                            return False
                    logger.info('Process does not exist: Exit')
                    return True
                except wmi.x_wmi:
                    logger.info('Exception: Reconnecting')
                    self.connect_windows(self.host, self.username, self.password)
                    continue
            raise AssertionError("Could not establish connection \
                                        with remote computer")

        for _ in range(timeout):
            time.sleep(1)
            ret = loop_until_process_exit()
            if ret:
                return
        raise AssertionError("Installation process did not exit even after timeout")

    def get_resource_directory(self, source):
        return source[:source.rindex('\\')] + '\\resource'

    def move_log_files_to_temp_directory_windows(self, log_location):
        """ Moves the following files to the temporary directory on the remote computer
            C:\\Users\\Administrator\\AppData\\Local\\Temp\\temp

            1. C:\\Users\\Administrator\\AppData\\Local\\Temp\\HPSUM_Logs_*.zip

            2. C:\\Users\\Administrator\\AppData\\Local\\Temp\\HPSUM

            3. C:\\Users\\Administrator\\AppData\\Local\\Temp\\localhpsum

            4. C:\\cpqsystem\\hp\\log\\${log_location}\\hpsum*


        Example:
        | Move Log Files To Temp Directory Windows | localhost |
        """
        timeout = 5
        tmp_dir = r'C:\\Users\\%s\\AppData\\Local\\Temp' % (self.username)
        logger.info('Temporary directory is ' + tmp_dir)
        cmd = r'cmd.exe /c mkdir %s\\temp' % (tmp_dir)
        self.execute_windows_command_and_wait(cmd, timeout)
        cmd = r'cmd.exe /c move /Y %s\\HPSUM_Logs_*.zip %s\\temp' % (tmp_dir, tmp_dir)
        self.execute_windows_command_and_wait(cmd, timeout)
        cmd = r'cmd.exe /c move /Y %s\\HPSUM %s\\temp' % (tmp_dir, tmp_dir)
        self.execute_windows_command_and_wait(cmd, timeout)
        cmd = r'cmd.exe /c move /Y %s\\localhpsum %s\\temp' % (tmp_dir, tmp_dir)
        self.execute_windows_command_and_wait(cmd, timeout)
        log_dir = r'C:\\cpqsystem\\hp\\log\\%s\\' % (log_location)
        logger.info('Log directory is ' + log_dir)
        cmd = r'cmd.exe /c move  /Y %s\\hpsum* %s\\temp' % (log_dir, tmp_dir)
        self.execute_windows_command_and_wait(cmd, timeout)

    def remove_deploy_preview_win(self):
        '''
            Remove cpqsystem folder after generating second deploy preview report
        '''
        timeout = 5
        cmd = r'cmd.exe /c rmdir /S /Q C:\\cpqsystem'
        self.execute_windows_command_and_wait(cmd, timeout)

    def clean_logs_windows(self):
        """ Deletes the following files from the remote computer.

            1. C:\\cpqsystem

            2. C:\\Users\\Administrator\\AppData\\Local\\Temp\\localhpsum

            3. C:\\Users\\Administrator\\AppData\\Local\\Temp\\HPSUM

            4. C:\\Users\\Administrator\\AppData\\Local\\Temp\\HPSUM_Logs_*.zip
           
            5. C:\\Users\\Administrator\\AppData\\Local\\Temp\\temp
            
            6. C:\\Users\\Administrator\\AppData\\Local\\Temp\\enter.txt

        Example:
        | Clean Logs Windows |
        
        Modified on 1 April, 2016
        @author: Rahul Verma
        """
        timeout = 5
        tmp_dir = r'C:\Users\%s\AppData\Local\Temp' % (self.username)
        logger.info('Temporary directory is ' + tmp_dir)
        cmd = r'cmd.exe /c rmdir /S /Q C:\\cpqsystem %s\\localhpsum %s\\HPSUM %s\\temp' % (tmp_dir, tmp_dir, tmp_dir)
        self.execute_windows_command_and_wait(cmd, timeout)
        cmd = r'cmd.exe /c del %s\HPSUM_*.zip %s\\enter.txt' % (tmp_dir, tmp_dir)
        self.execute_windows_command_and_wait(cmd, timeout)

    def connect_copy(self):
        """ Function used by W2W_Copy to establish a win32wnet connection
            before copying the files.

        Example:
        | self.connect_copy | This function should be called by W2W_Copy to establish a connection |
        """
        unc = ''.join(['\\\\', self.host])
        try:
            win32wnet.WNetAddConnection2(0, None, unc, None, self.username, self.password)
        except Exception as err:
            if isinstance(err, win32wnet.error):
                # Disconnect previous connections if detected, and reconnect.
                if err[0] == 1219:
                    win32wnet.WNetCancelConnection2(unc, 0, 0)
                    return self.connect_copy()
            raise err

    def W2W_Copy(self, src, dst, to_sut=u'False'):
        """ Copies files or directories to a from remote computer
            and RG server.

            src - Source files/directory

            dst - Destination directory.

            If to_sut is True, file is copied from RG server to SUT,
            else from SUT to RG server.

        Example:
        | W2W_Copy | C:\\cpqsystem\\hp\\log\\${LOG_LOCATION}\\hpsum_detail_log.txt | .\\${LOG_PATH} |
        """

        self.connect_copy()
        if eval(to_sut):
            logger.info('To SUT file %s' % (src))
            dst = ''.join(['\\\\', self.host, '\\', dst.replace(':', '$')])
            logger.info('Destination is %s' % (dst))
        else:
            logger.info('From SUT file %s ' % (src))
            src = ''.join(['\\\\', self.host, '\\', src.replace(':', '$')])
            logger.info('Source is %s' % (src))

        # Create the destination dir if its not there.
        if not os.path.exists(dst):
            logger.info('Destination does not exist, creating')
            os.makedirs(dst)
        else:
            if not os.path.isdir(dst):
                logger.info('Destination not a directory, hence deleting and creating')
                shutil.rmtree(dst)
                os.makedirs(dst)

        # Add glob module to handle wildcards for gatherlogs package
        for file in glob.glob(src):
            shutil.copy(file, dst)
        time.sleep(2)

    def Wait_for_psexec_process(self, timeout, pid):
        #logger.info('command executing is ' + command)
        #pid, status = self.connection.Win32_Process.Create(CommandLine=command, CurrentDirectory=cwd)
        logger.info('Process started with pid ' + str(pid))
        pid = int(pid)
        if not pid:
            raise AssertionError(WMI_ERROR_DEFINITION[status])

        timeout = int(timeout)

        def loop_until_process_exit():
            '''
                This function checks the processes in remote server
                and returns True if it does not exist and False if it exists
            '''
            for _ in range(self.retry):
                try:
                    for process in self.connection.Win32_Process():
                        if pid == process.ProcessId:
                            return False
                    logger.info('Process does not exist: Exit')
                    return True
                except wmi.x_wmi:
                    logger.info('Exception: Reconnecting')
                    self.connect_windows(self.host, self.username, self.password)
                    continue
            raise AssertionError("Could not establish connection \
                                        with remote computer")

        for _ in range(timeout):
            time.sleep(1)
            ret = loop_until_process_exit()
            if ret:
                return
        raise AssertionError("Installation process did not exit even after timeout")

    '''
    Created on Mar 5, 2015 @author: girish devappa
    '''

    def PIV_hpsumlog_check(self):
        """ This function will verify HPSUM logs by doing a check for files 'node', 'inventory', 'deploy', 'hpsum_log',
            'hpsum_detail_log' on the file system of the host machine. Result would be logged to the file piv_connect_windows.log
        """
        working_directory_path = '\\Users\\Administrator\\AppData\\Local\\Temp\\temp\\hpsum\\localhost\\'
        file_types_list = ['node', 'inventory', 'deploy', 'hpsum_log', 'hpsum_detail_log']
        querystring = "Select * From CIM_DataFile WHERE Path = '%s' AND Drive = 'C:\'" % (working_directory_path)
        working_directory_file_list = []  # list of files queried from working_directory_path
        logger.info(querystring)
        resultset = self.connection.query(querystring)
        test_flag = True
        zero_size_files = []
        files_not_found = []

        for item in resultset:
            working_directory_file_list.append(str(item.filename))
            if item.filename in file_types_list:
                if int(item.FileSize) == 0:
                    test_flag = False
                    zero_size_files.append(item.filename)
                    logger.info(item.filename + " size is zero ")

        for sub_list_name in file_types_list:
            if sub_list_name not in working_directory_file_list:
                test_flag = False
                files_not_found.append(sub_list_name)
                #logger.info(sub_list_name + " file not found ")

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
    Modified on Jun 13, 2016
    @author: Kapil Chauhan
    '''

    def PIV_hpservice_check(self,server_type):
        """ The function will check if the required services like HP AMS Storage Service ,HP Insight Event Notifier,
            HP Insight Foundation Agents,HP Insight NIC Agents,HP Insight Server Agents,HP Insight Storage Agents,
            HP ProLiant Agentless Management Service,HP ProLiant Health Monitor Service, 
            HP ProLiant System Shutdown Service,HP Smart Array SAS/SATA Event Notification Service,
            HP Smart Update Tools,HP System Management Homepage ,HP WMI Storage Providers 
            are running or not in Proliant\Synergy servers. Result would be logged to the file piv_connect_windows.log. 
            HP Smart Update tool service is currently excluded as same is not supported in SNAP6. It might be supported
            in next release hence not removing the same.
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

        for item in self.connection.Win32_Service():
            flag = 0
            service_name = ''
            for service in service_list:
                if not len(set(service.split()) - set(item.displayName.split())):
                    flag = 1
                    service_name = service
                    break
            if flag and item.State == 'Running':
                service_dict[service_name] = 1
            elif (service in item.displayName) and (item.State == 'Stopped' or item.State == 'Disabled' or item.State == 'Paused'):
                service_dict[service_name] = 2

        logger.info('service_dict' + str(service_dict))
        return service_dict

    '''
    Created on Mar 20, 2015 @author: girish devappa
    Modified on Mar 31, 2016
    @author: Chinmaya kumar Dash
    '''

    def PIV_UninstallPrograms_check(self):
        """ This function will uninstall the progarms HP Lights-Out Online Configuration Utility,
            HP ProLiant Integrated Management Log Viewer, HP Smart Storage Administrator CLI,
            log data is appended to piv_connect_windows.log
        """
        programs_list = ["Lights-Out Online Configuration Utility", "Integrated Management Log Viewer", "Smart Storage Administrator CLI"]
        products = []

        for product in self.connection.Win32_Product():
            products.append(product.Name.strip())
        
        common_products = []
        missing_products = []
        
        for program in programs_list:
            for product in products:
                if program in product:
                    common_products.append(product)
                    break
            else:
                missing_products.append(program)
        
        logger.info('common_products' + str(common_products))
        logger.info('missing_products' + str(missing_products))

        for product in self.connection.Win32_Product():
            try:
                for program in programs_list:
                    if program in product.Name:
                        logger.info("uninstalling " + str(product.Name))
                        product.Uninstall()
                        break
            except:
                raise AssertionError("Failed to uninstall " + str(product.Name))
                
        if len(common_products) != len(programs_list):
            raise AssertionError("Programs Not Found: " + "\n".join(list(missing_products)))

    def Device_Manger_Info(self):
        """ Detects if there are any yellowbang in the Device manager of
            remote computer.
        """
        colItems = self.connection.ExecQuery("Select * from Win32_PnPEntity WHERE ConfigManagerErrorCode <> 0")
        yellowbanglst = []
        for objItem in colItems:
            desc = str(objItem.Description)
            if desc not in yellowbanglst and 'Mouse' not in desc and 'Keyboard' not in desc:
                yellowbanglst.append(objItem.Description)
                logger.info('Yellow bang item: ' + desc)
        if len(yellowbanglst) > 0:
            raise AssertionError(" Yellow bang items:   " + ','.join([i for i in yellowbanglst if i]))
    '''
    Created on Mar 31, 2016 @author: Chinmaya kumar Dash
    '''

    def WBEM_Check(self):
        """ Check whether WMI Storage Providers is present in the system
        """
        flag = 0
        for item in self.connection.Win32_Service():
            service_name = {'WMI Storage Providers'}
            for service in service_name:
                if not len(set(service.split()) - set(item.displayName.split())) and item.State == 'Running':
                    flag = 1
                    break
        return flag
