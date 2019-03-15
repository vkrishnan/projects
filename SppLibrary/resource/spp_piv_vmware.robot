*** Settings ***
Library     RoboGalaxyLibrary
Library     String
Library     Collections
Library     OperatingSystem
Library     SSHLibrary
Library     SppLibrary


*** Variables ***


*** Keywords ***

Verify HPSUM Log Files Existence On Windows For Vmware Remote Node
    [Documentation]         Verifying HPSUM Log files Existence
    ...
    ...                     Example:
    ...
    ...                     | Verify HPSUM Log Files Existence On Windows For Vmware Remote Node |
    ${HPSUM_NAME} =         Run Keyword If      '${HPSUM_NAME}' == 'SUM'        Convert To Lowercase
    ...                     ${HPSUM_NAME}
    ...                     ELSE IF             '${HPSUM_NAME}' == 'HPSUM'      Set Variable
    ...                     ${HPSUM_NAME}
    Set Suite Variable      ${HPSUM_NAME}
    Run Keyword And Continue On Failure         SppLibrary.File Should Exist    ${HPSUM_TEMP_PATH_WIN}\\${HPSUM_DETAIL_LOG}
    Run Keyword And Continue On Failure         SppLibrary.File Should Exist
    ...                     ${HPSUM_TEMP_PATH_WIN}\\${HPSUM_DETAILS_LOG_XML}
    Run Keyword And Continue On Failure         SppLibrary.File Should Exist    ${HPSUM_TEMP_PATH_WIN}\\${HPSUM_LOG}
    #Run Keyword And Continue On Failure        SppLibrary.File Should Exist
    #...                    ${HPSUM_TEMP_PATH_WIN}\\${HPSUM_NAME}\\${REMOTE_NODE_IP}\\${HPSUM_DEPLOY_LOG}
    Run Keyword And Continue On Failure         SppLibrary.File Should Exist
    ...                     ${HPSUM_TEMP_PATH_WIN}\\${HPSUM_NAME}\\${REMOTE_NODE_IP}\\${HPSUM_INVENTORY_LOG}
    Run Keyword And Continue On Failure         SppLibrary.File Should Exist
    ...                     ${HPSUM_TEMP_PATH_WIN}\\${HPSUM_NAME}\\${REMOTE_NODE_IP}\\${HPSUM_NODE_LOG}
    Run Keyword And Continue On Failure         SppLibrary.File Should Exist
    ...                     ${HPSUM_TEMP_PATH_WIN}\\${HPSUM_NAME}\\${REMOTE_NODE_IP}\\${HPSUM_SCOUTING_LOG}

Verify HPSUM Log Files Existence On Linux For Vmware Remote Node
    [Documentation]         Verifying HPSUM Log files Existence
    ...
    ...                     Example:
    ...
    ...                     | Verify HPSUM Log Files Existence On Linux For Vmware Remote Node |
    ${HPSUM_NAME} =         Run Keyword If      '${HPSUM_NAME}' == 'SUM'        Convert To Lowercase
    ...                     ${HPSUM_NAME}
    ...                     ELSE IF             '${HPSUM_NAME}' == 'HPSUM'      Set Variable
    ...                     ${HPSUM_NAME}
    Set Suite Variable      ${HPSUM_NAME}
    Run Keyword And Continue On Failure         SSHLibrary.File Should Exist    ${HPSUM_TEMP_PATH_LIN}/${HPSUM_DETAIL_LOG}
    Run Keyword And Continue On Failure         SSHLibrary.File Should Exist    ${HPSUM_TEMP_PATH_LIN}/${HPSUM_DETAILS_LOG_XML}
    Run Keyword And Continue On Failure         SSHLibrary.File Should Exist    ${HPSUM_TEMP_PATH_LIN}/${HPSUM_LOG}
    Run Keyword And Continue On Failure         SSHLibrary.File Should Exist
    ...                     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/baseline/${HPSUM_BASELINE_LOG}
    #Run Keyword And Continue On Failure        SSHLibrary.File Should Exist
    #...                    ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/${REMOTE_NODE_IP}/${HPSUM_DEPLOY_LOG}
    Run Keyword And Continue On Failure         SSHLibrary.File Should Exist
    ...                     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/${REMOTE_NODE_IP}/${HPSUM_INVENTORY_LOG}
    Run Keyword And Continue On Failure         SSHLibrary.File Should Exist
    ...                     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/${REMOTE_NODE_IP}/${HPSUM_NODE_LOG}
    Run Keyword And Continue On Failure         SSHLibrary.File Should Exist
    ...                     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/${REMOTE_NODE_IP}/${HPSUM_SCOUTING_LOG}

