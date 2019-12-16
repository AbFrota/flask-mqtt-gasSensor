import eventlet
from flask import Flask, render_template
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
import pygal
import time
import os

eventlet.monkey_patch()

class Leitura:
  def __init__(self,nome ,read, cenario):
      self.nome = nome
      self.read = read
      self.cenario = cenario

lista = []
lista_leituras =[]
lista_leituras2 = []

app = Flask(__name__, template_folder='./views')
app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_REFRESH_TIME'] = 4.0

mqtt = Mqtt(app)
socketio = SocketIO(app)

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('/mqtt/safegas/out')



@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):  
      
    payload=message.payload.decode()
    if(len(payload)>=4):
        nome = 'Mq9'
        payload=int(payload)
        payload = payload - 1000
        lista_leituras2.append(payload)
        
    else:
        nome = 'Mq2'
        payload=int(payload)
        lista_leituras.append(payload)
        


    

    
    if(payload > 350):
        cenario = 'Crítico'
    else:
        cenario = 'Normal'
    leitura = Leitura(nome,payload,cenario)
    
    lista.append(leitura)
    # emit a mqtt_message event to the socket containing the message data
    #socketio.emit('mqtt_message', data=data)


@app.route('/')
def index():
    bar_chart = pygal.Line()                                            # Then create a bar graph object
    bar_chart.add('Mq2', lista_leituras)  # Add some values
    bar_chart.add('Mq9', lista_leituras2)  # Add some values
    bar_chart.render_to_file('static/images/bar_chart.svg')                          # Save the svg to a file
    img_url = 'static/images/bar_chart.svg?cache=' + str(time.time())

  
    return render_template('graph.html',image_url = img_url,leituras=lista)

@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port, debug=True)
