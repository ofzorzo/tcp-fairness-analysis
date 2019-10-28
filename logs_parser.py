import pandas as pd
import os
import argparse
import const
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt 

def divide_in_intervals(joined):
	first_row = joined.head(1)
	last_row = joined.tail(1)
	minimum = joined["Time"].min() # seleciona valor mínimo de tempo
	maximum = joined["Time"].max() # seleciona valor máximo de tempo
	merge_interval = pd.DataFrame(columns=list(joined))

	while minimum <= maximum:
		interval = joined[(joined["Time"] >= minimum) & (joined["Time"] < minimum+const.INTERVAL)] # seleciona linhas de um dado intervalo
		if interval.empty == False:
			time = interval["Time"].min()
			mbytes = interval["MBytes/s"].sum()
			bits = interval["bits/s"].sum()
			summary = pd.DataFrame([[time, bits, mbytes]], columns=list(joined))
			merge_interval = merge_interval.append([summary], ignore_index=True)
		minimum += const.INTERVAL

	last_row2 = merge_interval.tail(1)
	last_row2.reset_index(drop=True, inplace=True)
	last_row.reset_index(drop=True, inplace=True)
	if last_row.equals(last_row2) == False:
		merge_interval = merge_interval.append([last_row], ignore_index=True)
	
	return merge_interval

def join_csvs(files):
	df = pd.read_csv(files[0])
	for i in range(1, len(files)):
		next_df = pd.read_csv(files[i])
		df = df.append(next_df)
	df = df.sort_values('Time')
	df.reset_index(drop=True, inplace=True)
	return df

def plot_dataframes(dataframes):
	index = 0
	base_time = dataframes[0]["Time"].tolist()[0]
	max_time = dataframes[0]["Time"].tolist()[-1] - base_time + const.INTERVAL
	for dt in dataframes:
		time = dt["Time"].tolist()
		time = [round((t-base_time), 2) for t in time]	
		mbytes = dt["MBytes/s"].tolist()
		mbytes = [round(mb, 4) for mb in mbytes]
		if index == 0:
			plt.plot(time, mbytes, label = "Total")
		else:
			plt.plot(time, mbytes, label = "Con "+str(index))
		index += 1

	plt.ylabel('Transmission rate (MBytes/s)')
	plt.xlabel('Time (seconds)')
	plt.legend()
	plt.show()

# def files_to_dataframes(files):
# 	None

def interpolate_dataframes(dataframes):
	index = 0
	base_time = dataframes[0]["Time"].tolist()[0]
	max_time = dataframes[0]["Time"].tolist()[-1] - base_time + const.INTERVAL
	x = [round((t-base_time), 2) for t in dataframes[0]["Time"].tolist()]
	# print(x)
	del dataframes[0]
	lines = []
	zero_padding_before = []
	zero_padding_after = []
	for dt in dataframes:
		time = dt["Time"].tolist()
		time = [round((t-base_time), 2) for t in time]	
		mbytes = dt["MBytes/s"].tolist()
		mbytes = [round(mb, 4) for mb in mbytes]
		zeros = 0
		for t in x:
			if t < time[0]:
				zeros += 1
			else:
				break
		zero_padding_before.append(zeros)
		zeros = 0
		max_time = time[-1]
		for t in x:
			if max_time < t:
				zeros += 1
		zero_padding_after.append(zeros)
		lines.append([time, mbytes])
	total = []
	for i in x:
		total.append(0)
	for i in range(0, len(lines)):
		interp = np.interp(x, lines[i][0], lines[i][1])
		for j in range(0, zero_padding_before[i]):
			interp[j] = 0
		for j in range(0, zero_padding_after[i]):
			interp[-1-j] = 0
		for j in range(0, len(interp)):
			total[j] += interp[j]
		plt.plot(x, interp, label = "Con "+str(index))
		index += 1
	plt.plot(x, total, label = "Total")
	plt.ylabel('Transmission rate (MBytes/s)')
	plt.xlabel('Time (seconds)')
	plt.legend()
	plt.show()

def organize_comparison(joined, files):
	curr_time = datetime.now()
	curr_time = "\\comparisons\\" + curr_time.strftime("%d-%m-%Y_%H-%M-%S")
	target_folder = os.getcwd() + curr_time
	os.mkdir(target_folder)
	for file in files:
		os.replace(file, target_folder+"\\"+file)
	joined.to_csv(target_folder+"\\comparison.csv", index=False)

def parse_params():    
	parser = argparse.ArgumentParser(description="Joiner for logs of different Client-Server connections.")
	parser.add_argument('-f', '--files', nargs='+', type=str, required=True, help="CSV's to be joined.")
	args = parser.parse_args()
	return args.files

if __name__ == "__main__":
	files = parse_params()
	joined = join_csvs(files)
	joined = divide_in_intervals(joined)
	dataframes = []
	dataframes.append(joined)
	for i in range(0, len(files)):
		new_df = pd.read_csv(files[i])
		dataframes.append(new_df)
	organize_comparison(joined, files)
	# plot_dataframes(dataframes)
	interpolate_dataframes(dataframes)