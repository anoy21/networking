"""LƯU Ý: script dùng riêng cho hệ điều hành Windows"""
import subprocess
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

if not os.path.exists("raw_data"):
    os.makedirs("raw_data")

def get_network_commands(ip):
    return ["ping", "-n", "5", ip], ["tracert", "-d", "-h", "30", "-w", "1000" ip]

def measure_network(ip):
    ping_cmd, trace_cmd = get_network_commands(ip)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        ping_result = subprocess.run(ping_cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=20)
        trace_result = subprocess.run(trace_cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
        
        filename = f"raw_data/{ip}_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("=== PING TARGET ===\n")
            f.write(ping_result.stdout)
            f.write("\n=== TRACEROUTE FEATURES ===\n")
            f.write(trace_result.stdout)
            
        print(f"[+] Hoàn thành đo lường: {ip}")
    except subprocess.TimeoutExpired:
        print(f"[-] Bỏ qua do Timeout: {ip}")
    except Exception as e:
        print(f"[-] Lỗi hệ thống tại {ip}: {e}")

def run_schedule():
    with open("targets.txt", "r", encoding="utf-8") as file:
        ips = [line.strip() for line in file if line.strip() and not line.startswith("#")]
    
    print(f"\n--- Bắt đầu vòng đo lúc: {datetime.now().strftime('%H:%M:%S')} ---")
    print(f"Đã tải thành công {len(ips)} IP từ danh sách.")
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(measure_network, ips)
        
    print(f"--- Hoàn tất vòng đo. Máy đi ngủ chờ chu kỳ tiếp theo... ---\n")

while True:
    run_schedule()
    time.sleep(7200)
