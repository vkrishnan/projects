#importing variables defined in variables.py for .format
import variables

# Windows Commands
COMMAND_HPSUM_START_WINDOWS = r'%s\hp\swpackages\hpsum.bat'
COMMAND_HPSUM_WINDOWS = r'%s\hp\swpackages\hpsum.bat /s /use_snmp /use_wmi /use_ams /On_failed_dependency:OmitComponent /tpmbypass'
COMMAND_HPSUM_WINDOWS_FORCEALL = r'%s\hp\swpackages\hpsum.bat /s /use_snmp /use_wmi /use_ams /f:all /On_failed_dependency:OmitComponent'
COMMAND_HPSUM_WINDOWS_REWRITE = r'%s\hp\swpackages\hpsum.bat /s /rewrite /use_snmp /use_wmi /use_ams /On_failed_dependency:OmitComponent'
COMMAND_HPSUM_WINDOWS_DOWNGRADE = r'%s\hp\swpackages\hpsum.bat /s /downgrade /use_snmp /use_wmi /use_ams /On_failed_dependency:OmitComponent'
COMMAND_HPSUM_WINDOWS_FORCE_ROMONLY = r'%s\hp\swpackages\hpsum.bat /s /f /romonly /On_failed_dependency:OmitComponent'
COMMAND_HPSUM_WINDOWS_FORCE_SOFTWARE_ONLY = r'%s\hp\swpackages\hpsum.bat /s /f:software'
COMMAND_HPSUM_WINDOWS_FORCE_ROM_ONLY = r'%s\hp\swpackages\hpsum.bat /s /f:rom /skip_ilo'
COMMAND_HPSUM_WINDOWS_SOFTWARE_ONLY = r'%s\hp\swpackages\hpsum.bat /s /f:bundle /softwareonly /no_mgmt /veryv'
COMMAND_HPSUM_WINDOWS_FORCE_DRYRUN = r'%s\hp\swpackages\hpsum.bat /s /f /dryrun /logdir "C:\\USERDIR" /reboot_always /reboot_message "Checking Reboot Message" /reboot_delay 30'
COMMAND_HPSUM_WINDOWS_REMOTE_NODE = r'%s\hp\swpackages\hpsum.bat /target %s /user %s /password %s /s /use_snmp /use_wmi /use_ams /On_failed_dependency:OmitComponent'
COMMAND_HPSUM_WINDOWS_REMOTE_NODE_FORCEALL = r'%s\hp\swpackages\hpsum.bat /target %s /user %s /password %s /s /f:all /On_failed_dependency:OmitComponent'
COMMAND_HPSUM_WINDOWS_OA_NODE = r'%s\hp\swpackages\hpsum.bat /target %s /targettype "oa" /user %s /password %s /s'
COMMAND_HPSUM_WINDOWS_VC_NODE = r'%s\hp\swpackages\hpsum.bat /target %s /oa_username %s /oa_password %s /targettype "vc" /user %s /password %s /s'
COMMAND_HPSUM_WINDOWS_OA_NODE_DOWNGRADE = r'%s\hp\swpackages\hpsum.bat /target %s /targettype "oa" /user %s /password %s /downgrade /s'
COMMAND_HPSUM_INPUT_FILE_WINDOWS = r'%s\hp/swpackages\hpsum.bat /inputfile %s'
COMMAND_GATHERLOGS_WINDOWS = r'%s\hp\swpackages\gatherlogs.bat < {0}\enter.txt > {1}\gathter_log_output.txt'.format(variables.SUT_TEMP_DIR_WINDOWS,variables.SUT_TEMP_DIR_WINDOWS)
COMMAND_DEPLOY_PREVIEW_REPORT_WINDOWS = r'%s\hp\swpackages\hpsum.bat /s /report /reportdir "C:\\cpqsystem"'
COMMAND_DEPLOY_PREVIEW_REPORT_WINDOWS_REMOTE_NODE = r'%s\hp\swpackages\hpsum.bat /target %s /user %s /password %s /s /report /reportdir "C:\\cpqsystem"'
COMMAND_DEPLOY_PREVIEW_REPORT_WINDOWS_OA_NODE = r'%s\hp\swpackages\hpsum.bat /target %s /targettype "oa" /username %s /password %s /s /report /reportdir "C:\\cpqsystem"'
COMMAND_DEPLOY_PREVIEW_REPORT_WINDOWS_VC_NODE = r'%s\hp\swpackages\hpsum.bat /target %s /oa_username %s /oa_password %s /targettype "vc" /username %s /password %s /s /report /reportdir "C:\\cpqsystem"'
HPSUM_INVENTORY_FIRMWARE_DEPENDENCY_INSTALLED_COMBINED_REPORT = r'%s\hp\swpackages\hpsum.bat /s /inventory_report /firmware_report /dependency_report /installed_report /combined_report /reportdir "C:\\reports"'
COMMAND_GATHERLOGS_WINDOWS_LOCAL = r'C:\\Users\\%s\\AppData\\Local\\Temp\\localhpsum\\gatherlogs.bat < {0}\enter.txt > {1}\gathter_log_output.txt'.format(variables.SUT_TEMP_DIR_WINDOWS,variables.SUT_TEMP_DIR_WINDOWS)

