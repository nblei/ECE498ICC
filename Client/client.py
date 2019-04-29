import json
import re
import os
from sys import argv
import requests
import matplotlib.pyplot as plt

UPPER=100
LOWER=50
TIMEOUT=1.0

fake_data = {"Table1" : {None, None, {"name":"patch1", "value":73}, {"name":"patch2", "value":121} } }

def get_sensor_data_dict(host):
	url = "{host}/data".format(host=host)
	print("POST on ", url)
	try:
		response = requests.get(url, timeout=TIMEOUT)
	except requests.exceptions.Timeout:
		print("POST to {url} timedout".format(url=url))

	if response:
		print("POST successful")
		print(response.content)
		pyresp = json.loads(response.content)
		return pyresp['data']
	else:
		print("POST unsuccesful")
		return None

def get_color(val_0_255):
	if val_0_255 < LOWER:
		return 'r'
	if val_0_255 > UPPER:
		return 'r'
	return 'g'

def graph_data(data_dict):
	assert(data_dict is not None)
	ngraphs = len(data_dict)
	nvpairs = {}
	for name, data in data_dict.items():
		for datum in data:
			if datum is None:
				continue
			nvpairs[name+datum['name']] = (datum['value'] / 255.0, get_color(datum['value']))

	print(nvpairs)




if __name__ == "__main__":
	if len(argv) != 2:
		print("usage: {file} <http server>".format(file=argv[0]))
		exit(1)

	host = "http://{ip}:1880".format(ip=argv[1])
	print("Host: ", host)
	graph_data(fake_data)


