import socket
import os
import sys
from subprocess import PIPE
import subprocess

def send_data(sock, data):

    if type(data) == str:
        data = data.encode('utf-8')
    else:
        data = data

    # Get size of the data to be sent
    dataSizeStr = str(len(data))

    # Generate 10 byte long string with data size
    while len(dataSizeStr) < 10:
        dataSizeStr = "0" + dataSizeStr

    # Add data size string before data
    data = dataSizeStr.encode('utf-8') + data
    numSent = 0
    
    # Send all data making sure not to miss any
    while numSent != len(data):
	    numSent += sock.send(data[numSent:])

def recvAll(sock, numBytes):

    if type(numBytes) == int:
        pass
    else:
        numBytes = numBytes.decode('utf-8').strip()

    # The buffer
    recvBuff = b""

    # The temporary buffer
    tmpBuff = b""

    # Keep receiving till all is received
    while len(recvBuff) < int(numBytes):
        
        # Attempt to receive bytes
        tmpBuff = sock.recv(int(numBytes) - len(recvBuff))
        
        # The other side has closed the socket
        if not tmpBuff:
            break
        
        # Add the received bytes to the buffer
        recvBuff += tmpBuff

    return recvBuff

def getEphemeralSocket(clientSock):
    # This function creates an ephemeralsocket and 
    # sends to client, and waits for connection.

    eph_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    eph_socket.bind(('', 0))
    # Get Ephemeral socket number
    eph_socket_num = str(eph_socket.getsockname()[1])
    # Send Eph socket to client
    send_data(clientSock, eph_socket_num)
    # Listen for connections
    eph_socket.listen(1)
    # Accept any incoming connections
    ephemeral_socket, addr = eph_socket.accept()
    print(f"Accepted datasocket connection from client: {addr}")
    return ephemeral_socket

# CLI Checks
if len(sys.argv) < 2:
    print(f"USAGE: python {sys.argv[0]} <PORT>")
    exit()
# Check valid port number.  
if not sys.argv[1].isdigit():
    print(f"Not a port number, try again.")
    exit()

listenPort = int(sys.argv[1])

welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
welcomeSock.bind(('', listenPort))
welcomeSock.listen(1)

# Main loop, looks and keeps track of client socket.
while True:
    print("Awaiting Connections...")
    
    clientSock, addr = welcomeSock.accept()

    print(f"Accepted connect from client: {addr}")

    while True:
        try:
            # Get fileSize for command
            fileSize = recvAll(clientSock, 10)
            # Get Command from fileSize
            command = recvAll(clientSock, int(fileSize))

            if command.decode('utf-8') == "ls":
                # Generate and send ephemeral port to server.
                ephSocket = getEphemeralSocket(clientSock)
                # Get the ls -l of the server file's directory.
                result = subprocess.run(['ls', '-l', './'], stdout=PIPE, stderr=PIPE, universal_newlines=True).stdout
                # Send data to the client
                send_data(ephSocket, result)
                print("Successfully sent ls -l to client")
                ephSocket.close()
            
            elif command.decode('utf-8') == "get":
                # Get fileSize for filename
                fileSize = recvAll(clientSock, 10)
                # Get filname for checks
                filename = recvAll(clientSock, int(fileSize))
                filename = filename.decode('utf-8')
                if not os.path.exists(f"./{filename}") or filename == "server.py":
                    send_data(clientSock, "NUL")
                    continue
                # Generate Ephemeral Socket and wait for connection.
                ephSocket = getEphemeralSocket(clientSock)

                # Open file and send data
                try:
                    # Open file in bytes mode.
                    file = open(filename, "rb")
                    b = file.read(1)
                    bytessent = 0

                    # Send while bytes exist
                    while b:
                        send_data(ephSocket, b)
                        b = file.read(1)
                        bytessent += 1

                    print(f"SUCCESSS: Sent {bytessent} bytes to client")
                except Exception as e:
                    print(f"Issues opening the file or sending data: {e}")
                finally:
                    # Terminate data connection socket and close file.
                    ephSocket.close()
                    file.close()

            elif command.decode('utf-8') == "put":
                # Create and send data connection socket to client.
                ephSocket = getEphemeralSocket(clientSock)

                # Get filename from data socket.
                fileSize = recvAll(ephSocket, 10)
                filename = recvAll(ephSocket, int(fileSize)).decode('utf-8')

                print(f"Uploading {filename} from the client!")
                
                # Open file in bytes mode.
                file = open(filename, "wb")

                bytecount = 0

                while True:
                    headFileSize = recvAll(ephSocket, 10)

                    # Break if there no more data being sent.
                    if not headFileSize:
                        break

                    b = recvAll(ephSocket, int(headFileSize))

                    # Break if there no more data being sent. (double checker)
                    if not b:
                        break

                    # Write to file.
                    file.write(b)

                    bytecount += 1

                # Close file and terminaate
                file.close()
                ephSocket.close()

                print(f"SUCCESS: {bytecount} bytes transfered from client")

            elif command.decode('utf-8') == "quit":
                clientSock.close()
                print(f"Client, {addr} has disconnected.")
                break

            # This condition shouldn't ever happen, since any 
            # other command is filtered out at client side.
            else:
                pass
        except:
            pass