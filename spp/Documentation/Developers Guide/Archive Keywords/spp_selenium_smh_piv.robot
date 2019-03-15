*** Settings ***
Documentation   A resource file with reusable keywords and variables for PIV Verification on SMH using selenium.
...
...             The system specific keywords created here form our own
...             domain specific language.

Library     BuiltIn
Library     String
Library     Collections
Library     SppLibrary
Library     OperatingSystem


*** Variables ***
${BROWSER}              Firefox
${SMH_LOGIN_URL}        https://${SYSTEM_IP}:2381/
${WEBAPP_LOGIN_URL}     https://${SYSTEM_IP}:2381/hpdiags/frontend2/startup.php?
${SSA_LOGIN_URL}        https://${SYSTEM_IP}:2381/HPSSA/index.htm
${STATUS}
${FLAG}


*** Keywords ***

Open Browser And Login SMH
    [Documentation]     Open Browser and Login SMH Page
    ${FF_PROFILE} =     Get Firefox Profile             ${FF_PROFILE_TEMPLATE}
    Sleep               2
    Wait Until Keyword Succeeds                         3 min   1 sec                   Open Browser    ${SMH_LOGIN_URL}
    ...                 ${BROWSER}
    ...                 ff_profile_dir=${FF_PROFILE}
    Sleep               1
    Wait Until Keyword Succeeds                         1 min   1 sec                   Maximize Browser Window
    ${passed} =         Run Keyword And Return Status   Wait Until Keyword Succeeds     1 min           1 sec   Input Text
    ...                 user
    ...                 ${SYSTEM_USERNAME}
    Sleep               1
    Run Keyword If      '${passed}' == 'False'          Fail    User Name/Password Error.
    ${passed} =         Run Keyword And Return Status   Wait Until Keyword Succeeds     1 min           1 sec   Input Text
    ...                 password
    ...                 ${SYSTEM_PASSWORD}
    Sleep               1
    Run Keyword If      '${passed}' == 'False'          Fail    User Name/Password Error.
    ${passed} =         Run Keyword And Return Status   Wait Until Keyword Succeeds     2 min           1 sec   Click Element
    ...                 logonButton
    Run Keyword If      '${passed}' == 'False'          Fail    Login Failed
    ${TITLE}            Wait Until Keyword Succeeds     2 min   1 sec                   Get Title
    Should Contain      ${TITLE}                        System Management Homepage

Home Page Screenshot    [Arguments]     ${SMH_MODE}
                        Sleep           10
                        Wait Until Keyword Succeeds                 1 min   1 sec
                        ...             Capture Page Screenshot     filename=${RG_LOG_PATH}/ScreenShots/HOME_PAGE_${SMH_MODE}.png

Home Page
    [Documentation]     Go to Home Page
    unselect frame
    Sleep               5
    Wait Until Keyword Succeeds     1 min   1 sec   Select Frame    name=CHPHeaderFrame
    Wait Until Keyword Succeeds     1 min   1 sec   Click Element   xpath=//*[@id='menu']/ul/li[1]/a
    Sleep               6
    unselect frame

Change Window Format
    [Documentation]     Align windows by name
    ${TITLE}            Wait Until Keyword Succeeds     2 min   1 sec   Get Title
    Should Contain      ${TITLE}                        System Management Homepage
    Wait Until Keyword Succeeds                         1 min   1 sec   unselect frame
    Wait Until Keyword Succeeds                         2 min   1 sec   Select Frame    name=CHPHeaderFrame
    Sleep               10
    Wait Until Keyword Succeeds                         1 min   1 sec   Click Element   xpath=//*[@id='menu']/ul/li[2]/a
    Sleep               15
    unselect frame
    Wait Until Keyword Succeeds                         1 min   1 sec   Select Frame    name=CHPDataFrame
    Wait Until Keyword Succeeds                         1 min   1 sec   Click Element
    ...                 xpath=html/body/table/tbody/tr/td/div[3]/div[1]/ul/li[3]/div/a
    Sleep               2
    Wait Until Keyword Succeeds                         1 min   1 sec   Click Element
    ...                 xpath=/html/body/table/tbody/tr/td/div[2]/div/form/table/tbody/tr/td[1]/fieldset/div[1]/select/option[3]
    Sleep               2
    Wait Until Keyword Succeeds                         1 min   1 sec   Click Element
    ...                 xpath=/html/body/table/tbody/tr/td/div[2]/div/form/table/tbody/tr/td[1]/fieldset/div[2]/select/option[1]
    Sleep               2
    Wait Until Keyword Succeeds                         1 min   1 sec   Click Element
    ...                 xpath=/html/body/table/tbody/tr/td/div[2]/div/form/table/tbody/tr/td[1]/fieldset/div[3]/select/option[1]
    Sleep               2
    Wait Until Keyword Succeeds                         1 min   1 sec   Click Element   xpath=//*[@id='applyButton']
    Home Page

Change Window Format Linux
    [Documentation]     Align windows by name
    ${TITLE}            Wait Until Keyword Succeeds     2 min   1 sec   Get Title
    Should Contain      ${TITLE}                        System Management Homepage
    Wait Until Keyword Succeeds                         2 min   1 sec   Select Frame    name=CHPHeaderFrame
    Sleep               10
    Wait Until Keyword Succeeds                         1 min   1 sec   Click Element   xpath=//*[@id='menu']/ul/li[2]/a
    Sleep               15
    Wait Until Keyword Succeeds                         1 min   1 sec   unselect frame
    Wait Until Keyword Succeeds                         1 min   1 sec   Select Frame    name=CHPDataFrame
    Wait Until Keyword Succeeds                         1 min   1 sec   Click Element
    ...                 xpath=html/body/table/tbody/tr/td/div[2]/div[1]/ul/li[3]/div/a
    Sleep               2
    Wait Until Keyword Succeeds                         1 min   1 sec   Click Element
    ...                 xpath=/html/body/table/tbody/tr/td/div[2]/div/form/table/tbody/tr/td[1]/fieldset/div[1]/select/option[3]
    Wait Until Keyword Succeeds                         1 min   1 sec   Click Element
    ...                 xpath=/html/body/table/tbody/tr/td/div[2]/div/form/table/tbody/tr/td[1]/fieldset/div[2]/select/option[1]
    Wait Until Keyword Succeeds                         1 min   1 sec   Click Element
    ...                 xpath=/html/body/table/tbody/tr/td/div[2]/div/form/table/tbody/tr/td[1]/fieldset/div[3]/select/option[1]
    Wait Until Keyword Succeeds                         1 min   1 sec   Click Element   xpath=//*[@id='applyButton']
    Home Page

Change Window To SNMP
    [Documentation]     Set display mode to SNMP
    Wait Until Keyword Succeeds                 1 min   1 sec   unselect frame
    Wait Until Keyword Succeeds                 1 min   1 sec   Select Frame                    CHPHeaderFrame
    Wait Until Keyword Succeeds                 1 min   1 sec   Click Element                   xpath=//*[@id='menu']/ul/li[2]/a
    Sleep               15
    Wait Until Keyword Succeeds                 1 min   1 sec   unselect frame
    Wait Until Keyword Succeeds                 1 min   1 sec   Select Frame                    CHPDataFrame
    RoboGalaxyLibrary.Element Text Should Be    xpath=html/body/table/tbody/tr/td/div[2]/h4     Select SMH Data Source
    ...                 SMH tab doesn't contain
    Wait Until Keyword Succeeds                 1 min   1 sec   Click Element
    ...                 xpath=html/body/table/tbody/tr/td/div[2]/div[1]/ul/li/div/a
    Sleep               3
    Wait Until Keyword Succeeds                 1 min   1 sec   Click Element
    ...                 xpath=//*[@id='t1']/tbody/tr/td/form/input[11]
    Wait Until Keyword Succeeds                 1 min   1 sec   Click Element
    ...                 xpath=//*[@id='t1']/tbody/tr/td/form/input[15]
    Wait Until Keyword Succeeds                 1 min   1 sec   unselect frame
    Sleep               80
    Wait Until Keyword Succeeds                 1 min   1 sec   Close Browser
    Open Browser And Login SMH

