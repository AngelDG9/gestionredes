from pysnmp.hlapi import *

import time

import threading

# FUNCIONES

# el oid es de tipo string y debe llevar .0, la ip tambien string



def separar_en_hilo(func):
    # funcion decoradora que permite que las funciones poll,alarm y netmap se ejecuten en hilos separados, hay que poner el @
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
    return wrapper


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


@separar_en_hilo
def poll(oid,ip,pollId,interval):
    # hace muestreo periodico de una variable
    # debe estar en hilo separado
    while(True):
        resp=get(oid,ip)
        print("Poll "+str(pollId)+": "+resp) # Aqui poner mandar_a_telegram("Poll "+str(pollId)+": "+resp))
        time.sleep(interval)
        
        
@separar_en_hilo
def alarm(oid,ip,alarmId,thresh,text):
    # alarma, si se supera thresh se manda text
    # debe estar en hilo separado
    # solo debe permitir oids con valores numericos
    interval = 5 # por defecto ponemos 5s de sondeo para la alarma
    thresh_int=int(thresh)
    
    while(True):
        resp=get(oid,ip)
        resp_int=int(resp)
        if (resp_int > thresh_int):
            print("Alarm "+str(alarmId)+": "+text) # Aqui poner mandar_a_telegram("Alarm "+str(alarmId)+": "+text))
            break # se elimina la alarma (podemos cambiarlo)
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

@separar_en_hilo
def netmap(rango):
    # te saca los agentes snmp disponibles y su sistema operativo (en una lista de ip+so)
    # formato de rango es x.x.x.
    # queda mejorarlo para que sea más rápido (creo que podriamos hacerlo con varios hilos o modificando el timeout de get, aunque esto ultimo lo he intentado y no me ha funcionado bien)
    i=1
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
   
    print(lista_agentes) # mandar_a_telegram(lista_agentes), quizas hay que separar los elementos para que no se vean juntos
        



# MAIN
# valores para probar
oid_sysLocation='1.3.6.1.2.1.1.6.0'
oid_sysDescr='1.3.6.1.2.1.1.1.0'
oid_sysUpTime='1.3.6.1.2.1.1.3.0'
ip='192.168.138.134'
rango='192.168.138.'
interval = 3
pollId = 7
alarmId = 5
thresh=120000
text="Tiempo de encendido superior a "+str(thresh)


# probando set
# respuesta_set = set(oid_sysDescr, ip, 'Un maravilloso lugar')
# print("Reply: "+respuesta_set)


# probando poll
# poll(oid_sysDescr,ip,pollId,interval)


# probando get
# descr = get(oid_sysUpTime,ip) # probando get
# print(descr)


# probando netmap
# netmap(rango)


# probando alarm
# alarm(oid_sysUpTime,ip,alarmId,thresh,text)


# probando hilos de poll, alarm y netmap
netmap(rango)
poll(oid_sysUpTime,ip,pollId,interval)
alarm(oid_sysUpTime,ip,alarmId,thresh,text)

print("ejecutando hilos...")
