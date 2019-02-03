from xmlrpc.server import SimpleXMLRPCServer
import time

def is_even(n):
    time.sleep(50)
    return n % 2 == 0

def is_odd(n):
    return n % 2 != 0

def stupid_fn():
    return (2, "http://localhost:9001", False, [2]*32)


server = SimpleXMLRPCServer(("localhost", 9000))
print("Listening on port 9000...")
server.register_function(is_even, "is_even")
server.register_function(is_odd, "is_odd")
server.register_function(stupid_fn, "stupid_fn")
server.serve_forever()