from flask import Flask, render_template
import os, time

app = Flask(__name__)

# ---------------- CPU Usage ----------------
def get_cpu_usage():
    with open("/proc/stat", "r") as f:
        line = f.readline()
        parts = list(map(int, line.split()[1:]))   # Convert values to integers

    idle = parts[3]
    total = sum(parts)      # Total CPU time
    return idle, total

def calculate_cpu_percentage():   # Function to calculate CPU usage percentage

    idle1, total1 = get_cpu_usage()     # First CPU reading
    time.sleep(0.2)
    idle2, total2 = get_cpu_usage()     # Second CPU reading

    idle_delta = idle2 - idle1
    total_delta = total2 - total1       # Change in total time

    if total_delta == 0:
        return 0

    cpu_usage = 100 * (1 - idle_delta / total_delta)    # CPU Usage formula 
    return round(cpu_usage, 2)

# ---------------- Memory Usage ----------------
def get_memory_info():           # Function to read memory info from /proc/meminfo
    meminfo = {}
    with open("/proc/meminfo", "r") as f:
        for line in f:
            key, value = line.split(":")                 # Split name and value
            meminfo[key] = int(value.split()[0])         # Store value in KB

    total = meminfo["MemTotal"]                          # Total RAM
    free = meminfo["MemFree"] + meminfo["Buffers"] + meminfo["Cached"]
    used = total - free    

    return total // 1024, used // 1024, free // 1024   # Convert KB to MB

# ---------------- Process List ----------------
def get_process_list():    # Function to read first 20 running processes from /proc
    processes = []
    for pid in os.listdir("/proc"):           # Loop through all folder names in /proc
        if pid.isdigit():                      # Only numeric folders to process IDs
            try:
                with open(f"/proc/{pid}/stat", "r") as f:
                    data = f.read().split()
                    name = data[1].strip("()")        # process name
                    state = data[2]
                processes.append((pid, name, state))
            except:
                pass           # Ignore processes that disappear quickly
    return processes[:20]      # show 20 processes

# --------- Routing ---------
@app.route("/")
def home():
    cpu = calculate_cpu_percentage()
    total, used, free = get_memory_info()
    processes = get_process_list()

    return render_template(      # Sends data to HTML page
        "index.html",
        cpu=cpu,
        total=total,
        used=used,
        free=free,
        processes=processes
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

