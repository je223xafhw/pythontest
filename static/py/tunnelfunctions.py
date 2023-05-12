# ================================================================
# extra file with functions to connect to DB through sshtunnel
# Author: Jonny Ebinger
# finished: 17.10.2021
# please read the readme!
# ================================================================

import pandas as pd
import pymysql
import logging
import sshtunnel
from sshtunnel import SSHTunnelForwarder

# how this all works:
# first, we connect to the host maschine thought a tunnel that we have to establish
# that is done by the function open_ssh_tunnel(argument verbose is for debugging)
# then we connect to the database THROUGH the tunnel
# that is done by the function mysql_connect
# then we need to run the query with run_query(argument sql is a string for the query)
# and in the end we close connection and the tunnel

# THE BEST WAY TO USE THIS FILE
# implement this file in your python script by using from mysqlwithtunnel import conAndQuery
# that way, the function can be called and the script will handle the rest

# ssh information for the tunnel that we have to open first

# database information, including the name and the localhost address

database_name = 'optilima'
localhost = '127.0.0.1'
connection = None
query_done = False
result = []
query_time = None
first_round = True
# this function opens the tunnel, verbose enables debugging


def open_ssh_tunnel(ssh_host, ssh_username, ssh_password, verbose=False):
    if verbose:
        sshtunnel.DEFAULT_LOGLEVEL = logging.DEBUG

    global tunnel
    # the tunnel, including the maschine host as 2211, username and password
    tunnel = SSHTunnelForwarder(
        (ssh_host, 2211),
        ssh_username=ssh_username,
        ssh_password=ssh_password,
        # the port on the maschine at optilima.wolution.com runs on 3306
        remote_bind_address=('127.0.0.1', 3306)
    )
    # returns the tunnel
    return tunnel


def mysql_connect(database_username, database_password):
    # after establishing the tunnel, we need to connect to the database
    # the problem is, that is done on a RANDOM port on the localmaschine (or in the python commandline)
    connection = pymysql.connect(
        host='127.0.0.1',
        user=database_username,
        passwd=database_password,
        db=database_name,
        # this is the dynamically chosen port by the script, this doenst have to be 8080 like in the browser
        port=tunnel.local_bind_port)
    return connection


def run_query(sql, connection):
    # run a query
    return pd.read_sql_query(sql, connection)


def disconnect(connection):
    connection.close()
    tunnel.close
