import paho.mqtt.client as paho
from paho import mqtt
import os
import time
client = paho.Client()
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set("hivemq.webclient.1745834546662", "Fge.w;f!d36OW#4T9AYn")
client.connect("3a06204e5f944e08b8d312754d3f8ec7.s1.eu.hivemq.cloud", 8883)

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    if(str(msg.payload)=="b'A'"):
        print("A Destination")
    elif(str(msg.payload)=="b'B'"):
        print("B Destination")
    elif(str(msg.payload)=="b'H'"):
        print("Home Destination")

client.on_subscribe = on_subscribe
client.on_message = on_message
client.subscribe('dest', qos=1)
#time.sleep(5)
#x=client.publish("pos", payload="(20,20)", qos=1)
client.loop_forever()

