#!/usr/bin/python3 -O
import argparse
import subprocess
from os.path import exists
from time import perf_counter

sql_sqlcmd: str = "/opt/mssql-tools/bin/sqlcmd"

if __debug__:
    print("DEBUG: debug is", __debug__)

parser = argparse.ArgumentParser(description="Collect variables")
parser.add_argument('-w','--warn', type=float, help="Warning Threshold", required=True)
parser.add_argument('-c','--crit', type=float, help="Critical Threshold", required=True)
parser.add_argument('-d','--debug', help="Debug mode", action='store_true', required=False)
parser.add_argument('-H','--hostname', type=str, help="IP Address/Hostname",required=True)
parser.add_argument('-u','--username', type=str, help="username", required=True)
parser.add_argument('-p','--password', type=str, help="Password", required=True)
parser.add_argument('-q','--querypath',type=str,help='path to query file', required=True)

args = parser.parse_args()

if args.warn > args.crit:
    print("CRITICAL: warning level must be less than critical level")
    exit(2)
if __debug__:
    print("DEBUG: now outside the validate segment")

if __debug__:
    print("DEBUG: MAIN: In the main body.")
    print("==Parameters============================")
    print("========================================"\
            "\nDEBUG: MAIN: args: ",
            "\nDEBUG: Warn: ", args.warn,
            "\nDEBUG: Crit: ", args.crit,
            "\nDEBUG: SQLIp:", args.hostname,
            "\nDEBUG: SQLUser:", args.username,
            "\nDEBUG: SQLPass:", args.password,
            "\nDEBUG: SQLQuery:", args.querypath,
            "\nDEBUG: SQLPath:", sql_sqlcmd,
            "\n========================================"

            )
######################################### MAIN #############################################


sqlcmd_exists = exists(sql_sqlcmd)
if __debug__: print("DEBUG: MAIN: SQL Exists? ", sqlcmd_exists)
if (sqlcmd_exists != True):
    print("CRITICAL: sqlcmd not found! check -s parameter. current:", sql_sqlcmd, "-- Now exiting.")
    exit(1)

sqlquery_exists = exists(args.querypath)
if __debug__: print("DEBUG: MAIN: Query exists? ", sqlquery_exists)
if (sqlquery_exists != True):
    print("CRITICAL: sql query not fund! check -q parameter. current: ", args.querypath, "--- Now exiting.")
    exit(1)


tic = perf_counter()

if __debug__:
    print("DEBUG: MAIN: Running query")
sql = subprocess.call(
    [
        sql_sqlcmd,
        "-S",args.hostname,
        "-U",args.username,
        "-P",args.password,
        "-i",args.querypath
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
if (sql == 1):
    print("CRITICAL: Return code from subcommand:",sql)
    exit(sql)
else:

# Time Calculation
    toc = perf_counter()

    clock = toc - tic
    if __debug__:
        print("DEBUG: MAIN: clock is", clock)

    if clock > args.crit:
        print("CRITICAL: SQL Query Response Time:", clock, "|response_time=%f" % (clock))
        exit(2)

    elif clock > args.warn:
        print("WARN: SQL Query Response Time:", clock, "|response_time=%f" % (clock))
        exit(1)
    else:
        print("OK: SQL Query Response Time;", clock, "|response_time=%f" % (clock))
        exit(0)
