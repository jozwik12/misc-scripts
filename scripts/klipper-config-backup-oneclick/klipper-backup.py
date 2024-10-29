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

def load_config(config_path):
    config = ConfigParser()
    config.read(config_path)
    ssh_config = {
        'server': config["SSH"]["server"],
        'port': int(config["SSH"].get("port", 22)),
        'user': config["SSH"]["user"],
        'password': config["SSH"]["password"]
    }
    return ssh_config

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

def download_files(ssh_client, remote_path, local_dir, max_retries=3, delay=3):
    for attempt in range(max_retries):
        try:
            with SCPClient(ssh_client.get_transport()) as scp:
                scp.get(remote_path, local_dir, recursive=True)
            print(f"Downloaded files from {remote_path} to {local_dir}")
            break
        except (FileNotFoundError, socket.gaierror) as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                raise Exception("Maximum retries reached. Exiting.")

def download_file(ssh_client, remote_file, local_dir):
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, os.path.basename(remote_file))
    with SCPClient(ssh_client.get_transport()) as scp:
        scp.get(remote_file, local_path)
    print(f"Downloaded file {remote_file} to {local_path}")

def copy_folder(src, dst):
    os.makedirs(dst, exist_ok=True)
    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)
        if os.path.isdir(src_path):
            copy_folder(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)
    print(f"Copied folder from {src} to {dst}")

def unpack_config_folder(dst):
    src = os.path.join(dst, "config")
    for filename in os.listdir(src):
        shutil.move(os.path.join(src, filename), os.path.join(dst, filename))
    os.rmdir(src)
    print("Unpacked config folder")

if __name__ == "__main__":
    # Load configuration
    config_path = "D:\\Projects\\misc-scripts\\scripts\\klipper-config-backup-oneclick\\secrets.ini"
    ssh_config = load_config(config_path)

    # Define paths
    remote_config_path = "/home/joz/printer_data/config/"
    local_base_path = "D:\\Projects\\Klipper-personal-config"
    current_date = datetime.now().strftime("%Y-%m-%d")
    local_dir = os.path.join(local_base_path, current_date)

    os.makedirs(local_dir, exist_ok=True)

    # Establish SSH connection
    ssh_client = create_ssh_client(**ssh_config)

    # Download directories
    download_files(ssh_client, remote_config_path, local_dir)
    unpack_config_folder(local_dir)

    # Copy OrcaSlicer config
    orca_slicer_source = "C:\\Users\\Joz\\AppData\\Roaming\\OrcaSlicer\\user"
    orca_slicer_destination = os.path.join(local_dir, "OrcaSlicer\\user")
    copy_folder(orca_slicer_source, orca_slicer_destination)

    # Download specific file from Spoolman
    spoolman_remote_file = "/home/joz/.local/share/spoolman/spoolman.db"
    spoolman_destination = os.path.join(local_dir, "Spoolman")
    download_file(ssh_client, spoolman_remote_file, spoolman_destination)

    print(f"All files downloaded to {local_dir}")