
#xpath variables for HPSUM 7.x version

LOCALHOST_GUIDED_BUTTON = r'//*[@id="select-guided-update"]/div/a/div'

#User mode selection page
INTERACTIVE_MODE_RADIO_BUTTON = r'//*[@id="interactive-mode"]'
NON_INTERACTIVE_MODE_RADIO_BUTTON = r'//*[@id="non-interactive-mode"]'
INTERACTIVE_MODE_PAGE_OK_BUTTON = r'/*[@id="hpsum-action-ok-button"]'
INTERACTIVE_MODE_PAGE_CANCEL_BUTTON = r'//*[@id="hpsum-action-cancel-button"]'

#Inventory page
BASELINE_INVENTORY_TEXT = r'//*[@id="hpsum-otu-inventory-baseline"]/tbody/tr/td[3]'
BASELINE_INVENTORY_RESULT = r'//*[@id="hpsum-otu-inventory-baseline"]/tbody/tr/td[5]'
NODE_INVENTORY_TEXT = r'//*[@id="hpsum-otu-inventory-node"]/tbody/tr/td[3]'
NODE_INVENTORY_RESULT = r'//*[@id="hpsum-otu-inventory-node"]/tbody/tr/td[5]'
LOCALHOST_AS_NODE_NAME_INVENTORY_TEXT = r'//*[@id="hpsum-otu-inventory-node"]/tbody/tr/td[2]'
INVENTORY_NEXT_BUTTON = r'//*[@id="step0Next"]'
INVENTORY_ABORT_BUTTON = r'//*[@id="step0Abort"]'
INVENTORY_STAROVER_BUTTON = r'//*[@id="step0Reset"]'
INVENTORY_REBOOT_BUTTON = r'//*[@id="step0Reboot"]'

#Components page
STEP2_HEADER = r'//*[@id="hpsum-step2"]'
TOTAL_SELECTED_COMPONENTS_TEXT = r'//*[@id="selected-component-number-N1localhost"]'
TOTAL_AVAILABLE_COMPONENTS_TEXT = r'//*[@id="total-component-number-N1localhost"]'
COMPONENT_TABLE = r'//*[@id="hpsum-otu-installables-N1localhost-table"]/tbody/tr[*]'
COMPONENTS_SELECTED = r'//*[@id="hpsum-otu-installables-N1localhost-table"]/tbody/tr[contains(@class,"hp-selected")]'
COMPONENT_TEXT = r'//*[@id="hpsum-otu-installables-N1localhost-table"]/tbody/tr[{0}]/td[2]'
COMPONENT_SELECT_VALUE_TEXT = r'//*[@id="hpsum-otu-installables-N1localhost-table"]/tbody/tr[{0}]/td[1]'
DEPENDENCY_COMPONENTS = r'//*[@id="selected"]/div[contains(@class,"hp-status-error")]'
COMPONENTS_PAGE_COMMANDS = r'//*[@id="step1commands"]'
COMPONENTS_PAGE_PREVIOUS_BUTTON = r'//*[@id="step1Prev"]'
COMPONENTS_PAGE_NEXT_BUTTON = r'//*[@id="step1Next"]'
COMPONENTS_PAGE_STARTOVER_BUTTON = r'//*[@id="step1Reset"]'

#Deployment page
STEP3_HEADER = r'//*[@id="hpsum-step3"]'
DEPLOY_PAGE_HEADING = r'//*[@id="step2"]/div/h1'
LOCALHOST_AS_NODE_NAME_DEPLOY_TEXT = r'//*[@id="hpsum-otu-install-progress"]/tbody/tr/td[2]'
DEPLOYMENT_STATUS_TEXT = r'//*[@id="hpsum-otu-install-progress"]/tbody/tr/td[3]'
DEPLOYMENT_RESULT_TEXT = r'.//*[@id="hpsum-otu-install-progress"]/tbody/tr/td[5]'
DEPLOYMENT_PAGE_COMMANDS = r'//*[@id="step2commands"]'
DEPLOYMENT_PAGE_REBOOT = r'//*[@id="step2Reboot"]'
DEPLOYMENT_PAGE_REBOOT_CONFIRM = r'//*[@id="hp-body-div"]/div[8]/div/div/div/footer/div/button[1]'
DEPLOYMENT_PAGE_REBOOT_CONFIRM_UPDATED = r'/html/body/div[2]/div[7]/div/div/div/footer/div/button[1]'
DEPLOYED_COMPONENTS = r'//*[@id="hpsum-otu-node-N1localhost-installresult-table"]/tbody/tr'
DEPLOYED_COMPONENT_NAME_TEXT = r'//*[@id="hpsum-otu-node-N1localhost-installresult-table"]/tbody/tr[{0}]/td[2]'

