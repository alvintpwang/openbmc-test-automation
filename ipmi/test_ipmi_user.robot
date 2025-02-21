*** Settings ***
Documentation       Test suite for OpenBMC IPMI user management.

Resource            ../lib/ipmi_client.robot
Resource            ../lib/openbmc_ffdc.robot
Library             ../lib/ipmi_utils.py

Test Teardown       Test Teardown Execution
Suite Teardown      Delete All Non Root IPMI User

*** Variables ***

${invalid_username}     user%
${invalid_password}     abc123
${root_userid}          1
${operator_level_priv}  0x3
${user_priv}            2
${operator_priv}        3
${admin_level_priv}     4
${no_access_priv}       15
${valid_password}       0penBmc1
${max_password_length}  20
${ipmi_setaccess_cmd}   channel setaccess


*** Test Cases ***

Verify IPMI User Summary
    [Documentation]  Verify IPMI maximum supported IPMI user ID and
    ...  enabled user form user summary
    [Tags]  Verify_IPMI_User_Summary

    # Delete all non-root IPMI (i.e. except userid 1)
    Delete All Non Root IPMI User

    # Create a valid user and enable it.
    ${random_username}=  Generate Random String  8  [LETTERS]
    ${random_userid}=  Evaluate  random.randint(2, 15)  modules=random
    IPMI Create User  ${random_userid}  ${random_username}
    Run IPMI Standard Command  user enable ${random_userid}

    # Verify maximum user count IPMI local user can have. Also verify
    # currently enabled users.
    ${resp}=  Wait Until Keyword Succeeds  15 sec  5 sec  Run IPMI Standard Command  user summary
    ${enabled_user_count}=
    ...  Get Lines Containing String  ${resp}  Enabled User Count
    ${maximum_ids}=  Get Lines Containing String  ${resp}  Maximum IDs
    Should Contain  ${enabled_user_count}  2
    Should Contain  ${maximum_ids}  15


Verify IPMI User Creation With Valid Name And ID
    [Documentation]  Create user via IPMI and verify.
    [Tags]  Test_IPMI_User_Creation_With_Valid_Name_And_ID

    ${random_username}=  Generate Random String  8  [LETTERS]
    ${random_userid}=  Evaluate  random.randint(2, 15)  modules=random
    IPMI Create User  ${random_userid}  ${random_username}


Verify IPMI User Creation With Invalid Name
    [Documentation]  Verify error while creating IPMI user with invalid
    ...  name(e.g. user name with special characters).
    [Tags]  Verify_IPMI_User_Creation_With_Invalid_Name

    ${random_userid}=  Evaluate  random.randint(2, 15)  modules=random
    ${msg}=  Run Keyword And Expect Error  *  Run IPMI Standard Command
    ...  user set name ${random_userid} ${invalid_username}
    Should Contain  ${msg}  Invalid data


Verify IPMI User Creation With Invalid ID
    [Documentation]  Verify error while creating IPMI user with invalid
    ...  ID(i.e. any number greater than 15 or 0).
    [Tags]  Verify_IPMI_User_Creation_With_Invalid_ID

    @{id_list}=  Create List
    ${random_invalid_id}=  Evaluate  random.randint(16, 1000)  modules=random
    Append To List  ${id_list}  ${random_invalid_id}
    Append To List  ${id_list}  0

    FOR  ${id}  IN  @{id_list}
      ${msg}=  Run Keyword And Expect Error  *  Run IPMI Standard Command
      ...  user set name ${id} newuser
      Should Contain  ${msg}  User ID is limited to range
    END

Verify Setting IPMI User With Invalid Password
    [Documentation]  Verify error while setting IPMI user with invalid
    ...  password.
    [Tags]  Verify_Setting_IPMI_User_With_Invalid_Password

    # Create IPMI user.
    ${random_username}=  Generate Random String  8  [LETTERS]
    ${random_userid}=  Evaluate  random.randint(2, 15)  modules=random
    IPMI Create User  ${random_userid}  ${random_username}

    # Set invalid password for newly created user.
    ${msg}=  Run Keyword And Expect Error  *  Run IPMI Standard Command
    ...  user set password ${random_userid} ${invalid_password}

    Should Contain  ${msg}  Set User Password command failed

Verify Setting IPMI Root User With New Name
    [Documentation]  Verify error while setting IPMI root user with new
    ...  name.
    [Tags]  Verify_Setting_IPMI_Root_User_With_New_Name

    # Set invalid password for newly created user.
    ${msg}=  Run Keyword And Expect Error  *  Run IPMI Standard Command
    ...  user set name ${root_userid} abcd

    Should Contain  ${msg}  Set User Name command failed


