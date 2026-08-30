#!/usr/bin/env python3
import dbus, subprocess, re, sys, time, os
from pathlib import Path

RESET = "\033[0m"; BOLD = "\033[1m"
CYAN = "\033[96m"; GREEN = "\033[92m"; YELLOW = "\033[93m"; RED = "\033[91m"

def run(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except:
        return -1, "", ""

def ensure_session_bus():
    if "DBUS_SESSION_BUS_ADDRESS" in os.environ:
        return True
    proc = subprocess.Popen(["dbus-daemon", "--session", "--fork", "--print-address"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    addr, _ = proc.communicate()
    if addr.strip():
        os.environ["DBUS_SESSION_BUS_ADDRESS"] = addr.strip()
        return True
    return False

def change_alias(name):
    run(["bluetoothctl", "system-alias", name])
    print(f"{GREEN}[+] Alias: {name}{RESET}")

def scan():
    print(f"{CYAN}[*] Escaneando 15s...{RESET}")
    run(["bluetoothctl", "--timeout", "15", "scan", "on"], timeout=20)
    _, out, _ = run(["bluetoothctl", "devices"])
    devices = []
    for line in out.splitlines():
        m = re.match(r"Device\s+([0-9A-Fa-f:]{17})\s+(.+)", line.strip())
        if m:
            devices.append((m.group(1).upper(), m.group(2)))
    return devices

def send_vcard(mac, alias):
    vcard = Path("/tmp/DatosBancarios")
    vcard.write_text(
        "BEGIN:VCARD\r\nVERSION:3.0\r\n"
        f"FN:{alias}\r\nORG:Seguridad\r\nTITLE:ALERTA CRITICA\r\n"
        "NOTE:Su dispositivo ha sido comprometido\r\nEND:VCARD\r\n", encoding="utf-8")
    print(f"{CYAN}[*] Enviando vCard...{RESET}")
    if not ensure_session_bus():
        print(f"{RED}[!] No se pudo crear bus de sesión D‑Bus{RESET}")
        return
    try:
        bus = dbus.SessionBus()
        client = bus.get_object("org.bluez.obex", "/org/bluez/obex")
        iface = dbus.Interface(client, "org.bluez.obex.Client1")
        session_path = iface.CreateSession(dbus.String(mac), {"Target": dbus.String("opp")})
        session = bus.get_object("org.bluez.obex", session_path)
        push = dbus.Interface(session, "org.bluez.obex.ObjectPush1")
        push.SendFile(dbus.String(str(vcard)))
        print(f"{GREEN}[+] vCard enviada. Revisa la notificación en el teléfono.{RESET}")
    except Exception as e:
        print(f"{RED}[!] Error: {e}{RESET}")
        print(f"{YELLOW}[*] Si aparece 0x53, elimina el emparejamiento anterior y asegúrate de que el Bluetooth esté visible.{RESET}")

def main():
    alias = "Has sido jakiado por la grasa"
    change_alias(alias)
    devices = scan()
    if not devices:
        print(f"{RED}No hay dispositivos.{RESET}")
        sys.exit(1)
    for i, (mac, name) in enumerate(devices, 1):
        print(f"{i}. {name} ({mac})")
    idx = int(input("Selecciona: ")) - 1
    mac, name = devices[idx]
    print(f"\nObjetivo: {name} ({mac})")
    send_vcard(mac, alias)

if __name__ == "__main__":
    main()