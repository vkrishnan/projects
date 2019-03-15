*** Settings ***
Documentation   This file contains all common keywords which are used by both
...             Windows and Unix Library.
Library         RoboGalaxyLibrary
Library         DateTime
Library         Collections
Library         OperatingSystem
Library         XML
Library         SSHLibrary


*** Variables ***
${DEPLOY_ERROR_MESSAGE}     Deploy error.
@{ERROR_CODES}              -1      -2      -3


*** Keywords ***

Create Directory For Logs
    [Documentation]             Author : Vinay Krishnan
    ...
    ...                         This creates a new folder with test case name in current working directory and returns the folder name to calling function.
    ...
    ...                         Used in Initialize Test Case Variables keyword
    ...
    ...                         Example:
    ...
    ...                         | Create Dictionary For Log |
    ${current_time} =           Get Current Date    result_format=%Y_%b_%d_%I_%M_%S_%p
    ${log_directory_name} =     Catenate            SEPARATOR=_     ${SUITE NAME}   ${current_time}
    OperatingSystem.Create Directory                logs/${SUITE NAME}/${log_directory_name}/ScreenShots
    OperatingSystem.Create Directory                logs/${SUITE NAME}/${log_directory_name}/Failure_ScreenShots
    OperatingSystem.Directory Should Exist          logs/${SUITE NAME}/${log_directory_name}/ScreenShots
    OperatingSystem.Directory Should Exist          logs/${SUITE NAME}/${log_directory_name}/Failure_ScreenShots
    [Return]                    ${EXECDIR}/logs/${SUITE NAME}/${log_directory_name}

Initialze Test Case Variables
    [Documentation]         Author : Vinay Krishnan
    ...
    ...                     Initialize Log path variable as suite variable.
    ...
    ...                     This keyword calls "Create Directory For Logs" keyword internally which returns the log folder name for current test suite.
    ...                     Return value will be stored in ${RG_LOG_PATH} variable.
    ...
    ...                     Example:
    ...
    ...                     | Initialze Test Case Variables |
    ${RG_LOG_PATH} =        Create Directory For Logs
    Set Suite Variable      ${RG_LOG_PATH}

Return Host Ping Status     [Arguments]         ${host}
    [Documentation]         Author : Vinay Krishnan
    ...
    ...                     Returns Ping Status.
    ...
    ...                     Sends 5 ping to host from RG and based on the output. Return True if host is pinging else False
    ...
    ...                     Used in Wait Until Host Power Status.
    ...
    ...                     ${host} - Test machine's System IP or ILO IP.
    ...
    ...                     Example:
    ...
    ...                     | Return Host Ping Status | ${host} |
    ${output} =             Run                 ping -n 5 ${host}
    ${timeout_count} =      Get Count           '''${output}'''         timed out
    ${unreach_count} =      Get Count           '''${output}'''         unreachable
    ${total_count} =        Evaluate            ${timeout_count}+${unreach_count}
    ${status} =             Set Variable If     ${total_count} > 4      False   True
    [Return]                ${status}

Unmount SPP Image By Ilo
    [Documentation]         Author : Vinay Krishnan
    ...
    ...                     This keyword gets the iLO virtual media status.
    ...
    ...                     If image is connected through applet, it returns vm_applet value as 'CONNECTED' else returns image_inserted as 'YES' for url media.
    ...
    ...                     It will reset the ILO if image is connected through iLO. In case of url media it will just do a eject.
    ...
    ...                     Example:
    ...
    ...                     | Unmount SPP Image By Ilo |
    ${dict} =               Ilo Get Virtual Media Status
    Run Keyword If          ${dict} == None         Fail        Could Not retrieve virtual media status
    ${vm_applet} =          Get From Dictionary     ${dict}     vm_applet
    ${image_inserted} =     Get From Dictionary     ${dict}     image_inserted
    Run Keyword If          '${vm_applet}' == 'CONNECTED'       RunKeywords                     Ilo Reset Rib
    ...                     AND                     Wait Until Host Power Status                ${ILO_IP}   True
    Run Keyword If          '${vm_applet}' == 'DISCONNECTED' and '${image_inserted}' == 'YES'   Ilo Eject Virtual Media

Mount SPP Image By Ilo
    [Documentation]             Author : Vinay Krishnan
    ...
    ...                         This will mount url media to iLO.
    ...
    ...                         Example:
    ...
    ...                         | Mount the SPP image on ILO |
    Sleep                       5s
    Ilo Insert Virtual Media    image_url=${HTTP_IMAGE_PATH}
    Sleep                       5s
    Ilo Set Virtual Media Status

