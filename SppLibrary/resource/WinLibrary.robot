*** Settings ***
Documentation   This file contains all keywords which are used by
...             Windows Library.
Library         RoboGalaxyLibrary
Library         Process
Library         DateTime
Library         String
Library         SppLibrary
Resource        spp_utility.robot


*** Keywords ***
Setup Server
    [Documentation]     Author : Vinay Krishnan
    ...
    ...                 Setup server for tests.
    ...
    ...                 Performs the following actions.
    ...
    ...                 Connect to ILO and server.
    ...
    ...                 Install certificates, enable auto logon, disable UAC and reboot server.
    ...
    ...                 Example:
    ...
    ...                 | Setup Server |
    Initialze Test Case Variables

    Ilo Connect             ${ILO_IP}       ${ILO_USERNAME}         ${ILO_PASSWORD}
    Open Connection WMI     ${SYSTEM_IP}    ${SYSTEM_USERNAME}      ${SYSTEM_PASSWORD}

    # Delete spp temp dir from SUT, Install Certificates, Enable AutoLogOn & Disable UAC on SUT
    SppLibrary.Remove Dir       ${SUT_TEMP_DIR_WINDOWS}
    Sleep                       2s
    SppLibrary.Start Command    cmd.exe /c mkdir ${SUT_TEMP_DIR_WINDOWS}
    Install Certificates
    Enable AutoLogOn
    Disable UAC

    Unmount And Reboot Server

Open Connection WMI     [Arguments]         ${SYSTEM_IP}    ${SYSTEM_USERNAME}      ${SYSTEM_PASSWORD}
                        [Documentation]     Author : Vinay Krishnan
                        ...
                        ...                 Connect to Windows server over WMI.
                        ...
                        ...                 Example:
                        ...
                        ...                 | Open Connection WMI | ${SYSTEM_IP} | ${SYSTEM_USERNAME} | ${SYSTEM_PASSWORD} |
                        SppLibrary.Open Connection          ${SYSTEM_IP}            ${SYSTEM_USERNAME}      ${SYSTEM_PASSWORD}

Mount SPP Image
    [Documentation]             Author : Vinay Krishnan
    ...
    ...                         Mount the SPP image on server.
    ...
    ...                         Example:
    ...
    ...                         | Mount SPP Image |
    ...
    ...                         Changed By:Chinmaya kumar Dash
    ...
    ...                         Mount SPP image in case of SPP MOUNT TYPE is Virtual.
    Return From Keyword If      '${SPP_MOUNT_TYPE}' == 'USB' or '${SPP_MOUNT_TYPE}' == 'DVD'
    Mount SPP Image By Ilo
    Sleep                       10s

Unmount SPP Image
    [Documentation]             Author : Vinay Krishnan
    ...                         Unmount the SPP image from server.
    ...
    ...                         Example:
    ...
    ...                         | Unmount SPP Image |
    ...
    ...                         Changed By:Chinmaya Kumar Dash
    ...
    ...                         Unmount SPP image in case of SPP MOUNT TYPE is Virtual.
    Return From Keyword If      '${SPP_MOUNT_TYPE}' == 'USB' or '${SPP_MOUNT_TYPE}' == 'DVD'
    Unmount SPP Image By Ilo

Get SPP Mount Point
    [Documentation]         Author : Chinmaya Kumar Dash
    ...
    ...                     Return the SPP mount directory.
    ...
    ...                     Example:
    ...
    ...                     | Get SPP Mount Point |
    ${mount_point} =        Set Variable        None
    :FOR                    ${index}            IN RANGE    1                   10
    \                       Sleep               5s
    \                       ${mount_point} =    Wait Until Keyword Succeeds     5x
    \                       ...                 5 sec       _Return SPP Mount Point
    \                       Exit For Loop If    '${mount_point}' != 'None'
    Should Not Be True      '${mount_point}' == 'None'      Could not fetch mount point
    [Return]                ${mount_point}

Kill Process PID    [Arguments]                 ${pid}
                    [Documentation]             Author : Chinmaya Kumar Dash
                    ...
                    ...                         Kill process by process ID
                    ...
                    ...                         Example:
                    ...
                    ...                         | Kill Process PID | pid |
                    SppLibrary.Start Command    taskkill /pid ${pid} /f

