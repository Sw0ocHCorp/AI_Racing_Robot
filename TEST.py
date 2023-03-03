import string
import paho.mqtt.client as mqtt
import time

mqtt_client= mqtt.Client(client_id= "AI_Racing_Robot")
mqtt_client.connect("test.mosquitto.org")
array= [1, 2, 5, 0, 1, 3, 4]
str_array= ''.join(map(str, array))
mqtt_client.publish("AI_RACING_Robot/Best_Strategy", str_array)
print("message envoyé")

