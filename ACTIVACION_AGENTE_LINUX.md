# Instalacion dependencias
sudo su
apt-get install snmpd
apt-get install snmp
apt-get install emacs

# instalar todas las mibs
apt-get install snmp-mibs-downloader

# Acceso a fichero configuración snmpd.conf
emacs /etc/snmp/snmpd.conf

# Definir public como comunidad rw o ro
    cambia "rocommunity public" por "rwcommunity public default"

# Esto es para activar la MIB-2, debe estar descomentado
    view all included .1
    view all included .1.3.6.1.2.1.1
    view all included .1.3.6.1.2.1.25.1

# Pon desde donde quieres escuchar (creo que la por defecto vale, pero conviene cambiarla)
    AgentAddress udp:ip_agent:161

# Comenta todas las variables del fichero
	Por ejemplo #sysLocation

# Acceso a fichero configuración snmp.conf
emacs /etc/snmp/snmpd.conf
    comentar linea de "mibs:"

# Medidas adicionales, quitar el firewall para que permita tráfico snmp
iptables -A INPUT -p udp --dport 161 -j ACCEPT
#ufw disable creo que este no hace falta
ufw allow 161/udp
ufw allow 162/udp

# Reinicias servicio y verificas su funcionamiento
systemctl restart snmpd
systemctl status snmpd
