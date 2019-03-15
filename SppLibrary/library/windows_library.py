import _wmi
import _wnet
import os
import time
import logging
import collections
import subprocess
import threading
import re
from subprocess import PIPE
from _wmi import WMI_ERROR_DEFINITION

logger = logging.getLogger('SppLibrary.library')
fh = logging.FileHandler('library.log')
formatter = logging.Formatter('%(asctime)s - %(filename)s -%(funcName)s - %(lineno)d - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)

class WMILibrary(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def __init__(self):
        self.parameters = {}
        self.host = None
        self.username = None
        self.password = None
        self.wmi_connection = None
        self.wnet_connection = None

    def get_hostname(self):
        return self.host

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def open_connection(self, host=None, username=None, password=None):
        self.host = host
        self.username = username
        self.password = password
        self.wmi_connection = _wmi.WMI(self.host,self.username,self.password)
        self.wnet_connection = _wnet.Wnet(self.host,self.username,self.password)
        self.parameters[self.host] = {  'username':self.username, 
                                        'password':self.password, 
                                        'wmi_connection':self.wmi_connection, 
                                        'wnet_connection':self.wnet_connection
                                    }
        

    def switch_connection(self, host):
        self.host = host
        self.username = self.parameters[self.host]['username']
        self.password = self.parameters[self.host]['password']
        self.wmi_connection = self.parameters[self.host]['wmi_connection']
        self.wnet_connection = self.parameters[self.host]['wnet_connection']
        logger.debug('Switched connection to %s'%(self.host))

    def _start_command_wmi(self, command, cwd):
        (pid, status) = self.wmi_connection.wmi_execute_command(command, cwd)
        
        if not pid:
            raise AssertionError(WMI_ERROR_DEFINITION[status])

        return (pid, status)

    def start_command(self, command, cwd='.'):
        logger.info('Command: %s cwd: %s'%(command, cwd))
        (pid, status) = self._start_command_wmi(command, cwd)

        return (pid, status)

    def execute_command(self, command, timeout, cwd='.'):
        logger.info('Command: %s cwd: %s'%(command, cwd))
        (pid, status) = self.wmi_connection.wmi_execute_command(command, cwd)
        if not pid:
            raise AssertionError(WMI_ERROR_DEFINITION[status])

        self.wait_for_process_exit(pid, timeout)

    def _start_command_psexec(self, command):
        cmd = ['psexec.exe', '/accepteula',
                r'\\' + self.host,
               '-u', self.username,
               '-p', self.password,
               '-d', '-i',
               'cmd', r'/c']
        cmd.append(command)
        logger.debug(cmd)
        try:
            p = subprocess.Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=subprocess.STDOUT, shell=True)
        except Exception as ex:
            raise AssertionError(ex.message)
        
        output = p.stdout.read()
        logger.debug(str(output))

        if not output:
            raise AssertionError('Psexec output is None')

        return output

    def start_command_psexec(self, command):
        logger.info('Command: %s'%(command))
        output = self._start_command_psexec(command)
        pid = self._get_pid_psexec(str(output))
        return pid

    def execute_command_psexec(self, command, timeout):
        logger.info('Command: %s'%(command))
        output = self._start_command_psexec(command)
        pid = self._get_pid_psexec(str(output))
        self.wait_for_process_exit(pid, timeout)

    def _get_pid_psexec(self, output):
        try:
            return re.search(r'process ID (\d+).', output).group(1)
        except:
            raise AssertionError('Could not retrieve the PID from the text')

    def get_operating_system_name(self):
        os_type = self.wmi_connection.wmi_operating_system()[0]
        return os_type.caption + os_type.OSArchitecture

    def get_pid(self, process_name):
        process_list = self.wmi_connection.wmi_get_process()
        for (pid, name) in process_list:
            if process_name in name:
                return pid

    def wait_for_process_exit(self, process, timeout):
        ''' Wait for a process to exit within timeout else
            raise and exception.
            process - Process ID
            timeout - In seconds.
        '''
        time_taken = 0
        process_exist = True

        for i in range(int(timeout)):
            start_time = time.time()
            process_list = self.wmi_connection.wmi_get_process()
            end_time = time.time()

            time_taken += end_time - start_time

            if not [i for (i,n) in process_list if int(i) == int(process) ]:
                process_exist = False
                break

            if (int(timeout) - time_taken < 0) or not process_exist:
                process_list = self.wmi_connection.wmi_get_process()
                if not [i for (i,n) in process_list if int(i) == int(process) ]:
                    process_exist = False
                break
        
        logger.debug(time_taken)
        
        if process_exist:
            raise AssertionError('Process did not exit')


    def get_file(self, src, dst='.'):
        self.wnet_connection.wnet_get_file(src, dst)

    def put_file(self, src, dst):
        self.wnet_connection.wnet_put_file(src, dst)

    def get_mounted_drive(self):
        drive = self.wmi_connection.wmi_get_mounted_disk()
        return drive

    def move_file(self, source, destination):
        command = r'cmd.exe /c move /Y %s %s' %(source, destination)
        logger.debug(command)
        self.wmi_connection.wmi_execute_command(command)

    def remove_dir(self, dir):
        command = r'cmd.exe /c rmdir /S /Q %s' %(dir)
        logger.debug(command)
        self.wmi_connection.wmi_execute_command(command)

    def file_should_exist(self, path):
        if ':' not in path:
            raise TypeError('Absolute Path needed')

        querystring = "Select * From CIM_DataFile WHERE Name = '%s'"
        logger.debug(querystring)
        formatted_query = querystring %(path)

        ret = self.wmi_connection.wmi_query(formatted_query)

        if not ret:
            raise AssertionError('File Not Found')

    '''
    Created on 20 Oct, 2016
    @author: Sriram
    '''
    def folder_should_exist(self, path):
        ''' Checks if directory is present on SUT or not.'''
        if ':' not in path:
            raise TypeError('Absolute Path needed')

        querystring = "Select * From Win32_Directory Where Name = '%s'"
        logger.debug(querystring)
        formatted_query = querystring %(path)

        ret = self.wmi_connection.wmi_query(formatted_query)

        if ret:
            return True
        else:
            return False

    def list_files_in_directory(self, path, drive):
        ''' Returns the list of tuple containing the file name and size '''
        querystring = "Select * From CIM_DataFile WHERE Path = '%s' AND Drive = '%s'" % (path, drive)
        logger.debug(querystring)
        resultset = self.wmi_connection.wmi_query(querystring)
        return [(str(file.filename), int(file.FileSize)) for file in resultset]

    def get_device_manager_info(self):
        querystring = "Select * from Win32_PnPEntity WHERE ConfigManagerErrorCode <> 0"
        logger.debug(querystring)
        return self.wmi_connection.wmi_query(querystring)

    def get_event_logs(self, log_file, log_type):
        querystring = "SELECT * FROM Win32_NTLogEvent WHERE Logfile = '%s' AND Type = '%s'" % (log_file, log_type)
        logger.debug(querystring)
        return self.wmi_connection.wmi_query(querystring)
    
    def get_driver_details(self):
        querystring = "SELECT * FROM Win32_PnPSignedDriver"
        return self.wmi_connection.wmi_query(querystring)

    def get_services(self):
        return self.wmi_connection.wmi_get_service()

    def get_installed_programs(self):
        return self.wmi_connection.wmi_get_programs()  
   
    '''
    Created on June 1, 2015
    @author: Sriram
    This needs rework. Generalise function list files in directory and add keyword get file size.
    '''
    def get_file_names(self, path, drive, file_type):
        path = str(path)
        type = str(file_type)
        query_string = "Select * from CIM_DataFile WHERE Path = '%s' AND Drive = '%s' AND Extension = '%s'" % (path, drive, file_type)
        logger.debug(query_string)
        output = self.wmi_connection.wmi_query(query_string)
        files = []
        for item in output:
            logger.debug(str(item.Name))
            files.append(item.Name)
        return files

    '''
    Created on 20 July, 2016
    @author: Chinmaya Kumar Dash
    '''
    def connect_to_share_path(self):
        '''
        Establish a share connection.

        Example:
        | Connect To Share Path |
        '''
        self.wnet_connection.connect()

    def disconnect_from_share_path(self):
        '''
        Destroy a share connection.

        Example:
        | Disconnect From Share Path |
        '''
        self.wnet_connection.disconnect()