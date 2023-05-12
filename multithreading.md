# Functions in sqlfetch.py
## Function 1 - establishConnection 
1. get tunnel
    - `tunnel = open_ssh_tunnel(optilima.wolution.com, optilima, password)`
2. when tunnel is open, establish connection
    - `connection = mysql_connect(optilimadb, password)`
    - when connection is established, wait 5 minutes max 
    - if time is over 5 minutes, disconnect

## Function 2 - justquery 
1. get the query as a string
    - `query = 'SELECT timestamp_server FROM detections LIMIT 0,100'`
2. execute query
    - `run_query(query, connection)`

## Function 3 - main 
1. Open thread 1 in the background, keep the connection open
    - `conThread = threading.Thread(target=conAndQuery, args=(ChunkTimestamps_A, chosenColumn_S, logindata, csvFilePath))`
2. start the thread, leave it open until (terminate OR 5 min time passed) 
    - `conThread.start()`

4. for loop
    - `FOR 100 times...`
3. start the query function as a thread again and again, while still having the tunnel open
means:
- check for tunnel
    - `if conThread.is_alive():`
- start the thread for the query
    - i did this with all the threads in an array, to keep track of them and start them easily
    - `currentthread = threading.Thread(target=justquery,args=(str(query), csvFilePath))`
    - `queries.append(currentthread)`
    - `queries[i].start()`
- wait until querythread is finished
    - `queries[i].join()`
- start all over again

## IMPORTANT!!
check the returns of the threads/functions. end them properly, have a return for every option

# your work
1. timestamp in timestamp_server umwandeln
2. wenn timestamp unterschied grösser als zb 60000, muss das aufgeteilt werden
3. also teilen wir das in einem array in x mal (60000 timestampeinheiten) auf
    - also zb wir haben 120k unterschied, teilen also in 2 chunks mit jeweils 60k auf
    - BEISPIEL:[Start=100, punkt1= 100+60, punkt2= punkt1+60, Ende=punkt2+rest]

# my project
4. tunnel öffnen
5. connection zur datenbank öffnen
6. anfragen machen
- jetzt müssen kleine anfragen aus dem Array genommen werden
- also eine for schleife, die alle elemente nacheinander durchgeht und NUR 2 aufeinanderfolgende elemente des arrays als timestampvalues nimmt
- also zb start=array[0] und ende = array[1]
- Query wäre dann: Select * FROM database where timestamp>array[0] or timestamp < array[1]
- RETURN grosses array[dataframe1, dataframe2, dataframe3….]