Kill Process Name   [Arguments]                 ${name}
                    [Documentation]             Author : Chinmaya Kumar Dash
                    ...
                    ...                         Kill process by name
                    ...
                    ...                         Example:
                    ...
                    ...                         | Kill Process Name | name |
                    SppLibrary.Start Command    taskkill /im ${name}* /f

Reboot Remote Node
    [Documentation]             Author : Vinay Krishnan
    ...
    ...                         Reboot remote node.
    ...
    ...                         Example:
    ...
    ...                         | Reboot Remote Node |
    SppLibrary.Start Command    cmd.exe /c shutdown -r

Reboot Server
    [Documentation]             Author : Vinay Krishnan
    ...
    ...                         Reboot server.
    ...
    ...                         Set the one time boot to HDD, issue a shutdown command and then power on server by ILO
    ...
    ...                         Example:
    ...
    ...                         | Reboot Server |
    Ilo Set One Time Boot       hdd
    SppLibrary.Start Command    cmd.exe /c shutdown -p
    Power ON Server

Execute HPSUM And Get Log   [Arguments]         ${command_template}         ${live_log}
    [Documentation]         Author : Vinay Krishnan
    ...
    ...                     Execute hpsum command.
    ...
    ...                     Also, analysis the ${live_log} for any errors during execution.
    ...
    ...                     Example:
    ...
    ...                     | Execute HPSUM And Get Log | ${command_template} | ${live_log} |
    ${rg_root} =            Get RG Root
    ${handle} =             Start Process       python
    ...                     ${rg_root}\\tools\\${live_log}
    ...                     -SI                 ${SYSTEM_IP}                -SU     ${SYSTEM_USERNAME}
    ...                     -SP                 ${SYSTEM_PASSWORD}          -LL     ${SUT_LOG_LOCATION}
    ...                     -RU                 ${REMOTE_NODE_USERNAME}     -RP     ${REMOTE_NODE_PASSWORD}
    ...                     -HV                 ${HPSUM_VERSION}
    ...                     stderr=stderr.txt   stdout=stdout.txt           alias=myproc

    ${mounted_drive} =      WinLibrary.Get SPP Mount Point
    ${command}=             Construct Command   ${command_template}         ${mounted_drive}
    Run Keyword If          '${SIGNATURE_BYPASS}' == 'False'                SppLibrary.Execute Command      ${command}
    ...                     ${HPSUM_TIMEOUT}
    ...                     ELSE                Execute Command Psexec      ${command}                      ${HPSUM_TIMEOUT}
    Terminate Process       myproc              kill=true
    Wait Until Host Power Status                ${ILO_IP}                   True
    WinLibrary.Collect HPSUM Logs               @{HPSUM_LOG_FILES_WINDOWS}

Execute Gatherlogs And Get Log      [Arguments]         ${run_count}=
    [Documentation]     Author : Abhishek Katam
    ...
    ...                 Execute the private gatherlogs keyword and warns if keyword fails
    ...
    ...                 Example:
    ...
    ...                 | Execute Gatherlogs And Get Log | ${run_count} |
    ${status} =         Run Keyword And Return Status   WinLibrary._Execute GatherLog And Get Log
    Run Keyword IF      '${status}' == 'False'
    ...                 Log         ${run_count} Unable to get gatherlogs   WARN

