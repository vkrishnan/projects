*** Settings ***
Documentation   This file contains all keywords which are used by
...             Unix Library.
Library         RoboGalaxyLibrary
Library         Process
Library         SSHLibrary
Library         String
Resource        spp_utility.robot


*** Variables ***
${SPP_IMAGE_NAME}                       spp_mount_auto
${COMMAND_MOUNT_POINT_DEV_Virtual}      lsscsi | grep 'Virtual' | awk '{print $6}'
${COMMAND_MOUNT_POINT_DEV_DVD}          lsscsi | grep 'CDDVDW'      | awk '{print $7}'
${COMMAND_MOUNT_POINT_DEV_USB}          findfs LABEL=SPP_USB
${COMMAND_GREP_IMAGE_NAME}              mount                       | grep '${SPP_IMAGE_NAME}'


*** Keywords ***

_Manual Mount SPP Image
    [Documentation]     Author : Vinay Krishnan
    ...
    ...                 Private keyword used by keyword Mount SPP Image
    ...
    ...                 Mounts image to a predefined path by creating a directory and then mounting to it.
    ...
    ...                 Note: Unmount any auto mounted image before mounting.
    ...
    ...                 Example:
    ...
    ...                 | _Manual Mount SPP Image |
    : FOR               ${index}                IN RANGE            1                   10
    \                   Sleep                   1s
    \                   ${mount_device} =       Run Keyword If      '${SPP_MOUNT_TYPE}' == 'Virtual'
    \                   ...                     SSHLibrary.Execute Command
    \                   ...                     ${COMMAND_MOUNT_POINT_DEV_Virtual}
    \                   ...                     ELSE                Run Keyword If      '${SPP_MOUNT_TYPE}' == 'DVD'
    \                   ...                     SSHLibrary.Execute Command
    \                   ...                     ${COMMAND_MOUNT_POINT_DEV_DVD}
    \                   ...                     ELSE                Run Keyword If      '${SPP_MOUNT_TYPE}' == 'USB'
    \                   ...                     SSHLibrary.Execute Command              ${COMMAND_MOUNT_POINT_DEV_USB}
    \                   Continue For Loop If    'tmp' in '${mount_device}'
    \                   Exit For Loop If        'dev' in '${mount_device}'
    Run Keyword If      'dev' not in '${mount_device}'              Fail
    ...                 Image not mounted through ${SPP_MOUNT_TYPE} device
    Sleep               5s
    ${mpath} =          SSHLibrary.Execute Command                  umount -l ${mount_device}
    ${output} =         SSHLibrary.Execute Command                  mkdir ${SPP_IMAGE_NAME}
    Log                 ${mount_device}
    ${rc}=              SSHLibrary.Execute Command                  mount ${mount_device} ${SPP_IMAGE_NAME}
    ...                 return_stdout=False
    ...                 return_rc=True
    Run Keyword If      '${rc}' != '0'          Fail                Could not mount image

_Manual Unmount SPP Image
    [Documentation]         Author : Vinay Krishnan
    ...
    ...                     Private keyword used by keyword Unmount SPP Image.
    ...
    ...                     Unmount image using umount -l command and then deletes the mounted directory.
    ...
    ...                     Example:
    ...
    ...                     | _Manual Unmount SPP Image |
    ${image_count} =        SSHLibrary.Execute Command      ${COMMAND_GREP_IMAGE_NAME} | wc -l
    Should Not Contain      ${image_count}      None
    : FOR                   ${index}            IN RANGE    0   ${image_count}
    \                       ${mount_dir} =      SSHLibrary.Execute Command
    \                       ...                 ${COMMAND_GREP_IMAGE_NAME} | awk '{print $3}'
    \                       SSHLibrary.Start Command        umount -l ${mount_dir}
    \                       ${output} =         Read Command Output
    \                       SSHLibrary.Start Command        rm -rf ${mount_dir}
    \                       SSHLibrary.Read Command Output
    SSHLibrary.Start Command                    rm -rf ${SPP_IMAGE_NAME}
    SSHLibrary.Read Command Output

