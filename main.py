import telebot
from telebot import types
#from telegram.ext import Updater, CommandHandler, MessageHandler, filters, ConversationHandler
import requests
from snmpmanager  import *





TOKEN = '7068293902:AAFyCzoGMgreHWSF1jupPbdlOBohYc1dOhs'
API_KEY= 'a0a029a7f5655197fb581d8f1cba2d8a'
CHAT_ID = "-1002104041473"
bot = telebot.TeleBot(TOKEN)
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather?' 
gestion_dict = {}


# Variable para almacenar los datos
datos = []



#Funcion que envia un mensaje al chat de telegram
@bot.message_handler(commands=['ping'])
def send_telegram_message(message):
    # Token de tu bot de Telegram
    token = "7068293902:AAFyCzoGMgreHWSF1jupPbdlOBohYc1dOhs"
    # ID del chat al que deseas enviar el mensaje
    chat_id = "-1002104041473"
    
    # URL de la API de Telegram para enviar mensajes
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    # Parámetros del mensaje a enviar
    params = {
        "chat_id": chat_id,
        "text": message
    }
    
    # Envía la solicitud POST a la API de Telegram
    response = requests.post(url, params=params)
    
    # Verifica si la solicitud fue exitosa
    if response.status_code == 200:
        print("Mensaje enviado correctamente a Telegram.")
    else:
        print(f"Error al enviar el mensaje a Telegram: {response.status_code} - {response.text}")
lista_agentes = None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,'Hola! Soy tu ayudante de Gestion de Redes')
    
@bot.message_handler(commands=['netmap'])
def send_welcome(message):
    global lista_agentes
    lista_agentes = ['192.168.239.130']
    print("Agentes:")
    print(lista_agentes)
    for agente in lista_agentes:
        bot.reply_to(message,"Agente: " + agente)

    

@bot.message_handler(commands=['help2'])
def send_welcome(message):
    bot.reply_to(message,'En que necesitas que te ayude. Por ahora solo tengo los comandos /GET,/SET, /start y /help')
    

class Gestion:
    def __init__(self, red):
        self.red = red
        self.oid = None
        self.equipo = None
        self.cambio = None
        self.ident = None
        self.text = None


# Handle '/start' and '/help'
@bot.message_handler(commands=['get'])
def send_welcome(message):
    if lista_agentes:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('1')
        msg = bot.reply_to(message, 'Que red quieres monitorizar', reply_markup=markup)
        bot.register_next_step_handler(msg, process_red_step)
    else:
        bot.reply_to(message, 'Hay que hacer netmap primero para tener la lista de agentes')


def process_red_step(message):
    try:
        chat_id = message.chat.id
        red = message.text
        gestion = Gestion(red)
        gestion_dict[chat_id] = gestion
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('1.3.6.1.2.1.1.1.0','oid2','1.3.6.1.2.1.1.6.0')
        msg = bot.reply_to(message, 'Que oid quieres monitorizar', reply_markup=markup)
        bot.register_next_step_handler(msg, process_oid_step)

    except Exception as e:
        bot.reply_to(message, 'Algo ha salido mal2')

        
def process_oid_step(message):
    try:
        chat_id = message.chat.id
        oid = message.text
        gestion = gestion_dict[chat_id]
        gestion.oid = oid
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add(*lista_agentes)
        msg = bot.reply_to(message, 'Que equipo quieres monitorizar', reply_markup=markup)
        bot.register_next_step_handler(msg, process_equipo_step)

    except Exception as e:
        bot.reply_to(message, 'Algo ha salido mal3')


def process_equipo_step(message):
    try:
        chat_id = message.chat.id
        equipo = message.text
        gestion = gestion_dict[chat_id]
        gestion.equipo = equipo
        bot.send_message(chat_id, 'Monitorizando red: ' + gestion.red + '\n OID:' + gestion.oid + '\n Equipo:' + gestion.equipo)
        respuestafinal = pruebaget(gestion.oid,gestion.equipo)
        print(respuestafinal)
        bot.send_message(chat_id, 'Contenido del oid: ' + respuestafinal)
    except Exception as e:
        bot.reply_to(message, 'Algo ha salido mal')











        
        