_Execute GatherLog And Get Log
    [Documentation]         Author : Vinay Krishnan
    ...
    ...                     Execute the gatherlogs command and copies the files to ${RG_LOG_PATH}
    ...
    ...                     Example:
    ...
    ...                     | Execute Gatherlogs And Get Log |
    ...
    ...                     Modified By: Chinmaya Kumar Dash
    ...
    ...                     In Case of USB Execute gatherlogs command and read the command output. Move the gatherlog into temp_directory
    ...
    ...                     Modified By: Abhishek Katam
    ...
    ...                     Execute Gatherlog command on local directory and copy the .zip file to temp_directory
    ...
    ...                     Private Keyword Used in Execute Gatherlogs And Get Log
    ${rg_root} =            Get RG Root
    ${username} =           Get Username
    ${temp_directory} =     Replace String              ${SYSTEM_TEMP_DIR_WINDOWS}      {{USERNAME}}
    ...                     ${username}
    SppLibrary.Put File     ${rg_root}\\tools\\enter.txt
    ...                     ${SUT_TEMP_DIR_WINDOWS}
    ${command} =            Construct Command           ${COMMAND_GATHERLOGS_WINDOWS_LOCAL}     ${username}
    SppLibrary.Execute Command                          ${command}                      ${HPSUM_TIMEOUT}
    SppLibrary.Get File     ${SUT_TEMP_DIR_WINDOWS}\\gathter_log_output.txt             ${RG_LOG_PATH}
    : FOR                   ${index}                    IN RANGE                        1       20
    \                       Sleep                       5s
    \                       ${gather_log_location} =    Get Gatherlog Location
    \                       ...                         ${RG_LOG_PATH}\\gathter_log_output.txt
    \                       SppLibrary.Move File        ${gather_log_location}          ${temp_directory}
    \                       Sleep                       5s
    \                       SppLibrary.Get File         ${temp_directory}\\${GATHER_LOG_WINDOWS}
    \                       ...                         ${RG_LOG_PATH}
    \                       ${status}                   ${ret} =                        Run Keyword And Ignore Error
    \                       ...                         OperatingSystem.File Should Exist
    \                       ...                         ${RG_LOG_PATH}\\${GATHER_LOG_WINDOWS}
    \                       Exit For Loop If            '${status}' == 'PASS'

Collect HPSUM Logs      [Arguments]         @{hpsum_log_files}
                        [Documentation]     Author : Vinay Krishnan
                        ...
                        ...                 Copies the hpsum logs specified in config.py to ${RG_LOG_PATH}
                        ...
                        ...                 Example:
                        ...
                        ...                 | Collect HPSUM Logs | @{hpsum_log_files} |
                        :FOR                ${file}             IN                          @{hpsum_log_files}
                        \                   ${filename} =       Replace String              ${file}
                        \                   ...                 {{LOG_LOCATION}}
                        \                   ...                 ${SUT_LOG_LOCATION}
                        \                   ${status} =         Run Keyword And Return Status
                        \                   ...                 Wait Until Keyword Succeeds                         5x
                        \                   ...                 5 sec
                        \                   ...                 SppLibrary.File Should Exist
                        \                   ...                 ${filename}
                        \                   ${copied_file} =    Fetch From Right            ${filename}             \\
                        \                   Sleep               1s
                        \                   Run Keyword If      'False' in '${status}'      Log
                        \                   ...                 "${copied_file} is not generated"                   WARN
                        \                   Run Keyword If      'True' in '${status}'       SppLibrary.Get file     ${filename}
                        \                   ...                 ${RG_LOG_PATH}
                        \                   Sleep               1s

Clean Logs Server
    [Documentation]     Author : Vinay Krishnan
    ...
    ...                 Deletes the files specified by @{DELETE_LOG_FILES} in config.py
    ...
    ...                 Example:
    ...
    ...                 | Clean Logs Server |
    # Deleting directories
    ${username} =       Get Username
    :FOR                ${dir}          IN                          @{DELETE_LOG_DIRS_WINDOWS}
    \                   ${dir} =        String.Replace String       ${dir}      {{USERNAME}}    ${username}
    \                   ${output} =     SppLibrary.Start Command    cmd.exe /c rmdir /S /Q ${dir}

    # Deleting files
    :FOR    ${file}         IN                          @{DELETE_LOG_FILES_WINDOWS}
    \       ${file} =       String.Replace String       ${file}     {{USERNAME}}    ${username}
    \       ${output} =     SppLibrary.Start Command    cmd.exe /c del ${file}

Deploy Preview Report   [Arguments]                 ${command_template}     ${file_tag}=.
                        [Documentation]             Author : Vinay Krishnan
                        ...
                        ...                         Execute command to generate deploy preview report and copy to ${RG_LOG_PATH}
                        ...
                        ...                         Example:
                        ...
                        ...                         | Deploy Preview Report | ${command_template} | ${file_tag} |
                        ${mounted_drive} =          WinLibrary.Get SPP Mount Point
                        ${command}=                 Construct Command       ${command_template}     ${mounted_drive}
                        Execute Command Psexec      ${command}              ${HPSUM_TIMEOUT}
                        WinLibrary._Get Deploy Preview Report               ${file_tag}
                        _Check Deploy Preview Report                        ${file_tag}

