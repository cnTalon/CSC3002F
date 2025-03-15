# Code for server

import socket
import threading

clients = []                                                # stores all clients connecting to server
names = []                                                  # stores names of clients connected
onlineUsers = []                                            # stores name of people online
clientDict = {}                                             # stores name and ip & port of clients
private = {}                                                # stores the name of the sender of the UDP request
private1 = []

server =socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # IPV4 with TCP connection
ip_add = "0.0.0.0"
port_num = 28000
server.bind((ip_add, port_num))                             # bind to given address and portnumber

print("Server bound")
server.listen(4)                                            # can listen to clients
print("Server listening")
print("Server awaiting new connection(s). . .")

#send messages to all clients
def broadcast(msg):
    #send message to all clients on connection
    for client in clients:
        client.send(msg)

def handle(client):
    #send message to all clients
    while True:
        try:
            msg = client.recv(1024)
            message = msg.decode('ascii')
            message = message.split()[1]
            print(message)
            if message == "!menu":
                menulist(client)
            elif message.lower() == 'yes':                          # connection accepted, requester starts connection
                con = "Starting private connection process. . ."
                whisper(private1[0], con)                           # tell sender that connection process is starting (works)
                notif = f"You are being connected to {private1[0]}! {clientDict.get(private1[0])}"
                whisper(private1[1], notif)                         # tell receiver that they are being connected
                print("Relevant Socket(s) Obtained")
            elif message.lower() == 'no':
                client.send("Invitation declined.".encode('ascii'))
                dec = "Your invite was declined."
                whisper(private1[0], dec)
            else: 
                broadcast(msg)
        except:                                                     # terminate client if doesnt work
            index = clients.index(client)                           # find where client is in client list
            clients.remove(client)                                  # remove client from list
            client.close()
            name = names[index]                                     # remove name from list
            broadcast(f'{name} HAS DISCONNECTED'.encode('ascii'))
            print(f'{name} DISCONNECTED.')                          # note in server that user disconnected
            names.remove(name)
            del clientDict[name]
            break

#used by server to message particular client
def whisper(receiver, message):
    if receiver in clientDict:                                   # looks for the receipent in the dictionary
        receiverSocket = clients[names.index(receiver)]          # gets the receipents ip
        private.update({receiver: receiverSocket})               # adds user to private dictionary
        private1.append(receiver)                                # adds name of user for future use
        receiverSocket.send(message.encode('ascii'))             # uses ip to send the message
    else:
        print("Invalid Client.")

# work with messages received by server
def receive():
    while True:
        confirm =""
        client, addr = server.accept()                           # accepts client and their address
        print ("Got connection from ", addr)
        client.send('NICK'.encode('ascii'))                      # send keyword to client so they know they must enter nickname
        name = client.recv(1024).decode('ascii')
        names.append(name) 
        clientDict.update({name: addr})                          # adds name to the list
        clients.append(client)                                   # adds client to the list
        private1.clear()
        private.clear()
        print(f'SIGNUP_TAB: {name}')
        client.send("Connected to server!\nWould you like to be visible to other users? 'Yes' or 'No'".encode('ascii'))      # let client know they have successfully connected
        msg = client.recv(1024)
        message = msg.decode('ascii')
        confirm = message.split()[1]
        if confirm.lower() == 'yes':
            onlineUsers.append(name)
            broadcast(f'{name} JOINED!'.encode('ascii'))
            client.send("You are now VISIBLE to other users!\nUse '!menu' for list of options and '!q' to exit chatroom.".encode('ascii'))
        else:
            client.send("You are now INVISIBLE to other users!\nUse '!menu' for list of options and '!q' to exit chatroom.".encode('ascii'))

        thread = threading.Thread(target=handle,args=(client,))  # start thread handling connection to particular client
        thread.start()
        print("Server awaiting new connection(s). . .")

# menu of all options available to client
def menulist(client):
    option = ''
    while option != 'esc':
        client.send("********************\nAvailable options:\n~ !userlist - view current users on system\n~ !connect - connect with another user\n~ !sendfile - send a file to users\n~ !exit - to exit the menu\n********************".encode('ascii'))
        msg = client.recv(1024)
        message = msg.decode('ascii')
        option = message.split()[1]
        if option == '!userlist':
            client.send("Users currently online:".encode('ascii'))
            for name in onlineUsers:
                name = name + "\n"
                client.send(name.encode('ascii'))
        elif option == "!sendfile":
            client.send("Service not available.".encode('ascii'))
            break
        elif option == '!connect':
            senderUDP = message.split()[0].rstrip(":")                                             # get sender of request
            personUDP = message.split()[2]                                                         # get receiver of request
            if personUDP in onlineUsers:                                                           # checks if user is online
                private1.append(senderUDP)                                                         # save sender for later use
                print(senderUDP + " wants to go private")                                          # notify server that someone wants to go private
                print(senderUDP + " is connecting to: " + personUDP)                               # note who user wants to connect with
                confirm = f"{senderUDP} wishes to connect to you, do you accept? 'Yes' or 'No'"
                whisper(personUDP, confirm)                                                        # private message the recipient
                notif = f"Sent {personUDP} a connection invite!"
                whisper(senderUDP, notif)                                                          # notify sender that request was sent
            else:
                client.send("User not online.".encode('ascii'))
            break
        elif str(option) == '!exit':
            client.send("Exited menu!".encode('ascii'))
            break
        else:
            client.send("Invalid argument!".encode('ascii'))

receive()