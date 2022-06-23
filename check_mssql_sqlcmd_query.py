#!/usr/bin/python3 -O

import os
import getopt
import psutil
import sys
import subprocess
import time
from os.path import exists

sql_sqlcmd: str = "/opt/mssql-tools/bin/sqlcmd"

if __debug__:
    print("DEBUG: debug is", __debug__)
usage = "sqlcmd_path defaults to /opt/mssql-tools/bin/mssql.  Edit parameter in script to change.\n\n" \
        "usage: ./check_sqlcmd\n" \
        "-w|--warn num\t\t\t\t" \
        "-c|--crit num\t\t " \
        "-H|--hostname\n" \
        "-q|--query /path/queryfile.sql\t  "\
        "\t-u|--user username\t " \
        "-p|--password yourPassword\n\n"\
        "ex: ./check_sqlcmd -H 172.168.12.14 -w 10 -c 20 -q /usr/lib/nagios/plugins/perfquery.sql\n"\
        "-u myuser  -p msssqlpass\n\n"\
        "All parameters are required.\n"


def command_line_validate(argv):

    try:
        if __debug__: print("DEBUG: CLV: argv is",argv)
        opts, args = getopt.getopt(
                argv, "w:c:i::H::u::p::q::h::",
                ['warn=', 'crit=', 'ip', 'hostname=', 'user=','password=','query=','sqlcmd=','help'])
        if __debug__: print("opts:", opts,"\nargs:",args)
    except getopt.GetoptError:
        print(usage)
        exit(1)
    try:
        for opt, arg in opts:
            if opt in ("-w", "--warn"):
                try:
                    try:
                        warn = int(arg)
                        if __debug__: print("DEBUG: VALIDATE: warn int: ", warn)
                    except:
                        warn = float(arg)
                        if __debug__: print("DEBUG: VALIDATE: warn FLOAT: ", warn)
                except:
                    print("Warn value must be an int")
                    exit(2)
            elif opt in ("-c", "--crit"):
                try:
                    try:
                        crit = int(arg)
                        if __debug__: print("DEBUG: VALIDATE: crit int: ", crit)
                    except:
                        crit = float(arg)
                        if __debug__: print("DEBUG: VALIDATE: crit FLOAT: ", crit)
                except:
                    print("crit value must be an int")
                    exit(2)

            # Evaluate IP
            elif opt in ("-i", "--ip", "-H", "--hostname"):
                try:
                    sql_ip = arg
                    if __debug__:
                        print("DEBUG: IP: try got: ", sql_ip, "arg: ", arg)
                except:
                    print("SQL IP must be string")
                    print( "DEBUG: IP: recieved:", sql_ip, "you are in the except clause predebug")
                    if __debug__:
                        print(sql_ip, "you are in the except clause of eval ip")
                    exit(2)

            # evaluate user
            elif opt in ("-u", "--user"):
                try:
                    sql_user = arg
                    if __debug__:
                        print("DEBUG: USER: try got: ", sql_user, "arg: ", arg)
                except:
                    print("Username must be string")
                    if __debug__:    print( "DEBUG: USER: EXCEPT: recieved:", sql_user, "you are in the except clause predebug",)
                    exit(2)

            # evaluate password
            elif opt in ("-p", "--password"):
                try:
                    sql_password = arg
                    if __debug__:
                        print("DEBUG: PASSWORD: try got: ", sql_password, "arg: ", arg)
                except:
                    print("Password must be string")
                    if __debug__:    print( "DEBUG: PASSWORD: EXCEPT: recieved:", sql_password, "you are in the except clause predebug",)
                    exit(2)

            # evaluate queryfile
            elif opt in ("-q", "--query"):
                try:
                    sql_querypath = arg
                    if __debug__:
                        print("DEBUG: QUERYPATH: try got: ", sql_querypath, "arg: ", arg)
                except:
                    print("Query path must be string")
                    if __debug__:    print( "DEBUG: QUERYPATH: EXCEPT: recieved:", sql_querypath, "you are in the except clause predebug",)
                    exit(2)

            # print usage on help/?
            elif opt in ("-h", "--help"):
                    if __debug__: print ("DEBUG: USAGE: In usage block")
                    print(usage)
                    exit(2)
            #
        # Switches null validation

            else:
                print(usage)
                exit(2)
        try:
            isinstance(warn, int)
            if __debug__: print('DEBUG: VALIDATE: inner warn level:', warn)
        except:
            print("CRITICAL: warn level is required", warn)
            print(usage)
            exit(2)
        try:
            isinstance(crit, int)
            if __debug__: print("DEBUG: VALIDATE: inner crit level: ", crit)
        except:
            print("CRITICAL: crit level is required")
        try:
            isinstance(warn, int)
        except:
            print("CRITICAL: warn level is required")
            exit(2)
        try:
            isinstance(crit, int)
        except:
            print("CRITICAL: crit level is required")
            exit(2)
        try:
            isinstance(sql_ip, str)
        except:
            print("CRITICAL: sql_ip required")
            exit(2)
        try:
            isinstance(sql_querypath, str)
        except:
            print("CRITICAL: sql_querypath required")
            exit(2)
        try:
            isinstance(sql_user, str)
        except:
            print("CRITICAL: sql_user required")
            exit(2)
        try:
            isinstance(sql_password, str)
        except:
            print("CRITICAL: sql_password required")
            exit(2)
    except:
        exit(2)
    # confirm that warning level is less than critical level, alert and exit if check fails
    if warn > crit:
        print("CRITICAL: warning level must be less than critical level")
        exit(2)
    if __debug__:
        print("DEBUG: now outside the validate segment")
    return warn, crit, sql_ip, sql_user, sql_password, sql_querypath, sql_sqlcmd