Move Log Files To Temp Directory
    [Documentation]         Author : Vinay Krishnan
    ...
    ...                     Move log files specified by @{HPSUM_TEMP_FILES_LINUX} in config.py to temporary directory
    ...
    ...                     Example:
    ...                     | Move Log Files To Temp Directory |
    ${username} =           Get Username
    ${temp_directory} =     Replace String      ${SYSTEM_TEMP_DIR_WINDOWS}          {{USERNAME}}    ${username}
    SppLibrary.Start Command                    cmd.exe /c mkdir ${temp_directory}\\temp
    :FOR                    ${file}             IN                  @{HPSUM_TEMP_FILES_WINDOWS}
    \                       ${filename} =       Replace String      ${file}         {{USERNAME}}    ${username}
    \                       ${filename} =       Replace String      ${filename}     {{LOG_LOCATION}}
    \                       ...                 ${SUT_LOG_LOCATION}
    \                       SppLibrary.Start Command                cmd.exe /c move /Y ${filename} ${temp_directory}\\temp

Install Certificates
    [Documentation]         Author : Rahul Verma
    ...
    ...                     Install certificates present in ${CERTIFICATE_DIR} directory on SUT.
    ...
    ...                     ${RG_LOG_PATH} - Destination directory on the RG server where the files have to be copied.
    ...
    ...                     Example:
    ...
    ...                     | Install Certificates | Logs /${SUITE NAME} /${RG_LOG_PATH} |
    Return From Keyword If                  '${SIGNATURE_BYPASS}' == 'False'
    SppLibrary.Execute Command              ${COMMAND_VIEW_CERTIFICATE_STORE}               10      ${SUT_TEMP_DIR_WINDOWS}
    SppLibrary.Get File     ${SUT_TEMP_DIR_WINDOWS}\\CertStore_Out.txt                      ${RG_LOG_PATH}
    ${store_present} =      Grep File       ${RG_LOG_PATH}\\CertStore_Out.txt
    ...                     CertUtil: -store command completed successfully.
    ${store_absent} =       Grep File       ${RG_LOG_PATH}\\CertStore_Out.txt
    ...                     CertUtil: -store command FAILED
    ${COMMAND_CERTIFICATE} =                Set Variable If
    ...                     "successfully" in "${store_present}"        ${COMMAND_INSTALL_CERTIFICATE}
    ...                     "FAILED" in "${store_absent}"               ${COMMAND_FORCE_INSTALL_CERTIFICATE}
    @{DIR_LIST} =           OperatingSystem.List Files In Directory     ${CERTIFICATE_DIR}
    ${length}               Get Length      ${DIR_LIST}
    SppLibrary.Put File     ${CERTIFICATE_DIR}\\*.cer                   ${SUT_TEMP_DIR_WINDOWS}
    :For                    ${var}          IN                          @{DIR_LIST}
    \                       Log             ${var}
    \                       ${command}=     Construct Command           ${COMMAND_CERTIFICATE}
    \                       ...             ${var}
    \                       SppLibrary.Execute Command                  ${command}          60
    \                       ...             ${SUT_TEMP_DIR_WINDOWS}
    SppLibrary.Get File     ${SUT_TEMP_DIR_WINDOWS}\\CertUtil_Out.txt   ${RG_LOG_PATH}
    ${cert_present} =       Grep File       ${RG_LOG_PATH}\\CertUtil_Out.txt
    ...                     Certificate * already in store.
    ${len}                  Get Length      ${cert_present}
    Run Keyword If          ${len}!=0       Log                         ${cert_present}     WARN
    ${cert_installed} =     Grep File       ${RG_LOG_PATH}\\CertUtil_Out.txt
    ...                     Certificate * added to store.
    Log                     ${cert_installed}

