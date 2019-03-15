*** Settings ***
Library     RoboGalaxyLibrary
Library     String
Library     Collections
Library     OperatingSystem
Library     SSHLibrary


*** Variables ***
${LOG_LOCATION}     localhost
${PIV_TIMEOUT}      60
${PIV_TIMEOUT1}     120


*** Keywords ***
Execute Linux Command For SNMP Agents Configuration
    ### Configuring Agents by using hpsnmpconfig ###
    Write                       hpsnmpconfig --a --rws public --ros public --rwmips 127.0.0.1 public --romips 127.0.0.1 public --tcs public --tdips 127.0.0.1 public --sci Linux --sli USA
    Set Client Configuration    ${PIV_TIMEOUT1} seconds     prompt=#
    ${stdout} =                 Read Until Prompt
    Sleep                       5s
    @{lines} =                  Split To Lines              ${stdout}
    ${stdout}=                  Catenate                    SEPARATOR=      @{lines}
    Run Keyword And Continue On Failure                     Run Keyword If
    ...                         'Starting' not in '${stdout.strip()}'       Fail
    ...                         SNMP Configuration Not Started.
    Run Keyword And Continue On Failure                     Run Keyword If
    ...                         'started' not in '${stdout.strip()}'        Fail
    ...                         SNMP Configuration FAILED.
    Write                       service hp-snmp-agents restart
    Set Client Configuration    ${PIV_TIMEOUT} seconds      prompt=#
    ${stdout} =                 Read Until Prompt
    Sleep                       5s

Verify Services are Running
    ### Verifying Services are Running after Configuration ###
    ${output} =     SSHLibrary.Execute Command                      service hp-snmp-agents status   ${PIV_TIMEOUT}
    @{lines} =      Split To Lines          ${output}
    ${output}=      Catenate                SEPARATOR=              @{lines}
    Run Keyword And Continue On Failure     Run Keyword If
    \               ...                     'running' not in '${output.strip()}' or 'FAIL' in '${output.strip()}' or 'STOPPED' in '${output.strip()}'
    \               ...                     Fail                    Error in service: hp-snmp-agents
    ${output} =     SSHLibrary.Execute Command                      service hp-health status | grep running
    ...             ${PIV_TIMEOUT}
    Run Keyword And Continue On Failure     Run Keyword If
    ...             'running' not in '${output.strip()}' or 'FAIL' in '${output.strip()}' or 'STOPPED' in '${output.strip()}'
    ...             Fail                    service hp-health status failed
    ${output} =     SSHLibrary.Execute Command                      service hpsmhd status | grep running
    ...             ${PIV_TIMEOUT}
    Run Keyword And Continue On Failure     Run Keyword If          'running' not in '${output.strip()}'
    ...             Fail                    service hpsmhd status failed
    ${output} =     SSHLibrary.Execute Command                      lsmod | grep hpilo
    Run Keyword And Continue On Failure     Run Keyword If          'hpilo' not in '${output}'
    ...             Fail                    hpilo failed to load
    SSHLibrary.Execute Command              service snmpd restart   ${PIV_TIMEOUT}
    ${output} =     SSHLibrary.Execute Command                      service snmpd status | grep running
    ...             ${PIV_TIMEOUT}
    Run Keyword And Continue On Failure     Run Keyword If          'running' not in '${output.strip()}'
    ...             Fail                    snmpd fails to run

