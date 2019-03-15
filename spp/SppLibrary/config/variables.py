# iLO Variables
ILO_IP = r''
ILO_USERNAME = r'Administrator'
ILO_PASSWORD = r'Compaq123'

# Http url path, Mount Type - Virtual\USB\DVD
HTTP_IMAGE_PATH = r''
SPP_MOUNT_TYPE = r'Virtual'

# System Variables
SYSTEM_IP = r''
SYSTEM_USERNAME = r'Administrator'
SYSTEM_PASSWORD = r'Compaq123'

# Remote Node Variables
REMOTE_NODE_IP = r''
REMOTE_NODE_USERNAME = r'Administrator'
REMOTE_NODE_PASSWORD = r'Compaq123'

# Onboard Administrator Variables
OA_IP = r''
OA_USERNAME = r'Administrator'
OA_PASSWORD = r'Compaq123'

# Virtual Connect Variables
VC_PRIMARY_IP = r''
VC_SECONDARY_IP = r''
VC_USERNAME = r'Administrator'
VC_PASSWORD = r'Compaq123'

# RG System Variables
RG_SYSTEM_USERNAME = r''
RG_SYSTEM_PASSWORD = r''

# Build Verification Variables
LEFT_IMAGE_PATH = r''
RIGHT_IMAGE_PATH = r''
IMAGE_SHARE_IP = r''
IMAGE_SHARE_USERNAME = r''
IMAGE_SHARE_PASSWORD = r''

SIGNATURE_BYPASS = r'True'

'''Fixed and common variables needed by script. No User Input Needed'''

# Temp directory for automation tools
SUT_TEMP_DIR_WINDOWS = r'C:\spp_automation_setup'
SUT_TEMP_DIR_LINUX = r'/spp_automation_setup'

# Temporary directory location for Windows and Linux
SYSTEM_TEMP_DIR_WINDOWS = r'C:\Users\{{USERNAME}}\AppData\Local\Temp'

# Signature variables
CERTIFICATE_DIR = r'C:\dev\spp\tools\windows_certificate'
COMMAND_INSTALL_CERTIFICATE = r'cmd.exe /c certutil -addstore "TrustedPublisher" %s >> CertUtil_Out.txt'
COMMAND_FORCE_INSTALL_CERTIFICATE = r'cmd.exe /c certutil -addstore -f "TrustedPublisher" %s >> CertUtil_Out.txt'
COMMAND_VIEW_CERTIFICATE_STORE = r'cmd.exe /c certutil -store "TrustedPublisher" >> CertStore_Out.txt'

# PIV screen shot variables
SCREENSHOT_UTILITY_DIR = r'C:\dev\spp\tools\third_party\screenshot'

# AutoLogon and UAC variable.
DISABLE_UAC = r'reg ADD "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v EnableLUA /t REG_DWORD /d 0 /f'
CMD_ENABLE_AUTOLOGON = r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v AutoAdminLogon /t REG_SZ /d 1 /f'
CMD_ADD_AUTO_USERNAME = r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v DefaultUserName /t REG_SZ /d {{USERNAME}} /f'
CMD_ADD_AUTO_PASSWORD = r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v DefaultPassword /t REG_SZ /d {{PASSWORD}} /f'

# Time-outs
HPSUM_TIMEOUT = 8000
DEPLOY_PREVIEW_REPORT_TIMEOUT = 8000
ILO_RESET_PING_TIME = 50

# Firefox profile for selenium web driver
FF_PROFILE_TEMPLATE = r'C:\Users\%s\AppData\Roaming\Mozilla\Firefox\Profiles'

# Off line selenium script
OFFLINE_SCRIPT = r'spp_offline_selenium.py'

# Paths for utilities
STRAWBERRY_PERL = r'C:\Strawberry\perl\bin\perl'
LOCFG_UTILITY = r'C:\dev\spp\tests\spp\resource\locfg.pl'
BLOB = 'SMARTSTART_SELENIUM'

# RIBCL xml
CHANGE_BOOTORDER_TO_USB = r'C:\dev\spp\tests\spp\resource\ribcl\Set_One_Time_Boot_Order_To_USB.xml'
CHANGE_BOOTORDER_TO_HDD = r'C:\dev\spp\tests\spp\resource\ribcl\Set_One_Time_Boot_Order_To_HDD.xml'
COLD_REBOOT = r'C:\dev\spp\tests\spp\resource\ribcl\cold_reboot.xml'

RIBCL_TEMPLATE_XML = \
        '''<RIBCL VERSION="2.0">
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
        </RIBCL>'''