Change Window To WBEM
    [Documentation]     Set display mode to WBEM
    Wait Until Keyword Succeeds     1 min   1 sec                       unselect frame
    Wait Until Keyword Succeeds     1 min   1 sec                       Select Frame    CHPHeaderFrame
    Wait Until Keyword Succeeds     1 min   1 sec                       Click Element   xpath=//*[@id='menu']/ul/li[2]/a
    Sleep               15
    Wait Until Keyword Succeeds     1 min   1 sec                       unselect frame
    Wait Until Keyword Succeeds     1 min   1 sec                       Select Frame    CHPDataFrame
    Wait Until Keyword Succeeds     1 min   1 sec                       RoboGalaxyLibrary.Element Text Should Be
    ...                 xpath=html/body/table/tbody/tr/td/div[1]/h4     Select SMH Data Source
    ...                 SMH tab doesn't contain
    Wait Until Keyword Succeeds     1 min   1 sec                       Click Element
    ...                 xpath=html/body/table/tbody/tr/td/div[1]/div[1]/ul/li/div/a
    Sleep               3
    Wait Until Keyword Succeeds     1 min   1 sec                       Click Element
    ...                 xpath=//*[@id='t1']/tbody/tr/td/form/input[12]
    Wait Until Keyword Succeeds     1 min   1 sec                       Click Element
    ...                 xpath=//*[@id='t1']/tbody/tr/td/form/input[15]
    Wait Until Keyword Succeeds     1 min   1 sec                       unselect frame
    Sleep               80
    Wait Until Keyword Succeeds     1 min   1 sec                       Close Browser
    Open Browser And Login SMH

Firmware and Software Version Info SNMP
    [Documentation]     Get Firmware and Software information in SNMP mode
    Home Page
    Wait Until Keyword Succeeds                 1 min               1 sec       Select Frame    name=CHPDataFrame
    ${TITLE}            Wait Until Keyword Succeeds                 2 min       1 sec           Get Title
    Should Contain      ${TITLE}                System Management Homepage
    Sleep               10
    Click Link          Software / Firmware Version Info
    ${DIC_SOFTWARE} =   Create Dictionary
    ${COUNT}            Wait Until Keyword Succeeds                 1 min       1 sec
    ...                 Get Matching Xpath Count
    ...                 xpath=html/body/center/table[2]/tbody/tr
    ${COUNT} =          Evaluate                ${COUNT} + 1
    Sleep               5
    Wait Until Keyword Succeeds                 1 min               1 sec       Capture Page Screenshot
    ...                 filename=${RG_LOG_PATH}/ScreenShots/SNMP_Software_info.png
    Sleep               2
    Execute JavaScript    window.scrollTo(0,2000)
    Sleep               5
    Wait Until Keyword Succeeds                 1 min               1 sec       Capture Page Screenshot
    ...                 filename=${RG_LOG_PATH}/ScreenShots/SNMP_Firmware_info.png
    : FOR               ${INDEX}                IN RANGE            2           ${COUNT}
    \                   ${FNAME}                Wait Until Keyword Succeeds     1 min           1 sec   Get Text
    \                   ...                     xpath=html/body/center/table[2]/tbody/tr[${INDEX}]/td[1]/small/font
    \                   ${FVERSION}             Wait Until Keyword Succeeds     1 min           1 sec   Get Text
    \                   ...                     xpath=html/body/center/table[2]/tbody/tr[${INDEX}]/td[2]/small/font
    \                   Set To Dictionary       ${DIC_SOFTWARE}     ${FNAME}    ${FVERSION}
    @{var1}             Get Dictionary Items    ${DIC_SOFTWARE}
    Log                 SOFTWARE LOG
    : FOR               ${INDEX}                IN                  @{var1}
    \                   Log                     ${INDEX}
    ${DIC_FIRMWARE} =   Create Dictionary
    ${COUNT}            Wait Until Keyword Succeeds                 1 min       1 sec
    ...                 Get Matching Xpath Count
    ...                 xpath=html/body/center/table[4]/tbody/tr
    ${COUNT} =          Evaluate                ${COUNT} + 1
    : FOR               ${INDEX}                IN RANGE            2           ${COUNT}
    \                   ${FNAME}                Wait Until Keyword Succeeds     1 min           1 sec   Get Text
    \                   ...                     xpath=html/body/center/table[4]/tbody/tr[${INDEX}]/td[1]/small/font
    \                   ${FVERSION}             Wait Until Keyword Succeeds     1 min           1 sec   Get Text
    \                   ...                     xpath=html/body/center/table[4]/tbody/tr[${INDEX}]/td[2]/small/font
    \                   Set To Dictionary       ${DIC_FIRMWARE}     ${FNAME}    ${FVERSION}
    @{var1}             Get Dictionary Items    ${DIC_FIRMWARE}
    Log                 FIRMWARE LOG
    : FOR               ${INDEX}                IN                  @{var1}
    \                   Log                     ${INDEX}

Firmware and Software Version Info SNMP Linux
    [Documentation]     Get Firmware and Software information in SNMP mode
    Home Page
    Wait Until Keyword Succeeds                         1 min   1 sec   Select Frame    name=CHPDataFrame
    ${TITLE}            Wait Until Keyword Succeeds     2 min   1 sec   Get Title
    Should Contain      ${TITLE}                        System Management Homepage
    Sleep               10

    Wait Until Keyword Succeeds                     1 min                   1 sec
    ...                     RoboGalaxyLibrary.Element Text Should Be
    ...                     xpath=html/body/table/tbody/tr/td/div[6]/h4     System
    ...                     System tab doesn't contain
    ${software_version} =   Run Keyword And Return Status                   Wait Until Page Contains
    ...                     Software Version Info
    Run Keyword If          '${software_version}'=='True'                   Click Link      Software Version Info
    ${software_firmware_version} =                  Run Keyword And Return Status           Wait Until Page Contains
    ...                     Software/Firmware Version Information
    Run Keyword If          '${software_firmware_version}'=='True'          Click Link
    ...                     Software/Firmware Version Information
    ${DIC_SOFTWARE} =       Create Dictionary
    ${COUNT}                Wait Until Keyword Succeeds                     1 min           1 sec
    ...                     Get Matching Xpath Count
    ...                     xpath=html/body/center/table[2]/tbody/tr
    ${COUNT} =              Evaluate                ${COUNT} + 1
    Sleep                   5
    Wait Until Keyword Succeeds                     1 min                   1 sec           Capture Page Screenshot
    ...                     filename=${RG_LOG_PATH}/ScreenShots/SNMP_Software_info.png
    Sleep                   2
    Execute JavaScript    window.scrollTo(0,2000)
    Sleep                   5
    Wait Until Keyword Succeeds                     1 min                   1 sec           Capture Page Screenshot
    ...                     filename=${RG_LOG_PATH}/ScreenShots/SNMP_Firmware_info.png
    : FOR                   ${INDEX}                IN RANGE                2               ${COUNT}
    \                       ${FNAME}                Wait Until Keyword Succeeds             1 min   1 sec
    \                       ...                     Get Text
    \                       ...                     xpath=html/body/center/table[2]/tbody/tr[${INDEX}]/td[1]/small/font
    \                       ${FVERSION}             Wait Until Keyword Succeeds             1 min   1 sec
    \                       ...                     Get Text
    \                       ...                     xpath=html/body/center/table[2]/tbody/tr[${INDEX}]/td[2]/small/font
    \                       Set To Dictionary       ${DIC_SOFTWARE}         ${FNAME}        ${FVERSION}
    @{var1}                 Get Dictionary Items    ${DIC_SOFTWARE}
    Log                     SOFTWARE LOG
    : FOR                   ${INDEX}                IN                      @{var1}
    \                       Log                     ${INDEX}
    ${DIC_FIRMWARE} =       Create Dictionary
    ${COUNT}                Wait Until Keyword Succeeds                     1 min           1 sec
    ...                     Get Matching Xpath Count
    ...                     xpath=html/body/center/table[4]/tbody/tr
    ${COUNT} =              Evaluate                ${COUNT} + 1
    : FOR                   ${INDEX}                IN RANGE                2               ${COUNT}
    \                       ${FNAME}                Wait Until Keyword Succeeds             1 min   1 sec
    \                       ...                     Get Text
    \                       ...                     xpath=html/body/center/table[4]/tbody/tr[${INDEX}]/td[1]/small/font
    \                       ${FVERSION}             Wait Until Keyword Succeeds             1 min   1 sec
    \                       ...                     Get Text
    \                       ...                     xpath=html/body/center/table[4]/tbody/tr[${INDEX}]/td[2]/small/font
    \                       Set To Dictionary       ${DIC_FIRMWARE}         ${FNAME}        ${FVERSION}
    @{var1}                 Get Dictionary Items    ${DIC_FIRMWARE}
    Log                     FIRMWARE LOG
    : FOR                   ${INDEX}                IN                      @{var1}
    \                       Log                     ${INDEX}

