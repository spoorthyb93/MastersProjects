//
// A simple Mulithreaded server application. It listens to the port
// written in command line, accepts a connection, and a seperate server thread
// handles the communication with the client from there on.

// Server can handle multiple clients at the same time by creating
// a seperate thread for each client communication.
//
// Usage:
//      server [port_to_listen]
//
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <iostream>
#include <iomanip>
#include <sys/socket.h>
#include <netinet/in.h>
#include <string>
#include <thread>
#include <time.h>
#include <exception>
#include <typeinfo>
#include <stdexcept>
#include <pthread.h>
#include <fcntl.h>
#include <errno.h>
#include <netinet/in.h>
#include <resolv.h>
#include <arpa/inet.h>
#include <map>
#include <mutex>
#include <sstream>
#include <vector>


using namespace std;

static void usage()
{
    printf("Usage:\n"
           "     server <port_to_listen>\n");
}

void* SocketHandler(void*);

static void setValue(string,string,string);

static bool getValue(string,char*,string);

static bool deleteValue(string,string);

static void printValues(string);

static map<string, string> mymap;

static std::mutex mtx;

int main(int argc, char* argv[])
{
    if (argc > 1 && *(argv[1]) == '-')
    {
        usage();
        exit(1);
    }

    int listenPort;
    if (argc > 1)
        listenPort = atoi(argv[1]);

    if (argc < 2)
    {
       cerr << "Please enter the server port. Syntax: ./server <port>" << endl;
       return -1;
    }


    if((listenPort > 65535) || (listenPort < 2000))
    {
       cerr << "Please enter a port number between 2000 - 65535" << endl;
       return -1;
    }
    // Create a socket
    int s0 = socket(AF_INET, SOCK_STREAM, 0);
    if (s0 < 0)
    {
        perror("Cannot create a socket");
        exit(1);
    }

    // Fill in the address structure containing self address
    struct sockaddr_in myaddr;
    memset(&myaddr, 0, sizeof(struct sockaddr_in));
    myaddr.sin_family = AF_INET;
    myaddr.sin_port = htons(listenPort); // Port to listen
    myaddr.sin_addr.s_addr = htonl(INADDR_ANY);

    // Bind a socket to the address

    if( ::bind(s0, (struct sockaddr*)&myaddr, sizeof(myaddr)) < 0 ){
      perror("Cannot bind a socket");
      exit(1);
    }

    // Set the "LINGER" timeout to zero, to close the listen socket
    // immediately at program termination.
    // struct linger linger_opt = { 1, 0 }; // Linger active, timeout 0
    // setsockopt(s0, SOL_SOCKET, SO_LINGER, &linger_opt, sizeof(linger_opt));

    // Now, listen for a connection
    int res = listen(s0, 20); // "20" is the maximal length of the queue
    if (res < 0)
    {
        perror("Cannot listen");
        exit(1);
    }
    cout << "Server is ready to accept client connections.. ";

    pthread_t thread_id=0;

    while(true){
      cout << "\n" << endl;
      cout << "Waiting for new client connections.. " << endl;
      // Accept a connection (the "accept" command waits for a connection with
      // no timeout limit...)
      struct sockaddr_in peeraddr;
      socklen_t peeraddr_len;

      int s1 = accept(s0, (struct sockaddr*)&peeraddr, &peeraddr_len);
      if (s1 < 0)
      {
          perror("Cannot accept incoming client connetion.. Terminating");
          exit(1);
      }
      if (s1 == 0)
      {
          perror("Client timed out.. Terminating");
          close(s1); // Close the data socket
          exit(1);
      }

      // A connection is accepted. The new socket "s1" is created
      // for data input/output. The peeraddr structure is filled in with
      // the address of connected entity, print it.
      printf("Connection from IP %d.%d.%d.%d, port %d\n",
          (ntohl(peeraddr.sin_addr.s_addr) >> 24) & 0xff, // High byte of address
          (ntohl(peeraddr.sin_addr.s_addr) >> 16) & 0xff, // . . .
          (ntohl(peeraddr.sin_addr.s_addr) >> 8) & 0xff, // . . .
          ntohl(peeraddr.sin_addr.s_addr) & 0xff, // Low byte of addr
          ntohs(peeraddr.sin_port));

      //string name = "client-";
      //name += std::to_string(peeraddr.sin_port);

      //cout << "Accepted connection from a client. Assigning a name to it based on the port.. " << name << endl;
      //string *userData = new string(name);

      pthread_create(&thread_id,0,&SocketHandler, (void*)s1);
      cout << "Created a new thread for the client " << endl;
      pthread_detach(thread_id);

    }
    return 0;
}


