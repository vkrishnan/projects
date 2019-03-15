*** Settings ***
Documentation   A resource file with reusable keywords and variables for selenium.
...
...             The system specific keywords created here form our own
...             domain specific language.
Library         String
Library         Collections
Library         SppLibrary


*** Variables ***
${BROWSER}                      Firefox
${LOGIN URL}                    https://${SYSTEM_IP}:63002/index.html#/login
${CLICK_TIMEOUT}                2s
${PAGE_LOAD_TIMEOUT}            10s
${INVENTORY_TIMEOUT}            1800
${DEPLOYMENT_TIMEOUT}           1800
${INVENTORY_COMPLETED_MSG}      Inventory completed
${DEPLOYMENT_COMPLETED_MSG}     Deployment completed

${TABLE_REVIEW_PAGE}    hpsum-otu-installables-N1localhost-table

${COMPONENT_SELECT_REVIEW_2}    a#selectToggle-%s-N1localhost-hpToggle.hp-toggle ol li.hp-off

${HPSUM_IMA_RE}     .+\\((.+)\\)

${ID_LOGIN_USERNAME_EDIT}                   hp-login-user
${ID_LOGIN_PASSWORD_EDIT}                   hp-login-password
${ID_LOGIN_LOGIN_BUTTON}                    hp-login-button
${ID_LOGIN_SHUTDOWN_BUTTON}                 hp-shutdown-button
${ID_DEPLOYMENT_MODE_INTERACTIVE_RADIO}     interactive-mode
${ID_DEPLOYMENT_MODE_AUTOMATIC_RADIO}       non-interactive-mode
${ID_DEPLOYMENT_MODE_OK_BUTTON}             hpsum-action-ok-button
${ID_DEPLOYMENT_MODE_CANCEL_BUTTON}         hpsum-action-cancel-button

${XPATH_WELCOME_GUIDED_UPDATE_IMAGE}        .//*[@id='hp-welcome']/div[1]/ol/li[1]/div/a/div/img
${XPATH_WELCOME_BASELINE_LIBRARY_IMAGE}     .//*[@id='hp-welcome']/div[1]/ol/li[2]/div/div/a/div/img
${XPATH_WELCOME_NODES_IMAGE}                .//*[@id='hp-welcome']/div[1]/ol/li[3]/div/a/div/img
${XPATH_WELCOME_SCALABLE_UPDATE_IMAGE}      .//*[@id='hp-welcome']/div[1]/ol/li[4]/div/div/a/div/img
${XPATH_DEPLOYMENT_REBOOT_YES}              /html/body/div[2]/div[8]/div/div/div/footer/div/button[1]

${CSS_WELCOME_GET_STARTED_BUTTON}   a.hp-button.hp-primary
${CSS_INVENTORY_NEXT_BUTTON}        a#step0Next.hp-primary.hp-button
${CSS_REVIEW_DEPLOY_BUTTON}         a#step1Next.hp-primary.hp-button
${CSS_DEPLOYMENT_REBOOT}            a#step2Reboot.hp-primary.hp-button.hp-secondary

${RADIONAME_GUIDED_UPDATE_SHOW_MODE_RADIO}      mode-option


*** Keywords ***

Wait Until Inventory Operation Completes        [Arguments]                 ${timeout}
    [Documentation]     Wait Until Inventory Operation Completes.
    ...
    ...                 Wait until Inventory complete within given time out.
    ...
    ...                 ${timeout} - Waiting time for complete operation.
    ...
    ...                 Return operation status.
    ...
    ...                 Example:
    ...
    ...                 | Wait Until Inventory Operation Completes | 1800sec |
    Sleep               20s
    Set Test Variable   ${status_read}          Inventory completed
    ${status}           ${node_value} =         Run Keyword And Ignore Error                        Get Table Cell
    ...                 hpsum-otu-inventory-node
    ...                 2
    ...                 2
    Run Keyword If      '${status}' == 'FAIL'   Capture Page Screenshot
    Run Keyword If      '${status}' != 'PASS'   Fail                        " Inventory page couldn't open "
    Run Keyword If      '${node_value}' != 'localhost'                      Return From Keyword
    ...                 Error In Reading Page Data
    : FOR               ${index}                IN RANGE                    1                       ${timeout}
    \                   Sleep                   1s
    \                   ${status} =             Get Table Cell              hpsum-otu-inventory-node    2
    \                   ...                     3
    \                   Run Keyword If          '${status.strip()}' == '${status_read}'             Exit For Loop
    \                   Run Keyword If          'Install done with error' in '${status.strip()}'    Exit For Loop
    ${message} =        Get Table Cell          hpsum-otu-inventory-node    2                       5
    [Return]            ${status}:${message}