NIC Version Info SNMP   [Arguments]         ${BOX_POSITION}
                        [Documentation]     Get NIC card information in SNMP mode
                        Home Page
                        Wait Until Keyword Succeeds                     1 min               1 sec       Select Frame
                        ...                 name=CHPDataFrame
                        Sleep               10
                        ${DIC} =            Create Dictionary
                        ${COUNT}            Wait Until Keyword Succeeds                     1 min       1 sec
                        ...                 Get Matching Xpath Count
                        ...                 xpath=html/body/table/tbody/tr/td/div[${BOX_POSITION}]/div[1]/ul/li
                        Sleep               10
                        ${RSTATUS}          Wait Until Keyword Succeeds                     1 min       1 sec
                        ...                 Run Keyword And Return Status
                        ...                 Element Should Be Visible   xpath=html/body/table/tbody/tr/td/div[${BOX_POSITION}]/div[2]/p[1]/a/nobr
                        ${COUNT} =          Evaluate                    ${COUNT} + 1
                        : FOR               ${INDEX}                    IN RANGE            1           ${COUNT}
                        \                   Sleep                       20
                        \                   Run Keyword if              '${RSTATUS}' == 'True' and '${STATUS}' != 'True'
                        \                   ...                         Wait Until Keyword Succeeds     1 min
                        \                   ...                         1 sec
                        \                   ...                         click Element
                        \                   ...                         xpath=html/body/table/tbody/tr/td/div[${BOX_POSITION}]/div[2]/p[1]/a/nobr
                        \                   Sleep                       3
                        \                   ${ELEMENT}                  Wait Until Keyword Succeeds     1 min
                        \                   ...                         1 sec
                        \                   ...                         Get Text
                        \                   ...                         xpath=html/body/table/tbody/tr/td/div[${BOX_POSITION}]/div[1]/ul/li[${INDEX}]/div/a
                        \                   ${STATUS}                   Run Keyword And Return Status
                        \                   ...                         Should Match Regexp
                        \                   ...                         ${ELEMENT}
                        \                   ...                         Virtual
                        \                   continue_for_loop_if        '${STATUS}' == 'True'
                        \                   Sleep                       3
                        \                   Wait Until Keyword Succeeds                     2 min       1 sec
                        \                   ...                         click Element
                        \                   ...                         xpath=html/body/table/tbody/tr/td/div[${BOX_POSITION}]/div[1]/ul/li[${INDEX}]/div/a
                        \                   Sleep                       5
                        \                   Wait Until Keyword Succeeds                     1 min       1 sec
                        \                   ...                         Capture Page Screenshot
                        \                   ...                         filename=${RG_LOG_PATH}/ScreenShots/SNMP_NIC_info_${INDEX}.png
                        \                   ${STATUS1}                  Wait Until Keyword Succeeds     1 min
                        \                   ...                         1 sec
                        \                   ...                         Run Keyword And Return Status   Element Should Be Visible
                        \                   ...                         xpath=html/body/center/table[2]/tbody/tr[1]/td[7]/small/font
                        \                   ${FWARE}                    Run Keyword If      '${STATUS1}' == 'True'
                        \                   ...                         Wait Until Keyword Succeeds     1 min
                        \                   ...                         1 sec
                        \                   ...                         Get Text
                        \                   ...                         xpath=html/body/center/table[2]/tbody/tr[1]/td[5]/small/font/b
                        \                   ${FW_VERSION}               Run Keyword If      '${STATUS1}' == 'True'
                        \                   ...                         Wait Until Keyword Succeeds     1 min
                        \                   ...                         1 sec
                        \                   ...                         Get Text
                        \                   ...                         xpath=html/body/center/table[2]/tbody/tr[1]/td[7]/small/font
                        \                   ${TITLE}                    Wait Until Keyword Succeeds     1 min
                        \                   ...                         1 sec
                        \                   ...                         Get Text            xpath=html/body/center/center/font/b
                        \                   Run Keyword And Continue On Failure             Run Keyword If
                        \                   ...                         '${STATUS1}' != 'True'          Fail
                        \                   ...                         This NIC " ${TITLE} " doesn't Contain Firmware version 
                        \                   Set To Dictionary           ${DIC}              ${FWARE}    ${FW_VERSION}
                        \                   Wait Until Keyword Succeeds                     1 min       1 sec
                        \                   ...                         Go Back
                        \                   Sleep                       1
                        ${var1}             Get Dictionary Items        ${DIC}
                        : FOR               ${INDEX}                    IN                  @{var1}
                        \                   Log                         ${INDEX}
                        Wait Until Keyword Succeeds                     1 min               1 sec       unselect frame
                        Sleep               2

NIC Version Info SNMP Linux
    [Documentation]     Get NIC card information in SNMP mode
    Home Page
    Wait Until Keyword Succeeds                     1 min               1 sec       Select Frame
    ...                 name=CHPDataFrame
    Sleep               10
    Wait Until Keyword Succeeds                     1 min               1 sec
    ...                 RoboGalaxyLibrary.Element Text Should Be
    ...                 xpath=html/body/table/tbody/tr/td/div[2]/h4     NIC
    ...                 NIC tab doesn't contain
    ${DIC} =            Create Dictionary
    ${COUNT}            Wait Until Keyword Succeeds                     1 min       1 sec
    ...                 Get Matching Xpath Count
    ...                 xpath=html/body/table/tbody/tr/td/div[2]/div[1]/ul/li
    ${RSTATUS}          Wait Until Keyword Succeeds                     1 min       1 sec
    ...                 Run Keyword And Return Status
    ...                 Element Should Be Visible   xpath=html/body/table/tbody/tr/td/div[2]/div[2]/p[1]/a/nobr
    ${COUNT} =          Evaluate                    ${COUNT} + 1
    : FOR               ${INDEX}                    IN RANGE            1           ${COUNT}
    \                   Run Keyword if              '${RSTATUS}' == 'True' and '${STATUS}' != 'True'
    \                   ...                         Wait Until Keyword Succeeds     1 min
    \                   ...                         1 sec
    \                   ...                         click Element
    \                   ...                         xpath=html/body/table/tbody/tr/td/div[2]/div[2]/p[1]/a/nobr
    \                   Sleep                       3
    \                   ${ELEMENT}                  Wait Until Keyword Succeeds     1 min
    \                   ...                         1 sec
    \                   ...                         Get Text
    \                   ...                         xpath=html/body/table/tbody/tr/td/div[2]/div[1]/ul/li[${INDEX}]/div/a
    \                   ${STATUS}                   Run Keyword And Return Status
    \                   ...                         Should Match Regexp
    \                   ...                         ${ELEMENT}
    \                   ...                         Virtual
    \                   continue_for_loop_if        '${STATUS}' == 'True'
    \                   Sleep                       3
    \                   Wait Until Keyword Succeeds                     2 min       1 sec
    \                   ...                         click Element
    \                   ...                         xpath=html/body/table/tbody/tr/td/div[2]/div[1]/ul/li[${INDEX}]/div/a
    \                   Sleep                       5
    \                   Wait Until Keyword Succeeds                     1 min       1 sec
    \                   ...                         Capture Page Screenshot
    \                   ...                         filename=${RG_LOG_PATH}/ScreenShots/SNMP_NIC_info_${INDEX}.png
    \                   ${STATUS1}                  Wait Until Keyword Succeeds     1 min
    \                   ...                         1 sec
    \                   ...                         Run Keyword And Return Status   Element Should Be Visible
    \                   ...                         xpath=html/body/center/table[2]/tbody/tr[1]/td[7]/small/font
    \                   ${FWARE}                    Run Keyword If      '${STATUS1}' == 'True'
    \                   ...                         Wait Until Keyword Succeeds     1 min
    \                   ...                         1 sec
    \                   ...                         Get Text
    \                   ...                         xpath=html/body/center/table[2]/tbody/tr[1]/td[5]/small/font/b
    \                   ${FW_VERSION}               Run Keyword If      '${STATUS1}' == 'True'
    \                   ...                         Wait Until Keyword Succeeds     1 min
    \                   ...                         1 sec
    \                   ...                         Get Text
    \                   ...                         xpath=html/body/center/table[2]/tbody/tr[1]/td[7]/small/font
    \                   ${TITLE}                    Wait Until Keyword Succeeds     1 min
    \                   ...                         1 sec
    \                   ...                         Get Text            xpath=html/body/center/center/font/b
    \                   Run Keyword And Continue On Failure             Run Keyword If
    \                   ...                         '${STATUS1}' != 'True'
    \                   ...                         Fail                This NIC " ${TITLE} " doesn't Contain Firmware version 
    \                   Set To Dictionary           ${DIC}              ${FWARE}    ${FW_VERSION}
    \                   Wait Until Keyword Succeeds                     1 min       1 sec
    \                   ...                         Go Back
    \                   Sleep                       1
    ${var1}             Get Dictionary Items        ${DIC}
    : FOR               ${INDEX}                    IN                  @{var1}
    \                   Log                         ${INDEX}
    Wait Until Keyword Succeeds                     1 min               1 sec       unselect frame
    Sleep               2

