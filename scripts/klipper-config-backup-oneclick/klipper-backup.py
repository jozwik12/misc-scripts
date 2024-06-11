# Needs a secrets.ini file in the same folder in following format:

# [SSH]
# server = your_server_ip_or_hostname
# port = 22
# user = your_username
# password = your_password

import paramiko
from scp import SCPClient
import os
from datetime import datetime
import socket
import time
from configparser import ConfigParser

def create_ssh_client(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(server, port, user, password)
    except socket.gaierror as e:
        print(f"Failed to connect to {server}: {e}")
        raise
    return client

def download_files(server, port, user, password, remote_path, local_dir, file_names, max_retries=3, delay=3):
    for attempt in range(max_retries):
        try:
            ssh = create_ssh_client(server, port, user, password)
            with SCPClient(ssh.get_transport()) as scp:
                for file_name in file_names:
                    remote_file = os.path.join(remote_path, file_name)
                    local_file = os.path.join(local_dir, file_name)
                    try:
                        scp.get(remote_file, local_file)
                        print(f"Downloaded {remote_file} to {local_file}")
                    except FileNotFoundError:
                        print(f"File {remote_file} not found on the remote server")
            break  # Exit the retry loop if successful
        except socket.gaierror as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Maximum retries reached. Exiting.")
                raise

def copy_folder(src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)
    
    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)
        
        if os.path.isdir(src_path):
            copy_folder(src_path, dst_path)
        else:
            with open(src_path, "rb") as f_src:
                with open(dst_path, "wb") as f_dst:
                    while True:
                        chunk = f_src.read(1024*1024)
                        if not chunk:
                            break
                        f_dst.write(chunk)

    print(f"OrcaSlicer config copied to {dst}")

if __name__ == "__main__":
    # Load configuration from secrets.ini
    config = ConfigParser()
    config.read("C:\\Users\\Joz\\Projects\\misc-scripts\\scripts\\klipper-config-backup-oneclick\\secrets.ini")

    # SSH connection details
    server = config["SSH"]["server"]
    port = int(config["SSH"].get("port", 22))  # default SSH port
    user = config["SSH"]["user"]
    password = config["SSH"]["password"]
    
    # Paths
    remote_path = "/home/joz/printer_data/config/"  # Path to the directory on the Linux machine
    base_local_path = "C:\\Users\\Joz\\Projects\\Klipper-personal-config"  # Base path on your Windows machine
    
    # Files to download
    file_names = ["printer.cfg", "mainsail.cfg", "moonraker.conf", "telegram.conf"]
    
    # Get current date in format YYYY-MM-DD
    current_date = datetime.now().strftime("%Y-%m-%d")
    local_dir = os.path.join(base_local_path, current_date)
    
    # Ensure local_dir directory exists
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    
    # Download the specified files
    download_files(server, port, user, password, remote_path, local_dir, file_names)

    # Copy OrcaSlicer config
    orca_slicer_source = "C:\\Users\\Joz\\AppData\\Roaming\\OrcaSlicer\\user"
    orca_slicer_destination = os.path.join(local_dir, "user")

    if not os.path.exists(orca_slicer_destination):
        os.makedirs(orca_slicer_destination)

    copy_folder(orca_slicer_source, orca_slicer_destination)

    print(f"All files downloaded to {local_dir}")