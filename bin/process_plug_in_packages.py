#!/usr/bin/env python

import sys
import __builtin__
import subprocess
import os
import argparse

# python puts the program's directory path in sys.path[0].  In other words,
# the user ordinarily has no way to override python's choice of a module from
# its own dir.  We want to have that ability in our environment.  However, we
# don't want to break any established python modules that depend on this
# behavior.  So, we'll save the value from sys.path[0], delete it, import our
# modules and then restore sys.path to its original value.

save_path_0 = sys.path[0]
del sys.path[0]

from gen_print import *
from gen_valid import *
from gen_arg import *
from gen_plug_in import *
from gen_cmd import *

# Restore sys.path[0].
sys.path.insert(0, save_path_0)
# I use this variable in calls to print_var.
hex = 1

###############################################################################
# Create parser object to process command line parameters and args.

# Create parser object.
parser = argparse.ArgumentParser(
    usage='%(prog)s [OPTIONS]',
    description="%(prog)s will process the plug-in packages passed to it." +
                "  A plug-in package is essentially a directory containing" +
                " one or more call point programs.  Each of these call point" +
                " programs must have a prefix of \"cp_\".  When calling" +
                " %(prog)s, a user must provide a call_point parameter" +
                " (described below).  For each plug-in package passed," +
                " %(prog)s will check for the presence of the specified call" +
                " point program in the plug-in directory.  If it is found," +
                " %(prog)s will run it.  It is the responsibility of the" +
                " caller to set any environment variables needed by the call" +
                " point programs.\n\nAfter each call point program" +
                " has been run, %(prog)s will print the following values in" +
                " the following formats for use by the calling program:\n" +
                "  failed_plug_in_name:               <failed plug-in value," +
                " if any>\n  shell_rc:                          " +
                "<shell return code value of last call point program - this" +
                " will be printed in hexadecimal format.  Also, be aware" +
                " that if a call point program returns a value it will be" +
                " shifted left 2 bytes (e.g. rc of 2 will be printed as" +
                " 0x00000200).  That is because the rightmost byte is" +
                " reserverd for errors in calling the call point program" +
                " rather than errors generated by the call point program.>",
    formatter_class=argparse.RawTextHelpFormatter,
    prefix_chars='-+')

# Create arguments.
parser.add_argument(
    'plug_in_dir_paths',
    nargs='?',
    default="",
    help=plug_in_dir_paths_help_text + default_string)

parser.add_argument(
    '--call_point',
    default="setup",
    required=True,
    help='The call point program name.  This value must not include the' +
         ' "cp_" prefix.  For each plug-in package passed to this program,' +
         ' the specified call_point program will be called if it exists in' +
         ' the plug-in directory.' + default_string)

parser.add_argument(
    '--shell_rc',
    default="0x00000000",
    help='The user may supply a value other than zero to indicate an' +
         ' acceptable non-zero return code.  For example, if this value' +
         ' equals 0x00000200, it means that for each plug-in call point that' +
         ' runs, a 0x00000200 will not be counted as a failure.  See note' +
         ' above regarding left-shifting of return codes.' + default_string)

parser.add_argument(
    '--stop_on_plug_in_failure',
    default=1,
    type=int,
    choices=[1, 0],
    help='If this parameter is set to 1, this program will stop and return ' +
         'non-zero if the call point program from any plug-in directory ' +
         'fails.  Conversely, if it is set to false, this program will run ' +
         'the call point program from each and every plug-in directory ' +
         'regardless of their return values.  Typical example cases where ' +
         'you\'d want to run all plug-in call points regardless of success ' +
         'or failure would be "cleanup" or "ffdc" call points.')