Storage Information SNMP    [Arguments]             ${BOX_POSITION}
    [Documentation]         Get storage information in SNMP mode
    Home Page
    Wait Until Keyword Succeeds                     1 min                       1 sec               Select Frame
    ...                     name=CHPDataFrame
    ${DIC} =                Create Dictionary
    ${COUNT}                Wait Until Keyword Succeeds                         1 min               1 sec
    ...                     Get Matching Xpath Count
    ...                     xpath=html/body/table/tbody/tr/td/div[${BOX_POSITION}]/div[1]/ul/li
    ${COUNT} =              Evaluate                ${COUNT} + 1
    : FOR                   ${INDEX}                IN RANGE                    1                   ${COUNT}
    \                       Sleep                   5
    \                       Run Keyword if          ${COUNT} >= 7 and '${STATUS}' != 'True'
    \                       ...                     Wait Until Keyword Succeeds                     1 min           1 sec
    \                       ...                     Click Element
    \                       ...                     xpath=html/body/table/tbody/tr/td/div[${BOX_POSITION}]/div[2]/p[1]/a/nobr
    \                       ${ELEMENT}              Wait Until Keyword Succeeds                     1 min           1 sec
    \                       ...                     Get Text
    \                       ...                     xpath=html/body/table/tbody/tr/td/div[${BOX_POSITION}]/div[1]/ul/li[${INDEX}]/div/a
    \                       ${STATUS}               Run Keyword And Return Status                   Should Match Regexp
    \                       ...                     ${ELEMENT}
    \                       ...                     Smart Array
    \                       continue_for_loop_if    '${STATUS}' != 'True'
    \                       Sleep                   10
    \                       Run Keyword if          ${COUNT} >= 3               Wait Until Keyword Succeeds         1 min
    \                       ...                     1 sec
    \                       ...                     Click Element               xpath=html/body/table/tbody/tr/td/div[${BOX_POSITION}]/div[1]/ul/li[${INDEX}]/div/a
    \                       Run Keyword if          ${COUNT} == 2               Wait Until Keyword Succeeds         1 min
    \                       ...                     1 sec
    \                       ...                     Click Element               xpath=html/body/table/tbody/tr/td/div[${BOX_POSITION}]/div[1]/ul/li/div/a
    \                       Wait Until Keyword Succeeds                         1min                1sec            Select Frame
    \                       ...                     name=subdata
    \                       Sleep                   5
    \                       Wait Until Keyword Succeeds                         1min                1sec
    \                       ...                     Capture Page Screenshot     filename=${RG_LOG_PATH}/ScreenShots/SNMP_Storage_info.png
    \                       ${STATUS2}              Wait Until Keyword Succeeds                     1min            1sec
    \                       ...                     Run Keyword And Return Status                   Element Should Be Visible
    \                       ...                     xpath=html/body/center/table[2]/tbody/tr[3]/td[3]
    \                       ${FIRMWARE}             Run Keyword If              '${STATUS2}' == 'True'
    \                       ...                     Wait Until Keyword Succeeds                     1min            1sec
    \                       ...                     Get Text
    \                       ...                     xpath=html/body/center/table[2]/tbody/tr[3]/td[1]
    \                       ${FWVERSION}            Run Keyword If              '${STATUS2}' == 'True'
    \                       ...                     Wait Until Keyword Succeeds                     1min            1sec
    \                       ...                     Get Text
    \                       ...                     xpath=html/body/center/table[2]/tbody/tr[3]/td[3]
    \                       ${TITLE}                Wait Until Keyword Succeeds                     1min            1sec
    \                       ...                     Get Text                    xpath=html/body/center/center
    \                       Run Keyword And Continue On Failure                 Should Contain      '${STATUS2}'    True
    \                       ...                     This Array ${TITLE} doesn't Contain Firmware version
    \                       Set To Dictionary       ${DIC}                      ${FIRMWARE}         ${FWVERSION}
    \                       Home Page
    \                       Wait Until Keyword Succeeds                         1min                1sec            Select Frame
    \                       ...                     name=CHPDataFrame
    Home Page

Storage Information SNMP Linux
    [Documentation]     Get storage information in SNMP mode
    Home Page
    Wait Until Keyword Succeeds                     1min                1sec                Select Frame
    ...                 name=CHPDataFrame
    Wait Until Keyword Succeeds                     1 min               1 sec
    ...                 RoboGalaxyLibrary.Element Text Should Be
    ...                 xpath=html/body/table/tbody/tr/td/div[4]/h4     Storage             Storage tab doesn't contain
    ${DIC} =            Create Dictionary
    ${COUNT}            Wait Until Keyword Succeeds                     1min                1sec
    ...                 Get Matching Xpath Count    xpath=html/body/table/tbody/tr/td/div[4]/div[1]/ul/li
    ${COUNT} =          Evaluate                    ${COUNT} + 1
    : FOR               ${INDEX}                    IN RANGE            1                   ${COUNT}
    \                   Log                         ${INDEX}
    \                   Sleep                       5
    \                   Run Keyword if              ${COUNT} >= 7 and '${STATUS}' != 'True'
    \                   ...                         Wait Until Keyword Succeeds             1min                    1sec
    \                   ...                         Click Element
    \                   ...                         xpath=html/body/table/tbody/tr/td/div[4]/div[2]/p[1]/a/nobr
    \                   ${ELEMENT}                  Wait Until Keyword Succeeds             1min                    1sec
    \                   ...                         Get Text
    \                   ...                         xpath=html/body/table/tbody/tr/td/div[4]/div[1]/ul/li[${INDEX}]/div/a
    \                   ${STATUS}                   Run Keyword And Return Status           Should Match Regexp     ${ELEMENT}
    \                   ...                         Smart Array
    \                   continue_for_loop_if        '${STATUS}' == 'False'
    \                   Sleep                       10
    \                   Run Keyword if              ${COUNT} >= 3       Wait Until Keyword Succeeds                 1 min
    \                   ...                         1 sec
    \                   ...                         Click Element       xpath=html/body/table/tbody/tr/td/div[4]/div[1]/ul/li[${INDEX}]/div/a
    \                   Run Keyword if              ${COUNT} == 2       Wait Until Keyword Succeeds                 1 min   1sec
    \                   ...                         Click Element       xpath=html/body/table/tbody/tr/td/div[4]/div[1]/ul/li/div/a
    \                   Wait Until Keyword Succeeds                     1min                1sec                    Select Frame
    \                   ...                         name=subdata
    \                   Sleep                       5
    \                   Wait Until Keyword Succeeds                     1min                1sec
    \                   ...                         Capture Page Screenshot                 filename=${RG_LOG_PATH}/ScreenShots/SNMP_Storage_info_linux.png
    \                   ${STATUS2}                  Wait Until Keyword Succeeds             1min                    1sec
    \                   ...                         Run Keyword And Return Status           Element Should Be Visible
    \                   ...                         xpath=html/body/center/table[2]/tbody/tr[3]/td[3]
    \                   ${FIRMWARE}                 Run Keyword If      '${STATUS2}' == 'True'
    \                   ...                         Get Text
    \                   ...                         xpath=html/body/center/table[2]/tbody/tr[3]/td[1]
    \                   ${FWVERSION}                Run Keyword If      '${STATUS2}' == 'True'
    \                   ...                         Wait Until Keyword Succeeds             1min                    1sec
    \                   ...                         Get Text
    \                   ...                         xpath=html/body/center/table[2]/tbody/tr[3]/td[3]
    \                   ${TITLE}                    Get Text            xpath=html/body/center/a/font/b
    \                   Run Keyword And Continue On Failure             Should Contain      '${STATUS2}'            True
    \                   ...                         This Array ${TITLE} doesn't Contain Firmware version
    \                   Set To Dictionary           ${DIC}              ${FIRMWARE}         ${FWVERSION}
    \                   Home Page
    \                   Wait Until Keyword Succeeds                     1min                1sec                    Select Frame
    \                   ...                         name=CHPDataFrame

