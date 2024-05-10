import easysnmp
from easysnmp import Session
from easysnmp import snmp_get, snmp_set, snmp_walk
from pysnmp.hlapi import *

import time

# FUNCIONES

# el oid es de tipo string y debe llevar .0, la ip tambien string

def get(oid,ip):
    # saca valor de oid de esa ip
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData('public', mpModel=0),
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )

    if errorIndication:
        respuesta=errorIndication
    elif errorStatus:
        respuesta=+'%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex) - 1][0] or '?')
    else:
        for varBind in varBinds:
            respuesta=varBind[1].prettyPrint()

    # mandar_a_telegram("Reply: "+str(respuesta))
    return str(respuesta)


def poll(oid,ip,pollId,interval):
    while(True):
        resp=get(oid,ip)
        print("Poll "+str(pollId)+": "+resp) # Aqui poner mandar_a_telegram("Poll "+str(pollId)+": "+resp))
        time.sleep(interval)
        
        

def set(oid, ip, value):
    # cambia valor de oid de esa ip
    errorIndication, errorStatus, errorIndex, varBinds = next(
        setCmd(SnmpEngine(),
               CommunityData('public', mpModel=0),
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid), value))
    )

    if errorIndication:
        respuesta=errorIndication
    elif errorStatus:
        respuesta='%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex) - 1][0] or '?')
    else:
        respuesta="Success"

    # mandar_a_telegram("Reply: "+str(respuesta))
    return respuesta


def netmap(rango):
    # te saca los agentes snmp disponibles y su sistema operativo (en una lista de ip+so)
    # formato de rango es x.x.x.
    i=33
    lista_agentes=[]
    oid_sysDescr='1.3.6.1.2.1.1.1.0'
    while(i<255):
        ip=rango+str(i)
        print("vuelta numero: "+str(i)+" ip: "+ip)
        respuesta=get(oid_sysDescr,ip)
        print(str(respuesta))
        if "linux" in respuesta.lower():
            lista_agentes.append(ip+": Linux")
            print("Añadido linux en "+ip)

        if "windows" in respuesta.lower():
            lista_agentes.append(ip+": Windows")
            print("Añadido windows en "+ip)
        i=i+1

    # mandar_a_telegram(lista_agentes), quizas hay que separar los elementos para que no se vean juntos
    return lista_agentes
        



# MAIN
oid_sysLocation='1.3.6.1.2.1.1.6.0'
oid_sysDescr='1.3.6.1.2.1.1.1.0'
ip='192.168.138.134'
rango='192.168.138.'
interval = 3
pollId = 7


# probando set
# respuesta_set = set(oid_sysDescr, ip, 'Un maravilloso lugar')
# print("Reply: "+respuesta_set)


# probando poll
resp = poll(oid_sysDescr,ip,pollId,interval)


# probando get
# descr = get(oid_sysDescr,ip) # probando get
# print(descr)


# probando netmap
#lista_agentes = netmap(rango)
#print(lista_agentes)