parser.add_argument(
    '--stop_on_non_zero_rc',
    default=0,
    type=int,
    choices=[1, 0],
    help='If this parm is set to 1 and a plug-in call point program returns ' +
         'a valid non-zero return code (see "shell_rc" parm above), this' +
         ' program will stop processing and return 0 (success).  Since this' +
         ' constitutes a successful exit, this would normally be used where' +
         ' the caller wishes to stop processing if one of the plug-in' +
         ' directory call point programs returns a special value indicating' +
         ' that some special case has been found.  An example might be in' +
         ' calling some kind of "check_errl" call point program.  Such a' +
         ' call point program might return a 2 (i.e. 0x00000200) to indicate' +
         ' that a given error log entry was found in an "ignore" list and is' +
         ' therefore to be ignored.  That being the case, no other' +
         ' "check_errl" call point program would need to be called.' +
         default_string)

parser.add_argument(
    '--mch_class',
    default="obmc",
    help=mch_class_help_text + default_string)

# The stock_list will be passed to gen_get_options.  We populate it with the
# names of stock parm options we want.  These stock parms are pre-defined by
# gen_get_options.
stock_list = [("test_mode", 0), ("quiet", 1), ("debug", 0)]
###############################################################################


###############################################################################
def exit_function(signal_number=0,
                  frame=None):

    r"""
    Execute whenever the program ends normally or with the signals that we
    catch (i.e. TERM, INT).
    """

    dprint_executing()
    dprint_var(signal_number)

    qprint_pgm_footer()

###############################################################################


###############################################################################
def signal_handler(signal_number, frame):

    r"""
    Handle signals.  Without a function to catch a SIGTERM or SIGINT, our
    program would terminate immediately with return code 143 and without
    calling our exit_function.
    """

    # Our convention is to set up exit_function with atexit.registr() so
    # there is no need to explicitly call exit_function from here.

    dprint_executing()

    # Calling exit prevents us from returning to the code that was running
    # when we received the signal.
    exit(0)

###############################################################################


###############################################################################
def validate_parms():

    r"""
    Validate program parameters, etc.  Return True or False accordingly.
    """

    if not valid_value(call_point):
        return False

    global shell_rc
    if not valid_integer(shell_rc):
        return False

    # Convert to hex string for consistency in printout.
    shell_rc = "0x%08x" % int(shell_rc, 0)
    set_pgm_arg(shell_rc)

    gen_post_validation(exit_function, signal_handler)

    return True

###############################################################################