Firmware Information WBEM
    [Documentation]     Get Firmware information in WBEM mode
    Home Page
    Wait Until Keyword Succeeds                     1min        1sec                Select Frame    name=CHPDataFrame
    Wait Until Keyword Succeeds                     1min        1sec                Click Link      Firmware Information
    ${DIC} =            Create Dictionary
    ${COUNT}            Wait Until Keyword Succeeds             1min                1sec
    ...                 Get Matching Xpath Count    xpath=//*[@id='firmwareInfo']/tbody/tr
    ${COUNT} =          Evaluate                    ${COUNT} + 1
    Sleep               5
    Wait Until Keyword Succeeds                     1min        1sec                Capture Page Screenshot
    ...                 filename=${RG_LOG_PATH}/ScreenShots/WBEM_Firmware_info.png
    : FOR               ${INDEX}                    IN RANGE    2                   ${COUNT}
    \                   Log                         ${INDEX}
    \                   ${FNAME}                    Wait Until Keyword Succeeds     1min            1sec
    \                   ...                         Get Text    xpath=//*[@id='firmwareInfo']/tbody/tr[${INDEX}]/td[1]
    \                   ${FVERSION}                 Wait Until Keyword Succeeds     1min            1sec
    \                   ...                         Get Text    xpath=//*[@id='firmwareInfo']/tbody/tr[${INDEX}]/td[2]
    \                   Set To Dictionary           ${DIC}      ${FNAME}            ${FVERSION}
    @{DITEMS}           Get Dictionary Items        ${DIC}
    Log                 Firmware Information
    : FOR               ${INDEX}                    IN          @{DITEMS}
    \                   Log                         ${INDEX}
    Go Back
    unselect frame
    Sleep               2

Software Information WBEM
    [Documentation]                 Get Software information in WBEM mode
    Home Page
    Wait Until Keyword Succeeds     1min    1sec    Select Frame    name=CHPDataFrame

    Wait Until Keyword Succeeds                     1min                1sec            Click Link      Software Information
    ${DIC} =            Create Dictionary
    Sleep               5
    ${COUNT}            Get Matching Xpath Count    xpath=//*[@id="SIP"]/tbody/tr[*]/td[1]
    ${NEXT}             Get Matching Xpath Count    xpath=html/body/table[2]/tbody/tr[2]/td/div/input
    ${COUNT1}           Evaluate                    ${COUNT} + 1
    Wait Until Keyword Succeeds                     1min                1sec
    ...                 Capture Page Screenshot     filename=${RG_LOG_PATH}/ScreenShots/WBEM_Software_info.png
    : FOR               ${INDEX}                    IN RANGE            2               ${COUNT1}
    \                   ${FNAME}                    Wait Until Keyword Succeeds         1min            1sec
    \                   ...                         Get Text            xpath=//*[@id='SIP']/tbody/tr[${INDEX}]/td[1]
    \                   ${FVERSION}                 Wait Until Keyword Succeeds         1min            1sec
    \                   ...                         Get Text            xpath=//*[@id='SIP']/tbody/tr[${INDEX}]/td[2]
    \                   Set To Dictionary           ${DIC}              ${FNAME}        ${FVERSION}
    \                   Run Keyword If              '${INDEX}' == '${COUNT}' and '${NEXT}' == '1'
    \                   ...                         Wait Until Keyword Succeeds         1min            1sec
    \                   ...                         click Element
    \                   ...                         xpath=/html/body/table[2]/tbody/tr[2]/td/div/input
    ${COUNT}            Run Keyword If              ${NEXT} >= 1
    ...                 Get Matching Xpath Count
    ...                 xpath=//*[@id="SIP"]/tbody/tr[*]/td[1]
    ${COUNT} =          Evaluate                    ${COUNT} + 1
    Sleep               5
    Run Keyword if      ${COUNT} >= 2               Wait Until Keyword Succeeds         1min            1sec
    ...                 Capture Page Screenshot     filename=${RG_LOG_PATH}/ScreenShots/WBEM_Software_info_1.png
    : FOR               ${INDEX}                    IN RANGE            2               ${COUNT}
    \                   ${FNAME}                    Run Keyword if      ${COUNT} >= 2   Wait Until Keyword Succeeds     1min
    \                   ...                         1sec
    \                   ...                         Get Text            xpath=//*[@id='SIP']/tbody/tr[${INDEX}]/td[1]
    \                   ${FVERSION}                 Run Keyword if      ${COUNT} >= 2   Wait Until Keyword Succeeds     1min
    \                   ...                         1sec
    \                   ...                         Get Text            xpath=//*[@id='SIP']/tbody/tr[${INDEX}]/td[2]
    \                   Set To Dictionary           ${DIC}              ${FNAME}        ${FVERSION}
    @{DITEMS}           Get Dictionary Items        ${DIC}
    : FOR               ${INDEX}                    IN                  @{DITEMS}
    \                   Log                         ${INDEX}
    unselect frame
    Home Page
    Sleep               10

