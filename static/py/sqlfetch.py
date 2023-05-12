# global modules
import userbase
import time
import threading
import logging
import csv
import os
import ast
import datetime
import sys
# my modules
import passwords
import crypting
import tunnelfunctions
from tunnelfunctions import *
# sys.path.append('../')
logger = logging.getLogger(__name__)
# use this line for more information, logging levels:
# debug, info, warning, error
logging.basicConfig(level=logging.ERROR)
# bonusfunction


def Timechunks(timestamp_start, timestamp_end, chunk_size):
    # the total timespan that has to be covered
    total_difference = abs(timestamp_start-timestamp_end)
    # all the chunks that i can to with 60k steps
    total_chunks = int(total_difference / chunk_size)
    # the remainder of all those steps, for the last query
    Remainder = total_difference - int(total_chunks * chunk_size)
    # if theres just one chunk, theres no rest and it can be forgotten
    if (total_chunks == 0):
        Remainder = 0
    # print(str(total_difference) + ';' + str(total_chunks) + ';' + str(Remainder))
    # now i will calculate all the needed timestamps
    chunk_timestamps = [timestamp_start]  # fist, append the start
    timestamp_temp = timestamp_start  # new variable, for the individual timestamps
    for i in range(0, total_chunks):  # for loop to go through the chunks
        # increace temp variable and add the chunk_size
        timestamp_temp = timestamp_temp + chunk_size
        # append all of this to the array
        chunk_timestamps.append(timestamp_temp)
    # at last, add the remainder to the end and add that as well
    # but just if its not zero
    if (Remainder != 0):
        chunk_timestamps.append(timestamp_temp + Remainder)
    else:
        # if it is, i just append the last timestamp, that way i still have an array
        chunk_timestamps.append(timestamp_end)
    # print(chunk_timestamps)
    return chunk_timestamps

# function to connect to the database through the tunnel


def establishConnection(logindata, setdata=False):
    if setdata:
        passwords.logindata = crypting.encrypt(logindata)
    # how many half seconds, until theres a timeout?
    tunneltime = 600
    # open the tunnnel, use the logindata that has been provided
    # tunnel = open_ssh_tunnel(logindata[0], logindata[1], logindata[2])

    tunnel = open_ssh_tunnel(
        ast.literal_eval(crypting.decrypt(passwords.logindata))[0],
        ast.literal_eval(crypting.decrypt(passwords.logindata))[1],
        ast.literal_eval(crypting.decrypt(passwords.logindata))[2])
    # start the tunnel, if not, raise an exception
    try:
        tunnel.start()
    except Exception as e:
        logger.error(err(1, e))
        return 1
    # set the connection variable in the other file
    # this is just a way to keep track of everything, the data will be saved
    # globally, that way i dont have to switch them around all the time
    try:
        tunnelfunctions.connection = mysql_connect(
            ast.literal_eval(crypting.decrypt(passwords.logindata))[3],
            ast.literal_eval(crypting.decrypt(passwords.logindata))[4])
    except Exception as e:
        logger.error(err(7, e))
        return 7
    logger.warning(tunnelfunctions.connection)
    # as long as the queries are not done, so they are stil going
    # ========================================================================
    while not tunnelfunctions.query_done and tunneltime != 0 and not setdata:
        if tunnelfunctions.connection:
            time.sleep(1)
            logging.debug('still alive')
    # ========================================================================
            # after every second, substract one
        else:
            tunneltime = tunneltime - 1
    if setdata:
        setdata = False
    # when the whileloop is done, disconnect the database
    disconnect(tunnelfunctions.connection)
    logger.info("Disconnected from database")
    return 2


def justquery(query, csv_file_path):
    # tries, until the functions stops to establish a connection
    # this is here because the thread needs a while to get the connection ready
    # and this way it gives the function time, to wait until theres a tunnel and
    # a connection to the database
    tries_until_break = 10
    logger.debug("Next Query")
    # this loop is supposed to go through again and again,
    # i needed a way to keep the function going, even when theres no connection or anything
    # normally i would need a condition, but i havent figured out what that condition could be
    while 1:
        # so if the connection is established
        # (this never gets directly executed, it always goes into the else first)
        # just because it takes a while until the tunnel is open
        if tunnelfunctions.connection:
            logger.debug("i have connection")
            # get the time before the query started, just to keep track of everything
            before = datetime.now()
            try:
                # now try to run the query, use the connection from the other file
                # and the query string that has been given to the function
                try:
                    df = run_query(query, tunnelfunctions.connection)
                except Exception as e:
                    # logging.error("Here it is")
                    logger.error(err(6, e))
                # get the time, the query lasted
                tunnelfunctions.query_time = datetime.now() - before
                logger.debug('Query took:' + str(tunnelfunctions.query_time))
                # append the result from the query (the dataframe) if its not empty
                # to the result that is stored in the other file
                # but i append this as an array, otherwise it doenst work
                # ========================================================================
                if not df.empty:
                    # tunnelfunctions.result.append(df)
                    pd.DataFrame(df).to_csv(csv_file_path, mode='a',
                                            header=tunnelfunctions.first_round, index=False, quoting=csv.QUOTE_ALL)
                    tunnelfunctions.first_round = False

                # ========================================================================
                # return true, as the function is done now
                return True
            # if anyting goes wrong with the query, go into this exception
            # and end the function
            except Exception as e:
                logger.error(err(1, e))
                print(len(tunnelfunctions.result))
                # i also write the query_done here because when there is an exception,
                # most likely it wont be solved on the second attempt
                tunnelfunctions.query_done = True
                return False
        else:
            # so, if theres no connection yet, i go through a loop
            for i in range(tries_until_break):
                # if the connection gets established while we are in here...
                if tunnelfunctions.connection:
                    logger.debug("Connection found after" + str(i) + 'times')
                    # we exit the for loop
                    break
                else:
                    # if its not there, we wait for one second until we try again
                    time.sleep(1)
                    # and if the time is over and the connection is still not done
                    if i == tries_until_break and not tunnelfunctions.connection:
                        logger.error("Timeout")
                        # we tell everyone that it is done and exit the function
                        tunnelfunctions.query_done = True
                        return False
    return False

