import xmlrpc.client

with xmlrpc.client.ServerProxy("http://localhost:9000/") as proxy:
    # print("3 is odd: %s" % str(proxy.is_odd(3)))
    # print("100 is even: %s" % str(proxy.is_even(100)))
    node_id,successor,predecessor,finger = proxy.stupid_fn()
    # print("stupid_fn: " % str(proxy.is_even(100)))
    # print(str(proxy.find_node()))
    print(node_id, successor)