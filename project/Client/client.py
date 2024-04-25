import socket
import os
import sys

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

# CLI Checks
if len(sys.argv) < 3:
    print(f"USAGE: python {sys.argv[0]} <SERVER MACHINE> <PORT>")
    exit()

#Check Valid port number.
if not sys.argv[2].isdigit():
    print(f"Not a port number, try again.")
    exit()

server_machine = sys.argv[1]
port = int(sys.argv[2])

# Create socket for client
connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect to the server
connSock.connect((server_machine, port))

# Main Loop
while True:
    data = input("ftp> ")

    split_arg = data.split(" ")

    # ls Command
    if split_arg[0] == "ls":
        send_data(connSock, 'ls')

        # Recieve Ephemeral Socket
        ephfilesize = recvAll(connSock, 10)
        ephSocket = recvAll(connSock, int(ephfilesize))

        # Connect to Ephemeral Port for data transfer
        dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dataSock.connect((server_machine, int(ephSocket.decode('utf-8'))))

        # Recieve the ls string from server
        filesize = recvAll(dataSock, 10)
        lsStr = recvAll(dataSock, int(filesize))
        print(lsStr.decode('utf-8'))

        dataSock.close()
    
    # get Command
    elif split_arg[0] == "get":

        # Argument check
        if len(split_arg) < 2:
            print("Missing filename to get.")
            continue

        # Send get command to server.
        send_data(connSock, 'get')
        
        filename = split_arg[1]

        # Send filename for checks.
        send_data(connSock, filename)

        # Get ephemeral Socket from the server.
        filesize = recvAll(connSock, 10)
        ephSocket = recvAll(connSock, int(filesize))

        # If filename doesn't exist, NUL is returned, if no ephSocket given, None.
        if ephSocket.decode('utf-8') == "NUL" or ephSocket is None:
            print("ERROR: Server does not contain that file. Try again.")
            continue

        # Connect client to ephemeral socket for data transfer
        dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dataSock.connect((server_machine, int(ephSocket.decode('utf-8'))))

        print(f"Downloading {filename} from server.")

        # Open new file for writing, if file exist replace contents.
        file = open(filename, "wb")

        bytecount = 0

        while True:
            headFileSize = recvAll(dataSock, 10)

            # Break if there no more data being sent.
            if not headFileSize:
                break

            b = recvAll(dataSock, int(headFileSize))

            # Break if there no more data being sent. (double checker)
            if not b:
                break

            # Write to file.
            file.write(b)

            bytecount += 1
        
        # Close file and terminaate
        file.close()
        dataSock.close()

        print(f"File: {filename}:{bytecount} has been transfered to client.")
    # put Command
    elif split_arg[0] == "put":

        # Argument check
        if len(split_arg) < 2:
            print("Missing filename to get.")
            continue

        filename = split_arg[1]

        if not os.path.exists(f"./{filename}") or filename == "client.py":
            print("Error: This file was not found in the client's directory!")
            continue

        # Send put command to server.
        send_data(connSock, 'put')

        # Get ephemeral Socket from the server.
        filesize = recvAll(connSock, 10)
        ephSocket = recvAll(connSock, int(filesize))
        
        # If no ephSocket given for some reason, return none and return.
        if ephSocket is None:
            print("ERROR: Server did not return data transfer port.")
            continue
        
        # Connect client to ephemeral socket for data transfer
        dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dataSock.connect((server_machine, int(ephSocket.decode('utf-8'))))
        
        # Send filename through datasocket so server knows filename to save as.
        send_data(dataSock, filename)

        try:
            file = open(filename, "rb")
            b = file.read(1)
            bytessent = 0

            while b:
                send_data(dataSock, b)
                b = file.read(1)
                bytessent += 1

            print(f"Filename, {filename}:{bytessent} has successfully been sent to server.")

        except Exception as e:
            print(f"Issues opening the file or sending data: {e}")
        finally: 
            dataSock.close()
            file.close()

    # quit Command
    elif split_arg[0] == "quit":
        send_data(connSock, 'quit')
        print("Exiting FTP...")
        break
    # handle invalid input
    else:
        print("Unknown command, try again.")


connSock.close()
