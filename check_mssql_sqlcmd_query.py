#!/usr/bin/python3 -O
# check_mssql_sqlcmd_query 0.5.0 internal testing build
# Daniel Tate 2022 - Initial Release June 2022
# Uses native mcirosoft sqlcmd client to connect to sql server, execute a query, and get the approx time of execution.
# You must have the client installed and referenced in the sql_sqlcmd parameter below
# As of June 2022 the client is available at https://docs.microsoft.com/en-us/sql/linux/sql-server-linux-setup-tools


import argparse
import subprocess
from os.path import exists
from time import perf_counter

sql_sqlcmd = "/opt/mssql-tools/bin/sqlcmd"

if __debug__:
    print("DEBUG: debug is", __debug__)

parser = argparse.ArgumentParser(description="warn/crit time can be in 0 or 0.00 format, i.e -w 1.32 -c 60")
parser.add_argument('-d','--debug', help="Debug mode", action='store_true', required=False)
parser.add_argument('-H','--hostname', type=str, help="IP Address/Hostname",metavar='1.2.3.4',required=True)
parser.add_argument('-w','--warn', type=float,help="Warning Threshold",metavar='warn', required=True)
parser.add_argument('-c','--crit', type=float, help="Critical Threshold",metavar='crit', required=True)
parser.add_argument('-u','--username', type=str, help="SQL Username",metavar='username', required=True)
parser.add_argument('-p','--password', type=str, help="SQL Password",metavar='pass', required=True)
parser.add_argument('-q','--querypath',type=str,help='path to query file',metavar='path', required=True)
metavar='\b',
args = parser.parse_args()

if args.warn > args.crit:
    print("CRITICAL: warning level must be less than critical level")
    exit(2)
if __debug__ or args.debug:
    print("DEBUG: now outside the validate segment")

if __debug__ or args.debug:
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
if __debug__ or args.debug: print("DEBUG: MAIN: SQL Exists? ", sqlcmd_exists)
if (sqlcmd_exists != True):
    print("CRITICAL: sqlcmd not found! check -s parameter. current:", sql_sqlcmd, "-- Now exiting.")
    exit(1)

sqlquery_exists = exists(args.querypath)
if __debug__ or args.debug: print("DEBUG: MAIN: Query exists? ", sqlquery_exists)
if (sqlquery_exists != True):
    print("CRITICAL: sql query not fund! check -q parameter. current: ", args.querypath, "--- Now exiting.")
    exit(1)


tick = perf_counter()

if __debug__ or args.debug:
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
    tock = perf_counter()

    if __debug__ or args.debug: print(f"DEBUG: FINAL: tick: {tick} \nDEBUG: FINAL: tock: {tock}" )

    clock = tock - tick
    if __debug__ or args.debug:
        print("DEBUG: FINAL: clock: ", clock)

    if clock > args.crit:
        print("CRITICAL: SQL Query Response Time:", clock, "|response_time=%f" % (clock))
        exit(2)

    elif clock > args.warn:
        print("WARN: SQL Query Response Time:", clock, "|response_time=%f" % (clock))
        exit(1)
    else:
        print("OK: SQL Query Response Time;", clock, "|response_time=%f" % (clock))
        exit(0)
