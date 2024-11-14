# bwanCapp

bwanEdges.py is a tool that help list and delete Netskope Borderless SDWAN Clients.


## Prerequisites

1. Python3
2. The following python modules (see requirements.txt)
	- requests
  - tabulate



## Installation

```
$ git clone https://github.com/virtualmo/bwanEdges.git
$ cd bwanEdges
$ pip3 install -r requirements.txt
```


## Running

### Script help
```
$ python3 bwanEdges.py -h
usage: bwanEdges.py [-h] [-u TENANT_URL] [-t API_TOKEN] [-l] [-r CLIENT_ID] [-d FILENAME]

options:
  -h, --help            show this help message and exit
  -u TENANT_URL, --tenant_url TENANT_URL
                        BWAN Tenant URL
  -t API_TOKEN, --api_token API_TOKEN
                        BWAN Tenant API Token
  -l, --list_clients    List BWAN Clients
  -r CLIENT_ID, --remove_client CLIENT_ID
                        Remove a Client by ID, 0 for All
```

### BWAN API Token 
1. Log in to the SASE Orchestrator as a System Admin and navigate to Administration > Tokens.
2. Click the + icon to create a new token.
3. Provide a Name and Permissions details. The Permissions must be supplied in JSON format. use the following permissions
```
[
  {
    "rap_resource": "",
    "rap_privs": [
      "privSiteCreate",
      "privSiteRead",
      "privSiteWrite",
      "privSiteDelete"
    ]
  }
]
```
4. Modify the expiration date as required.

### List Clients
```
$ python3 bwanEdges.py -u https://tenant_url -t TOKENTOKEN -l
2024-11-14 15:29:15,472 WARNING: Config file doesn't exit, will look into CLI arguments
2024-11-14 15:29:15,472 INFO: Working with tenant: https://tenant_url
2024-11-14 15:29:15,472 INFO: Getting bwan egdes with model: Client
+--------------------------+-----------------+----------------------+----------------+
| ID                       | Name            | User                 | Assigned VIP   |
+==========================+=================+======================+================+
| 669bb43082xx82ed5a97e2e3 | DESKTOP-M3MUBT6 | email1@domain.com    | 10.44.44.177   |
+--------------------------+-----------------+----------------------+----------------+
| 66a16e485fxx08347bc70a0a | LTP-W8nXrR7yYCu | email2@domain.com    | 10.44.44.114   |
+--------------------------+-----------------+----------------------+----------------+
| 6735dae90fxx89fef377a7b7 | DESKTOP-3EAJN0P | email3@domain.com    | 10.44.44.188   |
+--------------------------+-----------------+----------------------+----------------+
```

## Disclaimer

This software is supplied "AS IS" without any warranties and support.