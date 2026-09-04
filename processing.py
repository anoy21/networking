import re
import os
import pandas as pd
import numpy as np
from glob import glob

def process_traceroute_file(file_path, time_of_day):
    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
        lines = file.readlines()
        
    hop_rtts = []
    timeout_count = 0
    hop_count = 0
    is_trace_section = False
    
    for line in lines:
        if "=== TRACEROUTE FEATURES ===" in line:
            is_trace_section = True
            continue 
            
        if not is_trace_section or line.strip() == "":
            continue 
            
        # Updated Regex: Handles Windows tracert format (e.g., "5 ms" or "<1 ms")
        raw_times = re.findall(r'(?:<)?\s*(\d+)\s+ms', line)
        times = [float(x) for x in raw_times]
        
        timeout_count += line.count('*')
        
        if times or '*' in line:
            hop_count += 1
            
        if times:
            hop_rtts.append(np.mean(times))
            
    if len(hop_rtts) > 1:
        target_rtt = hop_rtts.pop() 
    else:
        return None
        
    return {
        "hop_count": hop_count,
        "timeout_count": timeout_count,
        "mean_intermediate_RTT": np.mean(hop_rtts),
        "max_intermediate_RTT": np.max(hop_rtts),
        "variation": np.std(hop_rtts),
        "time_of_day": time_of_day,
        "target_RTT": target_rtt
    }


data_records = []

all_files = glob("raw_data/*.txt")
recent_files = sorted(all_files, key=os.path.getmtime, reverse=True)

for file_path in recent_files:
    filename = os.path.basename(file_path)
    
    try:
        time_str = filename.split('_')[-1].replace('.txt', '')
        hour = int(time_str[:2]) 
        
        # 24H format
        if 18 <= hour <= 21:
            time_of_day = "peak"
        elif 1 <= hour <= 5:
            time_of_day = "offpeak"
        else:
            time_of_day = "business"
            
        parsed_data = process_traceroute_file(file_path, time_of_day)
        if parsed_data:
            data_records.append(parsed_data)
            
    except Exception as e:
        print(f"Skipping {filename} due to parsing error: {e}")

df = pd.DataFrame(data_records)
print(df.head(12))
df.to_csv("final_network_data.csv", index=False)