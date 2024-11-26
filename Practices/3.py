import paho.mqtt.client as mqtt                                                          # type: ignore
def on_connect(client, userdata, flags, rc):
    print(f"Connected to broker with result code {rc}")
    client.subscribe("home/temperature")
def on_message(client, userdata, msg):
    print(f"Message received: {msg.topic}: {msg.payload.decode()}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("127.0.0.1", 1883, 60)
client.loop_start()

from time import sleep
from random import uniform
while True:
    temp = round(uniform(20.0, 30.0), 2)
    client.publish("home/temperature", temp)
    print(f"Published temperature: {temp}°C")
    sleep(5)