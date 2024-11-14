#!/usr/bin/python3

BWANCAPP_DESCRIPTION = """
    BWANCAPP is a script by Mohanad Elamin

    BWANCAPP Help configure, query Netskope Borderless SDWAN tenant custom apps in bulk via GraphQL API calls
    Requirements:
        python >= 3.11 (it should work with any version > 3 but I've only tested
                        it with 3.11)

        third-party libraries:
            requests >= 2.31.0   (http://docs.python-requests.org/en/latest/)
            tabulate
        You should be able to install the third-party libraries via pip (or pip3
        depending on the setup):

            pip3 install requests
            pip3 install tabulate
"""

BWANCAPP_VERSION = "2024-01-30_00"
CONFIG_FILENAME = "~/.bwanCapp.conf"
#
# Any of these can be customized in the configuration file, for example:
#
#    $ cat ~/.bwanCapp.conf
#    [bwan_config]
#    # auth details
#    tenant_url=
#    api_token=


import os
import os.path
import sys
import json
import tabulate
import argparse
import csv

from configparser import ConfigParser
from logging import basicConfig as logging_basicConfig, \
    addLevelName as logging_addLevelName, \
    getLogger as logging_getLogger, \
    log as logging_log, \
    DEBUG   as logging_level_DEBUG, \
    INFO    as logging_level_INFO,  \
    WARN    as logging_level_WARN,  \
    ERROR   as logging_level_ERROR, \
    debug   as debug,   \
    info    as info,    \
    warning    as warn,    \
    error   as error

from re import search as re_search, sub as re_sub
from signal import signal as signal_set_handler, SIGINT as signal_SIGINT

from requests import Session as RQ_Session, \
    ConnectionError as RQ_ConnectionError, \
    Timeout as RQ_Timeout, \
    RequestException as RQ_Exception

#
# 256 color terminal color test:
#
# print("FG | BG")
# for i in range(256):
#    # foreground color | background color
#    print("\033[48;5;0m\033[38;5;{0}m #{0} \033[0m | "
#            "\033[48;5;{0}m\033[38;5;15m #{0} \033[0m".format(i))
#
LOGGING_LEVELS = {
    'ERROR' : {
        'level' : logging_level_ERROR,
        'name'  : 'ERROR',
        'xterm' : '31m',
        '256color': '38;5;196m',
    },
    'NORMAL' : {
        'level' : 35,
        'name'  : 'CAD',
        'xterm' : '37m',
        '256color': '38;5;255m',
    },
    'WARNING' : {
        'level' : logging_level_WARN,
        'name'  : 'WARNING',
        'xterm' : '33m',
        '256color': '38;5;227m',
    },
    'INFO' : {
        'level' : logging_level_INFO,
        'name'  : 'INFO',
        'xterm' : '36m',
        '256color': '38;5;45m',
    },
    'DEBUG' : {
        'level' : logging_level_DEBUG,
        'name'  : 'DEBUG',
        'xterm' : '35m',
        '256color': '38;5;135m',
    },
}

#
# We allow the log level to be specified on the command-line or in the
# config by name (string/keyword), but we need to convert these to the
# numeric value:
#
LOGGING_LEVELS_MAP = {
    'NORMAL'    : LOGGING_LEVELS['NORMAL']['level'],
    'ERROR'     : logging_level_ERROR,
    'WARN'      : logging_level_WARN,
    'INFO'      : logging_level_INFO,
    'DEBUG'     : logging_level_DEBUG,
    'normal'    : LOGGING_LEVELS['NORMAL']['level'],
    'error'     : logging_level_ERROR,
    'warn'      : logging_level_WARN,
    'info'      : logging_level_INFO,
    'debug'     : logging_level_DEBUG
}

def custom_signal_handler(signal, frame):
    """Very terse custom signal handler

    This is used to avoid generating a long traceback/backtrace
    """

    warn("Signal {} received, exiting".format(str(signal)))
    sys.exit(1)

def api_get_request(session, url, headers, endpoint):
   return session.get(url=url + "/" + endpoint , headers=headers)
 
def api_delete_request(session, url, headers, endpoint):
   return session.delete(url=url + "/" + endpoint , headers=headers) 


