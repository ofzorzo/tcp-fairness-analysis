import pandas as pd
import os
import argparse
import const
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
        time = interval["Time"].min()
        mbytes = interval["MBytes/s"].mean()
        bits = interval["bits/s"].mean()
        summary = pd.DataFrame([[time, bits, mbytes]], columns=list(joined))
        merge_interval = merge_interval.append([summary], ignore_index=True)
        minimum += const.INTERVAL

    last_row2 = merge_interval.tail(1)
    last_row2.reset_index(drop=True, inplace=True)
    last_row.reset_index(drop=True, inplace=True)
    if last_row.equals(last_row2) == False:
        merge_interval = merge_interval.append([last_row], ignore_index=True)
    
    return merge_interval

def organize_comparison(joined, files):
    curr_time = datetime.now()
    curr_time = "\\comparisons\\" + curr_time.strftime("%d-%m-%Y_%H-%M-%S")
    target_folder = os.getcwd() + curr_time
    os.mkdir(target_folder)
    for file in files:
        # os.replace(file, target_folder+"\\"+file)
        None
    joined.to_csv(target_folder+"\\comparison.csv", index=False)

def join_csvs(files):
    df = pd.read_csv(files[0])
    for i in range(1, len(files)):
        next_df = pd.read_csv(files[i])
        df = df.append(next_df)
    df = df.sort_values('Time')
    df.reset_index(drop=True, inplace=True)
    return df

def plot_csvs(dataframes):
	for dt in dataframes:
		time = dt["Time"].tolist()
		time = [round((t-time[0]), 2) for t in time]	
		mbytes = dt["MBytes/s"].tolist()
		mbytes = [round(mb, 2) for mb in mbytes]
		plt.plot(time, mbytes, label = "Con1")	
	plt.ylabel('Transmission rate (MBytes/s)')
	plt.xlabel('Time (seconds)')
	plt.legend()
	plt.show() 

# def parse_params():    
# 	parser = argparse.ArgumentParser(description="Joiner for logs of different Client-Server connections.")
# 	parser.add_argument('-f', '--files', nargs='+', type=str, required=True, help="CSV's to be joined.")
# 	args = parser.parse_args()
# 	return args.files

if __name__ == "__main__":
	files = ["client_127-0-0-1_14002.csv", "client_127-0-0-1_14003.csv"]
	# files = parse_params()
	joined = join_csvs(files)
	joined = divide_in_intervals(joined)
	plot_csvs([joined])
    # organize_comparison(joined, files)