Network Information WBEM    [Arguments]                 ${BOX_POSITION}
    [Documentation]         Get Network details in WBEM mode
    ${NETWORK_ELEMENT} =    Set Variable If             ${BOX_POSITION} == 1
    ...                     html/body/table/tbody/tr/td/div[${BOX_POSITION}]/div/div[1]/ul/li
    ...                     ${BOX_POSITION} > 1         html/body/table/tbody/tr/td/div[${BOX_POSITION}]/div[1]/ul/li
    ${SHOW_ALL_ELEMENT} =   Set Variable If             ${BOX_POSITION} == 1
    ...                     html/body/table/tbody/tr/td/div[${BOX_POSITION}]/div/div[2]/p[1]/a/nobr
    ...                     ${BOX_POSITION} > 1         html/body/table/tbody/tr/td/div[${BOX_POSITION}]/div[2]/p[1]/a/nobr
    Home Page
    Wait Until Keyword Succeeds                         1min                1sec                Select Frame
    ...                     name=CHPDataFrame
    ${DIC} =                Create Dictionary
    ${COUNT}                Wait Until Keyword Succeeds                     1min                1sec
    ...                     Get Matching Xpath Count    xpath=${NETWORK_ELEMENT}
    ${COUNT} =              Evaluate                    ${COUNT} + 1
    : FOR                   ${INDEX}                    IN RANGE            1                   ${COUNT}
    \                       Sleep                       10
    \                       ${present}=                 Run Keyword And Return Status           Element Should Be Visible
    \                       ...                         xpath=${SHOW_ALL_ELEMENT}
    \                       Run Keyword If              ${present}          click Element       xpath=${SHOW_ALL_ELEMENT}
    \                       ${ELEMENT}                  Wait Until Keyword Succeeds             1min            1sec
    \                       ...                         Get Text
    \                       ...                         xpath=${NETWORK_ELEMENT}[${INDEX}]/div/a
    \                       ${STATUS}                   Run Keyword And Return Status           Should Match Regexp
    \                       ...                         ${ELEMENT}
    \                       ...                         Virtual
    \                       continue_for_loop_if        '${STATUS}' == 'True'
    \                       Wait Until Keyword Succeeds                     1min                1sec
    \                       ...                         Click Element       xpath=${NETWORK_ELEMENT}[${INDEX}]/div/a
    \                       Sleep                       5
    \                       Wait Until Keyword Succeeds                     1min                1sec
    \                       ...                         Capture Page Screenshot                 filename=${RG_LOG_PATH}/ScreenShots/WBEM_Network_info${INDEX}.png
    \                       ${STATUS1}                  Wait Until Keyword Succeeds             1min            1sec
    \                       ...                         Run Keyword And Return Status           Element Should Be Visible
    \                       ...                         xpath=//*[@id='t1']/tbody/tr[6]/td[2]
    \                       ${FIRMARE}                  Run Keyword If      '${STATUS1}' == 'True'
    \                       ...                         Wait Until Keyword Succeeds             1min            1sec
    \                       ...                         Get Text
    \                       ...                         xpath=//*[@id='t1']/tbody/tr[6]/td[1]
    \                       ${FWVERSION}                Run Keyword If      '${STATUS1}' == 'True'
    \                       ...                         Wait Until Keyword Succeeds             1min            1sec
    \                       ...                         Get Text
    \                       ...                         xpath=//*[@id='t1']/tbody/tr[6]/td[2]
    \                       ${TITLE}                    Wait Until Keyword Succeeds             1min            1sec
    \                       ...                         Get Text            xpath=//*[@id='maindivision']/table[1]/tbody/tr/td[1]/h1
    \                       Run Keyword And Continue On Failure             Should Contain      '${STATUS1}'    True
    \                       ...                         This NIC ${TITLE} doesn't Contain Firmware version
    \                       Set To Dictionary           ${DIC}              ${FIRMARE}          ${FWVERSION}
    \                       Go Back
    Wait Until Keyword Succeeds                         1min                1sec                unselect frame
    ${var1}                 Get Dictionary Items        ${DIC}
    : FOR                   ${INDEX}                    IN                  @{var1}
    \                       Log                         ${INDEX}
    Sleep                   2

Storage Information WBEM    [Arguments]                 ${BOX_POSITION}
    [Documentation]         Get Storage information in WBEM mode
    Home Page
    Wait Until Keyword Succeeds                         1min                1sec                Select Frame
    ...                     name=CHPDataFrame
    ${DIC} =                Create Dictionary
    ${COUNT}                Wait Until Keyword Succeeds                     1min                1sec
    ...                     Get Matching Xpath Count    xpath=html/body/table/tbody/tr/td/div[${BOX_POSITION}]/div[1]/ul/li
    ${COUNT} =              Evaluate                    ${COUNT} + 1
    : FOR                   ${INDEX}                    IN RANGE            1                   ${COUNT}
    \                       Sleep                       5
    \                       Run Keyword if              ${COUNT} >= 7 and '${STATUS}' != 'True'
    \                       ...                         Wait Until Keyword Succeeds             1min            1sec
    \                       ...                         click Element
    \                       ...                         xpath=html/body/table/tbody/tr/td/div[${BOX_POSITION}]/div[2]/p[1]/a/nobr
    \                       ${ELEMENT}                  Wait Until Keyword Succeeds             1min            1sec
    \                       ...                         Get Text
    \                       ...                         xpath=html/body/table/tbody/tr/td/div[${BOX_POSITION}]/div[1]/ul/li[${INDEX}]/div/a
    \                       ${STATUS}                   Run Keyword And Return Status           Should Match Regexp
    \                       ...                         ${ELEMENT}
    \                       ...                         Smart Array
    \                       continue_for_loop_if        '${STATUS}' == 'False'
    \                       Sleep                       10
    \                       Run Keyword if              ${COUNT} >= 3       Wait Until Keyword Succeeds         1min
    \                       ...                         1sec
    \                       ...                         Click Element       xpath=html/body/table/tbody/tr/td/div[${BOX_POSITION}]/div[1]/ul/li[${INDEX}]/div/a
    \                       Run Keyword if              ${COUNT} == 2       Wait Until Keyword Succeeds         1min
    \                       ...                         1sec
    \                       ...                         Click Element       xpath=html/body/table/tbody/tr/td/div[${BOX_POSITION}]/div[1]/ul/li/div/a
    \                       Wait Until Keyword Succeeds                     1min                1sec
    \                       ...                         Select Frame
    \                       ...                         name=right
    \                       Sleep                       5
    \                       Wait Until Keyword Succeeds                     1min                1sec
    \                       ...                         Capture Page Screenshot                 filename=${RG_LOG_PATH}/ScreenShots/WBEM_Storage_info_${INDEX}.png
    \                       ${STATUS1}                  Wait Until Keyword Succeeds             1min            1sec
    \                       ...                         Run Keyword And Return Status           Element Should Be Visible
    \                       ...                         xpath=//*[@id='Controller']/tbody/tr[4]/td[2]
    \                       ${FIRMWARE}                 Run Keyword If      '${STATUS1}' == 'True'
    \                       ...                         Wait Until Keyword Succeeds             1min            1sec
    \                       ...                         Get Text
    \                       ...                         xpath=//*[@id='Controller']/tbody/tr[4]/td[1]
    \                       ${FWVERSION}                Run Keyword If      '${STATUS1}' == 'True'
    \                       ...                         Wait Until Keyword Succeeds             1min            1sec
    \                       ...                         Get Text
    \                       ...                         xpath=//*[@id='Controller']/tbody/tr[4]/td[2]
    \                       ${TITLE}                    Wait Until Keyword Succeeds             1min            1sec
    \                       ...                         Get Text            xpath=//*[@id='maindivision']/table[1]/tbody/tr/td[1]/h1
    \                       Run Keyword And Continue On Failure             Should Contain      '${STATUS1}'    True
    \                       ...                         This Array ${TITLE} doesn't Contain Firmware version
    \                       Set To Dictionary           ${DIC}              ${FIRMWARE}         ${FWVERSION}
    \                       Wait Until Keyword Succeeds                     1min                1sec
    \                       ...                         unselect frame
    \                       Go Back
    \                       Wait Until Keyword Succeeds                     1min                1sec
    \                       ...                         Select Frame
    \                       ...                         name=CHPDataFrame
    ${var1}                 Get Dictionary Items        ${DIC}
    : FOR                   ${INDEX}                    IN                  @{var1}
    \                       Log                         ${INDEX}
    unselect frame
    Sleep                   2