Wait Until Deployment Operation Completes       [Arguments]                     ${timeout}
    [Documentation]     Wait Until Deployment Operation Completes.
    ...
    ...                 Wait until Deployment complete within given time out.
    ...
    ...                 ${timeout} - Waiting time for complete operation.
    ...
    ...                 Return operation status.
    ...
    ...                 Example:
    ...
    ...                 | Wait Until Deployment Operation Completes             | 1800sec |
    Sleep               20s
    Set Test Variable   ${status_read}          Deployment completed
    ${status}           ${node_value} =         Run Keyword And Ignore Error    Get Table Cell      hpsum-otu-install-progress
    ...                 2
    ...                 2
    Run Keyword If      '${status}' == 'FAIL'   Capture Page Screenshot
    Run Keyword If      '${status}' == 'FAIL'   Uncheck Dependency Components
    ${RSTATUS}          Run Keyword If          '${status}' == 'FAIL'           Run Keyword And Return Status   Click Element
    ...                 css=${CSS_REVIEW_DEPLOY_BUTTON}
    Run Keyword If      '${status}' == 'FAIL'   Run Keyword If                  '${RSTATUS}' != 'True'          Fail
    ...                 No Components to install in review page
    Sleep               20s
    ${status}           ${node_value} =         Run Keyword And Ignore Error    Get Table Cell      hpsum-otu-install-progress
    ...                 2
    ...                 2
    Run Keyword If      '${node_value}' != 'localhost'                          Return From Keyword
    ...                 Error In Reading Page Data
    : FOR               ${index}                IN RANGE                        1                   ${timeout}
    \                   Sleep                   1s
    \                   ${status} =             Get Table Cell                  hpsum-otu-install-progress      2
    \                   ...                     3
    \                   Run Keyword If          '${status.strip()}' == '${status_read}'             Exit For Loop
    \                   Run Keyword If          'Install done with error' in '${status.strip()}'    Exit For Loop
    ${message} =        Get Table Cell          hpsum-otu-install-progress      2                   5
    [Return]            ${status}:${message}

