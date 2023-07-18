import socket
import random
import time

client_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)



while True:
    hr_test = random.randint(40,200)
    msg = "2,{:d},C,,\"75\",".format(hr_test)
    server_address = ("::", 8909) 
    #server_address = ("[2a02:3033:602:b48f:b60c:8311:8b30:43fd]", 8909) 
    client_socket.sendto(msg.encode(), server_address)
    time.sleep(0.8)
