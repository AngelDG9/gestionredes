# Pasos para activar agente windows
1. Administrar Características opcionales > Agregar una caracteristica > Añadir "Proveedor WMI de SNMP" y "Protocolo simple de administracion de redes"
(no hagas otra cosa hasta que se termine de instalar)

2. Servicios >  Servicio SNMP > Propiedades 
•	Configuración del agente:
o	Contacto y ubicación.
o	Servicio: marcar Internet, Aplicaciones, Extremo a extremo, Vínculo de datos y Subred (en definitiva, todas menos “Físico”).
•	Configuración de seguridad:
o	Comunidad: añadir la comunidad public con permisos de lectura y escritura.
o	Le pegas el host que tenga asociada tu gestor en modo host-only
