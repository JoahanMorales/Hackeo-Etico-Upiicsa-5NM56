#!/usr/bin/env python3
import subprocess, re, sys, os

INTERFACE = "wlP1p1s0"  # ajusta según tu tarjeta

def check_root():
    if os.geteuid() != 0:
        sys.exit("[-] Ejecuta con sudo")

def get_devices():
    try:
        out = subprocess.check_output(["arp-scan", "--localnet"], text=True)
    except FileNotFoundError:
        sys.exit("[-] Instala arp-scan: sudo apt install arp-scan")
    # Busca líneas con IP y MAC
    devices = []
    for line in out.splitlines():
        m = re.match(r"(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F:]{17})", line)
        if m:
            devices.append((m.group(1), m.group(2)))
    return devices

def change_mac(mac):
    subprocess.run(["ip", "link", "set", INTERFACE, "down"], check=True)
    subprocess.run(["ip", "link", "set", INTERFACE, "address", mac], check=True)
    subprocess.run(["ip", "link", "set", INTERFACE, "up"], check=True)
    print(f"[+] MAC cambiada a {mac}")

def main():
    check_root()
    devices = get_devices()
    if not devices:
        sys.exit("[-] No se encontraron dispositivos")
    print("Dispositivos encontrados:")
    for i, (ip, mac) in enumerate(devices, 1):
        print(f"{i}. IP: {ip} - MAC: {mac}")
    try:
        idx = int(input("Elige número: ")) - 1
        if idx < 0 or idx >= len(devices):
            raise ValueError
    except ValueError:
        sys.exit("[-] Selección inválida")
    target_mac = devices[idx][1]
    change_mac(target_mac)
    print("[+] Listo. Recuerda restaurar MAC tras la prueba.")

if __name__ == "__main__":
    main()