Verify HPSUM Log Files Existence
    ### Verifying Log files are exists after reboot ###
    ${HPSUM_NAME} =         Run Keyword If              '${HPSUM_NAME}' == 'SUM'                Convert To Lowercase
    ...                     ${HPSUM_NAME}
    ...                     ELSE IF                     '${HPSUM_NAME}' == 'HPSUM'              Set Variable
    ...                     ${HPSUM_NAME}
    Set Suite Variable      ${HPSUM_NAME}
    ${hpsum_detail_log_status} =                        Run Keyword And Return Status           SSHLibrary.File Should Exist
    ...                     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_DETAIL_LOG}
    Run Keyword If          '${hpsum_detail_log_status}'=='False'   Log                         hpsum detail log Not Present
    ...                     WARN
    ${hpsum_log_status} =   Run Keyword And Return Status           SSHLibrary.File Should Exist
    ...                     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_LOG}
    Run Keyword If          '${hpsum_log_status}'=='False'          Log                         hpsum log Not Present
    ...                     WARN
    ${hpsum_install_details} =                          Run Keyword And Return Status           SSHLibrary.File Should Exist
    ...                     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_DETAILS_LOG_XML}
    Run Keyword If          '${hpsum_install_details}'=='False'     Log
    ...                     HPSUM Install Details Not Present
    ...                     WARN
    ${baseline} =           Run Keyword And Return Status           SSHLibrary.File Should Exist
    ...                     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/baseline/${HPSUM_BASELINE_LOG}
    Run Keyword If          '${baseline}'=='False'      Log         Baseline Log Not Present    WARN
    ${deploy} =             Run Keyword And Return Status           SSHLibrary.File Should Exist
    ...                     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/${LOG_LOCATION}/${HPSUM_DEPLOY_LOG}
    Run Keyword If          '${deploy}'=='False'        Log         deploy log Not Present      WARN
    ${inventory} =          Run Keyword And Return Status           SSHLibrary.File Should Exist
    ...                     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/${LOG_LOCATION}/${HPSUM_INVENTORY_LOG}
    Run Keyword If          '${inventory}'=='False'     Log         inventory log Not Present   WARN
    ${node} =               Run Keyword And Return Status           SSHLibrary.File Should Exist
    ...                     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/${LOG_LOCATION}/${HPSUM_NODE_LOG}
    Run Keyword If          '${node}'=='False'          Log         node log Not Present        WARN
    ${scouting} =           Run Keyword And Return Status           SSHLibrary.File Should Exist
    ...                     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/${LOG_LOCATION}/${HPSUM_SCOUTING_LOG}
    Run Keyword If          '${scouting}'=='False'      Log         scouting log Not Present    WARN
    ${component} =          Run Keyword And Return Status           SSHLibrary.File Should Exist
    ...                     /var/cpq/Component.log
    Run Keyword If          '${component}'=='False'     Log         Component Log Not Present   WARN

