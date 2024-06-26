from pysnmp.hlapi import *
from main import *
import time

import threading

import sys


# DICCIONARIOS (DE AMBITO GLOBAL, COMPARTIDA POR TODOS LOS HILOS)

hilos_poll = {}
hilos_alarm = {}



# FUNCIONES

# el oid es de tipo string y debe llevar .0, la ip tambien string



def separar_en_hilo(func):
    # funcion decoradora que permite que las funciones poll,alarm y netmap se ejecuten en hilos separados, hay que poner el @
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        
    return wrapper

    

def pruebaget(oid,ip):
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



def walk_table(oid, ip):
    # recorre una tabla entera (pasar la oid de la tabla)
    respuesta=[]
    for errorIndication, errorStatus, errorIndex, varBinds in nextCmd(
            SnmpEngine(),
            CommunityData('public', mpModel=0),
            UdpTransportTarget((ip, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
            lexicographicMode=False
    ):
        if errorIndication:
            respuesta.append(errorIndication)
        elif errorStatus:
            respuesta.append(errorStatus)
        elif errorIndex:
            respuesta.append(errorIndex)
        else:
            for varBind in varBinds:
                respuesta.append(str(varBind[1].prettyPrint()))

    return respuesta
        


@separar_en_hilo
def pruebapoll(oid,ip,pollId,interval):
    # hace muestreo periodico de una variable
    # debe estar en hilo separado
    thread=threading.current_thread()
    hilos_poll[pollId] = [thread,False]
    print("Añadido hilo de poll: "+str(pollId))
    
    while(True):
        resp=pruebaget(oid,ip)
        print("Poll "+str(pollId)+": "+resp) # Aqui poner mandar_a_telegram("Poll "+str(pollId)+": "+resp))
        time.sleep(interval)

        dupla=hilos_poll[pollId] # para que se pueda terminar
        if (dupla[1])==True:
            del hilos_poll[pollId] # elimino ese hilo del diccionario
            print("Poll con ID: "+str(pollId)+" finalizado.")
            sys.exit()
        
        
@separar_en_hilo
def pruebaalarm(oid,ip,alarmId,thresh,text):
    # alarma, si se supera thresh se manda text
    # debe estar en hilo separado
    # solo debe permitir oids con valores numericos
    thread=threading.current_thread()
    hilos_alarm[alarmId] = [thread,False]
    print("Añadido hilo de alarma: "+str(alarmId))
    
    interval = 5 # por defecto ponemos 5s de sondeo para la alarma
    thresh_int=int(thresh)
    
    while(True):
        resp=get(oid,ip)
        resp_int=int(resp)
        if (resp_int > thresh_int):
            print("Alarm "+str(alarmId)+": "+text) # Aqui poner mandar_a_telegram("Alarm "+str(alarmId)+": "+text))
            break # se elimina la alarma (podemos cambiarlo)
        time.sleep(interval)

        dupla=hilos_alarm[alarmId] # para que se pueda terminar
        if (dupla[1])==True:
            del hilos_alarm[alarmId] # elimino ese hilo del diccionario
            print("Alarma con ID: "+str(alarmId)+" finalizada.")
            sys.exit()
            
        
def pruebaset(oid, ip, value):
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
def pruebanetmap(rango):
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
        
def stoppoll(pollId):
    # elimina poll con esa id
    if (pollId in hilos_poll):
        dupla=hilos_poll[pollId]
        dupla[1]=True # Termino hilo
    else:
        print("No se encontró ningun poll con el ID "+str(pollId))


def stopalarm(alarmId):
    # elimina alarm con esa id
    if (alarmId in hilos_alarm):
        dupla=hilos_alarm[alarmId]
        dupla[1]=True # Termino hilo
    else:
        print("No se encontró ninguna alarma con el ID "+str(alarmId))

def map(ip,msg):
    # funcion traductora entre objeto telegram y oid
    oid=""

    # primero veo cual sistema operativo tiene esa ip
    so=""
    respuesta=get('1.3.6.1.2.1.1.1.0',ip)
    if "linux" in respuesta.lower():
        so = "linux"

    if "windows" in respuesta.lower():
        so = "windows"
    
    # compruebo mib-2
    if (msg=="name"):
        oid="1.3.6.1.2.1.1.5.0"
    elif (msg=="location"):
        oid="1.3.6.1.2.1.1.6.0"
    elif (msg=="description"):
        oid="1.3.6.1.2.1.1.1.0"
    elif (msg=="uptime"):
        oid="1.3.6.1.2.1.1.3.0"
    elif (msg=="ip"):
        oid="1.3.6.1.2.1.4.20"

    # compruebo mibs rendimiento, hay que diferenciar entre linux y windows (hay que meter oids correspondientes)
    elif (msg=="cpu"):
        if (so=="linux"):
            oid="1.3.6.1.4.1.2021.11.53"
        else:
            oid="1.3.6.1.2.1.25.3.3.1.2"

    elif (msg=="totaldisk"):
        if (so=="linux"):
            oid="lo que sea"
        else:
            oid="lo que sea"

    elif (msg=="disk"):
        if (so=="linux"):
            oid="1.3.6.1.4.1.2021.9"
        else:
            oid="1.3.6.1.2.1.25.2.3"

    elif (msg=="totalram"):
        if (so=="linux"):
            oid="lo que sea"
        else:
            oid="lo que sea"
            
    elif (msg=="ram"):
        if (so=="linux"):
            oid="1.3.6.1.4.1.2021.4.5.0"
        else:
            oid=".1.3.6.1.2.1.25.25.2.2.0"

    elif (msg=="numprocess"):
        if (so=="linux"):
            oid="1.3.6.1.4.1.2021.2.1.5.0"
        else:
            oid="1.3.6.1.2.1.25.1.6.0"

    elif (msg=="maxprocess"):
        if (so=="linux"):
            oid="1.3.6.1.4.1.2021.2.1.4.0"
        else:
            oid="1.3.6.1.2.1.25.1.7.0"

    # estos o son solo de windows o solo de linux
    elif (msg=="namesprocess"):
        oid="1.3.6.1.4.1.2021.2.1.2.0"

    elif (msg=="os"):
        oid="1.3.6.1.2.1.25.4.1.0"

    elif (msg=="software"):
        oid="1.3.6.1.2.1.25.4.2.1.2"
        
    else:
        return "Error: el objeto introducido no es correcto"
    
    return oid


# MAIN
# valores para probar
oid_sysLocation='1.3.6.1.2.1.1.6.0'
oid_sysDescr='1.3.6.1.2.1.1.1.0'
oid_sysUpTime='1.3.6.1.2.1.1.3.0'
oid_ipAddrTable='1.3.6.1.2.1.4.20'
#ip='192.168.138.134' # mi linux
ip='192.168.234.1' # mi windows
rango='192.168.138.'
interval = 3
pollId = 7
alarmId = 5
thresh=1200000
text="Tiempo de encendido superior a "+str(thresh)


# probando set
# respuesta_set = set(oid_sysDescr, ip, 'Linux Lubuntu')
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
# netmap(rango)
# poll(oid_sysUpTime,ip,pollId,interval)
# alarm(oid_sysUpTime,ip,alarmId,thresh,text)


# probando stopalarm y stoppoll
'''
poll(oid_sysUpTime,ip,1,5)
poll(oid_sysLocation,ip,2,6)
alarm(oid_sysUpTime,ip,8,thresh,"aviso de alarma")
print("HILOS POLL ACTUALES: "+str(hilos_poll))
print("HILOS ALARM  ACTUALES: "+str(hilos_alarm))
stoppoll(1)
stopalarm(8)
time.sleep(10)
print("HILOS POLL  TRAS ELIMINAR 1: "+str(hilos_poll))
print("HILOS ALARM TRAS ELIMINAR 1: "+str(hilos_alarm))
'''


# probando map
# result = map(ip,"name")
# print(result)
# result = map(ip,"keclwegfiwegf")
# print(result)
# result = map(ip,"disk")
# print(result)


# probando walk_table
resultado = walk_table(oid_ipAddrTable,ip)
print(resultado)
