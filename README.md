# SimplePerf

**SimplePerf** is a lightweight network performance testing tool inspired by `iperf`, implemented in Python using sockets. It allows you to measure data transfer rates between a server and a client.

## Features
- **Server and Client Modes**: Run as a server or client.
- **Data Formats**: Supports Bytes, Kilobytes, and Megabytes.
- **Custom Ports and IPs**: Specify server IP and port.
- **Interval Reporting**: Periodically print transfer rates.
- **Parallel Connections**: Support for multiple simultaneous connections.
- **Custom Data Size**: Send a specified amount of data.

## Usage

### Start the Server
```bash
python simpleperf.py -s -p <port> -b <bind_address> -f <format>
```

### Start the Client
```bash
python simpleperf.py -c -I <server_ip> -p <port> -t <time> -f <format> -n <num> -i <interval> -P <parallel_connections>
```

## Examples

Run the server on 127.0.0.1 port 8088:
```bash
python simpleperf.py -s -p 8088 -b 127.0.0.1 -f MB
```

Run the client for 20 seconds with 5-second intervals:
```bash
python simpleperf.py -c -I 127.0.0.1 -p 8088 -t 20 -f MB -i 5
```