Verification Of Files For Write Permission
    ### Verification of write permission of log files-The log file should not have write permission ###
    ${component} =          SSHLibrary.Execute Command          ls -lrt /var/cpq/| grep 'Component.log'     ${PIV_TIMEOUT}
    ${component_status} =   Run Keyword And Return Status       Should Not Be Empty                         ${component}
    Log                     ${component}
    Run Keyword If          '${component_status}'=='True'       Check Permission Of Files                   ${component}
    Run Keyword If          '${component_status}'=='False'      Log
    ...                     Permission Field is Not Present because Component Log is Absent
    ...                     WARN

    ${scouting} =           SSHLibrary.Execute Command
    ...                     ls -lrt ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/${LOG_LOCATION}/| grep '${HPSUM_SCOUTING_LOG}'
    ...                     ${PIV_TIMEOUT}
    ${scouting_status} =    Run Keyword And Return Status   Should Not Be Empty         ${scouting}
    Log                     ${scouting}
    Run Keyword If          '${scouting_status}'=='True'    Check Permission Of Files   ${scouting}
    Run Keyword If          '${scouting_status}'=='False'   Log
    ...                     Permission Field is Not Present because scouting Log is Absent
    ...                     WARN

    ${node} =           SSHLibrary.Execute Command
    ...                 ls -lrt ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/${LOG_LOCATION}/| grep '${HPSUM_NODE_LOG}'
    ...                 ${PIV_TIMEOUT}
    ${node_status} =    Run Keyword And Return Status   Should Not Be Empty         ${node}
    Log                 ${node}
    Run Keyword If      '${node_status}'=='True'        Check Permission Of Files   ${node}
    Run Keyword If      '${node_status}'=='False'       Log
    ...                 Permission Field is Not Present because node Log is Absent
    ...                 WARN

    ###Run Keyword And Continue On Failure                      SppLibrary.Check Permission Of Files    ${node}###
    ${inventory} =          SSHLibrary.Execute Command
    ...                     ls -lrt ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/${LOG_LOCATION}/| grep '${HPSUM_INVENTORY_LOG}'
    ...                     ${PIV_TIMEOUT}
    ${inventory_status} =   Run Keyword And Return Status       Should Not Be Empty                     ${inventory}
    Log                     ${inventory}
    Run Keyword If          '${inventory_status}'=='True'       Check Permission Of Files               ${inventory}
    Run Keyword If          '${inventory_status}'=='False'      Log
    ...                     Permission Field is Not Present because inventory Log is Absent
    ...                     WARN

    ###Run Keyword And Continue On Failure                  SppLibrary.Check Permission Of Files    ${inventory}###
    ${deploy} =             SSHLibrary.Execute Command
    ...                     ls -lrt ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/${LOG_LOCATION}/| grep '${HPSUM_DEPLOY_LOG}'
    ...                     ${PIV_TIMEOUT}
    ${deploy_status} =      Run Keyword And Return Status   Should Not Be Empty                     ${deploy}
    Log                     ${deploy}
    Run Keyword If          '${deploy_status}'=='True'      Check Permission Of Files               ${deploy}
    Run Keyword If          '${deploy_status}'=='False'     Log
    ...                     Permission Field is Not Present because deploy Log is Absent
    ...                     WARN

    ${baseline} =           SSHLibrary.Execute Command
    ...                     ls -lrt ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/baseline/| grep '${HPSUM_BASELINE_LOG}'
    ...                     ${PIV_TIMEOUT}
    ${baseline_status} =    Run Keyword And Return Status   Should Not Be Empty         ${baseline}
    Log                     ${baseline}
    Run Keyword If          '${baseline_status}'=='True'    Check Permission Of Files   ${baseline}
    Run Keyword If          '${baseline_status}'=='False'   Log
    ...                     Permission Field is Not Present because Baseline Log is Absent
    ...                     WARN

    ${hpsum_install_detail} =   SSHLibrary.Execute Command
    ...                         ls -lrt ${HPSUM_TEMP_PATH_LIN}/| grep '${HPSUM_DETAILS_LOG_XML}'
    ...                         ${PIV_TIMEOUT}
    ${hpsum_install_detail_status} =    Run Keyword And Return Status       Should Not Be Empty
    ...                         ${hpsum_install_detail}
    Log                         ${hpsum_install_detail}
    Run Keyword If              '${hpsum_install_detail_status}'=='True'    Check Permission Of Files
    ...                         ${hpsum_install_detail}
    Run Keyword If              '${hpsum_install_detail_status}'=='False'   Log
    ...                         Permission Field is Not Present because HPSUM_InstallDetails Log is Absent
    ...                         WARN

    ${hpsum_log} =          SSHLibrary.Execute Command          ls -lrt ${HPSUM_TEMP_PATH_LIN}/| grep '${HPSUM_LOG}'
    ...                     ${PIV_TIMEOUT}
    ${hpsum_log_status} =   Run Keyword And Return Status       Should Not Be Empty         ${hpsum_log}
    Log                     ${hpsum_log}
    Run Keyword If          '${hpsum_log_status}'=='True'       Check Permission Of Files   ${hpsum_log}
    Run Keyword If          '${hpsum_log_status}'=='False'      Log
    ...                     Permission Field is Not Present because hpsum Log is Absent
    ...                     WARN

    ${hpsum_detail_log} =   SSHLibrary.Execute Command              ls -lrt ${HPSUM_TEMP_PATH_LIN}/| grep '${HPSUM_DETAIL_LOG}'
    ...                     ${PIV_TIMEOUT}
    ${hpsum_detail_log_status} =    Run Keyword And Return Status   Should Not Be Empty         ${hpsum_detail_log}
    Log                     ${hpsum_detail_log}
    Run Keyword If          '${hpsum_detail_log_status}'=='True'    Check Permission Of Files   ${hpsum_detail_log}
    Run Keyword If          '${hpsum_detail_log_status}'=='False'   Log
    ...                     Permission Field is Not Present because hpsum detail Log is Absent
    ...                     WARN

    ###Run Keyword And Continue On Failure      SppLibrary.Check Permission Of Files    ${hpsum_detail_log}###

