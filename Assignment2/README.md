# How to run
* `PYTHONHASHSEED=0 python3 nodeutil.py localhost 8000` for node-0
* `PYTHONHASHSEED=0 python3 nodeutil.py localhost 800[1..] http://localhost:8000` for others
* `PYTHONHASHSEED=0 python3 dictionaryloader.py <chord-node-url> <path-to-dictionary-file>` for loading dictionary file
* `PYTHONHASHSEED=0 python3 client.py <chord-node-url>`