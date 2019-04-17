# Introduction
* Roll numbers: 17305R005, 17305R001

# How to run
* Run `sh start.sh` to start 8 chord nodes. Also you may use the commands below to add nodes independently
* `PYTHONHASHSEED=0 python3 nodeutil.py localhost 8000` for node-0
* `PYTHONHASHSEED=0 python3 nodeutil.py localhost 800[1..] http://localhost:8000` for others
* `PYTHONHASHSEED=0 python3 dictionaryloader.py <chord-node-url> <path-to-dictionary-file>` for loading dictionary file
* `PYTHONHASHSEED=0 python3 client.py <chord-node-url>`


# Known Bugs 

We have not encountered any bugs yet.


# Names of log files 

We will have a separate folder of log files under name 'logs'. It will have common_logs.txt and <node-hostname>_<node-port>_logs.txt files [for each node].