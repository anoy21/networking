import re
import numpy as np
from glob import glob
import pandas as pd

def process_traceroute_file(file_path, time_of_day):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
    hop_rtts = []
    timeout_count = 0
    hop_count = 0
    
    # skip header
    for line in lines[1:]:
        if line.strip() == "":
            continue
            
        # lọc số, tách khỏi ms
        times = [float(x) for x in re.findall(r'([\d\.]+)\s+ms', line)]
        timeout_count += line.count('*')
        
        if times or '*' in line:
            hop_count += 1
            
        if times:
            # TB probe cho mỗi hop
            hop_rtts.append(np.mean(times))
            
    if len(hop_rtts) > 1:
        target_rtt = hop_rtts.pop() 
    else:
        return None # Discard failed traces that didn't reach the destination
        
    # các features
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
for file in glob("traceroute_data/*.txt"):
    if "morning" in file:
        time_of_day = "morning"
    elif "peak" in file:
        time_of_day = "peak"
    else:
        time_of_day = "evening"
    
    parsed_data = process_traceroute_file(file, time_of_day)
    if parsed_data:
        data_records.append(parsed_data)

# Generate final DataFrame ready for Linear Regression
df = pd.DataFrame(data_records)
print(df.head())