Verify IPMI User Password Via Test Command
    [Documentation]  Verify IPMI user password using test command.
    [Tags]  Verify_IPMI_User_Password_Via_Test_Command

    # Create IPMI user.
    ${random_username}=  Generate Random String  8  [LETTERS]
    ${random_userid}=  Evaluate  random.randint(2, 15)  modules=random
    IPMI Create User  ${random_userid}  ${random_username}

    # Set valid password for newly created user.
    Run IPMI Standard Command
    ...  user set password ${random_userid} ${valid_password}

    # Verify newly set password using test command.
    ${msg}=  Run IPMI Standard Command
    ...  user test ${random_userid} ${max_password_length} ${valid_password}

    Should Contain  ${msg}  Success


Verify Setting Valid Password For IPMI User
    [Documentation]  Set valid password for IPMI user and verify.
    [Tags]  Verify_Setting_Valid_Password_For_IPMI_User

    # Create IPMI user.
    ${random_username}=  Generate Random String  8  [LETTERS]
    ${random_userid}=  Evaluate  random.randint(2, 15)  modules=random
    IPMI Create User  ${random_userid}  ${random_username}

    # Set valid password for newly created user.
    Run IPMI Standard Command
    ...  user set password ${random_userid} ${valid_password}

    # Enable IPMI user
    Run IPMI Standard Command  user enable ${random_userid}

    # Delay added for IPMI user to get enable
    Sleep  5s

    # Set admin privilege and enable IPMI messaging for newly created user
    Set Channel Access  ${random_userid}  ipmi=on privilege=${admin_level_priv}

    Verify IPMI Username And Password  ${random_username}  ${valid_password}


Verify IPMI User Creation With Same Name
    [Documentation]  Verify error while creating two IPMI user with same name.
    [Tags]  Verify_IPMI_User_Creation_With_Same_Name

    ${random_username}=  Generate Random String  8  [LETTERS]
    IPMI Create User  2  ${random_username}

    # Set same username for another IPMI user.
    ${msg}=  Run Keyword And Expect Error  *  Run IPMI Standard Command
    ...  user set name 3 ${random_username}
    Should Contain  ${msg}  Invalid data field in request


Verify Setting IPMI User With Null Password
    [Documentation]  Verify error while setting IPMI user with null
    ...  password.
    [Tags]  Verify_Setting_IPMI_User_With_Null_Password

    # Create IPMI user.
    ${random_username}=  Generate Random String  8  [LETTERS]
    ${random_userid}=  Evaluate  random.randint(2, 15)  modules=random
    IPMI Create User  ${random_userid}  ${random_username}

    # Set null password for newly created user.
    ${msg}=  Run Keyword And Expect Error  *  Run IPMI Standard Command
    ...  user set password ${random_userid} ""

    Should Contain  ${msg}  Invalid data field in request


Verify IPMI User Deletion
    [Documentation]  Delete user via IPMI and verify.
    [Tags]  Verify_IPMI_User_Deletion

    ${random_username}=  Generate Random String  8  [LETTERS]
    ${random_userid}=  Evaluate  random.randint(2, 15)  modules=random
    IPMI Create User  ${random_userid}  ${random_username}

    # Delete IPMI User and verify
    Run IPMI Standard Command  user set name ${random_userid} ""
    ${user_info}=  Get User Info  ${random_userid}
    Should Be Equal  ${user_info['user_name']}  ${EMPTY}


Test IPMI User Privilege Level
    [Documentation]  Verify IPMI user with user privilege can only run user level commands.
    [Tags]  Test_IPMI_User_Privilege_Level
    [Template]  Test IPMI User Privilege

    #Privilege level     User Cmd Status  Operator Cmd Status  Admin Cmd Status
    ${user_priv}         Passed           Failed               Failed


Test IPMI Operator Privilege Level
    [Documentation]  Verify IPMI user with operator privilege can only run user and operator levels commands.
    ...  level is set to operator.
    [Tags]  Test_IPMI_Operator_Privilege_Level
    [Template]  Test IPMI User Privilege

    #Privilege level     User Cmd Status  Operator Cmd Status  Admin Cmd Status
    ${operator_priv}     Passed           Passed               Failed


Test IPMI Administrator Privilege Level
    [Documentation]  Verify IPMI user with admin privilege can run all levels command.
    [Tags]  Test_IPMI_Administrator_Privilege_Level
    [Template]  Test IPMI User Privilege

    #Privilege level     User Cmd Status  Operator Cmd Status  Admin Cmd Status
    ${admin_level_priv}  Passed           Passed               Passed