void* SocketHandler(void* lp){

   int csock = *((int*)(&lp));

   char buffer[1024];
   int buffer_len = 1024;
   int bytecount;

   // Get thread id
   std::ostringstream ss;
   ss << std::this_thread::get_id();
   string thread_id = ss.str();

   while (true)
   {
       memset(buffer, 0, buffer_len);

       try
       {
         // wait for data from client
         int bytesReceived = read(csock, buffer, buffer_len);

         if (bytesReceived < 0)
         {
             cerr << "Error while getting data from client. Quitting" << endl;
             cout << "\n" << endl;
             break;
         }
         if (bytesReceived == 0)
         {
             cout << "Client disconnected" << endl;
             cout << "\n" << endl;
             break;
         }

         string msg_from_client = string(buffer, 0, bytesReceived).c_str();

         string message_to_client("");
         message_to_client += "Only GET, PUT & DELETE operations are supported. Your message: ";
         message_to_client += msg_from_client;

         // Display the message received from client
         cout << "Message from client: " << msg_from_client << endl;

         vector<std::string> tokens;
         stringstream data(msg_from_client);
         string line;
         while(std::getline(data,line,' ')){
            if (line !=""){
                tokens.push_back(line);
            }
         }
         if (tokens.size() != 0){

           if (tokens[0] == "BYE")
           {
               cout << "Client requested for disconnection. Closing the connection.." << endl;
               break;
           }

           if (tokens[0] == "GET" && tokens.size() == 2){

             // Message format: GET a
             cout << "Obtaining value for this key: " << tokens[1] << endl;

             // GET value from the key-store
             char* value_from_map = new char[1024];

             if (getValue(tokens[1], value_from_map, thread_id)){
                //cout << "value from map => " << tokens[1] << ": "<< value_from_map << endl;
                message_to_client = value_from_map;
             } else {
                cout << "Value for this key doesn't exist. Key: " << tokens[1] << endl;
                message_to_client = "";
             }
             cout << endl;

           } else if (tokens[0] == "PUT" && tokens.size() == 3){

             // Message format: PUT a 1
             //cout << "Putting key value pair into the key store => " << tokens[1] << ": " << tokens[2] << endl;

             // PUT value from the key store
             setValue(tokens[1], tokens[2], thread_id);
             message_to_client = "Key-Value pair inserted into key store successfully";


           } else if (tokens[0] == "DELETE" && tokens.size() == 2){

             // DELETE value from the key store
             cout << "DELETE operation not implemented" << endl;

             // Message format: GET a
             cout << "Deleting key-value pair from the key-store. Key => " << tokens[1] << endl;

             // GET value from the key-store
             int value_from_map;

             if (deleteValue(tokens[1], thread_id)){
                message_to_client = "Key-Value pair deleted from key store successfully";
             } else {
                message_to_client = "No such key to delete!";
             }
             cout << endl;

           } else{
             cout << "Unsupported operation. Sending client message back as-is" << endl;
           }
         }

         // Display the current time with millisecond precision on server

         time_t theTime = time(NULL);
         struct tm* aTime = localtime(&theTime);

         cout << "Server Timestamp : "
           << aTime->tm_mon + 1 << '-'
           << aTime->tm_mday << '-'
           << aTime->tm_year + 1900 << ' '
           << aTime->tm_hour << ':'
           << aTime->tm_min << ':'
           << aTime->tm_sec << '\n' << endl;

         // Echo message back to client
         char* toClient = new char[1024];
         strcpy(toClient, message_to_client.c_str());
         write(csock, toClient, 1000);

       }
       catch (...){
         cout << "error during reading data from client.. " << endl;
       }
   }

   close(csock);
   return 0;
}


static bool getValue(const string key, char* value, const string id){


  bool found = false;

  // Wait until lock is acquired
  std::cout << "Thread: "<< id <<" Trying to acquire lock for GET operation.."<< endl;
  mtx.lock();

  // Lock is obtained, do the work
  std::cout << "Thread: "<< id <<" Lock acquired!" << endl;

  auto it = mymap.find(key);
  if (it != mymap.end()){

    string sss = it->second;
    strcpy(value, sss.c_str());

    found = true;
  }
  std::cout << "Thread: "<< id <<" Lock will be released.." << endl;


  // Release the lock
  mtx.unlock();

  std::cout << "Thread: "<< id <<" Lock is released!" << endl;

  return found;
}

static bool deleteValue(const string key, const string id){


  bool deleted = false;

  // Wait until lock is acquired
  std::cout << "Thread: "<< id <<" Trying to acquire lock for DELETE operation.."<< endl;
  mtx.lock();

  // Lock is obtained, do the work
  std::cout << "Thread: "<< id <<" Lock acquired!" << endl;


  auto it = mymap.find(key);
  if (it != mymap.end()){
    mymap.erase (it);
    deleted = true;
  }

  std::cout << "Thread: "<< id <<" Lock will be released.." << endl;

  // Release the lock
  mtx.unlock();

  std::cout << "Thread: "<< id <<" Lock is released!" << endl;


  return deleted;
}
static void setValue(const string key, const string value, const string id){


  // Wait until lock is acquired
  std::cout << "Thread: "<< id <<" Trying to acquire lock for PUT operation.."<< endl;
  mtx.lock();

  // Lock is obtained, do the work
  std::cout << "Thread: "<< id <<" Lock acquired!" << endl;
  mymap.insert(std::pair<string,string>(key, value));
  std::cout << "Thread: "<< id <<" Lock will be released.." << endl;

  // Release the lock
  mtx.unlock();
  std::cout << "Thread: "<< id <<" Lock is released!" << endl;


}

static void printValues(const string id){

  // Wait until lock is acquired
  std::cout << "Thread: "<< id <<" Trying to acquire lock for PRINT operation.."<< endl;
  mtx.lock();

  // Lock is obtained, do the work
  std::cout << "Thread: "<< id <<" Lock acquired!" << endl;

  // Lock is obtained, do the work
  for(auto it = mymap.cbegin(); it != mymap.cend(); ++it) {
    cout << it->first << " " << it->second << endl;
  }
  std::cout << "Thread: "<< id <<" Lock will be released.." << endl;

  // Release the lock
  mtx.unlock();
  std::cout << "Thread: "<< id <<" Lock is released!" << endl;


}
