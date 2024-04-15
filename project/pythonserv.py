import socket

# The port on which to listen
serverPort = 12000

# Create a TCP socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
serverSocket.bind(('', serverPort))

# Start listening for incoming connections
serverSocket.listen(1)
print("The server is ready to receive")

# Forever accept incoming connections
while True:
    # Accept a connection; get client’s socket
    connectionSocket, addr = serverSocket.accept()

    # The data buffer
    data = b""  # Initialize an empty byte string

    # Receive data until 40 bytes are received
    while len(data) < 40:
        # Receive whatever the newly connected client has to send, up to 40 bytes
        tmpBuff = connectionSocket.recv(40 - len(data))
        if not tmpBuff:
            break  # If no more data is received, break the loop
        data += tmpBuff  # Append the received data to the buffer

    # Print the received data
    print("Received data:", data)

    # Close the socket for this client
    connectionSocket.close()

# The server will never reach here since it's an infinite loop, but theoretically, if it did, you would close the server socket
serverSocket.close()