if __debug__: print("DEBUG: MAIN: now in MAIN")
# def main():
argv = sys.argv[1:]
if __debug__: print("DEBUG: MAIN: now sys.argv[1:]", sys.argv[1:])

warn, crit, sql_ip, sql_user, sql_password, sql_querypath, sql_sqlcmd  = command_line_validate(argv)

if __debug__:
    print("DEBUG: MAIN: In the main body.")
    print("==Parameters============================")
    print("========================================"\
            "\nDEBUG: MAIN: args: ",
            "\nDEBUG: Warn: ", warn,
            "\nDEBUG: Crit: ", crit,
            "\nDEBUG: SQLIp:", sql_ip,
            "\nDEBUG: SQLUser:", sql_user,
            "\nDEBUG: SQLPass:", sql_password,
            "\nDEBUG: SQLQuery:", sql_querypath,
            "\nDEBUG: SQLPath:", sql_sqlcmd,
            "\n========================================"

            )
######################################### MAIN #############################################


sqlcmd_exists = exists(sql_sqlcmd)
if __debug__: print("DEBUG: MAIN: SQL Exists? ", sqlcmd_exists)
if (sqlcmd_exists != True):
    print("CRITICAL: sqlcmd not found! check -s parameter. current:", sql_sqlcmd, "-- Now exiting.")
    exit(1)

sqlquery_exists = exists(sql_querypath)
if __debug__: print("DEBUG: MAIN: Query exists? ", sqlquery_exists)
if (sqlquery_exists != True):
    print("CRITICAL: sql query not fund! check -q parameter. current: ", sql_querypath, "--- Now exiting.")
    exit(1)


tic = time.perf_counter()

# Prototype Query
# subprocess.call(["/opt/mssql-tools/bin/sqlcmd","-S 45.58.43.142","-U",sql_user, "-P","password", "-q", "exit(SELECT @@VERSION;)"], \
# )
# Short Query
if __debug__:
    print("DEBUG: MAIN: Running query")
sql = subprocess.call(
    [
        "/opt/mssql-tools/bin/sqlcmd",
        "-S",sql_ip,
        "-U",sql_user,
        "-P",sql_password,
        "-i",sql_querypath
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
if (sql == 1):
    print("CRITICAL: Return code from subcommand:",sql)
    exit(sql)
else:

# Time Calculation
    toc = time.perf_counter()

    clock = toc - tic
    if __debug__:
        print("DEBUG: MAIN: clock is", clock)

    if clock > crit:
        print("CRITICAL: SQL Query Response Time:", clock, "|response_time=%f" % (clock))
        exit(2)

    elif clock > warn:
        print("WARN: SQL Query Response Time:", clock, "|response_time=%f" % (clock))
        exit(1)
    else:
        print("OK: SQL Query Response Time;", clock, "|response_time=%f" % (clock))
        exit(0)