File Size Should Not Be Zero
    ### Verification of files size because file size should not be empty ###
    SSHLibrary.Get File     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_LOG}                 .\\
    ${Size} =               OperatingSystem.Get File Size                       ${HPSUM_LOG}
    OperatingSystem.Remove File                         ${HPSUM_LOG}
    Run Keyword And Continue On Failure                 Should Be True          '${Size}' > '0'
    ...                     file ${HPSUM_LOG} has zero size
    SSHLibrary.Get File     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_DETAIL_LOG}          .\\
    ${Size} =               OperatingSystem.Get File Size                       ${HPSUM_DETAIL_LOG}
    OperatingSystem.Remove File                         ${HPSUM_DETAIL_LOG}
    Run Keyword And Continue On Failure                 Should Be True          '${Size}' > '0'
    ...                     file ${HPSUM_DETAIL_LOG} has zero size
    SSHLibrary.Get File     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_DETAILS_LOG_XML}     .\\
    ${Size} =               OperatingSystem.Get File Size                       ${HPSUM_DETAILS_LOG_XML}
    OperatingSystem.Remove File                         ${HPSUM_DETAILS_LOG_XML}
    Run Keyword And Continue On Failure                 Should Be True          '${Size}' > '0'
    ...                     file ${HPSUM_DETAILS_LOG_XML} has zero size
    SSHLibrary.Get File     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/baseline/${HPSUM_BASELINE_LOG}             .\\
    ${Size} =               OperatingSystem.Get File Size                       ${HPSUM_BASELINE_LOG}
    OperatingSystem.Remove File                         ${HPSUM_BASELINE_LOG}
    Run Keyword And Continue On Failure                 Should Be True          '${Size}' > '0'
    ...                     file ${HPSUM_BASELINE_LOG} has zero size
    SSHLibrary.Get File     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/${LOG_LOCATION}/${HPSUM_DEPLOY_LOG}        .\\
    ${Size} =               OperatingSystem.Get File Size                       ${HPSUM_DEPLOY_LOG}
    OperatingSystem.Remove File                         ${HPSUM_DEPLOY_LOG}
    Run Keyword And Continue On Failure                 Should Be True          '${Size}' > '0'
    ...                     file ${HPSUM_DEPLOY_LOG} has zero size
    SSHLibrary.Get File     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/${LOG_LOCATION}/${HPSUM_INVENTORY_LOG}     .\\
    ${Size} =               OperatingSystem.Get File Size                       ${HPSUM_INVENTORY_LOG}
    OperatingSystem.Remove File                         ${HPSUM_INVENTORY_LOG}
    Run Keyword And Continue On Failure                 Should Be True          '${Size}' > '0'
    ...                     file ${HPSUM_INVENTORY_LOG} has zero size
    SSHLibrary.Get File     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/${LOG_LOCATION}/${HPSUM_NODE_LOG}          .\\
    ${Size} =               OperatingSystem.Get File Size                       ${HPSUM_NODE_LOG}
    OperatingSystem.Remove File                         ${HPSUM_NODE_LOG}
    Run Keyword And Continue On Failure                 Should Be True          '${Size}' > '0'
    ...                     file ${HPSUM_NODE_LOG} has zero size
    SSHLibrary.Get File     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/${LOG_LOCATION}/${HPSUM_SCOUTING_LOG}      .\\
    ${Size} =               OperatingSystem.Get File Size                       ${HPSUM_SCOUTING_LOG}
    OperatingSystem.Remove File                         ${HPSUM_SCOUTING_LOG}
    Run Keyword And Continue On Failure                 Should Be True          '${Size}' > '0'
    ...                     file ${HPSUM_SCOUTING_LOG} has zero size
    SSHLibrary.Get File     /var/cpq/Component.log      .\\
    ${Size} =               OperatingSystem.Get File Size                       Component.log
    OperatingSystem.Remove File                         Component.log
    Run Keyword And Continue On Failure                 Should Be True          '${Size}' > '0'
    ...                     file Component.log has zero size

Component Status Post Installation
    ### Verifying Component Status After Installation ###
    SSHLibrary.Get File                         ${HPSUM_TEMP_PATH_LIN}/${HPSUM_DETAIL_LOG}      .\\
    Get Component Status Post Installation      ${HPSUM_DETAIL_LOG}
    OperatingSystem.Remove File                 ${HPSUM_DETAIL_LOG}

Verify HP SSA Service
    ### Checking for SSA service is Functioning Properly###
    Write                       ssa -stop
    Set Client Configuration    ${PIV_TIMEOUT} seconds      prompt=#
    ${output} =                 Read Until Prompt
    @{lines} =                  Split To Lines              ${output}
    ${output}=                  Catenate                    SEPARATOR=      @{lines}
    Run Keyword And Continue On Failure                     Run Keyword IF
    ...                         'not running' not in '${output.strip()}' and 'stopped' not in '${output.strip()}'
    ...                         Fail                        Error in Stopping HPSSA.
    Write                       ssa -start
    Set Client Configuration    ${PIV_TIMEOUT} seconds      prompt=#
    ${output} =                 Read Until Prompt
    @{lines} =                  Split To Lines              ${output}
    ${output}=                  Catenate                    SEPARATOR=      @{lines}
    Run Keyword And Continue On Failure                     Run Keyword If
    ...                         'Only one instance of the HP Smart Storage' not in '${output.strip()}' and 'has started' not in '${output.strip()}'
    ...                         Fail                        Error in Starting HPSSA.

Restart hpsmhd Service
    [Documentation]     Restart snmpd and verify status
    ${output} =         SSHLibrary.Execute Command      ssa -start
    Sleep               2
    ${output} =         SSHLibrary.Execute Command      service hpsmhd restart
    Sleep               5
    ${output} =         SSHLibrary.Execute Command      service hpsmhd status | grep 'running'
    Run Keyword And Continue On Failure                 Should Contain      '${output}'     running
    ...                 " hpsmhd was not enabled "