@bot.message_handler(commands=['set'])
def set_command2(message):
    if lista_agentes:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('1')
        msg = bot.reply_to(message, 'Que red quieres monitorizar', reply_markup=markup)
        bot.register_next_step_handler(msg, process_red_step2)
    else:
        bot.reply_to(message, 'Hay que hacer netmap primero para tener la lista de agentes')


def process_red_step2(message):
    try:
        chat_id = message.chat.id
        red = message.text
        gestion = Gestion(red)
        gestion_dict[chat_id] = gestion
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('1.3.6.1.2.1.1.1.0','oid2','1.3.6.1.2.1.1.6.0')
        msg = bot.reply_to(message, 'Que oid quieres cambiar', reply_markup=markup)
        bot.register_next_step_handler(msg, process_oid_step2)

    except Exception as e:
        bot.reply_to(message, 'Algo ha salido mal2')

        
def process_oid_step2(message):
    try:
        chat_id = message.chat.id
        oid = message.text
        gestion = gestion_dict[chat_id]
        gestion.oid = oid
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add(*lista_agentes)
        msg = bot.reply_to(message, 'Que equipo quieres monitorizar', reply_markup=markup)
        bot.register_next_step_handler(msg, process_equipo_step2)

    except Exception as e:
        bot.reply_to(message, 'Algo ha salido mal3')


def process_equipo_step2(message):
    try:
        chat_id = message.chat.id
        equipo = message.text
        gestion = gestion_dict[chat_id]
        gestion.equipo = equipo
        bot.send_message(chat_id, 'Monitorizando red: ' + gestion.red + '\n OID:' + gestion.oid + '\n Equipo:' + gestion.equipo)
        msg = bot.reply_to(message, 'Escribe el nuevo valor del oid')
        bot.register_next_step_handler(msg, process_ip2)

    except Exception as e:
        bot.reply_to(message, 'Algo ha salido mal')

def process_ip2(message):
    try:
        
        chat_id = message.chat.id
        cambio = message.text
        gestion = gestion_dict[chat_id]
        gestion.cambio = cambio
        comprobacion = pruebaset(gestion.oid,gestion.equipo,gestion.cambio)
        print(comprobacion)
        bot.reply_to(message, comprobacion)        
        
        # Aquí puedes realizar acciones basadas en la dirección IP proporcionada por el usuario
        # Por ejemplo, podrías validar el formato de la dirección IP o realizar operaciones específicas con ella
        # En este ejemplo, simplemente enviamos un mensaje de confirmación con la dirección IP
        bot.send_message(chat_id, f'El nuevo valor del oid será: {cambio}')
    except Exception as e:
        bot.reply_to(message, 'Ocurrió un error al procesar tu solicitud')






    

    
    

alarmas_activas = False



@bot.message_handler(commands=['poll'])
def set_command3(message):
    if lista_agentes:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('1')
        msg = bot.reply_to(message, 'Que red quieres monitorizar', reply_markup=markup)
        bot.register_next_step_handler(msg, process_red_step3)
    else:
        bot.reply_to(message, 'Hay que hacer netmap primero para tener la lista de agentes')


def process_red_step3(message):
    try:
        chat_id = message.chat.id
        red = message.text
        gestion = Gestion(red)
        gestion_dict[chat_id] = gestion
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('1.3.6.1.2.1.1.1.0','oid2','1.3.6.1.2.1.1.6.0')
        msg = bot.reply_to(message, 'Que oid quieres monitorizar', reply_markup=markup)
        bot.register_next_step_handler(msg, process_oid_step3)

    except Exception as e:
        bot.reply_to(message, 'Algo ha salido mal2')

        