Webapp Information
    [Documentation]             Get Insight Diagnostics information.
    Wait Until Keyword Succeeds                         1min                    1sec
    ...                         Close Browser
    ${FF_PROFILE} =             Get Firefox Profile     ${FF_PROFILE_TEMPLATE}
    Wait Until Keyword Succeeds                         3 min                   1 sec           Open Browser
    ...                         ${WEBAPP_LOGIN_URL}
    ...                         ${BROWSER}              ff_profile_dir=${FF_PROFILE}
    Sleep                       1
    Wait Until Keyword Succeeds                         1 min                   1 sec
    ...                         Maximize Browser Window
    Wait Until Keyword Succeeds                         1min                    1sec            Input Text
    ...                         user
    ...                         ${SYSTEM_USERNAME}
    Sleep                       1
    Wait Until Keyword Succeeds                         1min                    1sec            Input Text
    ...                         password
    ...                         ${SYSTEM_PASSWORD}
    Sleep                       1
    Wait Until Keyword Succeeds                         1min                    1sec
    ...                         Click Element
    ...                         logonButton
    Wait Until Keyword Succeeds                         2min                    1sec
    ...                         Title Should Be
    ...                         Insight Diagnostics
    Sleep                       60
    Wait Until Element Is Visible                       xpath=//*[@id='diagnoseTab']            250
    ...                         " Diagnose page loading error "
    Wait Until Keyword Succeeds                         3min                    1sec
    ...                         Click Element
    ...                         xpath=//*[@id='diagnoseTab']
    Sleep                       5s
    ${STATUS}                   Get Text                xpath=//*[@id='diagnoseDeviceList']/li[1]
    ${ret_str} =                Get Lines Containing String                     ${STATUS}       Not
    ...                         case_insensitive=true
    ${length} =                 Get Length              ${ret_str}
    Run Keyword if              ${length} > 0           Log
    ...                         Insight Diags doesn't contain Logical Drive or Storage
    ...                         WARN
    Run Keyword Unless          ${length} > 0
    ...                         Wait Until Keyword Succeeds                     1min            1sec
    ...                         Click Element
    ...                         xpath=//*[@id='diagnoseDeviceList']/li[1]/input
    Run Keyword Unless          ${length} > 0           Wait Until Keyword Succeeds             1min
    ...                         1sec
    ...                         Click Element
    ...                         xpath=//*[@id='beginDiagnosis']
    ${ret}                      Run Keyword Unless      ${length} > 0
    ...                         Wait Until Operation Completes
    ...                         Diagnose
    ...                         200
    Run Keyword Unless          ${length} > 0
    ...                         Run Keyword If          'Testing Completed!' not in '${ret}'    Fail
    ...                         Diagnose ${ret}
    Sleep                       5
    Capture Page Screenshot     filename=${RG_LOG_PATH}/ScreenShots/Webapp_Diagnosis_info.png
    ${ret} =                    Run Keyword And Return Status                   Select Frame    statusFrameB
    Execute JavaScript    window.scrollTo(0,2000)
    Sleep                       5
    Capture Page Screenshot     filename=${RG_LOG_PATH}/ScreenShots/Webapp_Diagnosis_info_1.png
    ${ret} =                    Run Keyword And Return Status                   unselect frame
    Wait Until Keyword Succeeds                         1min                    1sec
    ...                         Click Element
    ...                         xpath=//*[@id='logTab']
    Wait Until Keyword Succeeds                         1min                    1sec            Select Frame
    ...                         errorLogFrame
    ${TEXT}                     Wait Until Keyword Succeeds                     1min            1sec
    ...                         Get Text
    ...                         xpath=//*[@id='errorLog']/tbody/tr/td
    Sleep                       5
    Wait Until Keyword Succeeds                         1min                    1sec
    ...                         Capture Page Screenshot
    ...                         filename=${RG_LOG_PATH}/ScreenShots/Webapp_Log_info.png
    Should Contain              ${TEXT}                 Error Log is empty      Error Log is not empty
    Wait Until Keyword Succeeds                         1min                    1sec
    ...                         unselect frame

Wait Until Operation Completes                      [Arguments]         ${operation}        ${timeout}
    Sleep               5s
    Run Keyword If      '${operation}' == 'Diagnose'                    Set Test Variable   ${Element}
    ...                 xpath=//*[@id='statusMessage']
    Run Keyword If      '${operation}' == 'NIC'     Set Test Variable   ${Element}
    ...                 xpath=html/body/table/tbody/tr/td/div[2]/div[2]/p[1]/a/nobr
    : FOR               ${index}                    IN RANGE            1                   ${timeout}
    \                   Sleep                       1s
    \                   ${status} =                 Get Text            ${Element}
    \                   Run Keyword If              '${status.strip()}' == 'Testing Completed!' and '${operation}' == 'Diagnose'
    \                   ...                         Exit For Loop
    [Return]            ${status}

Smart Storage Administrator Info
    [Documentation]     Get Smart Storage Administrator Information from storage tab
    Wait Until Keyword Succeeds                     1min                    1sec                    Close Browser
    Open Browser And Login SMH
    Run Keyword And Continue On Failure             Change Window Format Linux
    Sleep               5
    Wait Until Keyword Succeeds                     1min                    1sec                    Select Frame
    ...                 name=CHPDataFrame
    Sleep               5
    RoboGalaxyLibrary.Element Text Should Be        xpath=html/body/table/tbody/tr/td/div[4]/h4     Storage
    ...                 Storage tab doesn't contain
    ${COUNT}            Wait Until Keyword Succeeds                         1min                    1sec
    ...                 Get Matching Xpath Count    xpath=html/body/table/tbody/tr/td/div[4]/div[1]/ul/li
    ${COUNT1} =         Evaluate                    ${COUNT} + 1
    : FOR               ${INDEX}                    IN RANGE                1                       ${COUNT1}
    \                   Run Keyword If              '${FLAG}' == 'True'     Exit For Loop
    \                   Log                         ${INDEX}
    \                   Sleep                       5
    \                   Run Keyword if              ${COUNT} >= 7 and '${STATUS}' != 'True'
    \                   ...                         Wait Until Keyword Succeeds                     1min    1sec
    \                   ...                         Click Element
    \                   ...                         xpath=html/body/table/tbody/tr/td/div[4]/div[2]/p[1]/a/nobr
    \                   ${ELEMENT}                  Wait Until Keyword Succeeds                     1min    1sec
    \                   ...                         Get Text
    \                   ...                         xpath=html/body/table/tbody/tr/td/div[4]/div[1]/ul/li[${INDEX}]/div/a
    \                   ${STATUS}                   Run Keyword And Return Status                   Should Match Regexp
    \                   ...                         ${ELEMENT}
    \                   ...                         Smart Storage
    \                   ${FLAG}                     Set Variable If         '${STATUS}' == 'True'   True    None
    \                   Run Keyword If              '${INDEX}' == '${COUNT}' and '${FLAG}' != 'True'
    \                   ...                         Run Keyword And Continue On Failure
    \                   ...                         Should Contain          '${FLAG}'               True
    \                   ...                         " Storage tab doesn't contain SSA "
    \                   continue_for_loop_if        '${STATUS}' == 'False'
    \                   Sleep                       1
    \                   Run Keyword if              '${STATUS}' == 'True'   SSA Infomation

SSA Infomation
    [Documentation]     Get SSA information
    Wait Until Keyword Succeeds                         1min                1sec            Close Browser
    ${FF_PROFILE} =     Get Firefox Profile             ${FF_PROFILE_TEMPLATE}
    Wait Until Keyword Succeeds                         3 min               1 sec           Open Browser
    ...                 ${SSA_LOGIN_URL}
    ...                 ${BROWSER}
    ...                 ff_profile_dir=${FF_PROFILE}
    Sleep               1
    Wait Until Keyword Succeeds                         1 min               1 sec
    ...                 Maximize Browser Window
    Wait Until Keyword Succeeds                         1min                1sec            Input Text      user
    ...                 ${SYSTEM_USERNAME}
    Sleep               1
    Wait Until Keyword Succeeds                         1min                1sec            Input Text
    ...                 password
    ...                 ${SYSTEM_PASSWORD}
    Sleep               1
    Wait Until Keyword Succeeds                         3min                1sec            Click Element
    ...                 logonButton
    Sleep               30
    ${TITLE}            Wait Until Keyword Succeeds     2min                1sec            Get Title
    Run Keyword And Continue On Failure                 Should Contain      '${TITLE}'      Smart Storage
    ...                 " Smart Storage is not Enabled "
    Wait Until Keyword Succeeds                         1min                1sec
    ...                 Capture Page Screenshot         filename=${RG_LOG_PATH}/ScreenShots/Smart_storage_Admin_info.png

Linux PIV SMH verification
    [Documentation]     Post Install Verification
    Open Browser And Login SMH
    Wait Until Keyword Succeeds                         1 min   1 sec                       Select Frame   CHPHeaderFrame
    ${Data_Source}      Wait Until Keyword Succeeds     1 min   1 sec                       Get Text
    ...                 xpath=html/body/table/tbody/tr/td[6]/div/span/nobr
    unselect frame
    Run Keyword If      'SNMP' not in '${Data_Source}' and 'WBEM' not in '${Data_Source}'   Fail
    ...                 " Data Source is Empty "

    ## Verify PIV Information on SNMP
    Run Keyword And Continue On Failure     Change Window Format Linux
    Run Keyword And Continue On Failure     Home Page Screenshot                SNMP
    Run Keyword If                          'SNMP' not in '${Data_Source}'      Fail    " Page not in SNMP mode "
    Run Keyword And Continue On Failure     Storage Information SNMP Linux
    Run Keyword And Continue On Failure     Firmware and Software Version Info SNMP Linux
    Run Keyword And Continue On Failure     NIC Version Info SNMP Linux
    Run Keyword And Continue On Failure     Restart hpsmhd Service
    Run Keyword And Continue On Failure     Smart Storage Administrator Info
    Run Keyword And Continue On Failure     Webapp Information
    Close Browser