Select Components   [Arguments]         ${RUN_COUNT}
                    [Documentation]     Selecting the IMA , SNMP, WWBEM and SMH components for deployment by force.
                    ...
                    ...                 select components in review page.
                    ...
                    ...                 ${RUN_COUNT} - Execution of guided install first time or second time.
                    ...
                    ...                 Example:
                    ...
                    ...                 | Select Components | ${RUN_COUNT} |
                    ${COUNT}            Wait Until Keyword Succeeds                         1min                    1sec
                    ...                 Get Matching Xpath Count    xpath=//*[@id='hpsum-otu-installables-N1localhost-table']/tbody/tr
                    ${COUNT} =          Evaluate                    ${COUNT} + 1
                    : FOR               ${index}                    IN RANGE                1                       ${COUNT}
                    \                   Log                         ${index}
                    \                   Sleep                       2
                    \                   Run Keyword If              '${index}' == '1'       Run Keyword And Ignore Error
                    \                   ...                         Mouse Over
                    \                   ...                         xpath=//*[@id='hpsum-otu-installables-N1localhost-table']/tbody/tr[10]/td[2]
                    \                   Run Keyword If              '${index}' == '1'       Sleep                   3
                    \                   Run Keyword If              '${index}' == '3'       Run Keyword And Ignore Error
                    \                   ...                         Mouse Over
                    \                   ...                         xpath=//*[@id='hpsum-otu-installables-N1localhost-table']/thead/tr/td[1]/b
                    \                   Run Keyword If              '${index}' == '3'       Sleep                   3
                    \                   Run Keyword If              '${index}' == '3'       Capture Page Screenshot
                    \                   ...                         filename=${RG_LOG_PATH}/ScreenShots/Guided_Review_Components_${RUN_COUNT}_1.png
                    \                   Run Keyword If              '${index}' == '6'       Run Keyword And Ignore Error
                    \                   ...                         Mouse Over
                    \                   ...                         xpath=//*[@id='hpsum-step2']
                    \                   Run Keyword If              '${index}' == '9'       Run Keyword And Ignore Error
                    \                   ...                         Mouse Over
                    \                   ...                         xpath=//*[@id='hpsum-otu-installables-N1localhost-table']/tbody/tr[${index}]/td[2]
                    \                   Run Keyword If              '${index}' == '9'       Sleep                   3
                    \                   Run Keyword If              '${index}' == '9'       Capture Page Screenshot
                    \                   ...                         filename=${RG_LOG_PATH}/ScreenShots/Guided_Review_Components_${RUN_COUNT}_2.png
                    \                   Run Keyword If              '${index}' == '12'      Run Keyword And Ignore Error
                    \                   ...                         Mouse Over
                    \                   ...                         xpath=//*[@id='hpsum-otu-installables-N1localhost-table']/tbody/tr[7]/td[2]
                    \                   Run Keyword If              '${index}' == '16'      Run Keyword And Ignore Error
                    \                   ...                         Mouse Over
                    \                   ...                         xpath=//*[@id='hpsum-otu-installables-N1localhost-table']/tbody/tr[${index}]/td[2]
                    \                   Run Keyword If              '${index}' == '16'      Sleep                   3
                    \                   Run Keyword If              '${index}' == '16'      Capture Page Screenshot
                    \                   ...                         filename=${RG_LOG_PATH}/ScreenShots/Guided_Review_Components_${RUN_COUNT}_3.png
                    \                   Run Keyword If              '${index}' == '20'      Run Keyword And Ignore Error
                    \                   ...                         Mouse Over
                    \                   ...                         xpath=//*[@id='hpsum-otu-installables-N1localhost-table']/tbody/tr[14]/td[2]
                    \                   Run Keyword If              '${index}' == '23'      Run Keyword And Ignore Error
                    \                   ...                         Mouse Over
                    \                   ...                         xpath=//*[@id='hpsum-otu-installables-N1localhost-table']/tbody/tr[${index}]/td[2]
                    \                   Run Keyword If              '${index}' == '23'      Sleep                   3
                    \                   Run Keyword If              '${index}' == '23'      Capture Page Screenshot
                    \                   ...                         filename=${RG_LOG_PATH}/ScreenShots/Guided_Review_Components_${RUN_COUNT}_4.png
                    \                   Run Keyword If              '${index}' == '28'      Run Keyword And Ignore Error
                    \                   ...                         Mouse Over
                    \                   ...                         xpath=//*[@id='hpsum-otu-installables-N1localhost-table']/tbody/tr[22]/td[2]
                    \                   Run Keyword If              '${index}' == '30'      Run Keyword And Ignore Error
                    \                   ...                         Mouse Over
                    \                   ...                         xpath=//*[@id='hpsum-otu-installables-N1localhost-table']/tbody/tr[${index}]/td[2]
                    \                   Run Keyword If              '${index}' == '30'      Sleep                   3
                    \                   Run Keyword If              '${index}' == '30'      Capture Page Screenshot
                    \                   ...                         filename=${RG_LOG_PATH}/ScreenShots/Guided_Review_Components_${RUN_COUNT}_5.png
                    \                   ${status}                   ${switch} =             Run Keyword And Ignore Error
                    \                   ...                         Get Text
                    \                   ...                         xpath=//*[@id='hpsum-otu-installables-N1localhost-table']/tbody/tr[${index}]/td[1]
                    \                   ${status}                   ${value} =              Run Keyword And Ignore Error
                    \                   ...                         Get Text
                    \                   ...                         xpath=//*[@id='hpsum-otu-installables-N1localhost-table']/tbody/tr[${index}]/td[2]
                    \                   ${id} =                     Run Keyword If          'SNMP Agents' in '${value}'
                    \                   ...                         Re Match
                    \                   ...                         ${HPSUM_IMA_RE}         ${value}
                    \                   ${id1} =                    Run Keyword If          'smh-templates' in '${value}'
                    \                   ...                         Re Match
                    \                   ...                         ${HPSUM_IMA_RE}         ${value}
                    \                   ${id2} =                    Run Keyword If
                    \                   ...                         'Insight Management Agents' in '${value}'
                    \                   ...                         Re Match
                    \                   ...                         ${HPSUM_IMA_RE}         ${value}
                    \                   ${id3} =                    Run Keyword If          'WBEM' in '${value}'    Re Match
                    \                   ...                         ${HPSUM_IMA_RE}         ${value}
                    \                   Run Keyword If              '${status}' == 'FAIL'   Exit For Loop
                    \                   Run Keyword If              'SNMP Agents' in '${value}' and 'Select' in '${switch}'
                    \                   ...                         Run Keyword And Ignore Error                    Click Component
                    \                   ...                         ${id}
                    \                   Run Keyword If              'smh-templates' in '${value}' and 'Select' in '${switch}'
                    \                   ...                         Run Keyword And Ignore Error                    Click Component
                    \                   ...                         ${id1}
                    \                   Run Keyword If              'Insight Management Agents' in '${value}' and 'Select' in '${switch}'
                    \                   ...                         Run Keyword And Ignore Error                    Click Component
                    \                   ...                         ${id2}
                    \                   Run Keyword If              'WBEM' in '${value}' and 'Select' in '${switch}'
                    \                   ...                         Run Keyword And Ignore Error                    Click Component
                    \                   ...                         ${id3}

