PYTHONHASHSEED=0 python3 nodeutil.py localhost 8000 &
sleep 2
PYTHONHASHSEED=0 python3 nodeutil.py localhost 8001 http://localhost:8000 &
sleep 2
PYTHONHASHSEED=0 python3 nodeutil.py localhost 8002 http://localhost:8000 &
sleep 2
PYTHONHASHSEED=0 python3 nodeutil.py localhost 8003 http://localhost:8000 &
sleep 2
PYTHONHASHSEED=0 python3 nodeutil.py localhost 8004 http://localhost:8000 &
sleep 2
PYTHONHASHSEED=0 python3 nodeutil.py localhost 8005 http://localhost:8000 &
sleep 2
PYTHONHASHSEED=0 python3 nodeutil.py localhost 8006 http://localhost:8000 &
sleep 2
PYTHONHASHSEED=0 python3 nodeutil.py localhost 8007 http://localhost:8000 &