Test IPMI No Access Privilege Level
    [Documentation]  Verify IPMI user with no access privilege can not run only any level command.
    [Tags]  Test_IPMI_No_Access_Privilege_Level
    [Template]  Test IPMI User Privilege

    #Privilege level     User Cmd Status  Operator Cmd Status  Admin Cmd Status
    ${no_access_priv}    Failed           Failed               Failed


Enable IPMI User And Verify
    [Documentation]  Enable IPMI user and verify that the user is able
    ...  to run IPMI command.
    [Tags]  Enable_IPMI_User_And_Verify

    # Create IPMI user and set valid password.
    ${random_username}=  Generate Random String  8  [LETTERS]
    ${random_userid}=  Evaluate  random.randint(2, 15)  modules=random
    IPMI Create User  ${random_userid}  ${random_username}
    Run IPMI Standard Command
    ...  user set password ${random_userid} ${valid_password}

    # Set admin privilege and enable IPMI messaging for newly created user.
    Set Channel Access  ${random_userid}  ipmi=on privilege=${admin_level_priv}

    # Delay added for user privilge to get set.
    Sleep  5s

    # Enable IPMI user and verify.
    Run IPMI Standard Command  user enable ${random_userid}
    ${user_info}=  Get User Info  ${random_userid}
    Should Be Equal  ${user_info['enable_status']}  enabled

    # Verify that enabled IPMI  user is able to run IPMI command.
    Verify IPMI Username And Password  ${random_username}  ${valid_password}


Disable IPMI User And Verify
    [Documentation]  Disable IPMI user and verify that that the user
    ...  is unable to run IPMI command.
    [Tags]  Disable_IPMI_User_And_Verify

    # Create IPMI user and set valid password.
    ${random_username}=  Generate Random String  8  [LETTERS]
    ${random_userid}=  Evaluate  random.randint(2, 15)  modules=random
    IPMI Create User  ${random_userid}  ${random_username}
    Run IPMI Standard Command
    ...  user set password ${random_userid} ${valid_password}

    # Set admin privilege and enable IPMI messaging for newly created user.
    Set Channel Access  ${random_userid}  ipmi=on privilege=${admin_level_priv}

    # Disable IPMI user and verify.
    Run IPMI Standard Command  user disable ${random_userid}
    ${user_info}=  Get User Info  ${random_userid}
    Should Be Equal  ${user_info['enable_status']}  disabled

    # Verify that disabled IPMI  user is unable to run IPMI command.
    ${msg}=  Run Keyword And Expect Error  *  Verify IPMI Username And Password
    ...  ${random_username}  ${valid_password}
    Should Contain  ${msg}  Unable to establish IPMI


Verify IPMI Root User Password Change
    [Documentation]  Change IPMI root user password and verify that
    ...  root user is able to run IPMI command.
    [Tags]  Verify_IPMI_Root_User_Password_Change
    [Teardown]  Wait Until Keyword Succeeds  15 sec  5 sec
    ...  Set Default Password For IPMI Root User

    # Set new password for root user.
    Run IPMI Standard Command
    ...  user set password ${root_userid} ${valid_password}

    # Verify that root user is able to run IPMI command using new password.
    Wait Until Keyword Succeeds  15 sec  5 sec  Verify IPMI Username And Password
    ...  root  ${valid_password}


Verify Administrator And No Access Privilege For Different Channels
    [Documentation]  Set administrator and no access privilege for different channels and verify.
    [Tags]  Verify_Administrator_And_No_Access_Privilege_For_Different_Channels

    # Create IPMI user and set valid password.
    ${random_username}=  Generate Random String  8  [LETTERS]
    ${random_userid}=  Evaluate  random.randint(2, 15)  modules=random
    IPMI Create User  ${random_userid}  ${random_username}
    Run IPMI Standard Command
    ...  user set password ${random_userid} ${valid_password}

    # Set admin privilege for newly created user with channel 1.
    Set Channel Access  ${random_userid}  ipmi=on privilege=${admin_level_priv}  1

    # Set no access privilege for newly created user with channel 2.
    Set Channel Access  ${random_userid}  ipmi=on privilege=${no_access_priv}  2

    # Enable IPMI user and verify.
    Run IPMI Standard Command  user enable ${random_userid}
    ${user_info}=  Get User Info  ${random_userid}
    Should Be Equal  ${user_info['enable_status']}  enabled

    # Verify that user is able to run administrator level IPMI command with channel 1.
    Verify IPMI Command  ${random_username}  ${valid_password}  Administrator  1

    # Verify that user is unable to run IPMI command with channel 2.
    Run IPMI Standard Command  sel info 2  expected_rc=${1}  U=${random_username}  P=${valid_password}