# Linux Commands
SYSTEM_TEMP_DIR_LINUX = r'/tmp/'
HPSUM_DIR_LINUX = r'/hp/swpackages'
COMMAND_HPSUM_START_LINUX = r'./hpsum'
COMMAND_HPSUM_LINUX = r'./hpsum --s --use_ams --use_snmp --On_failed_dependency:OmitComponent --tpmbypass'
COMMAND_HPSUM_LINUX_FORCEALL = r'./hpsum --s --use_ams --use_snmp --f:all --On_failed_dependency:OmitComponent'
COMMAND_HPSUM_LINUX_REWRITE = r'./hpsum --s --rewrite --use_ams --use_snmp --On_failed_dependency:OmitComponent'
COMMAND_HPSUM_LINUX_DOWNGRADE = r'./hpsum --s --downgrade --use_ams --use_snmp --On_failed_dependency:OmitComponent'
COMMAND_HPSUM_LINUX_FORCE_ROMONLY = r'./hpsum --s --f --romonly --On_failed_dependency:OmitComponent'
COMMAND_HPSUM_LINUX_FORCE_SOFTWARE_ONLY = r'./hpsum --s --f:software'
COMMAND_HPSUM_LINUX_FORCE_ROM_ONLY = r'./hpsum --s --f:rom'
COMMAND_HPSUM_LINUX_SOFTWARE_ONLY = r'./hpsum --s --f:bundle --softwareonly --no_mgmt --veryv'
COMMAND_HPSUM_LINUX_FORCE_DRYRUN = r'./hpsum --s --f --dryrun --logdir "/USERDIR" --reboot_always --reboot_message "Checking_Reboot_Message" --reboot_delay 30'
COMMAND_HPSUM_LINUX_REMOTE_NODE = r'./hpsum --target %s --user %s --password %s --s --On_failed_dependency:OmitComponent'
COMMAND_HPSUM_LINUX_REMOTE_NODE_FORCEALL = r'./hpsum --target %s --user %s --password %s --s --f:all --On_failed_dependency:OmitComponent'
COMMAND_HPSUM_LINUX_OA_NODE = r'./hpsum --target %s --targettype "oa" --user %s --password %s --s'
COMMAND_HPSUM_LINUX_OA_NODE_DOWNGRADE = r'./hpsum --target %s --targettype "oa" --user %s --password %s --downgrade --s'
COMMAND_HPSUM_LINUX_VC_NODE = r'./hpsum --target %s --oa_username %s --oa_password %s --targettype "vc" --user %s --password %s --s'
COMMAND_HPSUM_INPUT_FILE_LINUX = r'./hpsum --inputfile %s'
COMMAND_GATHERLOGS_LINUX = r'./gatherlogs.sh'
COMMAND_DEPLOY_PREVIEW_REPORT_LINUX = r'./hpsum --s --report --reportdir /var/hp/log'
COMMAND_DEPLOY_PREVIEW_REPORT_LINUX_REMOTE_NODE = r'./hpsum --target %s --user %s --password %s --s --report --reportdir /var/hp/log'
COMMAND_DEPLOY_PREVIEW_REPORT_LINUX_OA_NODE = r'./hpsum --target %s --targettype "oa" --username %s --password %s --s --report --reportdir /var/hp/log'
COMMAND_DEPLOY_PREVIEW_REPORT_LINUX_VC_NODE = r'./hpsum --target %s --oa_username %s --oa_password %s --targettype "vc" --username %s --password %s --s --report --reportdir /var/hp/log'
HPSUM_INVENTORY_FIRMWARE_DEPENDENCY_INSTALLED_COMBINED_REPORT = r'./hpsum --s --inventory_report --firmware_report --dependency_report --installed_report --combined_report --reportdir /reports'
LINUX_GATHERLOGS_DIR = r'/tmp/localhpsum/'