Check Log File Sizes On Windows For Vmware Remote Node
    [Documentation]         Verification of HPSUM log files size because file size should not be empty
    ...
    ...                     Modified: Sriram Chowdary
    ...
    ...                     Removed hard coded filenames and passing filenames through variables
    ...
    ...                     Example:
    ...
    ...                     | Check Log File Sizes On Windows For Vmware Remote Node |
    # Check for hpsum_detail_log.txt
    SppLibrary.Get File     ${HPSUM_TEMP_PATH_WIN}\\${HPSUM_DETAIL_LOG}     .\\
    ${Size} =               OperatingSystem.Get File Size                   .\\${HPSUM_DETAIL_LOG}
    OperatingSystem.Remove File             .\\${HPSUM_DETAIL_LOG}
    Run Keyword And Continue On Failure     Run Keyword If                  '${Size}' == '0'
    ...                     Fail            file ${HPSUM_DETAIL_LOG} has zero size

    # Check for HPSUM_InstallDetails.xml
    SppLibrary.Get File     ${HPSUM_TEMP_PATH_WIN}\\${HPSUM_DETAILS_LOG_XML}    .\\
    ${Size} =               OperatingSystem.Get File Size                       .\\${HPSUM_DETAILS_LOG_XML}
    OperatingSystem.Remove File             .\\${HPSUM_DETAILS_LOG_XML}
    Run Keyword And Continue On Failure     Run Keyword If                      '${Size}' == '0'
    ...                     Fail            file ${HPSUM_DETAILS_LOG_XML} has zero size

    # Check for hpsum_log.txt
    SppLibrary.Get File     ${HPSUM_TEMP_PATH_WIN}\\${HPSUM_LOG}    .\\
    ${Size} =               OperatingSystem.Get File Size           .\\${HPSUM_LOG}
    OperatingSystem.Remove File             .\\${HPSUM_LOG}
    Run Keyword And Continue On Failure     Run Keyword If          '${Size}' == '0'
    ...                     Fail            file ${HPSUM_LOG} has zero size

    # Check for Baseline.log
    SppLibrary.Get File     ${HPSUM_TEMP_PATH_WIN}\\${HPSUM_NAME}\\baseline\\${HPSUM_BASELINE_LOG}      .\\
    ${Size} =               OperatingSystem.Get File Size       .\\${HPSUM_BASELINE_LOG}
    OperatingSystem.Remove File             .\\${HPSUM_BASELINE_LOG}
    Run Keyword And Continue On Failure     Run Keyword If      '${Size}' == '0'
    ...                     Fail            file ${HPSUM_BASELINE_LOG} has zero size

    # Check for deploy.log
    #SppLibrary.Get File    ${HPSUM_TEMP_PATH_WIN}\\${HPSUM_NAME}\\${REMOTE_NODE_IP}\\${HPSUM_DEPLOY_LOG}   .\\
    #${Size} =              OperatingSystem.Get File Size       .\\${HPSUM_DEPLOY_LOG}
    #OperatingSystem.Remove File            .\\${HPSUM_DEPLOY_LOG}
    #Run Keyword And Continue On Failure    Run Keyword If      '${Size}' == '0'
    #...                    Fail            file ${HPSUM_DEPLOY_LOG} has zero size

    # Check for inventory.log
    SppLibrary.Get File     ${HPSUM_TEMP_PATH_WIN}\\${HPSUM_NAME}\\${REMOTE_NODE_IP}\\${HPSUM_INVENTORY_LOG}    .\\
    ${Size} =               OperatingSystem.Get File Size       .\\${HPSUM_INVENTORY_LOG}
    OperatingSystem.Remove File             .\\${HPSUM_INVENTORY_LOG}
    Run Keyword And Continue On Failure     Run Keyword If      '${Size}' == '0'
    ...                     Fail            file ${HPSUM_INVENTORY_LOG} has zero size

    # Check for node.log
    SppLibrary.Get File     ${HPSUM_TEMP_PATH_WIN}\\${HPSUM_NAME}\\${REMOTE_NODE_IP}\\${HPSUM_NODE_LOG}     .\\
    ${Size} =               OperatingSystem.Get File Size       .\\${HPSUM_NODE_LOG}
    OperatingSystem.Remove File             .\\${HPSUM_NODE_LOG}
    Run Keyword And Continue On Failure     Run Keyword If      '${Size}' == '0'
    ...                     Fail            file ${HPSUM_NODE_LOG} has zero size

    # Check for scouting.log
    SppLibrary.Get File     ${HPSUM_TEMP_PATH_WIN}\\${HPSUM_NAME}\\${REMOTE_NODE_IP}\\${HPSUM_SCOUTING_LOG}     .\\
    ${Size} =               OperatingSystem.Get File Size       .\\${HPSUM_SCOUTING_LOG}
    OperatingSystem.Remove File             .\\${HPSUM_SCOUTING_LOG}
    Run Keyword And Continue On Failure     Run Keyword If      '${Size}' == '0'
    ...                     Fail            file ${HPSUM_SCOUTING_LOG} has zero size

