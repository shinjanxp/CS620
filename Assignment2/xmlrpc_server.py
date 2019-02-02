from xmlrpc.server import SimpleXMLRPCServer
import time

def is_even(n):
    time.sleep(50)
    return n % 2 == 0

def is_odd(n):
    return n % 2 != 0

server = SimpleXMLRPCServer(("localhost", 8000))
print("Listening on port 8000...")
server.register_function(is_even, "is_even")
server.register_function(is_odd, "is_odd")
server.serve_forever()