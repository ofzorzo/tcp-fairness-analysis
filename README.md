# tcp-fairness-analysis
Simples client-server application to analyze TCP's congestion control.

## Running

The first step is to run the server with
```
python server.py -p PORT_NUMBER
```
After that, run some clients with
```
python client.py -i SERVER_IP -p PORT_NUMBER
```
When you think the clients have sent enough data to the server, kill them with CTRL+C. Now you can visualize each client's transmission rate as time progressed by running:
```
python logs_parser.py -f client_179-219-202-77_14414.csv client_179-219-202-77_14416.csv
```
Each .csv is a log file created for a specific client. These .csv's are created in the project's root directory.