Enable AutoLogOn
    [Documentation]             Author : Rahul Verma
    ...
    ...                         Enable Auto Login on Windows SUT
    ...
    ...                         Example:
    ...
    ...                         | Enable AutoLogOn Windows |
    ${username} =               Get Username
    ${password} =               Get Password
    SppLibrary.Start Command    ${CMD_ENABLE_AUTOLOGON}
    ${command} =                String.Replace String   ${CMD_ADD_AUTO_USERNAME}    {{USERNAME}}    ${username}
    SppLibrary.Start Command    ${command}
    ${command} =                String.Replace String   ${CMD_ADD_AUTO_PASSWORD}    {{PASSWORD}}    ${password}
    SppLibrary.Start Command    ${command}

Disable UAC
    [Documentation]             Author : Rahul Verma
    ...
    ...                         Disable User Account Control on Windows 2008 SUT
    ...
    ...                         No parameters.
    ...
    ...                         Example:
    ...
    ...                         | Disable UAC |
    Return From Keyword If      '${SIGNATURE_BYPASS}' == 'False'
    ${os_version} =             Get Operating System Name
    Return From Keyword If      '2008' not in '${os_version}'
    SppLibrary.Start Command    ${DISABLE_UAC}

Install AutoKeyClick
    [Documentation]             Author : Rahul Verma
    ...
    ...                         Start AutoKeyClick.exe on the Windows SUT to click on install button of the pop up.
    ...
    ...                         Example:
    ...
    ...                         | Install AutoKeyClick |
    ${os_version} =             Get Operating System Name
    Return From Keyword If      '2008' not in '''${os_version}''' or 'False' in '${SIGNATURE_BYPASS}'
    ${rg_root} =                Get RG Root
    SppLibrary.Put File         ${rg_root}\\tools\\third_party\\AutoKeyClick.exe
    ...                         ${SUT_TEMP_DIR_WINDOWS}
    Start Command Psexec        ${SUT_TEMP_DIR_WINDOWS}\\AutoKeyClick.exe

PIV SPP Utility Capture Screenshot
    [Documentation]         Author : Girish
    ...
    ...                     Copy all utilities needed to take screen shot. After that it launch HPE utilities one by one and takes screenshot.
    ...
    ...                     Example:
    ...
    ...                     | PIV SPP Utility Capture Screenshot |
    SppLibrary.Put File     ${SCREENSHOT_UTILITY_DIR}\\*.*                      ${SUT_TEMP_DIR_WINDOWS}
    @{utility_names}=       Get Dictionary Keys         ${HP_UTILITIES}
    :FOR                    ${utility}                  IN                      @{utility_names}
    \                       ${utility_path} =           Get From Dictionary     ${HP_UTILITIES}     ${utility}
    \                       Start Command Psexec        ${utility_path}
    \                       Sleep                       5s
    \                       ${utility} =                Replace String          ${utility}          ${SPACE}    _
    \                       ${command} =                Set Variable
    \                       ...                         ${SUT_TEMP_DIR_WINDOWS}\\take_screenshot.bat ${utility} ${utility}.png ${SUT_TEMP_DIR_WINDOWS}
    \                       Execute Command Psexec      ${command}              5
    \                       SppLibrary.Get File         ${SUT_TEMP_DIR_WINDOWS}\\${utility}.png     ${RG_LOG_PATH}\\ScreenShots

PIV Device Manager Info
    [Documentation]     Author : Girish
    ...
    ...                 Executes a WMI query which fetches information from device manager. After that it parse that information to see if any yellow bang item are present or not.
    ...
    ...                 Example:
    ...
    ...                 | PIV Device Manager Info |
    ${resultset} =      Get Device Manager Info
    Run Keyword And Continue On Failure     Parse Device Manager Info   ${resultset}

