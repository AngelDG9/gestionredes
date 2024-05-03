
# Instalacion
sudo apt-get install snmpd

# Acceso a fichero configuración
sudo emacs /etc/snmp/snmpd.conf

# La comunidad debe estar en public
    rocommunity public

# Esto es para activar la MIB-2, debe estar descomentado
    view   systemonly  included   .1.3.6.1.2.1.1
    view   systemonly  included   .1.3.6.1.2.1.25.1

# Reinicias servicio y verificas su funcionamiento
sudo systemctl restart snmpd
sudo systemctl status snmpd

# Medidas adicionales, quitar el firewall para que permita tráfico snmp
sudo iptables -A INPUT -p udp --dport 161 -j ACCEPT
