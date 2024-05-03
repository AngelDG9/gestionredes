import pysnmp
from pysnmp.hlapi import *

import ipaddress
import subprocess

import time

# Funcion que te dice si un nodo es linux o windows segun su ip. Lo hace consultando el objeto mib-2 sysdescr (hay que configurarlo previamente)
def check_ip(ip):
    oid_sysdescr = "1.3.6.1.2.1.1.1.0"
    so = snmp_get(ip,oid_sysdescr)
    return so # puede ser windows o linux

# Obtener valor de un objeto segun su oid y su ip
def snmp_get(ip, oid):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData('public', mpModel=0),
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )

    if errorIndication:
        #print('Error al obtener el valor de OID %s en %s: %s' % (oid, ip, errorIndication))
        varBinds[1]="Error en solicitud: "+errorIndication
    elif errorStatus:
        #print('Error al obtener el valor de OID %s en %s: %s' % (oid, ip, errorStatus))
        varBinds[1]="Error en solicitud: "+errorIndication
    else:
        for varBind in varBinds:
            print('Valor de OID %s en %s: %s' % (oid, ip, varBind[1]))
        return varBinds


def set_snmp(ip, oid, value):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        setCmd(SnmpEngine(),
               CommunityData('public'),  # En principio usamos la comunidad public para todo
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid), value))
    )

    if errorIndication:
        return "fracaso: {}".format(errorIndication)
    elif errorStatus:
        return "fracaso: {} at {}".format(errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?')
    else:
        return "exito"


# Lista IP de nodos gestionables
def netmap(segmento_red):
    ips_activas = []
    i=1
    while (i < 255):
        ip="segmento_red"+"."+str(i)
        #resultado_ping = subprocess.run(['ping', '-c', '1', ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        resultado_ping = subprocess.run(['ping', '-c', '1', '-W', str(0.5), ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # tiempo espera de 0.5 s

        # Verificamos si el ping fue exitoso (0 significa éxito)
        if resultado_ping.returncode == 0:
            ips_activas.append(ip)

        i = i + 1
        time.sleep(0.2) # para no petar la red

    return ips_activas


# Te transforma el comando de telegram en su equivalente oid para poder hacerle consultas. Ej: get object ip -> te saca oid de ese object
def map(comando_telegram):
    object = comando_telegram[1] # saco el comando correspondiente. Puede que haya que cambiar la manera de sacarlo
    ip = comando_telegram[2]

    ip_checked = check_ip(ip)
    oid=""
    
    if ip_checked == "windows":
        
        if object=="name": # a partir de aqui generales para windows
            oid="sysName"
        elif object=="location":
            oid="sysLocation"
        elif object=="uptime":
            oid="sysUpTime"
        elif object=="description":
            oid="sysDescr"
        elif object=="ip":
            oid=""
        elif object=="cpu": # a partir de aqui de rendimiento para windows
            oid=""
        elif object=="totaldisk":
            oid=""
        elif object=="disk":
            oid=""
        elif object=="totalram":
            oid=""
        elif object=="ram":
            oid=""
        elif object=="numprocess":
            oid=""
        elif object=="maxprocess":
            oid=""
        elif object=="namesprocess": #los tres de alante solo en w o l
            oid=""
        elif object=="os":
            oid=""
        elif object=="software":
            oid=""
        else:
            oid="error en objeto pedido"

    else:
        if object=="name": # a partir de aqui generales para windows
            oid="sysName"
        elif object=="location":
            oid="sysLocation"
        elif object=="uptime":
            oid="sysUpTime"
        elif object=="description":
            oid="sysDescr"
        elif object=="ip":
            oid=""
        elif object=="cpu": # a partir de aqui de rendimiento para windows
            oid=""
        elif object=="totaldisk":
            oid=""
        elif object=="disk":
            oid=""
        elif object=="totalram":
            oid=""
        elif object=="ram":
            oid=""
        elif object=="numprocess":
            oid=""
        elif object=="maxprocess":
            oid=""
        elif object=="namesprocess": #los tres de alante solo en w o l
            oid=""
        elif object=="os":
            oid=""
        elif object=="software":
            oid=""
        else:
            oid="error en objeto pedido"

    return(oid)


#MAIN
# Ejemplo de escaneo de red - netmap
segmento_red = "192.168.138"
ips=netmap(segmento_red)

for ip in ips:
    print(ip)

# Ejemplo de consulta - get

