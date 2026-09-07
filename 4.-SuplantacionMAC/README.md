# Práctica: Suplantación de Dirección MAC en Red Local

## 1. Introducción Teórica

### 1.1 Dirección MAC
La dirección MAC (Media Access Control) es un identificador único de 48 bits asignado a cada interfaz de red (Wi-Fi, Ethernet, Bluetooth). Se representa con 6 pares hexadecimales separados por dos puntos (ej: `AA:BB:CC:DD:EE:FF`). Los primeros 3 bytes identifican al fabricante (OUI) y los últimos 3 son asignados por el fabricante.

### 1.2 Suplantación de MAC (MAC Spoofing)
Consiste en cambiar la dirección MAC que reporta el sistema operativo por otra, ya sea aleatoria o copiada de otro dispositivo. Se usa en auditorías de seguridad para:
- Evadir filtros MAC en redes.
- Realizar pruebas de suplantación de identidad.
- Ocultar la identidad real del equipo.

### 1.3 Descubrimiento de dispositivos en red local (ARP Scan)
En una red local, el protocolo ARP (Address Resolution Protocol) permite asociar direcciones IP con direcciones MAC. Herramientas como `arp-scan` envían paquetes ARP a todas las IPs de la subred y recopilan las respuestas, obteniendo una lista de dispositivos conectados con su IP y MAC. Este método no requiere configuración especial, solo una interfaz de red normal.

## 2. Objetivo de la Práctica
1. Identificar dispositivos conectados a la red local (obtener IP y MAC).
2. Seleccionar una MAC objetivo para suplantar.
3. Cambiar la dirección MAC de nuestra interfaz de red usando un script en Python.
4. Verificar el cambio y restaurar la MAC original.

## 3. Materiales y Herramientas
- Jetson Orin Nano con Linux (kernel 5.15).
- Adaptador Wi-Fi integrado Realtek RTL8822CE.
- Herramientas: `arp-scan`, `ip`, Python 3.

## 4. Procedimiento

### 4.1 Escaneo de dispositivos en la red local
- Se usó `sudo arp-scan --localnet`.
- Resultado:


Interface: wlP1p1s0, MAC: xx:xx:91:95:a4:11, IPv4: 192.168.0.87
192.168.0.1 xx:xx:10:82:b5:39
192.168.0.15 xx:xx:c4:32:5b:06
192.168.0.14 xx:xx:38:75:b3:3f
192.168.0.18 xx:xx:cf:34:65:62
192.168.0.48 xx:xx:42:62:06:50
192.168.0.88 xx:xx:b7:76:bf:55

- Se anotó la MAC original del equipo: `xx:xx:91:95:a4:11`.

### 4.2 Desarrollo del script Python
Se creó un script para automatizar el proceso: escanear la red, listar dispositivos, elegir uno y cambiar la MAC.

### 4.3 Prueba y verificación
- Se ejecutó el script con `sudo python3 supMac.py`.
- Se seleccionó un dispositivo y la MAC fue cambiada.
- Se intentó conectar por SSH a la IP anterior (`192.168.0.87`) y falló porque al cambiar la MAC, el router asignó una nueva IP o se perdió la conexión.
- Se restauró la MAC original reiniciando la interfaz o el equipo.

## Funcionamiento paso a paso

1. **Verificación de privilegios**: `check_root()` comprueba que el script se ejecute con `sudo`, ya que cambiar la MAC requiere permisos de administrador.
2. **Escaneo ARP**: `get_devices()` ejecuta `arp-scan --localnet`. Captura la salida y usa una expresión regular para extraer cada línea que contenga una IP y una MAC. Devuelve una lista de tuplas `(ip, mac)`.
3. **Listado y selección**: `main()` muestra los dispositivos encontrados con un índice. El usuario ingresa el número del dispositivo a suplantar.
4. **Cambio de MAC**: `change_mac(mac)` usa los comandos `ip link set` para desactivar la interfaz, asignar la nueva dirección MAC y reactivarla.
5. **Mensajes de error**: Si no se encuentran dispositivos o la selección es inválida, el script termina con un mensaje.

## 6. Resultados y Observaciones

- El escaneo ARP permitió identificar 6 dispositivos en la red local.
- El script cambió exitosamente la MAC de la interfaz `wlP1p1s0`.
- Al cambiar la MAC, se perdió la conexión Wi-Fi (y por tanto SSH), lo que demuestra que el cambio afecta la identidad en la red.
- La MAC original se restauró reiniciando el equipo o la interfaz de red.

## 7. Conclusiones

- Es posible obtener las MACs de dispositivos en una red local sin necesidad de herramientas complejas, usando ARP.
- La suplantación de MAC es un proceso sencillo con comandos `ip`, pero requiere privilegios de root.
- Es importante guardar la MAC original y tener en cuenta que la conexión se interrumpirá temporalmente.
- Esta técnica debe usarse solo con autorización y con fines educativos o de auditoría.