Click Component     [Arguments]         ${id}
                    [Documentation]     Click component on review page.
                    ...
                    ...                 Construct xpath with given parameter.
                    ...
                    ...                 ${id} - Component text to construct xpath.
                    ...
                    ...                 No return value.
                    ...
                    ...                 Example:
                    ...
                    ...                 | Click Component | ${id}|
                    ${id} =             Replace String      ${id}           .               _
                    ${ima_id} =         Construct Command   ${COMPONENT_SELECT_REVIEW_2}    ${id}
                    Run Keyword And Ignore Error            Click Element   css=${ima_id}

Open Browser And Login
    [Documentation]     Open Firefox Browser with given user name and password and maximize Window.
    ...
    ...                 check page title is Smart Update Manager or not.
    ...
    ...                 No return value.
    ...
    ...                 Example:
    ...
    ...                 | Open Browser And Login | No parameters|
    ${FF_PROFILE} =     Get Firefox Profile     ${FF_PROFILE_TEMPLATE}
    Wait Until Keyword Succeeds                 1 min   1 sec   Open Browser    ${LOGIN URL}    ${BROWSER}
    ...                 ff_profile_dir=${FF_PROFILE}

    Wait Until Keyword Succeeds     1 min       1 sec               Maximize Browser Window
    : FOR   ${index}                IN RANGE    1                   4
    \       ${title} =              Wait Until Keyword Succeeds     1 min           1 sec   Get Title
    \       Run Keyword If          'Smart Update Manager' not in '${title}'        Reload Page
    \       Run Keyword And Ignore Error        Wait Until Element Is Visible
    \       ...                     xpath=//*[@id='hp-login-page']/header/div[2]    300
    \       Run Keyword If          'Smart Update Manager' in '${title}'            Exit For Loop

    Run Keyword If          'Smart Update Manager' not in '${title}'    Fail
    ...                     " Problem in Loading HP Smart Update Manager page "
    Sleep                   ${CLICK_TIMEOUT}
    Input Text              ${ID_LOGIN_USERNAME_EDIT}                   ${SYSTEM_USERNAME}
    Sleep                   ${CLICK_TIMEOUT}
    Input Text              ${ID_LOGIN_PASSWORD_EDIT}                   ${SYSTEM_PASSWORD}
    Sleep                   ${CLICK_TIMEOUT}
    Click Button            ${ID_LOGIN_LOGIN_BUTTON}
    Sleep                   ${PAGE_LOAD_TIMEOUT}
    Page Should Contain     Smart Update Manager