Wait Until Host Power Status                [Arguments]                 ${host}                 ${status}
    ...                 ${ping_time}=${ILO_RESET_PING_TIME}
    [Documentation]     Author : Vinay Krishnan
    ...
    ...                 Waits until the power status of the ${host} matches the status for ${ILO_RESET_PING_TIME}
    ...
    ...                 If ${status} is True, then wait until the server turns ON
    ...
    ...                 If ${status} is False, then wait until the server turns OFF
    ...
    ...                 ${host} - Test machine's System IP.
    ...
    ...                 Example:
    ...
    ...                 | Wait Until Host Power Status | ${host} | ${status} | ${ping_time} |
    :FOR                ${index}            IN RANGE                    1                       ${ping_time}
    \                   ${sleep_time} =     Set Variable If             '${status}' == 'True'   10      20
    \                   Sleep               ${sleep_time}s
    \                   ${output} =         Return Host Ping Status     ${host}
    \                   Exit For Loop If    '${output}' == '${status}'
    ${message} =        Set Variable If     '${status}' == 'True'       start                   shutdown
    Run Keyword If      '${output}' != '${status}'                      Fail                    Server did not ${message}

Power ON Server
    [Documentation]     Author : Vinay Krishnan
    ...
    ...                 Wait for server to turn OFF, then issue a ILO Power ON command and wait for server to boot up.
    ...
    ...                 Example:
    ...
    ...                 | Power ON Server |
    :FOR                ${index}                IN RANGE        1               200
    \                   Sleep                   5s
    \                   ${status} =             Wait Until Keyword Succeeds     5x                      2s
    \                   ...                     Ilo Get Host Power Status
    \                   Exit For Loop If        '${status}' == 'OFF'
    Run Keyword If      '${status}' != 'OFF'    Fail            Server didn't shutdown
    :FOR                ${index}                IN RANGE        1               20
    \                   ${re}                   Run Keyword And Return Status   Ilo Set Host Power      True
    \                   Sleep                   5s
    \                   ${status} =             Wait Until Keyword Succeeds     5x                      2s
    \                   ...                     Ilo Get Host Power Status
    \                   Exit For Loop If        '${status}' == 'ON'
    Run Keyword If      '${status}' != 'ON'     Fail            Server didn't power ON
    Wait Until Host Power Status                ${SYSTEM_IP}    True

Wait Until Power Cycle      [Arguments]     ${host}
    [Documentation]         Author : Vinay Krishnan
    ...
    ...                     Waits until the server turn OFF and then ON. This do a internal call to "Wait Until Host Power Status" keyowrd.
    ...
    ...                     ${host} - Test machine's System IP.
    ...
    ...                     Example:
    ...
    ...                     | Wait Until Power Cycle | ${host} |
    Wait Until Host Power Status            ${host}     False
    Wait Until Host Power Status            ${host}     True

Analyze HPSUM Log   [Arguments]             ${message_tag}=.
                    [Documentation]         Author : Vinay Krishnan
                    ...
                    ...                     Parses the XML file and report the errors matching ${ERROR_CODES} defined in the VARIABLES section.
                    ...
                    ...                     ${XML} - HPSUM_Details.xml file to be parsed.
                    ...
                    ...                     Example:
                    ...
                    ...                     | Get Components Status | HPSUM_Details.xml |
                    ${status} =             Run Keyword And Return Status           OperatingSystem.File Should Exist
                    ...                     ${RG_LOG_PATH}\\${HPSUM_DETAILS_LOG_XML}
                    Return From Keyword If                      'False' in '${status}'
                    ${root} =               Parse XML           ${RG_LOG_PATH}\\${HPSUM_DETAILS_LOG_XML}
                    Should Be Equal         ${root.tag}         HPSUM_InstallDetails
                    @{components} =         Get Elements        ${root}             ComponentResults/Component
                    :FOR                    ${component}        IN                  @{components}
                    \                       ${component_description} =              Get Element     ${component}
                    \                       ...                 ComponentDescription
                    \                       ${result_code} =    Get Element         ${component}    ResultCode
                    \                       ${component_return_code} =              Get Element     ${component}
                    \                       ...                 ComponentReturnCode
                    \                       Log                 ${component_description.text}: ${result_code.text}: ${component_return_code.text}
                    \                       Run Keyword And Continue On Failure     Should Not Contain
                    \                       ...                 ${ERROR_CODES}
                    \                       ...                 ${result_code.text}
                    \                       ...                 ${message_tag}: ${component_description.text}: ${result_code.text}: ${component_return_code.text}
                    \                       ...                 False
                    ${deploy_status} =      Get Element         ${root}             NodeStatus
                    Run Keyword And Continue On Failure         Should Not Contain
                    \                       ...                 ${deploy_status.text}
                    \                       ...                 ${DEPLOY_ERROR_MESSAGE}
                    \                       ...                 ${deploy_status.text} ${message_tag}
                    \                       ...                 False

