Instructions:
============
This file contains instructions to compile and run the client and server application from command line.

Program Structure:
=================
* The root folder is named ClientServerApplication. 
* This folder contains

ClientServerApplicaton
  Server - Root folder for Server application.
    \server.cpp - Source file containing the server application.
	
  Client - Root folder containing the client application.
    \client.cpp - Source file containing the client application
 
README.txt
==========

Environemt: These are the details about the environment used in this project	
  Operating System: Ubuntu 16.04
  Programming Language: C++
  GCC compiler version: 5.4.0
 

Build and Run Instructions:
==========================

1. Run from Ubuntu commandLine:  
   Server
      Build:
	* To compile the program move to the target directory
	* Navigate to ClientServerApplication\Server folder
	* Type "g++ server.cpp -o server -std=c++11 -pthread" to compile/build the Server application  
	* If the build is successful, the following are output in the Server folder
		* server	
      Run:
	* From the same folder ClientServerApplication\Server,
		type server port_number (Note this port_number is specified as an argument on commandline)
	  Eg: ./server 2030
      
      Now the server is listening for connections on port 2030 

    Client
       Build:
	* To compile the program move to the target directory
	* Navigate to ClientServerApplication\Client folder
	* Type "g++ client.cpp -o client -std=c++11 -pthread" to compile/build the Client application  
	* If the build is successful, the following are output in the Client folder
		* client	
       Run:
	* From the same folder ClientServerApplication\Client,
		type Client serverip_address port_number (Note: server_ip_address and port_number are specified as arguments on commandline. 
             Also the port_number should match with the one used in Server application).
	  Eg: ./client 127.0.0.1 2030
      
      Now the client has established connection with server on port 2030
      
   Test:
   ====
	1. Run server & two clients in separate terminals and start issuing GET/PUT/DELETE operations from client.
            2. From the client terminal, you will notice a Client> prompt to type messages
	3. .Start issuing GET/PUT/DELETE operations from client. 
	4. For each input, Server will perform these operations and respond with messages to the clients on respective threads with acknowledgment message.
		PUT: Key-Value pair inserted into key store successfully
		DELETE: Key-Value pair deleted from key store successfully
	5.For GET operation server will give the value which will be displayed with on the client terminal.
	6.  Server will store all the key value pairs in a shared key store which is protected through mutex (using locks).
	7. One server thread (handling a particular client) at a time will acquire a lock on the shared resource (key store) and will be released after its operation is completed.
	8.  Next thread waiting on the lock will acquire it to complete its operation.
	7. Go back to client terminal.
	9. Notice that there is a Server> followed by the same message. This message is coming from Server.
	10. Now the client prints the time stamp after receiving the message from server.It should show up on client terminal.
           11. The above steps can be repeated for any number of clients to implement multithreading
   
           
   
     Terminate: 
     =========

         * You can exit the server by simply using Ctrl + C on the server terminal.
         * You can close the client by typing "BYE" on the client terminal.