###############################################################################
def run_pgm(plug_in_dir_path,
            call_point,
            caller_shell_rc):

    r"""
    Run the call point program in the given plug_in_dir_path.  Return the
    following:
    rc                              The return code - 0 = PASS, 1 = FAIL.
    shell_rc                        The shell return code returned by
                                    process_plug_in_packages.py.
    failed_plug_in_name             The failed plug in name (if any).

    Description of arguments:
    plug_in_dir_path                The directory path where the call_point
                                    program may be located.
    call_point                      The call point (e.g. "setup").  This
                                    program will look for a program named
                                    "cp_" + call_point in the
                                    plug_in_dir_path.  If no such call point
                                    program is found, this function returns an
                                    rc of 0 (i.e. success).
    caller_shell_rc                 The user may supply a value other than
                                    zero to indicate an acceptable non-zero
                                    return code.  For example, if this value
                                    equals 0x00000200, it means that for each
                                    plug-in call point that runs, a 0x00000200
                                    will not be counted as a failure.  See
                                    note above regarding left-shifting of
                                    return codes.
    """

    global autoscript

    rc = 0
    failed_plug_in_name = ""
    shell_rc = 0x00000000

    plug_in_name = os.path.basename(os.path.normpath(plug_in_dir_path))
    cp_prefix = "cp_"
    plug_in_pgm_path = plug_in_dir_path + cp_prefix + call_point
    if not os.path.exists(plug_in_pgm_path):
        # No such call point in this plug in dir path.  This is legal so we
        # return 0, etc.
        return rc, shell_rc, failed_plug_in_name

    # Get some stats on the file.
    cmd_buf = "stat -c '%n %s %z' " + plug_in_pgm_path
    dpissuing(cmd_buf)
    sub_proc = subprocess.Popen(cmd_buf, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
    out_buf, err_buf = sub_proc.communicate()
    shell_rc = sub_proc.returncode
    if shell_rc != 0:
        rc = 1
        print_var(shell_rc, hex)
        failed_plug_in_name = plug_in_name
        print(out_buf)
        print_var(failed_plug_in_name)
        print_var(shell_rc, hex)
        return rc, shell_rc, failed_plug_in_name

    print("------------------------------------------------- Starting plug-" +
          "in -----------------------------------------------")
    print(out_buf)
    if autoscript:
        stdout = 1 - quiet
        if AUTOBOOT_OPENBMC_NICKNAME != "":
            autoscript_prefix = AUTOBOOT_OPENBMC_NICKNAME + "."
        else:
            autoscript_prefix = ""
        autoscript_prefix += plug_in_name + ".cp_" + call_point
        autoscript_subcmd = "autoscript --quiet=1 --show_url=y --prefix=" +\
            autoscript_prefix + " --stdout=" + str(stdout) + " -- "
    else:
        autoscript_subcmd = ""

    cmd_buf = "PATH=" + plug_in_dir_path + ":${PATH} ; " + autoscript_subcmd +\
              cp_prefix + call_point
    pissuing(cmd_buf)

    sub_proc = subprocess.Popen(cmd_buf, shell=True)
    sub_proc.communicate()
    shell_rc = sub_proc.returncode
    # Shift to left.
    shell_rc *= 0x100
    if shell_rc != 0 and shell_rc != caller_shell_rc:
        rc = 1
        failed_plug_in_name = plug_in_name

    print("------------------------------------------------- Ending plug-in" +
          " -------------------------------------------------")
    if failed_plug_in_name != "":
        print_var(failed_plug_in_name)
    print_var(shell_rc, hex)

    return rc, shell_rc, failed_plug_in_name

###############################################################################


###############################################################################
def main():

    r"""
    This is the "main" function.  The advantage of having this function vs
    just doing this in the true mainline is that you can:
    - Declare local variables
    - Use "return" instead of "exit".
    - Indent 4 chars like you would in any function.
    This makes coding more consistent, i.e. it's easy to move code from here
    into a function and vice versa.
    """

    if not gen_get_options(parser, stock_list):
        return False

    if not validate_parms():
        return False

    qprint_pgm_header()

    # Access program parameter globals.
    global plug_in_dir_paths
    global mch_class
    global shell_rc
    global stop_on_plug_in_failure
    global stop_on_non_zero_rc

    plug_in_packages_list = return_plug_in_packages_list(plug_in_dir_paths,
                                                         mch_class)

    qpvar(plug_in_packages_list)
    qprint("\n")

    caller_shell_rc = int(shell_rc, 0)
    shell_rc = 0
    failed_plug_in_name = ""

    # If the autoscript program is present, we will use it to direct call point
    # program output to a separate status file.  This keeps the output of the
    # main program (i.e. OBMC Boot Test) cleaner and yet preserves call point
    # output if it is needed for debug.
    global autoscript
    global AUTOBOOT_OPENBMC_NICKNAME
    autoscript = 0
    AUTOBOOT_OPENBMC_NICKNAME = ""
    rc, out_buf = cmd_fnc("which autoscript", quiet=1, print_output=0,
                          show_err=0)
    if rc == 0:
        autoscript = 1
        AUTOBOOT_OPENBMC_NICKNAME = os.environ.get("AUTOBOOT_OPENBMC_NICKNAME",
                                                   "")
    ret_code = 0
    for plug_in_dir_path in plug_in_packages_list:
        rc, shell_rc, failed_plug_in_name = \
            run_pgm(plug_in_dir_path, call_point, caller_shell_rc)
        if rc != 0:
            ret_code = 1
            if stop_on_plug_in_failure:
                break
        if shell_rc != 0 and stop_on_non_zero_rc:
            qprint_time("Stopping on non-zero shell return code as requested" +
                        " by caller.\n")
            break

    if ret_code == 0:
        return True
    else:
        if not stop_on_plug_in_failure:
            # We print a summary error message to make the failure more
            # obvious.
            print_error("At least one plug-in failed.\n")
        return False

###############################################################################


###############################################################################
# Main

if not main():
    exit(1)

###############################################################################
