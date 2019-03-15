"""
Library for establishing connection and executing wmi commands.
"""

import wmi
import logging
import traceback
import os

logger = logging.getLogger('SppLibrary.library')
logger.setLevel(logging.DEBUG)

WMI_ERROR_DEFINITION = {0: 'Successful Completion',
                        2: 'Access Denied',
                        3: 'Insufficient Privilege',
                        8: 'Unknown failure',
                        9: 'Path Not Found',
                        21: 'Invalid Parameter'}

class WMI(object):
    """
    Windows Management Instrumentation (WMI) is the infrastructure for
    management data and operations on Windows-based operating systems.
    You can write WMI scripts or applications to automate administrative
    tasks on remote computers but WMI also supplies management data to
    other parts of the operating system and products, for example System
    Center Operations Manager, formerly Microsoft Operations Manager (MOM),
    or Windows Remote Management (WinRM).
    """
    def __init__(self, host, username, password):
        """
        Initialize the connection parameter.
        """
        self.host = host
        self.username = username
        self.password = password
        self.connection = None
        self.retry = 5
        logger.debug('Initialize parameters: %s, %s, %s'%(host, username, password))

    '''
    @author:Vinay Krishnan
    '''
    def _connect(self):
        """
        private function: Open a WMI connection to a remote server.
        """
        retry = self.retry
        while retry:
            try:
                self.connection = wmi.WMI(self.host,user=self.username,password=self.password)
            except Exception, err:
                logger.debug(traceback.print_exc())
                retry -= 1
                logger.debug("Exception: ping output")
                for i in range(10):
                    logger.debug(os.system("ping -n 1 %s > nul 2>&1" %(self.host)))
                
                if retry:
                    logger.debug('Retrying %s time' %(str(self.retry - retry)))
                    continue
                
                raise AssertionError('Connection Error: check for credentials and ip address')
            else:
                logger.info('Connection successful')
                return self.connection

    '''
    @author:Vinay Krishnan
    '''
    def _retry(f):
        """
        Decorator: Establish connection and execute function if no connection is already established or lost.
        """
        def wrapped(*args, **kwargs):
            self = args[0]
            try:
                logger.debug("Calling function: %s" %(f.func_name))
                ret = f(*args, **kwargs)
            except:
                logger.debug("Connecting")
                self.connection = self._connect()
                try:
                    ret = f(*args, **kwargs)
                except Exception as ex:
                    logger.debug(ex.message)
                    raise AssertionError("Error executing: %s" %(f.func_name))
            
            return ret
        
        return wrapped

    '''
    @author:Chinmaya Kumar Dash
    '''
    @_retry
    def wmi_get_mounted_disk(self):
        """
        Returns the list of tuple of mounted drive letter, caption and name.

        Example:
        drive = [(u'C:', u'Local Fixed Disk', u''),(u'D:', u'CD-ROM Disc', u'SPP2016100')]
        """
        drive = []
        for disk in self.connection.Win32_CDROMDrive():
            drive.append((disk.Drive, disk.Caption, disk.VolumeName))
        for disk in self.connection.Win32_LogicalDisk():
            drive.append((disk.Caption, disk.Description, disk.VolumeName))
        return drive

    '''
    @author:Chinmaya Kumar Dash
    '''
    @_retry
    def wmi_get_process(self):
        """
        Return the list of tuple of running process id and process caption.
        Example:
        processes = [(0, u'System Idle Process'), (4, u'System')]
        """
        processes = []        
        for process in self.connection.Win32_Process():
            processes.append((process.ProcessId, process.Caption))
        return processes

    '''
    @author:Chinmaya Kumar Dash
    '''
    @_retry
    def wmi_get_service(self):
        """
        Return the list of tuple of service and service state.
        Example:
        services = [(u'Adobe Acrobat Update Service', u'Running'),
        (u'Adobe Flash Player Update Service', u'Stopped')]
        """
        services = []
        for service in self.connection.Win32_Service():
            services.append((service.displayName,service.State))
        return services

    '''
    @author:Vinay Krishnan
    '''
    @_retry
    def wmi_execute_command(self,command,cwd='.'):
        """
        Create a process on remote machine to Execute the command
        and return the pid and status of that process.

        Note: Start the process and return without wait.
        """
        pid, status = self.connection.Win32_Process.Create(CommandLine=command, \
                                                        CurrentDirectory=cwd)

        if not pid:
            raise AssertionError(WMI_ERROR_DEFINITION[status])

        return pid,status

    '''
    @author:Vinay Krishnan
    '''
    @_retry
    def wmi_query(self,query_string):
        """
        Execute a wmi query and return the result as object.
        """
        return self.connection.query(query_string)

    '''
    @author:Vinay Krishnan
    '''
    @_retry
    def wmi_operating_system(self):
        """
        Return a object which will contain all information about operating system.
        Example:
        connection.Win32_OperatingSystem()[0].Caption = u'Microsoft Windows 7 Enterprise'
        connection.Win32_OperatingSystem()[0].OSArchitecture = u'64-bit'
        """
        return self.connection.Win32_OperatingSystem()

    '''
    @author:Vinay Krishnan
    '''
    @_retry
    def wmi_get_programs(self):
        """
        Return a object which will contain all information about installed programs.
        Example:
        connection.Win32_Product()[1].Caption = u'Microsoft Office Professional Plus 2013'
        connection.Win32_Product()[2].Caption = u'Microsoft OneNote MUI (English) 2013'
        """
        return self.connection.Win32_Product()