SSH Run Command     [Arguments]                 ${command}              ${cwd}      ${timeout}
                    [Documentation]             Author : Vinay Krishnan
                    ...
                    ...                         Executes the command ${command} by changing the directory to ${cwd},
                    ...
                    ...                         Waits until ${timeout} seconds for the command to complete then returns.
                    ...
                    ...                         Example:
                    ...
                    ...                         | SSH Run Command | ${command} | ${cwd} | ${timeout} |
                    Write                       cd ${cwd}
                    Set Client Configuration    ${timeout} seconds      prompt=#
                    Read Until Prompt
                    Write                       ${command}
                    ${output} =                 Read Until Prompt
                    [Return]                    ${output}

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
                        \                   ...                 SSHLibrary.File Should Exist
                        \                   ...                 ${filename}
                        \                   ${copied_file} =    Fetch From Right            ${filename}             /
                        \                   Run Keyword If      'False' in '${status}'      Log
                        \                   ...                 "${copied_file} is not generated"                   WARN
                        \                   Run Keyword If      'True' in '${status}'       SSHLibrary.Get file     ${filename}
                        \                   ...                 .\\
                        \                   Sleep               1s
                        \                   Run Keyword And Ignore Error                    OperatingSystem.Move File
                        \                   ...                 ${copied_file}              ${RG_LOG_PATH}
                        \                   Sleep               1s

