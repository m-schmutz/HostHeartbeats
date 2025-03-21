#!./env/bin/python3
from datetime import datetime, timezone, timedelta
from signal import signal, SIGTSTP
from json import load, dump
from subprocess import run
from time import sleep

# data paths
HOSTS = 'data/hosts.json'
LAST = 'data/last.json'
WEB_DATA = 'web/status.json'

# signal handler for immediate update of data
def immediate_update(sig, frame):
    log('Running Prompted Check-in')
    full_update()
    log('Prompted Check-in complete')


# register the signal handler
signal(SIGTSTP, immediate_update)


# get current timestamp and convert to ctime format
def timestamp() -> str:
    ts = datetime.now()
    pst = timezone(timedelta(hours=-8))
    return ts.astimezone(pst).ctime()


# read in hosts.json and return dict
def read_hosts() -> dict:
    with open(HOSTS, 'r') as f:
        hosts = load(f)
        return hosts


# read last.json and return dict
def read_last() -> dict:
    with open(LAST, 'r') as f:
        last = load(f)
        return last
    

# write dict to last.json
def write_last(new:dict):
    with open(LAST, 'w') as f:
        dump(new, f)


# write dict to status.json
def write_status(new:dict):
    with open(WEB_DATA, 'w') as f:
        dump(new, f)


# check if new hosts have been added to hosts.json
def check_new() -> tuple[dict, dict]:
    # get hosts and last check-ins
    hosts = read_hosts()
    last = read_last()

    # add host to checkin data if it does not exist
    for hostname in hosts.keys():
        if hostname not in last:
            last[hostname] = 'N/A'

    # return both dictionaries
    return hosts, last


# ping host and return data
def ping_host(ip:str) -> tuple[int, str, str]:
    # get timestamp
    ts = timestamp()

    # ping host (send 5 pings or stop after 10 seconds)
    result = run(['ping', '-q', '-c', '5', '-w', '10', ip], capture_output=True, text=True)

    # get the 4th line from output containing packet data
    data = result.stdout.splitlines()[3]

    # get package loss percentage and time 
    p, t = data.split(',')[-2:]

    # get just the percentage
    p = p[1:p.index('%') + 1]

    # convert time from ms to s
    t = f'{int(t[6:-2]) / 1000} seconds'

    # return the return value, packet loss and time taken
    return (not result.returncode, p, t, ts)


# check in with each host and store test stats
def checkin(hosts) -> dict[str, tuple]:
    # checkin with each host and store stats
    return {hostname: ping_host(ip) for hostname, ip in hosts.items()}


# update the last time that each host checked in
def update_last(cdata:dict, last:dict) -> dict:
    # get the previous check-ins
    last = read_last()

    # loop through each hostname
    for hostname, data in cdata.items():
        # update checkin time if ping was successful
        if data[0]:
            last[hostname] = data[3]

    # update last check-in data
    write_last(last)

    # return the checkin data
    return last


# update the web json
def update_status(cdata:dict, last:dict):
    # start with empty dictionary
    status = list()

    # loop through all hosts
    for hostname, data in cdata.items():
        # extract elements from data
        reachable, percent, elapsed, ts = data

        # define data for this host
        status.append({"hostname": hostname, "reachable": reachable, "lastCheckin": ts, "packetLoss": percent, "timeElapsed": elapsed, "lastReachable": last[hostname]})

    # update the web json
    write_status(status)


# run checkin and update of web json
def full_update():
    # check if new hosts have been added
    hosts, last = check_new()

    # get checkin data
    cdata = checkin(hosts)

    # update last dictionary and write to file
    last = update_last(cdata, last)

    # update web json
    update_status(cdata, last)


# log actions done by the script
def log(msg:str) -> None:
    print(f'\t[{timestamp()}] - {msg}')


# main function
if __name__ == '__main__':  
    # loop until interrupted
    try:
        while True:
            # run check in every 2 hours
            log('Running 2 hr Check-in')
            full_update()
            log('2 hr Check-in complete')
            sleep(7200)

    # exit
    except KeyboardInterrupt:
        exit(0)
