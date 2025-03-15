# Code for socket/client

import socket
import threading
import argparse
import re

ipBook = []                                                         # stores ip for future use
key = []                                                            # a flag to indicate if user will switch to UDP
key2 = []                                                           # another flag to be used for a second user so that both priv UDP functions are not run
user = []                                                           # saves usernames for later use
UDP = False                                                         # a flag

#######################################################

# command line input
parser = argparse.ArgumentParser(description='Client for chat application')
parser.add_argument('--server-ip', type=str, help='Server IP address')
parser.add_argument('--server-port', type=int, help='Server port number')

args = parser.parse_args()                                          # parse the command-line arguments
server_ip = args.server_ip                                          # get ip address and port numbe sqr for arguments
server_port = args.server_port

if not (server_ip and server_port):
    parser.error('Missing required argument(s)')                    # checks that arguments match

print("What would you like to do?")
print("[1] Join Chatroom")
print("[2] Private Chat")

option = input("")

# connect to main chatroom
if option == "1":
    clientTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # defines a TCP socket for main chatroom
    clientTCP.connect((server_ip, server_port))                        # connects to a host on port
    name = input("Username: ")                                         # sets a nickname
elif option == "2":                                                    # connects to a host on port
    print("Service not yet available.")
else:
    print("Option not recognised, try again.")
    exit()

# function when client recieves message
def receiveTCP():
    global UDP
    while not UDP:
        try:
            msg = clientTCP.recv(1024).decode('ascii')              # receives from server
            priv = msg.split()[1:]
            username = msg.split()[0]
            if msg == 'NICK':                                       # checks if message was NICK or something else
                clientTCP.send(name.encode('ascii'))                # sends name to server
            elif msg == "Would you like to be visible to other users? 'Yes' or 'No'":
                clientTCP.send(input(""))
            elif priv == "wishes to connect to you, do you accept? 'Yes' or 'No'":
                server_ip.send(input(""))
            elif msg == "Starting private connection process. . .": # connects sender of request to UDP
                print(msg)
                ip = socket.gethostbyname(socket.gethostname())     # gets IP address of this client
                ipBook.append(ip)                                   # save the IP to use in UDP connection establishment
                key.append("t")                                     # triggers the flag
                user.append(username)                               # add username for later
                clientTCP.close()                                   # closes TCP connection to chatroom
                break
            elif msg.startswith("You are being connected to "):
                    print(msg)                                      # prints who user is being connected to
                    print('Starting private connection. . .')       # informs user connection is starting
                    ipBook.append(last(msg))                        # takes IP address
                    user.append(username)                           # add username for later
                    key2.append("t")                                # trigger flag
                    clientTCP.close()                               # close TCP connection to chatroom
                    break
            else:
                print(msg)                                          # prints if not a nickname
        except (ConnectionResetError, ConnectionAbortedError):      # closes connection
            print("Connection Closed!")
            clientTCP.close()
            break
    if len(key2) > 0:                                               # if flag triggered, then UDP connection starts for one user
        privUDP2()
    if len(key) > 0:                                                # if flag triggered, then UDP connection starts for other user
        privUDP()
    
# function when client sends message for chatrooms
def messagingTCP():
    global UDP
    while not UDP:
        message = input("")
        if message == "!q":                                         # exit key for the client
            clientTCP.close()
            exit()
        elif UDP == False:
            clientTCP.send(f"{name}: {message}".encode())           # if TCP activated and message not !q then send message to chatroom
        else:
            pass

# function to find IP
def last(str):
    pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    addresses = re.findall(pattern, str)
    if addresses:
        ip = addresses[0]
    return ip

# establish UDP of one User
def privUDP():                                                  #used to create UDP connection to client
    global UDP
    UDP = True
    ip = socket.gethostbyname(socket.gethostname())                 # gets IP address of this client
    ipBook.append(ip)                                               # save IP for later
    clientUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # creates a UPD socket
    clientUDP.bind((ip, 56565))
    print("Private Connection Established!\nYou may now chat!\n(Press 'Enter' before sending a new message)")
    
    # receive function for UDP
    def receive():
        while UDP:
            try:
                msg, addr = clientUDP.recvfrom(1024)
                print(msg.decode())
            except:
                print("Connection Closed!")
                clientUDP.close()
                break

    # messaging function for UDP
    def broadcast():
        while UDP:
            msg = input("")
            if msg == "!q":
                clientUDP.sendto(f"{name} Left!".encode(), (ipBook[0], 60000))  # notifies other user that chat was closed
                clientUDP.close()
                exit()
            else:
                clientUDP.sendto(f"{name}: {msg}".encode(), (ipBook[0], 60000)) # sends message with username to other user

    ta1 = threading.Thread(target=receive)
    ta2 = threading.Thread(target=broadcast)
    ta1.start()
    ta2.start()
    
# UDP function for second user
def privUDP2():
    global UDP
    UDP =True
    clientUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientUDP.bind((ipBook[0], 60000))       
    print("Private Connection Established!\nYou may now chat!\n(Press 'Enter' before sending a new message)")

    # receive function same as other
    def receive():
        while UDP:
            try:
                msg, _ = clientUDP.recvfrom(1024)
                print(msg.decode())
            except:
                print("Connection Closed!")
                clientUDP.close()
                break
    tb = threading.Thread(target=receive)
    tb.start()

    # while loop opposed to function
    while UDP:
        msg = input("")
        if msg == "!q":
            clientUDP.sendto(f"{name} Left!".encode(), (ipBook[0], 56565))
            clientUDP.close()
            exit()
        else:
            clientUDP.sendto(f"{name}: {msg}".encode(), (ipBook[0], 56565))

receiveThread = threading.Thread(target=receiveTCP)
receiveThread.start()

sendThread = threading.Thread(target=messagingTCP)
sendThread.start()

receiveThread.join()
sendThread.join()