TPM Check Module
    [Documentation]     Author : Rahul Verma
    ...
    ...                 Check if the TPM module is present on the SUT or not. If present will give a warning.
    ...
    ...                 ${RG_LOG_PATH} - Destination directory on the RG server where the files have to be copied.
    ...
    ...                 Example:
    ...
    ...                 | TPM Check Module |
    ${tpm} =            Tpm Check           ${RG_LOG_PATH}\\${HPSUM_LOG}
    Run Keyword If      '${tpm}' == '1'     Log
    ...                 Warning - A Trusted Platform Module (TPM) has been detected in this system!
    ...                 WARN

Send Script To Blob     [Arguments]         ${script}
                        [Documentation]     Author : Vinay Krishnan
                        ...
                        ...                 Send the python script to ILO Blob.
                        ...
                        ...                 Example:
                        ...
                        ...                 | Send Script To Blob | ${script} |
                        ${rg_root} =        Get RG Root
                        Send Script To Blob Wrapper     ${ILO_IP}   ${ILO_USERNAME}     ${ILO_PASSWORD}     ${BLOB}
                        ...                 ${script}
                        ...                 ${STRAWBERRY_PERL}
                        ...                 ${rg_root}\\${LOCFG_UTILITY}
                        ...                 ${RIBCL_TEMPLATE_XML}

Dependency Check
    [Documentation]         Author : Rahul Verma
    ...
    ...                     Check for dependency of components. If found the keyword will fail with component name with reason for dependency.
    ...
    ...                     Modified : Rahul Verma
    ...
    ...                     Get dictionary with component name as key and reason for dependency as value.
    ...
    ...                     Example:
    ...
    ...                     | Dependency Check |
    ${dependency_dict} =    Check Dependency        ${RG_LOG_PATH}\\${HPSUM_LOG}
    ${check} =              Get From Dictionary     ${dependency_dict}      1
    Return From Keyword If                          None == ${check}
    Run Keyword If          None != ${check}        Move Log Files To Temp Directory
    ${components} =         Get Dictionary Keys     ${check}
    ${len}                  Get Length              ${components}
    :FOR                    ${index}                IN RANGE                0           ${len}
    \                       ${services}             Get From Dictionary     ${check}    ${components[${index}]}
    \                       Log                     Dependency in component:${components[${index}]} and Reason:${services}
    \                       ...                     ERROR
    Run Keyword If          None != ${check}        Fail                    Failed Due to dependency in component(s)

_Check Deploy Preview Report    [Arguments]                     ${file_tag}
    [Documentation]             Author : Chinmaya Kumar Dash
    ...
    ...                         Check for Deploy Preview Report on RG log location.
    ...
    ...                         Example:
    ...
    ...                         | _Check Deploy Preview Report | ${file_tag} |
    ...
    ...                         Private keyword used by Deploy Preview Report in WinLibrary.robot and UnixLibrary.robot.
    ${status} =                 Run Keyword And Return Status   OperatingSystem.File Should Exist
    ...                         ${RG_LOG_PATH}\\${file_tag}_deploy_preview_Report.html
    Run Keyword If              '${status}' == 'False'          Log
    ...                         ${file_tag} deploy preview Report is not generated
    ...                         WARN

Parse Deploy Preview Report     [Arguments]         ${file_tag}
    [Documentation]             Author : Rahul Verma
    ...
    ...                         Parses deploy preview report and checks components to install are there or not.
    ...
    ...                         ${RG_LOG_PATH} - Destination directory on the RG server where the files have to be copied.
    ...
    ...                         ${file_tag} -       HPSUM Deploy Run Count
    ...
    ...                         Example:
    ...
    ...                         | Parse Deploy Preview Report | Logs /${SUITE NAME} /${RG_LOG_PATH} | First Run |
    ${status} =                 Run Keyword And Return Status               OperatingSystem.File Should Exist
    ...                         .\\${RG_LOG_PATH}\\${file_tag}_deploy_preview_Report.html
    Return From Keyword If      '${status}' == 'False'
    ${flag} =                   Run Keyword If      'True' in '${status}'   HPSUM Deploy Report Check
    ...                         ${RG_LOG_PATH}\\${file_tag}_deploy_preview_Report.html
    Run Keyword If              '${file_tag}' == 'First_Run' and ${flag} == 1
    ...                         Log                 "System is already up to date"      WARN
    Run Keyword If              '${file_tag}' == 'Second_Run' and ${flag} == 0 or '${file_tag}' == 'Third_Run' and ${flag} == 0
    ...                         Log                 "Not all components are installed successfully. Check ${file_tag} Deploy Report"
    ...                         WARN

Unmount And Reboot Server
    [Documentation]     Author : Vinay Krishnan
    ...
    ...                 This will call 'Unmount SPP Image' and 'Reboot Server' keyword from either Windows or Linux library depending on script.
    ...
    ...                 Example:
    ...
    ...                 | Unmount And Reboot Server |
    Unmount SPP Image
    Reboot Server

