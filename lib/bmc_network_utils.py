#!/usr/bin/env python

r"""
Network generic functions.

"""

import gen_print as gp
import gen_cmd as gc
import gen_misc as gm
import var_funcs as vf
import collections
import re
import ipaddress
from robot.libraries.BuiltIn import BuiltIn


def netmask_prefix_length(netmask):
    r"""
    Return the netmask prefix length.

    Description of argument(s):
    netmask     Netmask value (e.g. "255.255.0.0", "255.255.255.0",
                                    "255.252.0.0", etc.).
    """

    # IP address netmask format: '0.0.0.0/255.255.252.0'
    return ipaddress.ip_network('0.0.0.0/' + netmask).prefixlen


def parse_nping_output(output):
    r"""
    Parse the output from the nping command and return as a dictionary.

    Example of output value:

    Starting Nping 0.6.47 ( http://nmap.org/nping ) at 2019-08-07 22:05 IST
    SENT (0.0181s) TCP Source IP:37577 >
      Destination IP:80 S ttl=64 id=39113 iplen=40  seq=629782493 win=1480
    SENT (0.2189s) TCP Source IP:37577 >
      Destination IP:80 S ttl=64 id=39113 iplen=40  seq=629782493 win=1480
    RCVD (0.4120s) TCP Destination IP:80 >
      Source IP:37577 SA ttl=49 id=0 iplen=44  seq=1078301364 win=5840 <mss 1380>
    Max rtt: 193.010ms | Min rtt: 193.010ms | Avg rtt: 193.010ms
    Raw packets sent: 2 (80B) | Rcvd: 1 (46B) | Lost: 1 (50.00%)
    Nping done: 1 IP address pinged in 0.43 seconds

    Example of data returned by this function:

    nping_result:
      [max_rtt]:                 193.010ms
      [min_rtt]:                 193.010ms
      [avg_rtt]:                 193.010ms
      [raw_packets_sent]:        2 (80B)
      [rcvd]:                    1 (46B)
      [lost]:                    1 (50.00%)
      [percent_lost]:            50.00

    Description of argument(s):
    output                          The output obtained by running an nping
                                    command.
    """

    lines = output.split("\n")
    # Obtain only the lines of interest.
    lines = list(filter(lambda x: re.match(r"(Max rtt|Raw packets)", x),
                        lines))

    key_value_list = []
    for line in lines:
        key_value_list += line.split("|")
    nping_result = vf.key_value_list_to_dict(key_value_list)
    # Extract percent_lost value from lost field.
    nping_result['percent_lost'] = \
        float(nping_result['lost'].split(" ")[-1].strip("()%"))
    return nping_result


openbmc_host = BuiltIn().get_variable_value("${OPENBMC_HOST}")


def nping(host=openbmc_host, parse_results=1, **options):
    r"""
    Run the nping command and return the results either as a string or as a dictionary.

    Do a 'man nping' for a complete description of the nping utility.

    Note that any valid nping argument may be specified as a function argument.

    Example robot code:

    ${nping_result}=  Nping  delay=${delay}  count=${count}  icmp=${None}  icmp-type=echo
    Rprint Vars  nping_result

    Resulting output:

    nping_result:
      [max_rtt]:                                      0.534ms
      [min_rtt]:                                      0.441ms
      [avg_rtt]:                                      0.487ms
      [raw_packets_sent]:                             4 (112B)
      [rcvd]:                                         2 (92B)
      [lost]:                                         2 (50.00%)
      [percent_lost]:                                 50.0

    Description of argument(s):
    host                            The host name or IP of the target of the
                                    nping command.
    parse_results                   1 or True indicates that this function
                                    should parse the nping results and return
                                    a dictionary rather than the raw nping
                                    output.  See the parse_nping_output()
                                    function for details on the dictionary
                                    structure.
    options                         Zero or more options accepted by the nping
                                    command.  Do a 'man nping' for details.
    """

    command_string = gc.create_command_string('nping', host, options)
    rc, output = gc.shell_cmd(command_string, print_output=0, ignore_err=0)
    if parse_results:
        return parse_nping_output(output)

    return output