Start Guided Interactive Installation   [Arguments]     ${RUN_COUNT}    ${SYSTEM_OS}
    [Documentation]             Install SPP with GUI.
    ...
    ...                         Wait Until Inventory Node Operation and Deployment operation Completes .
    ...
    ...                         ${LOG_PATH} - Destination directory on the RG server where the files have to be copied.
    ...
    ...                         ${pid} - Process id of HPSUM.
    ...
    ...                         ${RUN_COUNT} - Execution of guided install first time or second time.
    ...
    ...                         Return value is True or False.
    ...
    ...                         Example:
    ...
    ...                         | Start Guided Interactive Installation | ${LOG_PATH}| ${pid} | first_run |
    Wait Until Keyword Succeeds         1 min           1 sec           Click Element
    ...                         xpath=${XPATH_WELCOME_GUIDED_UPDATE_IMAGE}
    Sleep                       10s
    Select Radio Button         ${RADIONAME_GUIDED_UPDATE_SHOW_MODE_RADIO}
    ...                         ${ID_DEPLOYMENT_MODE_INTERACTIVE_RADIO}
    Radio Button Should Be Set To       ${RADIONAME_GUIDED_UPDATE_SHOW_MODE_RADIO}
    ...                         ${ID_DEPLOYMENT_MODE_INTERACTIVE_RADIO}
    Wait Until Keyword Succeeds         1 min           1 sec           Click Button
    ...                         ${ID_DEPLOYMENT_MODE_OK_BUTTON}
    Sleep                       5
    Capture Page Screenshot     filename=${RG_LOG_PATH}/ScreenShots/Guided_Inventory_info_${RUN_COUNT}_1.png

    ##                          Wait until Inventory Operation Completes
    ${ret} =                    Wait Until Inventory Operation Completes        ${INVENTORY_TIMEOUT}
    Run Keyword If              '${INVENTORY_COMPLETED_MSG}' not in '${ret}'    Fail    ${ret}
    Run Keyword And Ignore Error    Mouse Over                  xpath=//*[@id='step0commands']
    Capture Page Screenshot     filename=${RG_LOG_PATH}/ScreenShots/Guided_Inventory_info_${RUN_COUNT}_2.png
    Sleep                       3
    Wait Until Keyword Succeeds     1 min                       1 sec           Click Element
    ...                         css=${CSS_INVENTORY_NEXT_BUTTON}
    Sleep                       ${PAGE_LOAD_TIMEOUT}
    Capture Page Screenshot     filename=${RG_LOG_PATH}/ScreenShots/Guided_Review_info_${RUN_COUNT}.png
    Run Keyword And Ignore Error    Select Components           ${RUN_COUNT}
    Run Keyword And Ignore Error    Mouse Over                  xpath=//*[@id='step1commands']
    Sleep                       4
    Capture Page Screenshot     filename=${RG_LOG_PATH}/ScreenShots/Guided_Review_Info_${RUN_COUNT}_6.png
    ${RSTATUS}                  Run Keyword And Return Status   Click Element
    ...                         css=${CSS_REVIEW_DEPLOY_BUTTON}

    ##      Change HPSUM_InstallDetails.xml file name as HPSUM_InstallDetails_first_run.xml if components in second run
    Run Keyword And Ignore Error        Run Keyword If
    ...     'True' in '${RSTATUS}' and '${RUN_COUNT}' == 'Second_Run'
    ...     OperatingSystem.Move File   ${RG_LOG_PATH}/HPSUM_InstallDetails.xml
    ...     ${RG_LOG_PATH}/HPSUM_InstallDetails_first_run.xml

    ##          Wait until Deployment Operation Completes
    ${ret} =    Run Keyword If      'True' in '${RSTATUS}'
    ...         Wait Until Deployment Operation Completes   ${DEPLOYMENT_TIMEOUT}

    ##                  Copy HPSUM_InstallDetails.xml file into SUT from RG logpath if no components in second run
    Run Keyword And Continue On Failure                 Run Keyword If
    ...                 'True' not in '${RSTATUS}' and '${RUN_COUNT}' == 'Second_Run' and '${SYSTEM_OS}' == 'Windows'
    ...                 SppLibrary.Put File             ${RG_LOG_PATH}\\HPSUM_InstallDetails.xml
    ...                 C:\\cpqsystem\\hp\\log\\${SUT_LOG_LOCATION}\\
    Run Keyword And Continue On Failure                 Run Keyword If
    ...                 'True' not in '${RSTATUS}' and '${RUN_COUNT}' == 'Second_Run' and '${SYSTEM_OS}' == 'Linux'
    ...                 SSHLibrary.Put File
    ...                 ${RG_LOG_PATH}\\HPSUM_InstallDetails.xml
    ...                 /var/hp/log/${SUT_LOG_LOCATION}/HPSUM_InstallDetails.xml
    Run Keyword If      'True' not in '${RSTATUS}'      Return From Keyword     ${RSTATUS}
    Sleep               10

    ##                          Take deployment components screen-shorts
    ${COUNT}                    Wait Until Keyword Succeeds         1min            1sec
    ...                         Get Matching Xpath Count            xpath=//*[@id='hpsum-otu-node-N1localhost-installresult-table']/tbody/tr
    Run Keyword And Ignore Error                    Mouse Over      xpath=//*[@id='step2commands']
    Sleep                       3
    Run Keyword If              ${COUNT} > 1        Run Keyword And Ignore Error    Mouse Over
    ...                         xpath=//*[@id='hpsum-otu-node-N1localhost-installresult-table']/thead/tr/th[2]
    Sleep                       3
    Run Keyword If              ${COUNT} > 1        Capture Page Screenshot
    ...                         filename=${RG_LOG_PATH}/ScreenShots/Guided_Deployment_Components_${RUN_COUNT}_1.png
    Run Keyword And Ignore Error                    Mouse Over      xpath=//*[@id='step2commands']
    Run Keyword If              ${COUNT} > 8        Run Keyword And Ignore Error    Mouse Over
    ...                         xpath=//*[@id='hpsum-otu-node-N1localhost-installresult-table']/tbody/tr[8]/td[3]
    Sleep                       3
    Run Keyword If              ${COUNT} > 8        Capture Page Screenshot
    ...                         filename=${RG_LOG_PATH}/ScreenShots/Guided_Deployment_Components_${RUN_COUNT}_2.png
    Run Keyword And Ignore Error                    Mouse Over      xpath=//*[@id='step2commands']
    Sleep                       3
    Capture Page Screenshot     filename=${RG_LOG_PATH}/ScreenShots/Guided_Deployment_info_${RUN_COUNT}_2.png
    Run Keyword If              'True' in '${RSTATUS}'              Run Keyword And Continue On Failure
    ...                         Run Keyword If      '${DEPLOYMENT_COMPLETED_MSG}' not in '${ret}'   Fail    ${ret}

    ##                  Copy log files into RG log path
    Run Keyword And Continue On Failure                 Copy HPSUM_Details And Analyse      ${RSTATUS}      ${RUN_COUNT}
    Unmount SPP Image By Ilo
    ${RSTATUS}          Run Keyword And Return Status   Wait Until Keyword Succeeds         1 min
    ...                 1 sec
    ...                 Click Element                   css=${CSS_DEPLOYMENT_REBOOT}
    Sleep               ${CLICK_TIMEOUT}
    Run Keyword If      'True' in '${RSTATUS}'          Click Element
    ...                 xpath=${XPATH_DEPLOYMENT_REBOOT_YES}
    [Return]            ${RSTATUS}
    Close Browser

Uncheck Dependency Components
    ${src}=             Get Source
    OperatingSystem.Create File                     ${RG_LOG_PATH}/source.html      ${src}
    ${comp_id} =        Uncheck Dependency Comp     ${RG_LOG_PATH}\\source.html
    ${len} =            Get Length                  ${comp_id}
    Run Keyword If      '${len}'=='0'               Run Keywords                    Log     No Components to install    WARN
    ...                 AND
    ...                 Return From Keyword
    :FOR                ${i}                        IN RANGE                        0       ${len}
    \                   Click Element               id=${comp_id[${i}]}

