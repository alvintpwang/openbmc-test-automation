#!/usr/bin/python

r"""
Contains xpaths and related string constants applicable to all openBMC GUI
menus.
"""


class resource_variables():

    xpath_textbox_hostname = "//input[@id='host']"
    xpath_textbox_username = "//input[@id='username']"
    xpath_textbox_password = "//input[@id='password']"
    xpath_button_login = "//*[@id='login__submit']"
    xpath_button_logout = '//a[contains(text(), "Log out")]'
    xpath_yes_button = "//button[text()='Yes']"
    xpath_openbmc_url = "http://localhost:8080/#/login"
    xpath_openbmc_ip = "//*[@id='login__form']/input[1]"
    xpath_power_indicator = "//*[@id='power-indicator-bar']"
    xpath_select_button_power_on = "//*[@id='power__power-on']"

    xpath_select_button_warm_reboot = \
        "//*[@id='power__warm-boot']"
    xpath_operation_warning_message = \
        "//*[@class='inline__confirm active']"
    xpath_select_button_warm_reboot_no = \
        "//*[@id='power-operations']/div[3]" \
        "/div[3]/confirm/div/div[2]/button[2]"
    text_warm_reboot_warning_message = "warm reboot?"
    xpath_select_button_warm_reboot_yes = \
        "//*[@id='power-operations']" \
        "/div[3]/div[3]/confirm/div/div[2]/button[1]"

    xpath_select_button_cold_reboot = \
        "//*[@id='power__cold-boot']"
    xpath_select_button_cold_reboot_no = \
        "//*[@id='power-operations']/div[3]/div[4]" \
        "/confirm/div/div[2]/button[2]"
    text_cold_reboot_warning_message = "cold reboot?"
    xpath_select_button_cold_reboot_yes = \
        "//*[@id='power-operations']" \
        "/div[3]/div[4]/confirm/div/div[2]/button[2]"

    xpath_select_button_orderly_shutdown = \
        "//*[@id='power__soft-shutdown']"
    xpath_select_button_orderly_shutdown_button_no = \
        "//*[@id='power-operations']/div[3]/div[5]"\
        "/confirm/div/div[2]/button[2]"
    text_orderly_shutdown_warning_message = "orderly shutdown?"
    xpath_select_button_orderly_shutdown_yes = \
        "//*[@id='power-operations']/div[3]/div[5]" \
        "/confirm/div/div[2]/button[1]"

    xpath_select_button_immediate_shutdown = \
        "//*[@id='power__hard-shutdown']"
    xpath_select_button_immediate_shutdown_no = \
        "//*[@id='power-operations']/div[3]/div[6]" \
        "/confirm/div/div[2]/button[2]"
    text_immediate_shutdown_warning_message = "immediate shutdown?"
    xpath_select_button_immediate_shutdown_yes = \
        "//*[@id='power-operations']/div[3]/div[6]" \
        "/confirm/div/div[2]/button[1]"

    obmc_off_state = "Off"
    obmc_standby_state = "Standby"
    obmc_running_state = "Running"

    # Power operation elements needed for power on.
    header_wrapper = "3"
    header_wrapper_elt = "3"

    # Power operation elements needed for power operations confirmation.
    power_operations = "3"
    warm_boot = "3"
    cold_boot = "4"
    shut_down = "5"
    power_off = "6"
    confirm_msg = "2"
    yes = "1"
    No = "2"

    # GUI header elements locators.
    xpath_select_server_power = "//a[@href='#/server-control/power-operations']"

    # Server health elements locators.
    xpath_select_server_health = "//a[@href='#/server-health/event-log']"
    xpath_server_health_text =  \
        "//*[@id='header__wrapper']/div/div[3]/a[2]/span"
    xpath_select_refresh_button = \
        "//*[contains(text(),'Refresh')]"
    xpath_event_severity_all = "//*[text()='Filter by severity']/following-sibling::button[1]"
    xpath_event_severity_high = "//*[text()='Filter by severity']/following-sibling::button[2]"
    xpath_event_severity_medium = "//*[text()='Filter by severity']/following-sibling::button[3]"
    xpath_event_severity_low = "//*[text()='Filter by severity']/following-sibling::button[4]"
    xpath_drop_down_timezone_edt = \
        "//*[@id='event-log']/section[1]/div/div/button"
    xpath_refresh_circle = "/html/body/main/loader/div[1]/svg/circle"
    xpath_drop_down_timezone_utc =  \
        "//*[@id='event-log']/section[1]/div/div/ul/li[2]/button"
    xpath_event_filter_all = "//*[@id='event-filter']/div[3]/div/button"
    xpath_event_filter_resolved =  \
        "//*[@id='event-filter']/div[3]/div/ul/li[2]/button"
    xpath_event_filter_unresolved = \
        "//*[@id='event-filter']/div[3]/div/ul/li[3]/button"
    xpath_event_action_bars = \
        "//*[@id='event__actions-bar']/div[1]/label/span"
    xpath_event_action_delete = \
        "//*[@id='event__actions-bar']/div[2]/div[2]/button[1]"
    xpath_event_action_export = \
        "//*[@id='event__actions-bar']/div[2]/div[2]/a"
    xpath_number_of_events = \
        "//*[@id='event__actions-bar']/div[2]/p[2]/span"
    xpath_mark_as_resolved = \
        "//*[@id='event__actions-bar']/div[2]/div[2]/button[2]"
    xpath_events_export = "//*[@id='event__actions-bar']/div[2]/div[2]/a"
    xpath_event_delete_no = \
        "//*[@id='event__actions-bar']/div[2]/div[1]/div[2]/button[2]"
    xpath_event_delete_yes = \
        "//*[@id='event__actions-bar']/div[2]/div[1]/div[2]/button[1]"
    xpath_individual_event_select = \
        "//*[@id='event-log__events']/log-event[1]/div/div[1]/div[2]/label/" +\
        "span"
    xpath_individual_event_delete = \
        "//*[@id='event__actions-bar']/div[2]/div[2]/button[1]"
    xpath_second_event_select = \
        "//*[@id='event-log__events']/log-event[2]/div/div[1]/div[2]/label/" +\
        "span"
    xpath_individual_event_resolved = \
        "//*[@id='event__actions-bar']/div[2]/div[2]/button[2]"
    xpath_individual_event_export = \
        "//*[@id='event__actions-bar']/div[2]/div[2]/a"
