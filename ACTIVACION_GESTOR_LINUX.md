# ACTIVAR EL GESTOR
sudo apt-get install snmp
sudo pip install easysnmp

# Medidas adicionales, quitar el firewall para que permita tráfico snmp
sudo iptables -A INPUT -p udp --dport 161 -j ACCEPT
#sudo ufw disable creo que esta no hace falta