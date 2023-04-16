import socket
import threading
import time
import argparse
import re
import sys

BUFFER_SIZE = 1000

def handleClient(client_socket, ipAddress, port, unitConverter):

    # a client handler function 
    received_bytes = 0
    start_time = time.time()
    while True:
        # we receive data in 1000B chunks
        data = client_socket.recv(BUFFER_SIZE)
        # then we check if all data have been recived
        if "BYE" in data.decode():
                break
        received_bytes += len(data)

    # here we are calculating transfer time and rate
    # first, by using time.time() we record the current time
    end_time = time.time() 
    duration = end_time - start_time
    #calculating the size of the data transferred
    transfer_size = received_bytes/ unitConverter 
    #We calculateing the rate in megabits per second, then dividing by 1000000 to convert the result to megabits per second
    rate = (received_bytes / duration) * 8 / 1000000

    # print results to console
    print('ID                  Interval          Received             Rate')
    print(f'{ipAddress}:{port}     0.0 - {duration:.1f}       {transfer_size:.2f} MB         {rate:.2f} Mbps')
    # Sends acknowledgement message to client, and then close the connection
    client_socket.send('ACK'.encode())
    client_socket.close()


def server(args):
    #defindes the 'ipAdress', 'port' and 'format' and connect it to the values in the args

    ipAdress = args.bind
    port = args.port
    format = args.format

    #The if statement checks if 'format' is one of the allowed values, and if nor it prints an error message and returns.
    if format not in ['B', 'KB', 'MB']:
        print('Invalid format argument. Allowed formats: B, KB, MB')
        return
    #The unitConverter variable is set based on the 'format' value.
    unitConverter = 1000 ** ['B', 'KB', 'MB'].index(format)

    #This creates a new 'socket' object for the server.
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #Bind it to the ipAdress and port variables.
    server_socket.bind((ipAdress, port))
    #Start listening for incoming connections.
    server_socket.listen(5) 
    #It then prints a message to the console indicating that the server is listening.
    print("------------------------------------------")
    print(f"A simpleperf server is listening on port {port}")
    print("------------------------------------------")
    #This is the main loop of the server

    while True:
        #it waits for a client to connect, accept the connection
        client_socket, address = server_socket.accept()
        print(f'A simpleperf client with {ipAdress}:{port} is connected with {ipAdress}:{port}')
        # create a new thread to handle the client connection
        client_thread = threading.Thread(target=handleClient, args=(client_socket, address, port, unitConverter))
        client_thread.start()