def list_bwan_edge(session, headers, tenant_url, model):
  try:
   info("Getting bwan egdes with model: {}".format(model))
   response = api_get_request(session, tenant_url, headers, "edges")
   response_data = response.json()
   response_list = response_data["data"]
   edge_dict = [d for d in response_list if d.get("model") == model]
  #  print(edge_dict)
  #  print(edge_dict[0].keys())
   table_data = []
   if model == "Client":
    for entry in edge_dict:
        row = [
            entry["id"],
            entry["name"],
            entry["createdBy"]["name"],
            # entry["swversion"],
            entry["clientConfiguration"]["assignedVirtualIPAddress"]
        ]
        table_data.append(row)
      
    # table_header = ["ID","Name","User", "SW Version","Assigned VIP"]
    table_header = ["ID","Name","User","Assigned VIP"]
    #  table_data = [[row[col] for col in table_header] for row in edge_dict]
    print(tabulate.tabulate(table_data, headers=table_header, tablefmt="grid"))
    print("\nTotal edges ({}) is {}\n".format(model,len(edge_dict)))
    id_list = [ id['id'] for id in edge_dict ]
    return(id_list)
  except:
    print(response_data)
  
def remove_bwan_edge(session, headers, tenant_url, edge_id):
   response = api_delete_request(session, tenant_url, headers, "/edges/" + edge_id)
   response_data = response.json()
   if response.status_code == 200:
     info("Client ID {} delete successfully!".format(edge_id))


def main():
    session = RQ_Session()

    #
    # Set logging to INFO by default (log everything except DEBUG).
    #
    # Also try to add colors to the logging output if the logging output goes
    # to a capable device (not a file and a terminal supporting colors).
    #
    # Actually adding the ANSI escape codes in the logging level name is pretty
    # much an ugly hack but it is the easiest way (less changes).
    #
    # An elegant way of doing this is described here:
    #  http://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
    #
    fmt_str = '%(asctime)s %(levelname)s: %(message)s'

    logging_basicConfig(format=fmt_str, level=logging_level_INFO,
                        stream=sys.stdout)
    logger = logging_getLogger()

    argparser = argparse.ArgumentParser()

    argparser.add_argument('-u','--tenant_url', help='BWAN Tenant URL')
    argparser.add_argument('-t','--api_token', help='BWAN Tenant API Token')
    argparser.add_argument('-l','--list_clients', help='List BWAN Clients', action='store_true')
    argparser.add_argument('-r','--remove_client', help='Remove a Client by ID, 0 for All', metavar='CLIENT_ID')
    argparser.add_argument('-d','--dump_clients', help='Dump Clients to CSV file', metavar='FILENAME')
  

    args = argparser.parse_args(args=None if sys.argv[1:] else ['--help'])


    cfgparser = ConfigParser()
    
    try:
        if not cfgparser.read(os.path.expanduser(CONFIG_FILENAME)):
          warn("Config file doesn't exit, will look into CLI arguments")
          if (args.tenant_url is not None):
            if "api" not in args.tenant_url:
              tenant_url = re_sub(r"(://[^.]+)", rf"\1.{"api"}", args.tenant_url, count=1)
            else:
              tenant_url = args.tenant_url
          else:
              error("add the tenant_url to arguments or to the config file.")
              sys.exit(1)
              
          if (args.api_token is not None):
              bwan_api_token = args.api_token
          else:
              error("add the api_token to arguments or to the config file.")
              sys.exit(1)      
        else:
          config = cfgparser['bwan_config']
          if ('bwan_config' not in cfgparser):
              error("Configuration file {} doesn't contain 'bwan_config' section"
                    "".format(os.path.expanduser(CONFIG_FILENAME)))
              sys.exit(1)
          elif (('tenant_url' not in cfgparser['bwan_config']) or
                  ('api_token' not in cfgparser['bwan_config'])):
              error("Config file doesn't contain (all) required authentication info")
              sys.exit(1)
    except:
        error("Can't parse configuration file {}"
              "".format(os.path.expanduser(CONFIG_FILENAME)))
        sys.exit(1)

    info("Working with tenant: {}".format(tenant_url))
    headers = {
      "Authorization": f"Bearer {bwan_api_token}",
      "Content-Type": "application/json"
    }

    if args.list_clients:
      model = "Client"
      list_bwan_edge(session, headers, tenant_url, model)

    # if args.add_custom_app:
    #     add_custom_app(session, headers, tenant_url, ip_list_file=args.add_custom_app)
    
    if args.remove_client:
       if args.remove_client == "0":
          id_list = list_bwan_edge(session, headers, tenant_url, "Client")
          if len(id_list) == 0:
            info("No client found. Nothing to delete.")
            exit(0)
          info("The script will delete {} Client(s)".format(len(id_list)))
          while True:
            answer = input("Do you want to Continue? (Yes/Y or No/N) ")
            if answer.lower() in ["y","yes"]:
              for client_id in id_list:
                remove_bwan_edge(session, headers, tenant_url, client_id)
              break
            elif answer.lower() in ["n","no"]:
              info("No Client deleted. Exiting...")
              exit(0)
            else:
              error("Please select Yes/y or No/n")
          
       else:
          remove_bwan_edge(session, headers, tenant_url, args.remove_client)


if (__name__ == '__main__'):
    main()