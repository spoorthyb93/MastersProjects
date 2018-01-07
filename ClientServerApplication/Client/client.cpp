//
// A simple client application.
// It connects to a remote server,
// and it transmits messages to the server unless terminated,
// Client will be terminated when it sends 'BYE' to the server;
//
//
// Usage:
//          client <IP_address_of_server> <port_of_server>
//      where IP_address_of_server is either IP number of server
//      or a symbolic Internet name;
//      port_of_server is a port number.
//

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <iostream>
#include <iomanip>
#include <cstring>
#include <time.h>

using namespace std;

static void usage();

int main(int argc, char *argv[]) {
    if (argc > 1 && *(argv[1]) == '-') {
        usage(); exit(1);
    }

    // Create a socket
    int s0 = socket(AF_INET, SOCK_STREAM, 0);
    if (s0 < 0) {
        perror("Cannot create a socket"); exit(1);
    }

    // Fill in the address of server
    struct sockaddr_in peeraddr;
    int peeraddr_len;
    memset(&peeraddr, 0, sizeof(peeraddr));
    char* peerHost = "localhost";
    if (argc > 1)
        peerHost = argv[1];




    // Resolve the server address (convert from symbolic name to IP number)
    struct hostent *host = gethostbyname(peerHost);
    if (host == NULL) {
        perror("Cannot define host address"); exit(1);
    }
    peeraddr.sin_family = AF_INET;
    short peerPort = 2020;
    //if (argc >= 3)
    //    peerPort = (short) atoi(argv[2]);
    //peeraddr.sin_port = htons(peerPort);

    if(argc < 3)
     {
         cerr<<"Please enter hostname and server port. Syntax: ./client <host name> <port>"<<endl;
         return 0;
     }

     peerPort = (short)atoi(argv[2]);
     peeraddr.sin_port = htons(peerPort);


     if((peerPort > 65535) || (peerPort < 2000))
     {
         cerr<<"Please enter port number between 2000 - 65535"<<endl;
         return 0;
     }


    // Print a resolved address of server (the first IP of the host)
    printf(
        "peer addr = %d.%d.%d.%d, port %d\n",
        host->h_addr_list[0][0] & 0xff,
        host->h_addr_list[0][1] & 0xff,
        host->h_addr_list[0][2] & 0xff,
        host->h_addr_list[0][3] & 0xff,
        (int) peerPort
    );

    // Write resolved IP address of a server to the address structure
    memmove(&(peeraddr.sin_addr.s_addr), host->h_addr_list[0], 4);

    // Connect to a remote server
    int res = connect(s0, (struct sockaddr*) &peeraddr, sizeof(peeraddr));
    if (res < 0) {
        perror("Cannot connect"); exit(1);
    }

    cout << "Connected to the server. Start sending your messages.. " << endl;


	// Do-while loop to send and receive data
	char buff[10000];
	string userSpecifiedInput;
	do {
		cout << "CLIENT> ";

		// Keep reading userSpecifiedInput line by line from user
		getline(cin, userSpecifiedInput);

    if (userSpecifiedInput.size() > 0 && strcmp (userSpecifiedInput.c_str(),"BYE") ==0)
    {
        cout << "Client requested for disconnection. Closing the connection with server.." << endl;
        break;
    }


    // Send the user provided text to server
		if (userSpecifiedInput.size() > 0) {

      int sendResult = write(s0, userSpecifiedInput.c_str(), userSpecifiedInput.size()+1);

			// Successfully sent data to server
			if (sendResult > 0) {
        // cout << "sent a message to server successfully " << endl;

				// Wait for server response
				int bytesReceived = read(s0, buff, 4096);

        // Response from server to client successful
				if (bytesReceived > 0) {
					cout << "SERVER> " << string(buff, 0, bytesReceived) << endl;

					// Print the current system time in millisec precision

					time_t theTime = time(NULL);
					struct tm *aTime = localtime(&theTime);

					cout << "Client Timestamp : "
            << aTime->tm_mon + 1 << '-'
            << aTime->tm_mday << '-'
            << aTime->tm_year + 1900 << ' '
            << aTime->tm_hour << ':'
						<< aTime->tm_min << ':'
						<< aTime->tm_sec << '\n';
				}
			}
      else {
        cerr << "failed to send the message to the server. Response code: "<< sendResult << endl;
      }
		}

	} while (userSpecifiedInput.size() > 0);

    close(s0);
    return 0;
}

static void usage() {
    printf(
        "A simple Internet client application.\n"
        "Usage:\n"
        "         ./client [IP_address_of_server [port_of_server]]\n"
        "     where IP_address_of_server is either IP number of server\n"
        "     or a symbolic Internet name, \n"
        "     port_of_server is a port number\n"
        "The client connects to a server which address is given in a\n"
        "command line, receives a message from a server, sends the message\n"
        "Send BYE to terminate the connection\n"
    );
}