Verify Operator And User Privilege For Different Channels
    [Documentation]  Set operator and user privilege for different channels and verify.
    [Tags]  Verify_Operator_And_User_Privilege_For_Different_Channels

    # Create IPMI user and set valid password.
    ${random_username}=  Generate Random String  8  [LETTERS]
    ${random_userid}=  Evaluate  random.randint(2, 15)  modules=random
    IPMI Create User  ${random_userid}  ${random_username}
    Run IPMI Standard Command
    ...  user set password ${random_userid} ${valid_password}

    # Set operator privilege for newly created user with channel 1.
    Set Channel Access  ${random_userid}  ipmi=on privilege=${operator_priv}  1

    # Set user privilege for newly created user with channel 2.
    Set Channel Access  ${random_userid}  ipmi=on privilege=${user_priv}  2

    # Enable IPMI user and verify.
    Run IPMI Standard Command  user enable ${random_userid}
    ${user_info}=  Get User Info  ${random_userid}
    Should Be Equal  ${user_info['enable_status']}  enabled

    # Verify that user is able to run operator level IPMI command with channel 1.
    Verify IPMI Command  ${random_username}  ${valid_password}  Operator  1

    # Verify that user is able to run user level IPMI command with channel 2.
    Verify IPMI Command  ${random_username}  ${valid_password}  User  2


*** Keywords ***

Set Default Password For IPMI Root User
    [Documentation]  Set default password for IPMI root user (i.e. 0penBmc).
    # Set default password for root user.
    ${result}=  Run External IPMI Standard Command
    ...  user set password ${root_userid} ${OPENBMC_PASSWORD}
    ...  P=${valid_password}
    Should Contain  ${result}  Set User Password command successful

    # Verify that root user is able to run IPMI command using default password.
    Verify IPMI Username And Password  root  ${OPENBMC_PASSWORD}


Test IPMI User Privilege
    [Documentation]  Test IPMI user privilege by executing IPMI command with different privileges.
    [Arguments]  ${privilege_level}  ${user_cmd_status}  ${operator_cmd_status}  ${admin_cmd_status}

    # Description of argument(s):
    # privilege_level     Privilege level of IPMI user (e.g. 4, 3).
    # user_cmd_status     Expected status of IPMI command run with the "User"
    #                     privilege (i.e. "Passed" or "Failed").
    # operator_cmd_status Expected status of IPMI command run with the "Operator"
    #                     privilege (i.e. "Passed" or "Failed").
    # admin_cmd_status    Expected status of IPMI command run with the "Administrator"
    #                     privilege (i.e. "Passed" or "Failed").

    # Create IPMI user and set valid password.
    ${random_username}=  Generate Random String  8  [LETTERS]
    ${random_userid}=  Evaluate  random.randint(2, 15)  modules=random
    IPMI Create User  ${random_userid}  ${random_username}
    Run IPMI Standard Command
    ...  user set password ${random_userid} ${valid_password}

    # Set privilege and enable IPMI messaging for newly created user.
    Set Channel Access  ${random_userid}  ipmi=on privilege=${privilege_level}

    # Delay added for user privilge to get set.
    Sleep  5s

    # Enable IPMI user and verify.
    Run IPMI Standard Command  user enable ${random_userid}
    ${user_info}=  Get User Info  ${random_userid}
    Should Be Equal  ${user_info['enable_status']}  enabled

    Verify IPMI Command  ${random_username}  ${valid_password}  User
    ...  expected_status=${user_cmd_status}
    Verify IPMI Command  ${random_username}  ${valid_password}  Operator
    ...  expected_status=${operator_cmd_status}
    Verify IPMI Command  ${random_username}  ${valid_password}  Administrator
    ...  expected_status=${admin_cmd_status}


Verify IPMI Command
    [Documentation]  Verify IPMI command execution with given username,
    ...  password, privilege and expected status.
    [Arguments]  ${username}  ${password}  ${privilege}  ${channel}=${1}  ${expected_status}=Passed
    # Description of argument(s):
    # username         The user name (e.g. "root", "robert", etc.).
    # password         The user password (e.g. "0penBmc", "0penBmc1", etc.).
    # privilege        The session privilge for IPMI command (e.g. "User", "Operator", etc.).
    # channel          The user channel number (e.g. "1" or "2").
    # expected_status  Expected status of IPMI command run with the user
    #                  of above password and privilege (i.e. "Passed" or "Failed").

    ${expected_rc}=  Set Variable If  '${expected_status}' == 'Passed'  ${0}  ${1}
    Wait Until Keyword Succeeds  15 sec  5 sec  Run IPMI Standard Command
    ...  sel info ${channel}  expected_rc=${expected_rc}  U=${username}  P=${password}
    ...  L=${privilege}


Test Teardown Execution
    [Documentation]  Do the test teardown execution.

    FFDC On Test Case Fail
