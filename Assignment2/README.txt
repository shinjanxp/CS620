a) Instructions :

1) First run  - PYTHONHASHSEED=0 python3 nodeutil.py <hostname-or-ip> <host-port-number>  [for node-0]
PYTHONHASHSEED is for maintaining same hash values across all programs.

2) Then run - PYTHONHASHSEED=0 python3 nodeutil.py <hostname-or-ip> <host-port-number> <url-of-node-0> [for other nodes]

3) Next run - PYTHONHASHSEED=0 python3 dictionaryloader.py <chord-node-url> <path-to-dictionary-file> [to load dictionary across the ring]

4) Run - PYTHONHASHSEED=0 python3 client.py <chord-node-url> [to lookup for meaning of a word]


b) Known Bugs :

We have not encountered any bugs yet.


c) Names of log files :

We will have a separate folder of log files under name 'logs'. It will have common_logs.txt and <node-hostname>_<node-port>_logs.txt files [for each node].