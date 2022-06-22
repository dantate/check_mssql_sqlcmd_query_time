#!/usr/bin/python3

# Model Command: sqlcmd -S 45.58.43.142 -U sql_user -P "PW" -i sgmetric_query.sql

import os
import getopt
import psutil
import sys
import subprocess
import time

log_location = "/var/lib/portsentry"
SQLCMD: str = "/opt/mssql-tools/bin/sqlcmd"

if __debug__:
    print("DEBUG: debug is", __debug__)
usage = "usage: ./check_sqlcmd -w|--warn=num -c|--crit=num -i|--ip=ServerIP -q|--query=queryfile.sql -P|--Pathx sqlcmd_path [defaults to /opt/mssql-tools/bin/mssql] -u|--user=username -p|--password=yourPassword"

def command_line_validate(argv):

    try:
        opts, args = getopt.getopt(
                argv, "w:c:i::u::p::q::o:", ["warn=", "crit=", "ip=", "user","password","query"])
    except getopt.GetoptError:
        #print(usage)
        pass
    try:
        for opt, arg in opts:
            if opt in ("-w", "--warn"):
                try:
                    warn = int(arg)
                except:
                    print("Warn value must be an int")
                    exit(2)
            elif opt in ("-c", "--crit"):
                try:
                    crit = int(arg)
                except:
                    print("crit value must be an int")
                    exit(2)

            # Evaluate IP
            elif opt in ("-i", "--ip"):
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
                        print("DEBUG: USER: user try got: ", sql_user, "arg: ", arg)
                except:
                    print("Username must be string")
                    if __debug__:    print( "DEBUG: USER: EXCEPT: recieved:", sql_user, "you are in the except clause predebug",)
                    exit(2)

            # evaluate password
            elif opt in ("-p", "--password"):
                try:
                    sql_password = arg
                    if __debug__:
                        print("DEBUG: PASSWORD: user try got: ", sql_password, "arg: ", arg)
                except:
                    print("Password must be string")
                    if __debug__:    print( "DEBUG: PASSWORD: EXCEPT: recieved:", sql_password, "you are in the except clause predebug",)
                    exit(2)

            # evaluate queryfile
            elif opt in ("-q", "--query"):
                try:
                    sql_querypath = arg
                    if __debug__:
                        print("DEBUG: QUERYPATH: user try got: ", sql_querypath, "arg: ", arg)
                except:
                    print("Query path must be string")
                    if __debug__:    print( "DEBUG: QUERYPATH: EXCEPT: recieved:", sql_querypath, "you are in the except clause predebug",)
                    exit(2)



        # Switches null validation

            else:
                print(usage)
                exit(2)
                #pass
        try:
            isinstance(warn, int)
            # print('warn level:', warn
        except:
            print("warn level is required")
            #print(usage)
            exit(2)
        try:
            isinstance(crit, int)
        except:
            print("crit level is required")
        try:
            isinstance(warn, int)
            # print('warn level:', warn
        except:
            print("warn level is required")
            #print(usage)
            exit(2)
        try:
            isinstance(crit, int)
        except:
            print("crit level is required")
            #print(usage)
            exit(2)
    except:
        exit(2)
    # confirm that warning level is less than 2 level, alert and exit if check fails
    if warn > crit:
        print("warning level must be less than critical level***")
        exit(2)
    return warn, crit, sql_ip, sql_user, sql_password, sql_querypath


if __debug__:
    print("DEBUG: now outside the validate segment")

# def main():
argv = sys.argv[1:]
if __debug__: print("DEBUG: MAIN: now past sys.argv[1:]", sys.argv[1:])

warn, crit, sql_ip, sql_user, sql_password, sql_querypath  = command_line_validate(argv)

if __debug__:
    print("DEBUG: In the main body. Debug ON")
    print("========================================\
            \nDEBUG: MAIN: args: ",
            "\nDEBUG: Warn: ", warn,
            "\nDEBUG: Crit: ", crit,
            "\nDEBUG: SQLIp:", sql_ip,
            "\nDEBUG: SQLUser:", sql_user,
            "\nDEBUG: SQLPass:", sql_password,
            "\nDEBUG: SQLQuery:", sql_querypath\
            "\n========================================\
            )

# if __name__ == '__main__':
# main()

# def main():

tic = time.perf_counter()

# Prototype Query
# subprocess.call(["/opt/mssql-tools/bin/sqlcmd","-S 45.58.43.142","-U",sql_user, "-P","Nothingsoloudashearingwhenwelie", "-q", "exit(SELECT @@VERSION;)"], \
# )
# Short Query
if __debug__:
    print("DEBUG: Running short query")
sql = subprocess.call(
    [
        "/opt/mssql-tools/bin/sqlcmd",
        "-S",sql_ip,
        "-U",sql_user,
        "-P",sql_password,
        "-i",sql_querypath
    ]
)
if (sql == 1):
    print("CRITICAL: Return code from subcommand:",sql)
    exit(sql)

# Time Calculation
    toc = time.perf_counter()

    tock = toc - tic
    if __debug__:
        print("DEBUG: tock is", tock)
        print("DEBUG: sql_ip is", sql_ip)

    if tock > crit:
        print("CRITICAL: SQL Query Response Time:", tock, "|response_time=%f" % (tock))
        exit(2)

    elif tock > warn:
        print("WARN: SQL Query Response Time:", tock, "|response_time=%f" % (tock))
        exit(1)
    else:
        print("OK: SQL Query Response Time;", tock, "|response_time=%f" % (tock))
        exit(0)