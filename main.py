from fastapi import FastAPI, HTTPException
import paho.mqtt.client as mqtt
import ssl
import threading
import os

MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT", "8883"))
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASS = os.getenv("MQTT_PASS")
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
MQTT_QOS = int(os.getenv("MQTT_QOS", "1"))

app = FastAPI(title="WoL - WakeOnLan")

def publish_message(payload: str):
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.tls_set(tls_version=ssl.PROTOCOL_TLS)
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.publish(MQTT_TOPIC, payload, qos=MQTT_QOS).wait_for_publish()
    client.disconnect()

@app.get("/")
async def root():
    threading.Thread(target=publish_message, args=("/wol",)).start()
    return {"status": "sent", "topic": MQTT_TOPIC, "message": "/wol"}