PIV Get Event Logs
    [Documentation]             Author : Vinay Krishnan
    ...
    ...                         Executes a WMI query which fetches critical events and errors from system and Application. After that it consolidate all events and copy system and application log at test suite log path.
    ...
    ...                         Example:
    ...
    ...                         | PIV Get Event Logs |
    ${event_logs_error} =       Get Event Logs      System                  Error
    ${event_logs_critical} =    Get Event Logs      System                  Critical
    ${event_logs_system} =      Combine Lists       ${event_logs_error}     ${event_logs_critical}
    Run Keyword And Continue On Failure             Generate Event Logs     System      ${event_logs_system}
    ...                         ${RG_LOG_PATH}

    ${event_logs_error} =       Get Event Logs      Application             Error
    ${event_logs_critical} =    Get Event Logs      Application             Critical
    ${event_logs_application} =                     Combine Lists           ${event_logs_error}     ${event_logs_critical}
    Run Keyword And Continue On Failure             Generate Event Logs     Application             ${event_logs_system}
    ...                         ${RG_LOG_PATH}

PIV Hpsum Log File Check
    [Documentation]             Author : Girish
    ...
    ...                         Check for hpsum log file existence
    ...
    ...                         Example:
    ...
    ...                         | PIV Hpsum Log File Check |
    ${username} =               Get Username
    ${temp_dir} =               Replace String      ${SYSTEM_TEMP_DIR_WINDOWS}      {{USERNAME}}                ${username}
    ${HPSUM_NAME} =             Run Keyword If      '${HPSUM_NAME}' == 'SUM'        Convert To Lowercase        ${HPSUM_NAME}
    ...                         ELSE IF             '${HPSUM_NAME}' == 'HPSUM'      Set Variable                ${HPSUM_NAME}
    Set Suite Variable          ${HPSUM_NAME}
    ${hpsum_logs_directory} =   Set Variable        ${temp_dir}\\temp\\${HPSUM_NAME}\\${SUT_LOG_LOCATION}\\
    ${drive_letter}             ${file_path} =      Split String                    ${hpsum_logs_directory}     :   1
    ${files} =                  SppLibrary.List Files In Directory                  ${file_path}                ${drive_letter}:
    Log                         ${files}
    Run Keyword And Continue On Failure             Hpsum Log File Check            ${files}
    ...                         ${FILE_TYPES_LIST}

PIV Check Services
    [Documentation]     Author : Kapil Chauhan
    ...
    ...                 Check for services and their running status
    ...
    ...                 Example:
    ...
    ...                 | PIV Hpsum Log File Check |
    ...
    ...                 Modified By:Chinmaya Kumar Dash
    ...
    ...                 Check for Wbem service. After that check the services for Proliant or synergy server.
    ${services} =       Get Services
    ${smh} =            Wbem Check          ${services}
    ${server} =         Set Variable If     ${smh} == 0             synergy                 proliant
    ${PIV_URL} =        Set Variable        https://{{SYSTEM_IP}}:2381
    ${URL}=             Replace String      ${PIV_URL}              {{SYSTEM_IP}}           ${SYSTEM_IP}
    Run Keyword And Continue On Failure     SMH PIV Check
    ...                 ${URL}              ${SYSTEM_USERNAME}      ${SYSTEM_PASSWORD}      ${RG_LOG_PATH}      windows
    ...                 ${server}

PIV Uninstall Programs
    [Documentation]     Author : Kapil Chauhan
    ...
    ...                 Uninstall Light-Out OCU,IML viewer,SSA Cli
    ...
    ...                 Example:
    ...
    ...                 | PIV Uninstall Programs |
    ${programs} =       Get Installed Programs
    ${status}           ${value} =              Run Keyword And Ignore Error    PIV Uninstall Programs Check    ${programs}
    Run Keyword If      '${status}' != 'PASS'   Log     ${value}                WARN

PIV HPSUM Log Parsing
    [Documentation]         Author : Girish
    ...
    ...                     Parse HPSUM logs and check for discrepancy in return code, component name and component number. If any information is missing it will report the same.
    ...
    ...                     Example:
    ...
    ...                     | PIV Hpsum Log File Check |
    ${username} =           Get Username
    ${temp_dir} =           Replace String      ${SYSTEM_TEMP_DIR_WINDOWS}      {{USERNAME}}    ${username}
    SppLibrary.Get File     ${temp_dir}\\temp\\${HPSUM_DETAIL_LOG}              .\\
    Run Keyword And Continue On Failure         Get Component Status Post Installation Windows
    ...                     ${HPSUM_DETAIL_LOG}
    OperatingSystem.Remove File                 ${HPSUM_DETAIL_LOG}