def process_oid_step3(message):
    try:
        chat_id = message.chat.id
        oid = message.text
        gestion = gestion_dict[chat_id]
        gestion.oid = oid
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add(*lista_agentes)
        msg = bot.reply_to(message, 'Que equipo quieres monitorizar', reply_markup=markup)
        bot.register_next_step_handler(msg, process_equipo_step3)

    except Exception as e:
        bot.reply_to(message, 'Algo ha salido mal3')


def process_equipo_step3(message):
    try:
        chat_id = message.chat.id
        equipo = message.text
        gestion = gestion_dict[chat_id]
        gestion.equipo = equipo
        bot.send_message(chat_id, 'Monitorizando red: ' + gestion.red + '\n OID:' + gestion.oid + '\n Equipo:' + gestion.equipo)
        msg = bot.reply_to(message, 'Escribe el identificador del poll')
        bot.register_next_step_handler(msg, process_ip3)

    except Exception as e:
        bot.reply_to(message, 'Algo ha salido mal')

def process_ip3(message):
    try:
        
        chat_id = message.chat.id
        pollid = message.text
        gestion = gestion_dict[chat_id]
        gestion.pollid = pollid
        msg = bot.reply_to(message, 'Escribe el valor del intervalo')
        bot.register_next_step_handler(msg, process_intervalo)      
    except Exception as e:
        bot.reply_to(message, 'Ocurrió un error al procesar tu solicitud')

def process_intervalo(message):
    try:
        
        chat_id = message.chat.id
        cambio = message.text
        gestion = gestion_dict[chat_id]
        gestion.cambio = cambio
        if gestion.cambio.isdigit():
            pruebapoll(gestion.oid, gestion.equipo, gestion.ident, gestion.cambio)
            bot.send_message(chat_id, 'Se ha configurado el poll correctamente')
        else:
            bot.send_message(chat_id, 'El valor del intervalo tiene que ser un número') 
        
    except Exception as e:
        bot.reply_to(message, 'Ocurrió un error al procesar tu solicitud')






  




@bot.message_handler(commands=['stoppoll'])
def send_stoppoll(message):
    global alarmas_activas
    if alarmas_activas:
        alarmas_activas = False
        bot.reply_to(message, 'Las alarmas han sido detenidas.')
    else:
        bot.reply_to(message, 'No hay alarmas activas en este momento.')







      
@bot.message_handler(commands=['alarm'])
def set_command4(message):
    if lista_agentes:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('1')
        msg = bot.reply_to(message, 'Que red quieres monitorizar', reply_markup=markup)
        bot.register_next_step_handler(msg, process_red_step4)
    else:
        bot.reply_to(message, 'Hay que hacer netmap primero para tener la lista de agentes')


def process_red_step4(message):
    try:
        chat_id = message.chat.id
        red = message.text
        gestion = Gestion(red)
        gestion_dict[chat_id] = gestion
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('1.3.6.1.2.1.1.1.0','oid2','1.3.6.1.2.1.1.6.0')
        msg = bot.reply_to(message, 'Que oid quieres monitorizar', reply_markup=markup)
        bot.register_next_step_handler(msg, process_oid_step4)

    except Exception as e:
        bot.reply_to(message, 'Algo ha salido mal2')

        
def process_oid_step4(message):
    try:
        chat_id = message.chat.id
        oid = message.text
        gestion = gestion_dict[chat_id]
        gestion.oid = oid
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add(*lista_agentes)
        msg = bot.reply_to(message, 'Que equipo quieres monitorizar', reply_markup=markup)
        bot.register_next_step_handler(msg, process_equipo_step4)

    except Exception as e:
        bot.reply_to(message, 'Algo ha salido mal3')


def process_equipo_step4(message):
    try:
        chat_id = message.chat.id
        equipo = message.text
        gestion = gestion_dict[chat_id]
        gestion.equipo = equipo
        bot.send_message(chat_id, 'Monitorizando red: ' + gestion.red + '\n OID:' + gestion.oid + '\n Equipo:' + gestion.equipo)
        msg = bot.reply_to(message, 'Escribe el identificador de la alarma')
        bot.register_next_step_handler(msg, process_ip4)

    except Exception as e:
        bot.reply_to(message, 'Algo ha salido mal')

