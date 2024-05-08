import easysnmp
from easysnmp import snmp_get, snmp_set, snmp_walk

# FUNCIONES

def get(oid,ip):
    # obtiene valor de oid
    # el oid es de tipo string y debe llevar .0, la ip tambien string
    respuesta = snmp_get(oid, hostname=ip, community='public', version=1)
    return respuesta



# MAIN
descr = get('.1.3.6.1.2.1.1.1.0','192.168.138.134') # el objeto es sysDescr
print(descr)