def client(args):

    ipAdress = args.serverip
    port = args.port
    format = args.format

    if format not in ['B', 'KB', 'MB']:

        print('Invalid format argument. Allowed formats: B, KB, MB')

        return
    
    unitConverter = 1000 ** ['B', 'KB', 'MB'].index(format)
    total_duration = args.time
    start_time = time.time()
    interval_time = args.interval
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ipAdress, port))
    print(f'Client connected with {ipAdress} port {port}')

    total_bytes_sent = 0
    bytes_per_interval = 0

    if args.num:
        num = args.num
        match = re.match(r"([0-9]+)([a-z]+)", num, re.I)

        if match:
            num, unit = match.groups()
            unit_convert = 1000 ** ['B', 'KB', 'MB'].index(unit.upper())
            transfer_size = int(num) * unit_convert

        else:

            print('Invaild num argumet. Usage: --num<number><unit>')
            return

        while total_bytes_sent < transfer_size:
            data = client_socket.recv(BUFFER_SIZE)
            client_socket.send(data)
            total_bytes_sent += len(data)
        client_socket.send(b'BYE')
        client_socket.recv(BUFFER_SIZE)
        client_socket.close()
        end_time = time.time()
        duration = end_time - start_time
        rate = (transfer_size / duration) * 8 / 1000000
        transfer_size = transfer_size / unitConverter

        print(f'ID               Interval      Transfer      Bandwidth')
        print(f'{ipAdress}:{port}       0.0 - {duration:.1f}       {transfer_size:.2f}  {format}         {rate:.2f} Mbps')

    elif interval_time != 0:
        intervals = total_duration // interval_time
        prev_interval_end_time = start_time 
        timer = time.time()

        for i in range(intervals):
            interval_start_time = time.time()
            while time.time() - interval_start_time < interval_time:

                data = bytes(BUFFER_SIZE)
                client_socket.send(data)
                bytes_per_interval += len(data)

            interval_end_time = time.time()
            interval_duration = interval_end_time - interval_start_time
            interval_rate = (bytes_per_interval / interval_duration) * 8 / 1000000

            print(f'ID              Interval     Transfer        Rate')
            print(f'{ipAdress}:{port}     {prev_interval_end_time - timer:.1f} - {interval_end_time - timer:.1f}       {bytes_per_interval/unitConverter:.2f} {format}         {interval_rate:.2f} Mbps')

            prev_interval_end_time = interval_end_time
            total_bytes_sent += bytes_per_interval
            bytes_per_interval = 0
            time.sleep(max(0, interval_time - interval_duration))
        client_socket.send(b'BYE')
        client_socket.recv(BUFFER_SIZE)
        client_socket.close()

        print(f'----------------------------------------------------------------------')
        print(f'Total Interval: {start_time - timer:.1f} - {interval_end_time - timer:.1f}')
        print(f'Total Transfer: {total_bytes_sent/unitConverter:.2f} {format}')
        total_duration = interval_end_time - start_time
        total_rate = (total_bytes_sent / total_duration) * 8 / 1000000
        print(f'Total Rate: {total_rate:.2f} Mbps')

    else:

        while time.time() - start_time < total_duration:

            data = bytes(BUFFER_SIZE)
            client_socket.send(data)
            total_bytes_sent += len(data)

        client_socket.send(b'BYE')
        client_socket.recv(BUFFER_SIZE)
        client_socket.close()
        end_time = time.time()
        duration = end_time - start_time
        transfer_size = total_bytes_sent / unitConverter
        rate = (total_bytes_sent / duration) * 8 / 1000000

        print(f'ID               Interval      Transfer      Bandwidth')
        print(f'{ipAdress}:{port}       0.0 - {duration:.1f}       {transfer_size:.2f} {format}         {rate:.2f} Mbps')
def main():
    #Create an ArgumentParse to parse the command line arguments
    parser = argparse.ArgumentParser(description='A simplified version of iperf using sockets.')
    #Add various command line arguments

    parser.add_argument('-b', '--bind', default='127.0.0.1', help='allows to select the ip address of the server"s interface')
    parser.add_argument('-p', '--port',  default=8088, type=int, help='port number on which the server should listen')
    parser.add_argument('-s', '--server', action='store_true', help='enable server mode')
    parser.add_argument('-c', '--client', action='store_true', help='enable client mode')
    parser.add_argument('-I', '--serverip', default='127.0.0.1', help='the IP address of the server to connect to')
    parser.add_argument('-t', '--time', type=int, default=10, help='the duration of the test in seconds')
    parser.add_argument('-P', '--parallel', type=int, default=1, help='the number of parallel connections to use')
    parser.add_argument('-f', '--format', choices=['B', 'KB', 'MB'], default='MB', help='the transfer rate format to use')
    parser.add_argument('-n', '--num', metavar="<number><unit>", default=0, help="number of times to send message")
    parser.add_argument('-i', '--interval', type=int, default=0, help='the interval to print results in seconds')

    #Parse the command line arguments

    args = parser.parse_args()

#This range is dafualt for all port values, because this is a 16-bit and the maximum value for 16-bit is 65535

    if args.port < 1024 or args.port > 65535: 
        print("Invalid port number. Must be in the range [1024, 65535]")
        sys.exit(1)
    #Check if both server and client modes are enabled, and print an error message if so

    if args.server and args.client:
        print('Cannot specify both server and client mode')
        return
    
    #Check if neither server nor client mode is enabled, and print an error message if so
    if not args.server and not args.client:
        print('Must specify either server or client mode')
        return
#if server mode is enabled, call the server() function
    if args.server:
        server(args)

    #if client mode is enabled, call the client() function

    if args.client:
        if args.parallel > 1:
            for i in range(args.parallel - 1):
                thread = threading.Thread(target=client, args=(args,))
                thread.start()
        client(args)

#Run the main function if this script is being run directly

if __name__ == '__main__':
    main()