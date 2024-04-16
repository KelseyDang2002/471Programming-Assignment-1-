# 471 Programming Assignment 1

## Group Members:

1. Daniel Garcia, dannygarcia2120@csu.fullerton.edu
2. Kelsey Dang, kdangdo2002@csu.fullerton.edu
3. Jacob Corletto, jacob.corletto@csu.fullerton.edu
4. Sai chetan Kamisetty, kamisetty@csu.fullerton.edu
5. Irvin Rafael, irvin999rafael6@csu.fullerton.edu

## Programming Language(s) Used:

1. Python (using sockets and os libraries)

### Set Up

1. Start at "project" folder
2. Open a seperate terminal in the same directory
3. Open the "Client" folder in one terminal and "Server" in the other
4. Starting in the "Server" terminal run the command:

```console
python3 server.py <port number>
```

5. In the "Client" terminal run the command:

```console
python3 client.py <server machine> <server port>
```

### Program Execution

While connected to the server database, the client terminal has access to the following commands:

- ls
  - Use this command to list the contents of the database
- get [file name]
  - Use this command to retrieve a file from the database
  - Use the parameter "file name" to request the file by name (not path)
- put [file name]
  - Use this command to send a file to the database
  - Use the parameter "file name" to request the file by name (not path)

## Anything special about submission to take note of:

Set up steps are to be taken in order for functional FTP communications.

If any bugs are found please contact by email or submit pull request.

Thanks!

\- Students of CPSC 471