#HPSUM Name
HPSUM_NAME = r'HPSUM'

#HPSUM source
SOURCE = r'\\hp\\swpackages\\'

# LOGS Location
LOGS_LINUX = r'/var/hp/log/'
LOGS_WINDOWS = r'C:\\cpqsystem\\hp\\log'
LOGS_WINDOWS_REPORT = r'C:\cpqsystem'

#HPSUM config file
HPSUM_CONFIG_FILE = r'hpsum.ini'

#HPSUM Content File
HPSUM_CONTENT_FILE = r'contents.html'

#HPSUM Directory location under temp
HPSUM_TMP_DIR_PATH =r'C:\\Users\\{{USERNAME}}\\AppData\\Local\\Temp\\HPSUM'

#Scouting log location
SCOUTING_LOG_WINDOWS = r'C:\\Users\\%s\\AppData\\Local\\Temp\\HPSUM\\%s\\scouting.log'
SCOUTING_LOG_LINUX = r'/tmp/HPSUM/%s/scouting.log'

#VMware siganture script variable
VIB_CHECK_STRING = r'bypass_vib_sig_check'

#Deploy preview report
DEPLOY_PREVIEW_REPORT = r'HPSUM_deploy_preview_Report'

#HPUSM Logs
HPSUM_TEMP_PATH_WIN = 'C:\\Users\\Administrator\\AppData\\Local\\Temp\\temp'
HPSUM_TEMP_PATH_LIN = r'/tmp/temp'
TEMP_HPSUM_LOGS =r'temp\\hpsum\\localhost\\'
HPSUM_LOG = r'hpsum_log.txt'
HPSUM_DETAIL_LOG = r'hpsum_detail_log.txt'
HPSUM_DETAILS_LOG_XML = r'HPSUM_InstallDetails.xml'
GATHER_LOG_WINDOWS = r'HPSUM_Logs_*.zip'
GATHER_LOG_LINUX = r'HPSUM_Logs_*.tar.gz'
HPSUM_INVENTORY_LOG = r'inventory.log'
HPSUM_BASELINE_LOG = r'Baseline.log'
HPSUM_SCOUTING_LOG = r'scouting.log'
HPSUM_DEPLOY_LOG = r'deploy.log'
HPSUM_NODE_LOG = r'node.log'


HPSUM_LOG_FILES_WINDOWS       = [   r'C:\cpqsystem\hp\log\{{LOG_LOCATION}}\hpsum_detail_log.txt',
                                    r'C:\cpqsystem\hp\log\{{LOG_LOCATION}}\hpsum_log.txt',
                                    r'C:\cpqsystem\hp\log\{{LOG_LOCATION}}\HPSUM_InstallDetails.xml'
                                ]

