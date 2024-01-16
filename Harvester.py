import tkinter as tk
import socket
import subprocess
import re
import nmap
import shutil
import psutil
from pystray import Icon as icon, Menu as menu, MenuItem as item
from PIL import Image
import json
import threading
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image


# Constants
IMAGE_PATH = r'D:\Ecole\Code\test.png'
NETWORK_SCAN_TARGET = '192.168.1.1'
NETWORK_SCAN_ARGS = '-sn'
PING_TARGET = 'google.com'
PING_COUNT = 4
DISK_PATH = "/"


def get_memory_info():
    memory = psutil.virtual_memory()
    return memory.total // (2 ** 20), memory.used // (2 ** 20), memory.available // (2 ** 20)

def create_image():
    with Image.open(IMAGE_PATH) as image:
        return image.copy()

def on_clicked():
    main_app()
    automatic_data_collection()

def get_system_info():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return hostname, local_ip

def scan_network():
    nm = nmap.PortScanner()
    nm.scan(NETWORK_SCAN_TARGET, arguments=NETWORK_SCAN_ARGS)
    connected_hosts = [(host, nm[host].hostname()) for host in nm.all_hosts()]
    return len(connected_hosts), connected_hosts

def measure_latency(target=PING_TARGET, count=PING_COUNT):
    if not re.match(r'^[a-zA-Z0-9.-]+$', target) or not isinstance(count, int):
        raise ValueError("Invalid input for latency measurement")

    command = ['ping', target, '-n', str(count)]
    try:
        response = subprocess.run(command, stdout=subprocess.PIPE, check=True)
        output = response.stdout.decode('cp1252')
    except (subprocess.CalledProcessError, UnicodeDecodeError) as e:
        return f"Error: {e}"

    match = re.search(r'Moyenne = (\d+)ms', output)
    return int(match.group(1)) if match else "Non ms"

def update_ui(label, text):
    label.config(text=text)

def get_disk_space():
    total, used, free = shutil.disk_usage(DISK_PATH)
    return total, used, free

def collect_all_data():
    system_info = get_system_info()
    network_info = scan_network()
    latency = measure_latency()
    disk_space = get_disk_space()
    memory_info = get_memory_info()

    data = {
        "timestamp": datetime.now().isoformat(),
        "system_info": {
            "hostname": system_info[0],
            "local_ip": system_info[1]
        },
        "network_info": {
            "connected_hosts_count": network_info[0],
            "connected_hosts": network_info[1]
        },
        "latency": latency,
        "disk_space": {
            "total": disk_space[0],
            "used": disk_space[1],
            "free": disk_space[2]
        },
        "memory_info": {
            "total": memory_info[0],
            "used": memory_info[1],
            "available": memory_info[2]
        }
    }
    return data

def export_to_json(data):
    hostname = socket.gethostname()
    current_time = datetime.now()
    formatted_time = current_time.strftime("%d.%m.%Y-%H-%M")
    file_name = f"{hostname}-{formatted_time}.json"
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

def automatic_data_collection():
    data = collect_all_data()
    export_to_json(data)
    threading.Timer(86400, automatic_data_collection).start()

def create_json_button_command():
    data = collect_all_data()
    export_to_json(data)
    # Show a message or update the UI to indicate that the JSON file has been created

def main_app():
    app = tk.Tk()
    app.title("Seahawks Harvester")
    app.geometry("800x600")

    hostname, local_ip = get_system_info()

    hostname_label = tk.Label(app, text=f"Hostname: {hostname}")
    hostname_label.pack()

    ip_label = tk.Label(app, text=f"Adresse IP Locale: {local_ip}")
    ip_label.pack()

    def update_network_info():
        count, hosts = scan_network()
        update_ui(network_info_label, f"Nombre de Machines Connectées: {count}\nDernier Scan: {hosts}")

    network_scan_button = tk.Button(app, text="Scanner le Réseau", command=update_network_info)
    network_scan_button.pack()

    network_info_label = tk.Label(app, text="Infos Réseau")
    network_info_label.pack()

    def update_latency_label():
        latency = measure_latency()
        update_ui(latency_label, f"Latence Moyenne: {latency} ms")

    latency_label = tk.Label(app, text="Latence Moyenne:")
    latency_label.pack()

    latency_button = tk.Button(app, text="Mesurer la Latence", command=update_latency_label)
    latency_button.pack()

    def update_disk_space():
        total, used, free = get_disk_space()
        update_ui(disk_space_label, f"Espace Total: {total // (2 ** 30)} Go, Utilisé: {used // (2 ** 30)} Go, Libre: {free // (2 ** 30)} Go")

    disk_space_label = tk.Label(app, text="Espace Disque:")
    disk_space_label.pack()

    disk_space_button = tk.Button(app, text="Vérifier l'Espace Disque", command=update_disk_space)
    disk_space_button.pack()

    def update_memory_info():
        total, used, available = get_memory_info()
        update_ui(memory_info_label, f"Mémoire Totale: {total} Mo, Utilisée: {used} Mo, Disponible: {available} Mo")

    memory_info_label = tk.Label(app, text="Mémoire:")
    memory_info_label.pack()

    memory_info_button = tk.Button(app, text="Vérifier la Mémoire", command=update_memory_info)
    memory_info_button.pack()

    memory_info_label = tk.Label(app, text="JSON:")
    memory_info_label.pack()
    create_json_button = tk.Button(app, text="Créer le JSON", command=create_json_button_command)
    create_json_button.pack()

    app.mainloop()

def setup(icon):
    icon.visible = True

if __name__ == "__main__":
    threading.Thread(target=on_clicked).start()
    icon('test_icon', create_image(), menu=menu(
        item('Ouvrir', lambda icon, item: on_clicked()),
        item('Quitter', lambda icon, item: icon.stop())
    )).run(setup)