Windows PIV SMH WBEM verification
    [Documentation]     Post Install Windows PIV SMH WBEM verification
    Run Keyword And Continue On Failure             Change Window Format
    Run Keyword And Continue On Failure             Home Page Screenshot    WBEM
    Select Frame        name=CHPDataFrame
    ${COUNT}            Get Matching Xpath Count    xpath=/html/body/table/tbody/tr/td/div[1]/div/h4
    ${T_COUNT}          Get Matching Xpath Count    xpath=/html/body/table/tbody/tr/td/div[*]/h4
    ${BOX_COUNT}        Run Keyword If              ${T_COUNT} > 3          Evaluate    ${COUNT} + ${T_COUNT} + 2
    ...                 ELSE IF                     ${T_COUNT} <= 3         Evaluate    ${COUNT} + ${T_COUNT} + 1
    unselect frame
    ${BOX_NAMES} =      Create List                 Software                Network     Storage

    : FOR   ${INDEX}                    IN RANGE            1               ${BOX_COUNT}
    \       Continue For Loop If        ${index} == 5
    \       Sleep                       10
    \       Select Frame                name=CHPDataFrame
    \       Wait Until Element Is Visible                   xpath=/html/body/table/tbody/tr/td/div[1]/div/h4
    \       ...                         60
    \       ${BOX_NAME}                 Run Keyword If      ${INDEX} == 1   Get Text
    \       ...                         xpath=/html/body/table/tbody/tr/td/div[1]/div/h4
    \       ...                         ELSE IF             ${INDEX} > 1    Get Text
    \       ...                         xpath=/html/body/table/tbody/tr/td/div[${INDEX}]/h4
    \       unselect frame
    \       Remove Values From List     ${BOX_NAMES}        ${BOX_NAME}
    \       Run Keyword If              'Software' in '${BOX_NAME}'         Run Keyword And Continue On Failure
    \       ...                         Firmware Information WBEM
    \       Run Keyword If              'Software' in '${BOX_NAME}'         Run Keyword And Continue On Failure
    \       ...                         Software Information WBEM
    \       ...                         ELSE IF             'Network' in '${BOX_NAME}'      Run Keyword And Continue On Failure
    \       ...                         Network Information WBEM
    \       ...                         ${INDEX}
    \       ...                         ELSE IF             'Storage' in '${BOX_NAME}'      Run Keyword And Continue On Failure
    \       ...                         Storage Information WBEM
    \       ...                         ${INDEX}

    ${LEN}              Get Length      ${BOX_NAMES}
    Run Keyword If      ${LEN} > 0      Log     WBEM page doesn't contain this boxes : ${BOX_NAMES}     WARN

Windows PIV SMH verification
    [Documentation]     Post Install Verification
    Open Browser And Login SMH
    Wait Until Keyword Succeeds     1 min                       1 sec                       Select Frame   CHPHeaderFrame
    ${Data_Source}      Run Keyword And Continue On Failure     Wait Until Keyword Succeeds                 1 min   1sec
    ...                 Get Text    xpath=html/body/table/tbody/tr/td[6]/div/span/nobr
    Wait Until Keyword Succeeds     1 min                       1 sec                       unselect frame
    Run Keyword If      'SNMP' not in '${Data_Source}' and 'WBEM' not in '${Data_Source}'   Fail
    ...                 " Data Source is Empty "

    ## Verify PIV Information on WBEM
    Run Keyword If      '${Data_Source}' == 'SNMP'      Change Window To WBEM
    Wait Until Keyword Succeeds                         1 min               1 sec   unselect frame
    Wait Until Keyword Succeeds                         1 min               1 sec   Select Frame
    ...                 CHPHeaderFrame
    ${Data_Source}      Run Keyword And Continue On Failure                 Wait Until Keyword Succeeds         1min
    ...                 1sec
    ...                 Get Text                        xpath=html/body/table/tbody/tr/td[6]/div/span/nobr
    Run Keyword If      'WBEM' not in '${Data_Source}'                      Log     " WBEM is not enabled "     WARN
    Run Keyword And Continue On Failure                 Run Keyword If      'WBEM' not in '${Data_Source}'      Fail
    ...                 " WBEM is not enabled "
    Run Keyword If      'WBEM' in '${Data_Source}'      Windows PIV SMH WBEM verification

    ## Verify PIV Information on SNMP
    Change Window To SNMP
    Wait Until Keyword Succeeds         1 min                       1 sec   unselect frame
    Wait Until Keyword Succeeds         1 min                       1 sec   Select Frame
    ...                     CHPHeaderFrame
    ${Data_Source}          Run Keyword And Continue On Failure     Wait Until Keyword Succeeds     1min
    ...                     1sec
    ...                     Get Text    xpath=html/body/table/tbody/tr/td[6]/div/span/nobr
    Wait Until Keyword Succeeds         1 min                       1 sec   unselect frame
    Run Keyword If          'SNMP' not in '${Data_Source}'          Log     " SNMP is not enabled "
    ...                     WARN
    Run Keyword If          'SNMP' not in '${Data_Source}'          Fail    " Page not in SNMP mode "
    Change Window Format
    Home Page Screenshot    SNMP

    Select Frame            name=CHPDataFrame
    ${COUNT}                Get Matching Xpath Count    xpath=/html/body/table/tbody/tr/td/div[1]/div/h4
    ${T_COUNT}              Get Matching Xpath Count    xpath=/html/body/table/tbody/tr/td/div[*]/h4
    ${BOX_COUNT}            Run Keyword If              ${T_COUNT} > 3          Evaluate    ${COUNT} + ${T_COUNT} + 2
    ...                     ELSE IF                     ${T_COUNT} <= 3         Evaluate    ${COUNT} + ${T_COUNT} + 1
    unselect frame
    ${SNMP_BOX_NAMES} =     Create List                 System Configuration    NIC         Storage

    : FOR   ${INDEX}                    IN RANGE            1                       ${BOX_COUNT}
    \       Continue For Loop If        ${index} == 5
    \       Sleep                       10
    \       unselect frame
    \       Select Frame                name=CHPDataFrame
    \       Wait Until Element Is Visible                   xpath=/html/body/table/tbody/tr/td/div[1]/div/h4
    \       ...                         60
    \       ${BOX_NAME}                 Run Keyword If      ${INDEX} == 1           Get Text
    \       ...                         xpath=/html/body/table/tbody/tr/td/div[1]/div/h4
    \       ...                         ELSE IF             ${INDEX} > 1            Get Text
    \       ...                         xpath=/html/body/table/tbody/tr/td/div[${INDEX}]/h4
    \       unselect frame
    \       Remove Values From List     ${SNMP_BOX_NAMES}   ${BOX_NAME}
    \       Run Keyword If              'System Configuration' in '${BOX_NAME}'     Run Keyword And Continue On Failure
    \       ...                         Firmware and Software Version Info SNMP
    \       ...                         ELSE IF             'NIC' in '${BOX_NAME}'          Run Keyword And Continue On Failure
    \       ...                         NIC Version Info SNMP
    \       ...                         ${INDEX}
    \       ...                         ELSE IF             'Storage' in '${BOX_NAME}'      Run Keyword And Continue On Failure
    \       ...                         Storage Information SNMP
    \       ...                         ${INDEX}

    ${LEN}              Get Length          ${SNMP_BOX_NAMES}
    Run Keyword If      ${LEN} > 0          Log     SNMP page doesn't contain this boxes : ${SNMP_BOX_NAMES}    WARN
    Run Keyword And Continue On Failure     Webapp Information
    Close Browser

