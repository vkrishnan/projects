import os
import logging
import glob
import sys
import wmi
import urllib2
import re
logger = logging.getLogger('SppLibrary.library')
logger.setLevel(logging.DEBUG)

class Common(object):

    """
    This Contains all the common keywords required for SPP Automation. These Keywords Doesn't depends on SUT, it will execute on RG.
    """

    def __init__(self):
        pass

    '''
    @author:Vinay Krishnan
    '''
    def get_firefox_profile(self, profile_template):
        """
        Fetches the firefox profile from the template path provided in profile_template.

        profile_template - Defined in variables.py

        Example:
        | Get Firefox Profile | C:\Users\%s\AppData\Roaming\Mozilla\Firefox\Profiles |
        """
        user = os.popen(r'whoami').read().strip().split('\\')[1].capitalize()
        logger.debug('username:' + user)
        logger.debug('profile_template:' + profile_template)
        profile_dir = profile_template % (user)
        logger.debug('profile dir:' + profile_dir)

        try:
            os.chdir(profile_dir)
            profile_name = glob.glob('*.default')[0]
        except Exception as ex:
            raise AssertionError("Could not fetch the firefox profile: %s" %(ex.message))

        complete_path = profile_dir + '\\' + profile_name
        return complete_path

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
        logger.debug(command_template)
        if args:
            return command_template % (args)
        else:
            return command_template

    '''
    @author:Vinay Krishnan
    '''
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
    Created on Jan 7, 2016
    @author: Sriram Chowdary
    '''
    def replace_string_in_file(self, file_path, replace_dict):
        """
        Finds and replaces key in dictionary with value.

        file_path - file name of the file whose macro substitution has to be done

        replace_dict - dictionary whose keys have to replaced with values in file_path.

        Example:
        | Replace String In File | file_path | replace_dict |
        """

        # Converting keys from unicode to str as robot sends unicode
        replace_dict = dict((str(key).strip(), str(replace_dict[key]).strip()) for key in replace_dict)
        logger.debug('Replace dict' + str(replace_dict))

        # Creating a temporary file with name preprended with '_temp'
        path, script_name = os.path.split(file_path)
        filename, ext = os.path.splitext(script_name)
        temp_file = os.path.join(path, filename + '_temp' + ext)
        logger.debug('Temp file is ' + temp_file)

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
    Created on Nov 27, 2015
    @author: Vinay Krishnan
    '''
    def get_RG_root(self):
        """
        Returns the RG root Path.

        Example:
        | Get RG Root |
        """
        path = os.path.realpath(__file__)
        logger.debug(path)
        return "\\".join(path.split("\\")[0:3])

    '''
    Created on Nov 27, 2015
    @author: Vinay Krishnan
    '''
    def re_match(self, re_str, match_str):
        """
        Returns matched regular expression pattern

        Example:
        | Re Match | re_str | match_str |
        """
        if not match_str:
            return match_str
        try:
            return re.match(str(re_str), match_str).group(1)
        except:
            raise AssertionError("Error in matching regular expression pattern")

    '''
    Created on 25 May, 2016
    @author: Sriram Chowdary
    '''
    def download_file_from_http_server(self, url, dow_path):
        """
        Download ssp image from web server using http URL

        url - image location on web.

        dow_path - location where file will download

        Example:
        | Download File From Http Server | url | dow_path |
        """
        proxy_handler = urllib2.ProxyHandler({})
        opener = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener)

        filename = url.split('/')[-1].strip()
        logger.debug(dow_path + filename)

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
        """
        Kill hpsum process on rg server.

        Example:
        | Kill Hpsum Process RG |
        """
        c = wmi.WMI ()
        for process in c.Win32_Process():
            if 'hpsum_service' in process.caption:
                return process.ProcessId