_Get Deploy Preview Report                          [Arguments]     ${file_tag}
    [Documentation]     Author : Chinmaya Kumar Dash
    ...
    ...                 Private keyword used by keyword Deploy Preview Report
    ...
    ...                 Copies the deploy preview report file from server to ${RG_LOG_PATH}
    ...
    ...                 The copied filename is perpended with ${file_tag}_
    ...
    ...                 Example:
    ...
    ...                 | _Get Deploy Preview Report | ${file_tag} |
    :FOR                ${index}                    IN RANGE        1
    ...                 30
    \                   Sleep                       1s
    \                   SSHLibrary.Execute Command                  mv ${LOGS_LINUX}/${DEPLOY_PREVIEW_REPORT}*/*.html ${LOGS_LINUX}
    \                   Run Keyword And Ignore Error                SSHLibrary.Get File
    \                   ...                         ${LOGS_LINUX}/${DEPLOY_PREVIEW_REPORT}_*.html
    \                   ...                         .\\
    \                   Run Keyword And Ignore Error                OperatingSystem.Move File
    \                   ...                         .\\${DEPLOY_PREVIEW_REPORT}_*.html
    \                   ...                         ${RG_LOG_PATH}\\${file_tag}_deploy_preview_Report.html
    \                   ${status} =                 Run Keyword And Return Status
    \                   ...                         OperatingSystem.File Should Exist
    \                   ...                         ${RG_LOG_PATH}\\${file_tag}_deploy_preview_Report.html
    \                   Return From Keyword If      '${status}' == 'True'

Open Connection SSH     [Arguments]         ${host}     ${username}     ${password}
                        [Documentation]     Author : Vinay Krishnan
                        ...
                        ...                 Opens a SSH connection to the system with variables SYSTEM_IP, SYSTEM_USERNAME
                        ...
                        ...                 and ILO_PASSWORD preset in the variables.py file or passed as command line arguments.
                        ...
                        ...                 *TBD* - This keyword can be removed once Open Connection And Log In iLO is parametrized.
                        ...
                        ...                 Example:
                        ...
                        ...                 | Open Connection SSH | ${host} | ${username} | ${password} |
                        SSHLibrary.Open Connection      ${host}         alias=${host}
                        Wait Until Keyword Succeeds     5 min           30sec   SSHLibrary.Login    ${username}     ${password}

Mount SPP Image
    [Documentation]     Author : Vinay Krishnan
    ...
    ...                 Mount the SPP image on server.
    ...
    ...                 Example:
    ...
    ...                 | Mount SPP Image |
    UnixLibrary.Unmount SPP Image
    Run Keyword If      '${SPP_MOUNT_TYPE}' == 'Virtual'    Mount SPP Image By Ilo
    UnixLibrary._Manual Mount SPP Image

Unmount SPP Image
    [Documentation]     Author : Vinay Krishnan
    ...
    ...                 Unmount the SPP image from server.
    ...
    ...                 Example:
    ...
    ...                 | Unmount SPP Image |
    UnixLibrary._Manual Unmount SPP Image
    Run Keyword If      '${SPP_MOUNT_TYPE}' == 'Virtual'    Unmount SPP Image By Ilo

Get SPP Mount Point
    [Documentation]     Author : Vinay Krishnan
    ...
    ...                 Return the SPP mount directory.
    ...
    ...                 Example:
    ...
    ...                 | Get SPP Mount Point |
    : FOR               ${index}            IN RANGE                        1               25
    \                   Sleep               2s
    \                   ${mount_dir} =      SSHLibrary.Execute Command      ${COMMAND_GREP_IMAGE_NAME} | awk '{print $3}'
    \                   @{lines} =          Split To Lines                  ${mount_dir}    0
    \                   ${line_count} =     Get Length                      ${lines}
    \                   Run Keyword If      ${line_count} < 1               Continue For Loop
    \                   ${mount_dir} =      Get From List                   ${lines}        0
    \                   Exit For Loop
    Should Contain      ${mount_dir}        ${SPP_IMAGE_NAME}               Could Not Fetch Mount Point
    [Return]            ${mount_dir}

Reboot Remote Node
    [Documentation]             Author : Vinay Krishnan
    ...
    ...                         Reboot remote node.
    ...
    ...                         Example:
    ...
    ...                         | Reboot Remote Node |
    SSHLibrary.Start Command    reboot

Reboot Server
    [Documentation]             Author : Vinay Krishnan
    ...
    ...                         Reboot server.
    ...
    ...                         Set the one time boot to HDD, issue a power off command and then power on server by ILO
    ...
    ...                         Example:
    ...
    ...                         | Reboot Server |
    Ilo Set One Time Boot       hdd
    SSHLibrary.Start Command    poweroff
    Power ON Server

Clean Logs Server
    [Documentation]     Author : Vinay Krishnan
    ...
    ...                 Deletes the files specified by @{DELETE_LOG_FILES} in config.py
    ...
    ...                 Example:
    ...
    ...                 | Clean Logs Server |
    ${files} =          Catenate    @{DELETE_LOG_FILES_LINUX}
    Log                 ${files}
    SSHLibrary.Execute Command      rm -rf ${files}

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
    ...                     -SI                 ${SYSTEM_IP}                -SU                 ${SYSTEM_USERNAME}
    ...                     -SP                 ${SYSTEM_PASSWORD}          -LL                 ${SUT_LOG_LOCATION}
    ...                     -RU                 ${REMOTE_NODE_USERNAME}     -RP                 ${REMOTE_NODE_PASSWORD}
    ...                     -HV                 ${HPSUM_VERSION}
    ...                     stderr=stderr.txt   stdout=stdout.txt           alias=myproc
    ${mount_point} =        UnixLibrary.Get SPP Mount Point
    ${hpsum_dir} =          Catenate            SEPARATOR=                  ${mount_point}      ${HPSUM_DIR_LINUX}
    ${command}=             Construct Command   ${command_template}
    SSH Run Command         ${command}          ${hpsum_dir}                ${HPSUM_TIMEOUT}
    Terminate Process       myproc              kill=true
    Wait Until Host Power Status                ${ILO_IP}                   True
    Collect HPSUM Logs      @{HPSUM_LOG_FILES_LINUX}

Execute Gatherlogs And Get Log      [Arguments]         ${run_count}=
    [Documentation]     Author : Vinay Krishnan
    ...
    ...                 Execute the gatherlog command and copies the files to ${RG_LOG_PATH}
    ...
    ...                 Example:
    ...
    ...                 | Execute Gatherlogs And Get Log |
    ${status} =         Run Keyword And Return Status   UnixLibrary._Execute GatherLog And Get Log
    Run Keyword IF      '${status}' == 'False'
    ...                 Log         ${run_count} Unable to get gatherlogs   WARN

Deploy Preview Report   [Arguments]         ${command_template}     ${file_tag}
                        [Documentation]     Author : Vinay Krishnan
                        ...
                        ...                 Execute command to generate deploy preview report and copy to ${RG_LOG_PATH}
                        ...
                        ...                 Example:
                        ...
                        ...                 | Deploy Preview Report | ${command_template} | ${file_tag} |
                        ${mount_point} =    UnixLibrary.Get SPP Mount Point
                        ${hpsum_dir} =      Catenate                SEPARATOR=      ${mount_point}
                        ...                 ${HPSUM_DIR_LINUX}
                        ${command}=         Construct Command       ${command_template}
                        UnixLibrary.SSH Run Command                 ${command}      ${hpsum_dir}    ${HPSUM_TIMEOUT}
                        UnixLibrary._Get Deploy Preview Report      ${file_tag}
                        _Check Deploy Preview Report                ${file_tag}

Kill Process PID    [Arguments]                 ${pid}
                    [Documentation]             Author : Chinmaya Kumar Dash
                    ...
                    ...                         Kill process by process ID
                    ...
                    ...                         Example:
                    ...
                    ...                         | Kill Process PID | ${pid} |
                    SSHLibrary.Start Command    kill -9 ${pid}

Kill Process Name   [Arguments]                 ${name}
                    [Documentation]             Author : Chinmaya Kumar Dash
                    ...
                    ...                         Kill process by name
                    ...
                    ...                         | Kill Process PID | ${name} |
                    SSHLibrary.Start Command    killall -r ${name}

Move Log Files To Temp Directory
    [Documentation]     Author : Vinay Krishnan
    ...
    ...                 Move log files specified by @{HPSUM_TEMP_FILES_LINUX} in config.py to temporary directory
    ...
    ...                 Example:
    ...
    ...                 | Move Log Files To Temp Directory |
    SSHLibrary.Start Command                        mkdir ${SYSTEM_TEMP_DIR_LINUX}/temp/
    :FOR                ${file}                     IN                  @{HPSUM_TEMP_FILES_LINUX}
    \                   ${filename} =               Replace String      ${file}     %s      ${SUT_LOG_LOCATION}
    \                   SSHLibrary.Start Command    mv -f ${filename} ${SYSTEM_TEMP_DIR_LINUX}/temp/

Unix Server Setup
    [Documentation]         Author : Vinay Krishnan
    ...
    ...                     Server setup before starting tests.
    ...
    ...                     Performs the following actions
    ...
    ...                     Close all open connections
    ...
    ...                     Connect to ILO and server
    ...
    ...                     Kill any preexisting hpsum process and mount SPP image
    ...
    ...                     Example:
    ...
    ...                     | Unix Server Setup |
    Close All Connections
    Ilo Connect             ${ILO_IP}       ${ILO_USERNAME}         ${ILO_PASSWORD}
    Open Connection SSH     ${SYSTEM_IP}    ${SYSTEM_USERNAME}      ${SYSTEM_PASSWORD}

Testcase Cleanup
    [Documentation]     Author : Chinmaya Kumar Dash
    ...
    ...                 Kill hpsum process, unmount SPP image and move files specified by @{TEMP_TEST_CASE_LOGS} to ${RG_LOG_PATH}
    ...
    ...                 Example:
    ...
    ...                 | Testcase Cleanup |
    Run Keyword And Ignore Error    Kill Process Name   ${HPSUM_SERVICE_NAME}
    Run Keyword And Ignore Error    Unmount SPP Image
    Run Keyword And Ignore Error    Move Files          @{TEMP_TEST_CASE_LOGS}      ${RG_LOG_PATH}

Check Node Architecture
    [Documentation]         Author : Chinmaya Kumar Dash
    ...
    ...                     Copy the Scouting log and detect the remote node type
    ...
    ...                     Example:
    ...
    ...                     | Check Node Architecture |
    ${scouting_log} =       Construct Command   ${SCOUTING_LOG_LINUX}       ${SUT_LOG_LOCATION}
    SSHLibrary.Get File     ${scouting_log}     .\\
    ${node_type} =          Get Node Type
    Run Keyword And Ignore Error                OperatingSystem.Move File   scouting.log    ${RG_LOG_PATH}
    [Return]                ${node_type}

Get HPSUM Version
    [Documentation]         Author:                 Rahul Verma
    ...
    ...                     Check for the bat file in the image
    ...
    ...                     Detects the version of HPSUM
    ...
    ...                     Import config file according to the version
    ...
    ...                     Modified:               Abhishek
    ...                     Date                    :                       29th Nov 2016
    ...                     Make HPSUM version variable a suite variable
    ...
    ...                     Example:
    ...
    ...                     | Get HPSUM Version |
    UnixLibrary.Mount SPP Image
    ${mount_point} =        UnixLibrary.Get SPP Mount Point
    ${STATUS}               Run Keyword And Return Status                   SSHLibrary.File Should Exist
    ...                     ${mount_point}/launch_sum.bat
    ${HPSUM_VERSION} =      Set Variable If
    ...                     ${STATUS} == True       8
    ...                     ${STATUS} == False      7
    Run Keyword If          ${HPSUM_VERSION} == 8   Import Variables        SppLibrary/config/hpsum_config_8.py
    ...                     ELSE IF                 ${HPSUM_VERSION} == 7   Import Variables
    ...                     SppLibrary/config/hpsum_config_7.py
    ...                     ELSE                    Run Keyword If          ${HPSUM_VERSION} != 8 and ${HPSUM_VERSION} != 7
    ...                     Fail                    " Didn't find HPSUM version "
    Set Suite Variable      ${HPSUM_VERSION}

_Execute GatherLog And Get Log
    [Documentation]         Author : Chinmaya Kumar Dash
    ...
    ...                     Executes gather logs command and gets the generated .tar file on to RG_LOG_PATH
    ...
    ...                     Private function used by Execute gatherlogs and get log keyword
    ...
    ...                     Example:
    ...
    ...                     | _Execute GatherLog And Get Log |
    ${GATHER_OUTPUT} =      SSH Run Command         ${COMMAND_GATHERLOGS_LINUX}
    ...                     ${LINUX_GATHERLOGS_DIR}             ${HPSUM_TIMEOUT}
    ${GATHER_LOG_LOCATION} =                        Get Lines Containing String         ${GATHER_OUTPUT}    logs are in
    ${GATHER_LOG_LOCATION} =                        Evaluate
    ...                     re.findall(r'in .*','${GATHER_LOG_LOCATION}')[0].strip('in ')                   modules=re
    SSHLibrary.Start Command                        mv -f ${GATHER_LOG_LOCATION} ${SYSTEM_TEMP_DIR_LINUX}/
    : FOR                   ${index}                IN RANGE    1                       20
    \                       Sleep                   5s
    \                       SSHLibrary.Get File     ${SYSTEM_TEMP_DIR_LINUX}/${GATHER_LOG_LINUX}
    \                       ...                     .\\
    \                       OperatingSystem.Move Files          ${GATHER_LOG_LINUX}     ${RG_LOG_PATH}
    \                       ${status}               ${ret} =    Run Keyword And Ignore Error
    \                       ...                     OperatingSystem.File Should Exist
    \                       ...                     ${RG_LOG_PATH}\\${GATHER_LOG_LINUX}
    \                       Exit For Loop If        '${status}' == 'PASS'

