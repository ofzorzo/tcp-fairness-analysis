import pandas as pd
import os
import argparse
import copy
import const
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt 

def join_dataframes(dataframes):
	dataframescpy = copy.deepcopy(dataframes)
	df = dataframescpy[0]
	del dataframescpy[0]
	for d in dataframescpy:
		df = df.append(d)
	df.reset_index(drop=True, inplace=True)
	return df

def files_to_dataframes(files):
	dataframes = []
	for f in files:
		df = pd.read_csv(f)
		dataframes.append(df)
	return dataframes

def get_time_points(conns):
	joined = join_dataframes(conns)
	joined = joined.sort_values("Time")
	return joined["Time"].tolist()

def get_relative_time_points(conns):
	time = get_time_points(conns)
	base_time = time[0]
	time = [round((t-base_time), 2) for t in time]
	time = list(dict.fromkeys(time)) # removes duplicates from time
	return time, base_time

def interpolate_connections(x, base_time, conns):
	lines = []
	zero_padding_before = []
	zero_padding_after = []
	for c in conns:
		time = c["Time"].tolist()
		time = [round((t-base_time), 2) for t in time]	
		mbytes = c["MBytes/s"].tolist()
		mbytes = [round(mb, 4) for mb in mbytes]
		zeros = 0
		for t in x:
			if t < time[0]:
				zeros += 1
		zero_padding_before.append(zeros)
		zeros = 0
		max_time = time[-1]
		for t in x:
			if max_time < t:
				zeros += 1
		zero_padding_after.append(zeros)
		lines.append([time, mbytes])
	interpolated_lines = []
	for i in range(0, len(lines)):
		interp = np.interp(x, lines[i][0], lines[i][1])
		for j in range(0, zero_padding_before[i]):
			interp[j] = 0
		for j in range(0, zero_padding_after[i]):
			interp[-1-j] = 0
		interpolated_lines.append(interp)
	return interpolated_lines

def total_connection(interps):
	total = []
	for x in interps[0]: # number of different values for the x-axis
		total.append(0)
	for i in interps:
		for j in range(0, len(i)):
			total[j] += i[j]
	return total

def plot_connections(times, conns, total):
	fig = plt.figure()
	index = 0
	for c in conns:
		plt.plot(times, c, label = "Con "+str(index))
		index += 1
	plt.plot(times, total, label = "Total")
	plt.ylabel('Transmission rate (MBytes/s)')
	plt.xlabel('Time (seconds)')
	plt.legend()
	plt.show()
	return fig

def organize_comparison(files, fig):
	curr_time = datetime.now()
	curr_time = "\\comparisons\\" + curr_time.strftime("%d-%m-%Y_%H-%M-%S")
	target_folder = os.getcwd() + curr_time
	os.mkdir(target_folder)
	for file in files:
		os.replace(file, target_folder+"\\"+file)
	fig.savefig(target_folder+"\\tcp_fairness.png")	

def parse_params():    
	parser = argparse.ArgumentParser(description="Joiner for logs of different Client-Server connections.")
	parser.add_argument('-f', '--files', nargs='+', type=str, required=True, help="CSV's to be joined.")
	args = parser.parse_args()
	return args.files

if __name__ == "__main__":
	files = parse_params()
	connections = files_to_dataframes(files)	
	times, base_time = get_relative_time_points(connections)
	interps = interpolate_connections(times, base_time, connections)
	total = total_connection(interps)
	fig = plot_connections(times, interps, total)
	organize_comparison(files, fig)