_Return SPP Mount Point
    [Documentation]         Author : Chinmaya Kumar Dash
    ...
    ...                     Detect the mounted drive letter according to mount type and returns the drive letter.
    ...
    ...                     Example:
    ...
    ...                     | _Return SPP Mount Point |
    ...
    ...                     Private Function used in Get SPP Mount Point
    ${drive_return} =       Set Variable                    None
    ${SPP_MOUNT_TYPE}       Set Variable If
    ...                     '${SPP_MOUNT_TYPE}' == 'Virtual'
    ...                     Virtual
    ...                     '${SPP_MOUNT_TYPE}' == 'DVD'    CDDVDW
    ...                     '${SPP_MOUNT_TYPE}' == 'USB'    Removable
    @{drives} =             Get Mounted Drive
    :FOR                    ${drive}                        IN              @{drives}
    \                       Continue For Loop If            '${SPP_MOUNT_TYPE}' not in '@{drive}[1]'
    \                       ${drive_return} =               Set Variable    @{drive}[0]
    Should Not Be True      '${drive_return}' == 'None'     Unable to find mount point
    [Return]                ${drive_return}

_Get Deploy Preview Report                          [Arguments]     ${file_tag}
    [Documentation]     Author : Chinmaya Kumar Dash
    ...
    ...                 Get the Deploy Preview Report Form SUT to RG log location and rename it according to run Count
    ...
    ...                 Example:
    ...
    ...                 | _Get Deploy Preview Report | ${file_tag} |
    ...
    ...                 Private Function used in Deploy Preview Report
    :FOR                ${index}                    IN RANGE        1
    ...                 10
    \                   Sleep                       3s
    \                   SppLibrary.Get File         ${LOGS_WINDOWS_REPORT}\\${DEPLOY_PREVIEW_REPORT}*\\${DEPLOY_PREVIEW_REPORT}*.html
    \                   ...                         .\\
    \                   Run Keyword And Ignore Error                OperatingSystem.Move File
    \                   ...                         .\\${DEPLOY_PREVIEW_REPORT}*.html
    \                   ...                         ${RG_LOG_PATH}\\${file_tag}_deploy_preview_Report.html
    \                   ${status} =                 Run Keyword And Return Status
    \                   ...                         OperatingSystem.File Should Exist
    \                   ...                         ${RG_LOG_PATH}\\${file_tag}_deploy_preview_Report.html
    \                   Return From Keyword If      '${status}' == 'True'

_PIV Service Check      [Arguments]         ${server_type}          ${services}
                        [Documentation]     Author : Kapil Chauhan
                        ...
                        ...                 Check for Services Running status and report back if the service is not running.
                        ...
                        ...                 Example:
                        ...
                        ...                 | _PIV Service Check | ${server_type} | ${services} |
                        ...
                        ...                 Private Function used in PIV Check Services
                        ${services} =       PIV Hpservice Check     ${server_type}          ${services}
                        @{keys}=            Get Dictionary Keys     ${services}
                        : FOR               ${key}                  IN                      @{keys}
                        \                   ${item}=                Get From Dictionary     ${services}     ${key}
                        \                   Run Keyword If          '${item}' == '1'
                        \                   ...                     Run Keywords            Log
                        \                   ...                     Service: ${key} is running
                        \                   ...                     AND                     Continue For Loop
                        \                   Run Keyword If          '${item}' == '2'
                        \                   ...                     Run Keywords            Log
                        \                   ...                     Service: ${key} is not running
                        \                   ...                     WARN
                        \                   ...                     AND                     Continue For Loop
                        \                   Run Keyword If          'ProLiant Agentless Management Service' in '${key}' and '${item}' == '0'
                        \                   ...                     Run Keywords            Log
                        \                   ...                     Service: ${key} is not present in the system
                        \                   ...                     WARN
                        \                   ...                     AND                     Continue For Loop
                        #Below code is not needed as component removed from SNAP6. However keeping the code as it might get added again in next release.
                        #\                  Run Keyword If          'Smart Update Tools' in '${key}' and '${item}' == '0'
                        #\                  ...                     Run Keywords            Log
                        #\                  ...                     Service: ${key} is not present in the system
                        #\                  ...                     WARN
                        #\                  ...                     AND                     Continue For Loop
                        \                   Run Keyword And Continue On Failure             Run Keyword If
                        \                   ...                     'Truth' != 'False'
                        \                   ...                     Fail                    Service: ${key} is not present in the system