HPSUM_LOG_FILES_LINUX       =   [   r'/var/hp/log/{{LOG_LOCATION}}/hpsum_detail_log.txt',
                                    r'/var/hp/log/{{LOG_LOCATION}}/hpsum_log.txt',
                                    r'/var/hp/log/{{LOG_LOCATION}}/HPSUM_InstallDetails.xml'
                                ]
HPSUM_TEMP_FILES_WINDOWS      = [r'C:\Users\{{USERNAME}}\AppData\Local\Temp\HPSUM_Logs_*.zip',
                                 r'C:\Users\{{USERNAME}}\AppData\Local\Temp\HPSUM',
                                 r'C:\Users\{{USERNAME}}\AppData\Local\Temp\localhpsum',
                                 r'C:\cpqsystem\hp\log\{{LOG_LOCATION}}\hpsum*'
                                ]

DELETE_LOG_DIRS_WINDOWS =   [
                        r'C:\\cpqsystem',
                        r'C:\Users\{{USERNAME}}\AppData\Local\Temp\localhpsum',
                        r'C:\Users\{{USERNAME}}\AppData\Local\Temp\HPSUM',
                        r'C:\Users\{{USERNAME}}\AppData\Local\Temp\temp',
                    ]

DELETE_LOG_FILES_WINDOWS =  [
                        r'C:\Users\{{USERNAME}}\AppData\Local\Temp\HPSUM_*.zip',
                        r'C:\Users\{{USERNAME}}\AppData\Local\Temp\enter.txt'
                    ]

DELETE_LOG_FILES_LINUX = [
                        r'/var/cpq/',
                        r'/var/hp/',
                        r'/tmp/HPSUM*',
                        r'/tmp/temp*',
                        r'/tmp/localhpsum*',
                        r'/tmp/hpsum*',
                        r'/tmp/HPSUM_Logs*'
                         ]

TEMP_TEST_CASE_LOGS = [r'HPSUM_Live.log',
                        r'stdout.txt',
                        r'stderr.txt']

HPSUM_TEMP_FILES_LINUX = [  r'{0}/HPSUM_Logs_*.tar.gz'.format(SYSTEM_TEMP_DIR_LINUX),
                            r'{0}/HPSUM'.format(SYSTEM_TEMP_DIR_LINUX),
                            r'{0}/localhpsum'.format(SYSTEM_TEMP_DIR_LINUX),
                            r'/var/hp/log/%s/*.*']

LOG_FILES_USERDIR_WINDOWS = [r'C:\USERDIR\hp\log\{{LOG_LOCATION}}\hpsum_detail_log.txt',
                             r'C:\USERDIR\hp\log\{{LOG_LOCATION}}\hpsum_log.txt',
                             r'C:\USERDIR\hp\log\{{LOG_LOCATION}}\HPSUM_InstallDetails.xml'
                             ]

LOG_FILES_USERDIR_LINUX = [r'/USERDIR/hp/log/{{LOG_LOCATION}}/hpsum_log.txt',
                           r'/USERDIR/hp/log/{{LOG_LOCATION}}/hpsum_detail_log.txt',
                           r'/USERDIR/hp/log/{{LOG_LOCATION}}/HPSUM_InstallDetails.xml'
                           ]

HPSUM_SERVICE_NAME = r'hpsum_service'

FILE_TYPES_LIST = ['node', 'inventory', 'deploy', 'hpsum_log', 'hpsum_detail_log']

HP_UTILITIES = {
                    r'HP Smart Storage Administrator': r'C:\Program Files\Smart Storage Administrator\ssa\bin\ssaclient.exe',
                    r'HP ProLiant Integrated Management Log Viewer': r'C:\Program Files\Compaq\Cpqimlv\cpqimlv.exe',
                    r'HP Lights-Out Online Configuration Utility': r'C:\Program Files\HP\HPONCFG\hponcfg_gui.exe',
                    r'hpssacli': r'C:\Program Files\Smart Storage Administrator\ssacli\bin\ssacli.exe'
                }

