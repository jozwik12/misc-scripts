# Needs a secrets.ini file in the same folder in following format:

# [SSH]
# server = your_server_ip_or_hostname
# port = 22
# user = your_username
# password = your_password

import paramiko
from scp import SCPClient
import os
import shutil
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

def download_files(server, port, user, password, remote_path, local_dir, max_retries=3, delay=3):
    for attempt in range(max_retries):
        try:
            ssh = create_ssh_client(server, port, user, password)
            with SCPClient(ssh.get_transport()) as scp:
                try:
                    scp.get(remote_path, local_dir, recursive=True)
                    print(f"Downloaded files from {remote_path} to {local_dir}")
                except FileNotFoundError:
                    print(f"Folder {remote_path} not found on the remote server")
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

def unpack_config_folder(dst):
    src = dst + "\\config"
    for filename in os.listdir(src):
        source_path = os.path.join(src, filename)
        destination_path = os.path.join(dst, filename)
        shutil.move(source_path, destination_path)
    os.rmdir(src)
    print("Unpacked config folder")

if __name__ == "__main__":
    # Load configuration from secrets.ini
    config = ConfigParser()
    config.read("D:\\Projects\\misc-scripts\\scripts\\klipper-config-backup-oneclick\\secrets.ini")

    # SSH connection details
    server = config["SSH"]["server"]
    port = int(config["SSH"].get("port", 22))  # default SSH port
    user = config["SSH"]["user"]
    password = config["SSH"]["password"]
    
    # Paths
    remote_path = "/home/joz/printer_data/config/"  # Path to the directory on the Linux machine
    base_local_path = "D:\\Projects\\Klipper-personal-config"  # Base path on your Windows machine
    
    # Get current date in format YYYY-MM-DD
    current_date = datetime.now().strftime("%Y-%m-%d")
    local_dir = os.path.join(base_local_path, current_date)
    
    # Ensure local_dir directory exists
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    
    # Download the specified files
    download_files(server, port, user, password, remote_path, local_dir)

    # Unpack the config directory
    unpack_config_folder(local_dir)

    # Copy OrcaSlicer config
    orca_slicer_source = "C:\\Users\\Joz\\AppData\\Roaming\\OrcaSlicer\\user"
    orca_slicer_destination = os.path.join(local_dir, "user")

    if not os.path.exists(orca_slicer_destination):
        os.makedirs(orca_slicer_destination)

    copy_folder(orca_slicer_source, orca_slicer_destination)

    print(f"All files downloaded to {local_dir}")