# logindata is an array with the following strucutre:
# [ssh_host, ssh_username, ssh_password, database_username, database_password]
# chunk_timestamps is the array with all the different times in there

# Print iterations progress


def main(chunk_timestamps, chosen_column, logindata, csv_file_path):
    # Chunks are all the chunks, i just get them by counting the elements in the array
    try:
        Chunks = len(chunk_timestamps) - 1
    except Exception as e:
        logging.error(str(e) + ' -- did you read the README file??')
        return False
    logger.info(str(Chunks) + " Queries")
    # a list for all the querythreads, just to keep track of how many we have
    # and to make it a bit easier to dynamically start them
    # because i can access them one by one without having to give them a name
    query_thread_list = list()
    loadingbar = []
    # try to start the first thread to establish the connection
    conThread = threading.Thread(target=establishConnection,
                                 args=(logindata, chunk_timestamps))
    try:
        conThread.start()
    except Exception as e:
        # raise and exception if it doesnt work
        logger.error(err(2, e))
        # also end the function
        return False

    # now we have to start a query for every chunk that we have
    for active_chunk in range(Chunks):
        # alright, the loading bar
        # i need to know in every moment, how many of the chunks i did, then i can draw 100 max and then how many i think i need
        for i in range(100):
            if i <= int(active_chunk / ((Chunks - 1) / 100)):
                loadingbar.append('#')
            else:
                loadingbar.append('-')
        # so we start by getting the values out of the function, meaning the iTH and the (i+1)TH element
        timestamp_start = chunk_timestamps[active_chunk]
        timestamp_end = chunk_timestamps[active_chunk+1]
        # as long as the conthread is alive, all is perfect
        if conThread.is_alive():
            # now we generate the query, insert the chosencolumns
            # and also the times from the array
            query = 'SELECT ' + chosen_column + \
                ' FROM `detections` WHERE `timestamp_server`>= ' + \
                str(timestamp_start) + ' AND `timestamp_server`<' + \
                str(timestamp_end)
            logger.debug(query)
            # now we get a thread, just a general one
            # this variable gets overwritten every time we are in the loop
            currentthread = threading.Thread(target=justquery,
                                             args=(str(query), csv_file_path))
            # this thread, we add to the list of threads that we
            # mad earlier
            query_thread_list.append(currentthread)
            # logger.info(query_thread_list)
            try:
                # now we try to start the thread
                query_thread_list[active_chunk].start()
                logger.debug('Start thread' + str(active_chunk))
                # and then we wait until it is finished
                query_thread_list[active_chunk].join()
                logger.debug('waiting for thread' + str(active_chunk))
                # here i get the threadtime
                print(f"query time: {tunnelfunctions.query_time}")
                logger.debug(query_thread_list[active_chunk])
                # print(*loadingbar, end='\r')
                print(''.join(str(i) for i in loadingbar) + ' ' +
                      str(Chunks - active_chunk) + ' left', end='\r')
                # logger.warning('Query lasted: ' + str(tunnelfunctions.query_time))
                # now the tricky part
                # we want to know when the last thread is done
                # so we wait until one thread is finished, and as long as the loop
                # function is also at its end...
                # ========================================================================
                if not query_thread_list[active_chunk].is_alive() and active_chunk == (Chunks - 1):
                    # we can tell everyone that all the queries are done and that we can
                    # end all the functions
                    print('')
                    tunnelfunctions.query_done = True
                    logger.info("Queries Done")
                    return tunnelfunctions.result
                # ========================================================================
            except Exception as e:
                # if something goes wrong with the threads,
                # tell everyone to stop and raise an exception
                tunnelfunctions.query_done = True
                logger.error(err(3, e))
                return False
        else:
            logger.warning('Tunnel ist geschlossen')
            # if the thread isnt activated or has been stopped
            # print the soluction and end the function
            return False


def err(num, e):
    # the lazy cat....
    print("[" + str(num) + "]" + str(e))
