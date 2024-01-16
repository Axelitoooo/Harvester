import tkinter as tk
import socket
import subprocess
import re
import nmap
import shutil
import psutil
from pystray import Icon as icon, Menu as menu, MenuItem as item
from PIL import Image

# Constants
IMAGE_PATH = r'D:\Ecole\Code\test.png'
NETWORK_SCAN_ARGS = '-sn'
NETWORK_SCAN_TARGET = '192.168.1.1'
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
    # Cette fonction sera appelée lorsque l'icône du plateau est cliquée.
    # Ici, vous pouvez lancer ou afficher l'interface principale de votre application.
    main_app()


def main_app():
    app = tk.Tk()
    app.title("Seahawks Harvester")
    app.geometry("800x600")

    # Refactored UI update functions

    # Fonction pour obtenir l'adresse IP locale et le nom de la machine

    def get_system_info():
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return hostname, local_ip

    # Fonction pour scanner le réseau et retourner le nombre de machines connectées
    def scan_network():
        nm = nmap.PortScanner()
        nm.scan('192.168.1.1', arguments='-sn')  # Ajustez selon votre réseau
        connected_hosts = [(host, nm[host].hostname()) for host in nm.all_hosts()]
        return len(connected_hosts), connected_hosts

    # Fonction pour exécuter un ping et calculer la latence moyenne
    def measure_latency(target='google.com', count=4):
        response = subprocess.run(['ping', target, '-n', str(count)], stdout=subprocess.PIPE)

        try:
            output = response.stdout.decode('cp1252')
        except UnicodeDecodeError:
            output = response.stdout.decode('cp1252', 'ignore')

        # Expression régulière pour extraire le temps moyen de réponse
        match = re.search(r'Moyenne = (\d+)ms', output)

        if match:
            average_latency = int(match.group(1))
            return average_latency
        else:
            return "Non ms"

    # Mise à jour des informations du système à l'ouverture de l'app
    hostname, local_ip = get_system_info()

    # Interface utilisateur
    hostname_label = tk.Label(app, text=f"Hostname: {hostname}")
    hostname_label.pack()

    ip_label = tk.Label(app, text=f"Adresse IP Locale: {local_ip}")
    ip_label.pack()

    def update_network_info():
        count, hosts = scan_network()
        network_info_label.config(text=f"Nombre de Machines Connectées: {count}\nDernier Scan: {hosts}")

    network_scan_button = tk.Button(app, text="Scanner le Réseau", command=update_network_info)
    network_scan_button.pack()

    network_info_label = tk.Label(app, text="Infos Réseau")
    network_info_label.pack()

    def update_latency_label():
        latency = measure_latency()
        latency_label.config(text=f"Latence Moyenne: {latency} ms")

    latency_label = tk.Label(app, text="Latence Moyenne:")
    latency_label.pack()

    latency_button = tk.Button(app, text="Mesurer la Latence", command=update_latency_label)
    latency_button.pack()

    # Fonction pour obtenir les informations sur l'espace disque
    def get_disk_space():
        total, used, free = shutil.disk_usage("/")  # Changez le chemin si nécessaire
        return total, used, free

    # Fonction pour mettre à jour l'information d'espace disque sur l'interface
    def update_disk_space():
        total, used, free = get_disk_space()
        disk_space_label.config(
            text=f"Espace Total: {total // (2 ** 30)} Go, Utilisé: {used // (2 ** 30)} Go, Libre: {free // (2 ** 30)} Go")

    # Éléments d'interface utilisateur pour l'espace disque
    disk_space_label = tk.Label(app, text="Espace Disque:")
    disk_space_label.pack()

    disk_space_button = tk.Button(app, text="Vérifier l'Espace Disque", command=update_disk_space)
    disk_space_button.pack()

    def update_memory_info():
        total, used, available = get_memory_info()
        memory_info_label.config(text=f"Mémoire Totale: {total} Mo, Utilisée: {used} Mo, Disponible: {available} Mo")

    # Éléments d'interface utilisateur pour la mémoire
    memory_info_label = tk.Label(app, text="Mémoire:")
    memory_info_label.pack()

    memory_info_button = tk.Button(app, text="Vérifier la Mémoire", command=update_memory_info)
    memory_info_button.pack()

    app.mainloop()


def setup(icon):
    icon.visible = True


icon('test_icon', create_image(), menu=menu(
    item('Ouvrir', lambda icon, item: on_clicked()),
    item('Quitter', lambda icon, item: icon.stop())
)).run(setup)
