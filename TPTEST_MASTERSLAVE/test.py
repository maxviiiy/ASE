# ROUTING_TABLE = {
#     'A.txt': ('127.0.0.1', 9000, 900),
#     'B.txt': ('127.0.0.1', 9000, 700),
#     'C.txt': ('127.0.0.1', 9001, 500),
#     'D.txt': ('127.0.0.1', 9001, 300),
#     'E.txt': ('127.0.0.1', 9001, 200),
#     'F.txt': ('127.0.0.1', 9002, 100),
# }

# print(ROUTING_TABLE)

l_index=0
ROUTES = [["A.txt", "127.0.0.1", 9000, 900]]
target = ROUTES[l_index]
server_ip, server_port = target[1], target[2]



print(server_ip, server_port)