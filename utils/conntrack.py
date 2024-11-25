import subprocess
import re

def get_conntrack_entry(ip, port):
    command = f"sudo conntrack -L | agrep 'dst={ip};sport={port}'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        output = result.stdout        
        match = re.search(r'dst=([\d\.]+)', output)
        if match:
            dst_ip = match.group(1)
            return dst_ip
        else:
            print("No dst IP found in the output")