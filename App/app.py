import tkinter as tk
from tkinter import PhotoImage
import paho.mqtt.client as paho
from paho import mqtt
import datetime
import time
title="Robot assistant"
title2="RobotApp"
global client
client = paho.Client(client_id='55', clean_session=True, userdata=None, protocol=paho.MQTTv31)
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set("hivemq.webclient.1745834546662", "Fge.w;f!d36OW#4T9AYn")
co=client.connect("3a06204e5f944e08b8d312754d3f8ec7.s1.eu.hivemq.cloud", 8883)
def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    poslabel.config(text="Robot Position (X,Y) = "+str(payload))
client.on_subscribe = on_subscribe
client.on_message = on_message
client.subscribe('pos', qos=1)
client.loop_start()

def A(event):
    x=client.publish("dest", payload="A", qos=1)
    print(x)
def B(event):
    x=client.publish("dest", payload="B", qos=1)
    print(x)
def Home(event):
    x=client.publish("dest", payload="H", qos=1)
    print(x)

root = tk.Tk()
root.title(title)
root.geometry("400x550")
frame = tk.Frame(root)
l2 = tk.Label(root, width=27, text=title2,font=("Arial", 20),foreground="blue")
l2.pack(pady=5)
image_path = "robotapp.png"  # Change this to the path of your image file
img = PhotoImage(file=image_path)
# Create a label and set the image
label = tk.Label(root, image=img)
label.pack()
poslabel = tk.Label(root, width=27, text="Robot Position (X,Y) = ",font=("Arial", 15))
poslabel.pack(pady=5)
button = tk.Button(frame, text="Home")
button2 = tk.Button(frame, text="A")
button3 = tk.Button(root, text="B")
button.bind("<Button-1>", Home)
button2.bind("<Button-1>", A)
button3.bind("<Button-1>", B)
dest = tk.Label(root, width=27, text="Destination",font=("Arial", 15),foreground="blue")
dest.pack(pady=5)
button.pack(side=tk.LEFT, padx=10)
button2.pack(side=tk.LEFT, padx=5)
button3.pack(pady=10)
#button.pack(pady=5)
#button2.pack(pady=10)
#button3.pack(pady=15)
frame.pack()
root.mainloop()
