import xmlrpc.client

with xmlrpc.client.ServerProxy("http://localhost:8000/") as proxy:
    # print("3 is odd: %s" % str(proxy.is_odd(3)))
    # print("100 is even: %s" % str(proxy.is_even(100)))
    print(str(proxy.find_node()))