Check Log File Sizes On Linux For Vmware Remote Node
    [Documentation]         Verification HPSUM log files size because file size should not be empty
    ...
    ...                     Modified: Sriram Chowdary
    ...
    ...                     Removed hard coded filenames and passing filenames through variables
    ...
    ...                     Example:
    ...
    ...                     | Check Log File Sizes On Linux For Vmware Remote Node |
    SSHLibrary.Get File     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_DETAIL_LOG}      .\\
    ${Size} =               OperatingSystem.Get File Size                   .\\${HPSUM_DETAIL_LOG}
    OperatingSystem.Remove File             .\\${HPSUM_DETAIL_LOG}
    Run Keyword And Continue On Failure     Run Keyword If                  '${Size}' == '0'
    ...                     Fail            file ${HPSUM_DETAIL_LOG} has zero size

    SSHLibrary.Get File     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_LOG}     .\\
    ${Size} =               OperatingSystem.Get File Size           .\\${HPSUM_LOG}
    OperatingSystem.Remove File             .\\${HPSUM_LOG}
    Run Keyword And Continue On Failure     Run Keyword If          '${Size}' == '0'
    ...                     Fail            file ${HPSUM_LOG} has zero size

    SSHLibrary.Get File     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_DETAILS_LOG_XML}     .\\
    ${Size} =               OperatingSystem.Get File Size                       .\\${HPSUM_DETAILS_LOG_XML}
    OperatingSystem.Remove File             .\\${HPSUM_DETAILS_LOG_XML}
    Run Keyword And Continue On Failure     Run Keyword If                      '${Size}' == '0'
    ...                     Fail            file ${HPSUM_DETAILS_LOG_XML} has zero size

    SSHLibrary.Get File     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/baseline/${HPSUM_BASELINE_LOG}     .\\
    ${Size} =               OperatingSystem.Get File Size       .\\${HPSUM_BASELINE_LOG}
    OperatingSystem.Remove File             .\\${HPSUM_BASELINE_LOG}
    Run Keyword And Continue On Failure     Run Keyword If      '${Size}' == '0'
    ...                     Fail            file ${HPSUM_BASELINE_LOG} has zero size

    #SSHLibrary.Get File    ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/${REMOTE_NODE_IP}/${HPSUM_DEPLOY_LOG}      .\\
    #${Size} =              OperatingSystem.Get File Size       .\\${HPSUM_DEPLOY_LOG}
    #OperatingSystem.Remove File            .\\${HPSUM_DEPLOY_LOG}
    #Run Keyword And Continue On Failure    Run Keyword If      '${Size}' == '0'
    #...                    Fail            file ${HPSUM_DEPLOY_LOG} has zero size

    SSHLibrary.Get File     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/${REMOTE_NODE_IP}/${HPSUM_INVENTORY_LOG}   .\\
    ${Size} =               OperatingSystem.Get File Size       .\\${HPSUM_INVENTORY_LOG}
    OperatingSystem.Remove File             .\\${HPSUM_INVENTORY_LOG}
    Run Keyword And Continue On Failure     Run Keyword If      '${Size}' == '0'
    ...                     Fail            file ${HPSUM_INVENTORY_LOG} has zero size

    SSHLibrary.Get File     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/${REMOTE_NODE_IP}/${HPSUM_NODE_LOG}    .\\
    ${Size} =               OperatingSystem.Get File Size       .\\${HPSUM_NODE_LOG}
    OperatingSystem.Remove File             .\\${HPSUM_NODE_LOG}
    Run Keyword And Continue On Failure     Run Keyword If      '${Size}' == '0'
    ...                     Fail            file ${HPSUM_NODE_LOG} has zero size

    SSHLibrary.Get File     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_NAME}/${REMOTE_NODE_IP}/${HPSUM_SCOUTING_LOG}    .\\
    ${Size} =               OperatingSystem.Get File Size       .\\${HPSUM_SCOUTING_LOG}
    OperatingSystem.Remove File             .\\${HPSUM_SCOUTING_LOG}
    Run Keyword And Continue On Failure     Run Keyword If      '${Size}' == '0'
    ...                     Fail            file ${HPSUM_SCOUTING_LOG} has zero size

Component Status Post Installation On Windows For Vmware Remote Node
    [Documentation]         Verifying Component Status After Installation
    ...
    ...                     Modified: Sriram Chowdary
    ...
    ...                     Removed hard coded filenames and passing filenames through variables
    ...
    ...                     Example:
    ...
    ...                     | Component Status Post Installation On Windows For Vmware Remote Node |
    SppLibrary.Get File     ${HPSUM_TEMP_PATH_WIN}\\${HPSUM_DETAIL_LOG}     .\\
    Run Keyword And Continue On Failure     Get Component Status Post Installation For Vmware Remote Node
    ...                     .\\${HPSUM_DETAIL_LOG}
    OperatingSystem.Remove File             .\\${HPSUM_DETAIL_LOG}

Component Status Post Installation On Linux For Vmware Remote Node
    [Documentation]         Verifying Component Status After Installation
    ...
    ...                     Modified: Sriram Chowdary
    ...
    ...                     Removed hard coded filenames and passing filenames through variables
    ...
    ...                     Example:
    ...
    ...                     | Component Status Post Installation On Linux For Vmware Remote Node |
    SSHLibrary.Get File     ${HPSUM_TEMP_PATH_LIN}/${HPSUM_DETAIL_LOG}      .\\
    Run Keyword And Continue On Failure     Get Component Status Post Installation For Vmware Remote Node
    ...                     .\\${HPSUM_DETAIL_LOG}
    OperatingSystem.Remove File             .\\${HPSUM_DETAIL_LOG}

