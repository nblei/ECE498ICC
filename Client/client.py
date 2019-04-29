import json
import re
import os
from sys import argv
import requests
import matplotlib.pyplot as plt
import time

UPPER=100
LOWER=50
TIMEOUT=1.0

fake_data = {"Table1" : [None, None, {"name":"patch1", "value":73}, {"name":"patch2", "value":121}, None, None, None, None ],
 			 "Table2" : [None, {"name":"rasp1","value":17,}, None, {"name":"rasp2", "value":55}, None, None, None, None]}

def get_sensor_data_dict(host):
	url = "{host}/data".format(host=host)
	print("POST on ", url)
	try:
		response = requests.get(url, timeout=TIMEOUT)
	except requests.exceptions.Timeout:
		print("POST to {url} timedout".format(url=url))
		exit(1)

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

def graph_data(data_dict, fig, ax):
	assert(data_dict is not None)
	ngraphs = len(data_dict)
	rnames = []
	rdata = []
	rcolors = []
	for name, data in data_dict.items():
		for datum in data:
			if datum is None:
				continue
			pname = "{n}.{d}".format(n=name,d=datum['name'])
			rnames.append(pname)
			rdata.append(datum['value'] / 255.0)
			rcolors.append(get_color(datum['value']))
			#nvpairs.append([pname, datum['value'] / 255.0, get_color(datum['value'])])

	print(rnames)
	print(rdata)
	print(rcolors)

	if (fig is None or ax is None):
		fig, ax = plt.subplots()

	locations = [x+1 for x in range(len(rdata))]
	plt_list = plt.bar(locations, rdata)
	for idx, artist in enumerate(plt_list):
		artist.set_facecolor(rcolors[idx])

	ax.set_xticks(locations)
	ax.set_xticklabels(rnames)
	ax.set_ylabel('Moisture Level')
	ax.set_title('Moisture Monitor')
	plt.pause(5)
	print("Done")
	return fig, ax



if __name__ == "__main__":
	input = ""
	if len(argv) != 2:
		print("usage: {file} <http server>".format(file=argv[0]))
		input = "172.16.182.16"
		exit(1)
	else:
		input = argv[1]
	host = "http://{ip}:1880".format(ip=input)
	print("Host: ", host)
	fig = None
	ax = None
	while True:
		print("Graphing")
		#data = get_sensor_data_dict(host)
		#fig, ax = graph_data(data, fig, ax)
		fig, ax = graph_data(fake_data, fig, ax)
		fake_data['Table1'][2]['value'] += 10
		fake_data['Table1'][2]['value'] %= 255
