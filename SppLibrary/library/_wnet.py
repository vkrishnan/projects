"""
This library is used for wnet connections.
"""
import win32wnet
import os
import glob
import shutil
import logging

logger = logging.getLogger('SppLibrary.library')
logger.setLevel(logging.DEBUG)

class Wnet(object):
    """
    WNet APIs provide Windows networking (WNet) functions that allow
    networking capabilities for applications. Also known as the Win32 APIs,
    applications that are created by using Wnet APIs function independently
    from the network on which they operate. By using WNet APIs, applications
    can be developed that run successfully on all platforms while still able
    to take advantage of unique features and capabilities of any particular
    platform
    """
    def __init__(self, host, username, password):
        """
        Initialize the connection parameter.
        """
        self.host = host
        self.username = username
        self.password = password
        self.retry = 5

    '''
    @author:Vinay Krishnan
    '''
    def connect(self):
        """
        Open a WNET connection to a remote server if any exception
        occures Disconnect previous connections if detected, and reconnect.
        """
        self.unc = ''.join(['\\\\', self.host])
        logger.debug(self.unc)
        retry = self.retry
        while retry:
            try:
                win32wnet.WNetAddConnection2(0, None, self.unc, None, self.username, self.password)
                logger.debug("wnet connection successful")
                break
            except Exception as err:
                retry -= 1
                logger.debug('Exception: retrying connection')
                if isinstance(err, win32wnet.error):
                    # Disconnect previous connections if detected, and reconnect.
                    if err[0] == 1219:
                        logger.debug('Connection error 1219')
                        try:
                            win32wnet.WNetCancelConnection2(self.unc, 0, 0)
                            win32wnet.WNetAddConnection2(0, None, self.unc, None, self.username, self.password)
                        except:
                            logger.debug('Either cancel connection or create connection failed')
                            continue
                if retry:
                    logger.debug('Retrying %s time' %(str(self.retry - retry)))
                    continue

                logger.debug(str(err))
                raise AssertionError('Unable to establish connection')

    '''
    @author:Chinmaya Kumar Dash
    '''
    def disconnect(self):
        """
        Close a WNET connection from a remote server.
        """
        win32wnet.WNetCancelConnection2(self.unc, 0, 0)

    '''
    @author:Vinay Krishnan
    '''
    def handle_connection(func):
        """
        Decorator: Reestablish the WNET connection if Connection is lost.
        """
        def wrapper(*args, **kwargs):
            self = args[0]
            try:
                self.connect()
                logger.debug("Calling function: %s" %(func.func_name))
                func(*args, **kwargs)
                self.disconnect()
            except:
                logger.debug("Connecting")
                self.connect()
                func(*args, **kwargs)
        return wrapper

    '''
    @author:Vinay Krishnan
    '''
    def _copy_files(self, src, dst):
        """
        private function: copy the file from the remote server.
        If Destination directory is not exist then create
        the directory and copy the file.
        """
        if not os.path.exists(dst):
            logger.debug('Destination directory does not exist')
            os.makedirs(dst)
        else:           # File exists but not directory
            if not os.path.isdir(dst):
                shutil.rmtree(dst)
                logger.debug('Creating destination directory: %s' %(dst))
                os.makedirs(dst)

        for file in glob.glob(src):
            logger.info('Copying file: %s' %(file))
            shutil.copy(file, dst)

    '''
    @author:Vinay Krishnan
    '''
    @handle_connection
    def wnet_get_file(self, src, dst):
        """
        Copy the file from remote source to local destination.
        """
        src = ''.join(['\\\\', self.host, '\\', src.replace(':', '$')])
        logger.debug('Source: %s, destination: %s' %(src, dst))
        self._copy_files(src, dst)

    '''
    @author:Vinay Krishnan
    '''
    @handle_connection
    def wnet_put_file(self, src, dst):
        """
        Copy the file from local source to remote destination.
        """
        dst = ''.join(['\\\\', self.host, '\\', dst.replace(':', '$')])
        logger.debug('Source: %s, destination: %s' %(src, dst))
        self._copy_files(src, dst)