Testcase Cleanup
    [Documentation]     Author : Chinmaya Kumar Dash
    ...
    ...                 Test case teardown
    ...
    ...                 Unmount SPP image, move log files specified by @{TEMP_TEST_CASE_LOGS} to ${RG_LOG_PATH}
    ...
    ...                 and deletes the temp directory      on server.
    ...
    ...                 Example:
    ...
    ...                 | Testcase Cleanup |
    Run Keyword And Ignore Error    WinLibrary.Unmount SPP Image
    Run Keyword And Ignore Error    Move Files              @{TEMP_TEST_CASE_LOGS}      ${RG_LOG_PATH}
    Run Keyword And Ignore Error    SppLibrary.Remove Dir   ${SUT_TEMP_DIR_WINDOWS}

Get Contents HTML File
    [Documentation]         Author : Rahul Verma
    ...
    ...                     Copy the Contents.html from SUT to RG loglocation
    ...
    ...                     Example:
    ...
    ...                     | Get Contents HTML File |
    ${mounted_drive} =      WinLibrary.Get SPP Mount Point
    SppLibrary.Execute Command                  cmd.exe /c copy ${mounted_drive}\\contents.html C:\\Users\\     5
    :FOR                    ${index}            IN RANGE                    1   10
    \                       Run Keyword And Continue On Failure             SppLibrary.Get File
    \                       ...                 C:\\Users\\contents.html
    \                       ...                 ${RG_LOG_PATH}
    \                       Sleep               5s
    \                       ${count} =          Count Files In Directory    ${RG_LOG_PATH}
    \                       ...                 contents.html
    \                       Exit For Loop If    '${count}' == '1'
    Run Keyword If          '1' != '${count}'   Fail                        "Unable to copy Contents.html"

Check Node Architecture
    [Documentation]         Author : Chinmaya Kumar Dash
    ...
    ...                     Copy the Scouting log from SUT to RG logpath and detect the remote node type.
    ...
    ...                     Example:
    ...
    ...                     | Check Node Architecture |
    ${scouting_log} =       Construct Command   ${SCOUTING_LOG_WINDOWS}     ${SYSTEM_USERNAME}
    ...                     ${SUT_LOG_LOCATION}
    SppLibrary.Get File     ${scouting_log}     .\\
    ${node_type} =          Get Node Type
    Run Keyword And Ignore Error                OperatingSystem.Move File   scouting.log    ${RG_LOG_PATH}
    [Return]                ${node_type}

Get HPSUM Version
    [Documentation]         Author: Rahul Verma
    ...
    ...                     Check for the bat file in the image
    ...
    ...                     Detects the version of HPSUM
    ...
    ...                     Import config file according to the version
    ...
    ...
    ...                     Modified: Chinmaya Kumar Dash
    ...
    ...                     Make HPSUM version variable a suite variable
    ...
    ...                     Example:
    ...
    ...                     | Get HPSUM Version |
    WinLibrary.Mount SPP Image
    ${mounted_drive} =      WinLibrary.Get SPP Mount Point
    ${STATUS}               Run Keyword And Return Status                   SppLibrary.File Should Exist
    ...                     ${mounted_drive}\\launch_sum.bat
    ${HPSUM_VERSION} =      Set Variable If
    ...                     ${STATUS} == True       8
    ...                     ${STATUS} == False      7
    Run Keyword If          ${HPSUM_VERSION} == 8   Import Variables        SppLibrary/config/hpsum_config_8.py
    ...                     ELSE IF                 ${HPSUM_VERSION} == 7   Import Variables
    ...                     SppLibrary/config/hpsum_config_7.py
    ...                     ELSE                    Run Keyword If          ${HPSUM_VERSION} != 8 and ${HPSUM_VERSION} != 7
    ...                     Fail                    " Didn't find HPSUM version "
    Set Suite Variable      ${HPSUM_VERSION}

