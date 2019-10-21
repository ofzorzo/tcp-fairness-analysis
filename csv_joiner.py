import pandas as pd
import os
import argparse
from datetime import datetime

def organize_comparison(joined, files):
    curr_time = datetime.now()
    curr_time = "\\comparisons\\" + curr_time.strftime("%d-%m-%Y_%H-%M-%S")
    target_folder = os.getcwd() + curr_time
    os.mkdir(target_folder)
    for file in files:
        os.replace(file, target_folder+"\\"+file)
    joined.to_csv(target_folder+"\\comparison.csv", index=False)

def join_csvs(files):
    df = pd.read_csv(files[0])
    for i in range(1, len(files)):
        next_df = pd.read_csv(files[i])
        df = df.append(next_df)
    df = df.sort_values('Time')
    df.reset_index(drop=True, inplace=True)
    return df

def parse_params():    
	parser = argparse.ArgumentParser(description="Joiner for logs of different Client-Server connections.")
	parser.add_argument('-f', '--files', nargs='+', type=str, required=True, help="CSV's to be joined.")
	args = parser.parse_args()
	return args.files

if __name__ == "__main__":
    # files = ["client_127-0-0-1_14002.csv", "client_127-0-0-1_14003.csv"]
    files = parse_params()
    joined = join_csvs(files)
    organize_comparison(joined, files)