def process_ip4(message):
    try:
        
        chat_id = message.chat.id
        pollid = message.text
        gestion = gestion_dict[chat_id]
        gestion.pollid = pollid
        msg = bot.reply_to(message, 'Escribe el valor del umbral')
        bot.register_next_step_handler(msg, process_umbral)      
    except Exception as e:
        bot.reply_to(message, 'Ocurrió un error al procesar tu solicitud')

def process_umbral(message):
    try:
        
        chat_id = message.chat.id
        cambio = message.text
        gestion = gestion_dict[chat_id]
        gestion.cambio = cambio
        msg = bot.reply_to(message, 'Escribe el mensaje de alarma')
        bot.register_next_step_handler(msg, process_mensaje)      
    except Exception as e:
        bot.reply_to(message, 'Ocurrió un error al procesar tu solicitud')

def process_mensaje(message):
    try:
        
        chat_id = message.chat.id
        text = message.text
        gestion = gestion_dict[chat_id]
        gestion.text = text
        pruebaalarm(gestion.oid, gestion.equipo, gestion.ident, gestion.cambio, gestion.text)
        bot.reply_to(message, 'Alarma configurada')
    except Exception as e:
        bot.reply_to(message, 'Ocurrió un error al procesar tu solicitud')

        


        


# Función para enviar una notificacion
def enviar_noti(notificacion):
    bot.send_message(CHAT_ID, notificacion)

# No olvides el código para iniciar y detener alarmas según sea necesario

# Lógica para detener el envío de alarmas
def detener_alarma():
    global alarmas_activas
    alarmas_activas = False

    




    
    
@bot.message_handler(commands =['help'])
def send_options(message):
    markup = types.InlineKeyboardMarkup(row_width=2) 
    
    
    btn_get= types.InlineKeyboardButton('/get', callback_data='snmp_get')   
    btn_set= types.InlineKeyboardButton('/set',callback_data='snmp_set')
    btn_alarm= types.InlineKeyboardButton('/alarm',callback_data='snmp_alarm')
    btn_poll= types.InlineKeyboardButton('/poll',callback_data='snmp_poll')
    btn_stoppoll= types.InlineKeyboardButton('/stoppoll',callback_data='snmp_stoppoll')
    btn_stopalarm= types.InlineKeyboardButton('/stopalarm',callback_data='snmp_stopalarm')
    btn_netmap= types.InlineKeyboardButton('/netmap',callback_data='snmp_netmap')
    markup.add(btn_get,btn_set,btn_alarm,btn_poll,btn_stoppoll,btn_stopalarm,btn_netmap)
    
    bot.send_message(message.chat.id,"Comandos disponibles",reply_markup=markup)
    
    
@bot.callback_query_handler(func=lambda call:True)
def callback_query(call):
    if call.data == 'snmp_get':
        bot.answer_callback_query(call.id,'Escribe /get')
    elif call.data =='snmp_set':
         bot.answer_callback_query(call.id,'Escribe /set ')
    elif call.data =='snmp_alarm':
         bot.answer_callback_query(call.id,'Escribe /alarm ')     
    elif call.data =='snmp_poll':
         bot.answer_callback_query(call.id,'Escribe /poll ')
    elif call.data =='snmp_setalarm':
         bot.answer_callback_query(call.id,'Escribe /setalarm ')
    elif call.data =='snmp_stoppoll':
         bot.answer_callback_query(call.id,'Escribe /stoppoll ')
    elif call.data =='snmp_stopalarm':
         bot.answer_callback_query(call.id,'Escribe /stopalarm ')
    elif call.data =='snmp_netmap':
         bot.answer_callback_query(call.id,'Escribe /netmap ')
         
if __name__ == "__main__":
    bot.polling(none_stop=True)  
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
  
    
    
    
    
    
    
    
    
  
