import datetime
import time
import subprocess
import json
import re
import os
from sys import argv
import requests

TIMEOUT = 1.0
MAX_SENSOR_COUNT = 8
INTERNAL_CFG = "./.sa.cfg"
CFG = "./sensor_array.cfg"
PUT = 0
POST = 1
CRUNNER = "/home/pi/testss/pig_run"


def file_to_pyobj(file):
    sa_name = ""
    s_names = [None for _ in range(MAX_SENSOR_COUNT)]
    cfg_data = {}
    try:
        with open(file, "r") as f:
            for line in f:
                line = line.strip()
                if (len(sa_name) == 0):
                    sa_name = line
                else:
                    m = re.search('([0-7]) (.*)', line)
                    idx = int(m.group(1))
                    assert(idx >= 0)
                    assert(idx <= 7)
                    s_names[idx] = m.group(2)
        cfg_data['name'] = sa_name
        cfg_data['sensors'] = s_names
    except FileNotFoundError:
        raise FileNotFoundError
    return cfg_data

def get_name(file):
    sa_name = ""
    with open(file, "r") as f:
        for line in f:
            line = line.strip()
            sa_name = line
            break
    return sa_name

def put_or_post(cfg_obj):
    try:
        hidden_obj = file_to_pyobj(INTERNAL_CFG)
    except FileNotFoundError:
        #  Need to make file, return POST
        os.system("cp {cfg} {icfg}".format(cfg=CFG, icfg=INTERNAL_CFG))
        print("created internal config file")
        return POST, None
    if hidden_obj == cfg_obj:
        print("No changes to configuration")
        return -1, None
    else:
        print("Changes to configuration detected")
        old_name = get_name(INTERNAL_CFG)
        print("Old name: ", old_name)
        os.system("cp {cfg} {icfg}".format(cfg=CFG, icfg=INTERNAL_CFG))
        return PUT, old_name

def post_sensor_array(cfg_obj, host):
    #post_test(cfg_obj, host)
    url = "{host}/sensorarray".format(host=host)
    print("POST on ", url)
    try:
        data = {'body' : cfg_obj}
        print("JSON:")
        print(json.dumps(data))
        response = requests.post(url, data=json.dumps(data))
    except requests.exceptions.Timeout:
        print("POST to {url} timedout".format(url=url))
        exit(1)

    if response:
        print("POST successful")
        print(response.content)
    else:
        print("response code {rc}.  Exiting.".format(rc=response.status_code))
        exit(1)


def put_sensor_array(cfg_obj, host, old_name):
    url = "{host}/sensorarray".format(host=host)
    print("PUT on ", url)
    try:
        data = {'body':cfg_obj, 'prev_name' : old_name}
        response = requests.put(url, data=json.dumps(data))
    except requests.exceptions.Timeout:
        print("PUT to {url} timedout".format(url=url))
        exit(1)

def post_test(cfg_obj, host):
    url = "{host}/test".format(host=host)
    print("POST on ", url)
    try:
        data = {'body' : cfg_obj}
        response = requests.post(url, data=json.dumps(data))
        print(response.content)
        print(response.status_code)
        exit(1)
    except requests.exceptions.Timeout:
        print("POST to {url} timedout".format(url=url))
        exit(1)
    

def get_config(cfile, host):
    cfg_obj = file_to_pyobj(cfile)
    req_type, old_name = put_or_post(cfg_obj)
    if req_type == POST:
        post_sensor_array(cfg_obj, host)
    elif req_type == PUT:
        put_sensor_array(cfg_obj, host, old_name)
    return cfg_obj

def time_test(host):
    url = "http://{host}:1880/time".format(host=host)
    response = requests.get(url, timeout=TIMEOUT)
    print(response)
    print(response.content)


def run(cfg, host):
    runlist = [CRUNNER]
    for idx in range(len(cfg['sensors'])):
        if cfg['sensors'][idx] is not None:
            runlist.append("{n}".format(n=idx))
    data = {}
    data['name'] = cfg['name']
    data['sdata'] = cfg['sensors']
    data['time'] = None
    print(runlist)
    while True:
        #stdout_data = p.stdout.read()
        #if (stderr_data != None):
            #print("stderr: {str}".format(str=stderr_data))
            #exit(1)
        #print("stdout: {str}".format(str=stdout_data))
        p = subprocess.Popen(runlist, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                universal_newlines=True)
        (stdout_data, stderr_data) = p.communicate()
        if (stderr_data is not None):
            print("stderr: ", stderr_data)
            exit(1)

        print(stdout_data)
        for line in stdout_data.splitlines():
            line = line.strip()
            m = re.search('([0-7]):([0-9]+)', line)
            idx = int(m.group(1))
            val = int(m.group(2))
            data['sdata'][idx] = val
        
        data['time'] = str(datetime.datetime.now())

        
        url = "{host}/sensordata".format(host=host)
        print("POST on ", url)
        send_json = json.dumps({'body' : data})
        print("JSON: ", send_json)
        try:
            response = requests.post(url, send_json, timeout=TIMEOUT*5.0)
        except requests.exceptions.Timeout:
            print("POST to {url} timedout".format(url=url))
            exit(1)

        time.sleep(5)


if __name__ == "__main__":
    if len(argv) != 2:
        print("usage: {file} <http server>".format(file=argv[0]))
        exit(1)
    host = "http://{arg}:1880".format(arg=argv[1])
    cfg = get_config(CFG, host)
    #exit(0)
    run(cfg, host)

    #time_test(argv[1])

