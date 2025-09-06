from fastapi import FastAPI, HTTPException
import os
import ssl
import paho.mqtt.client as mqtt

app = FastAPI(title="WOL -> HiveMQ publisher")

# Config MQTT da variabili ambiente
MQTT_HOST = os.getenv("HIVEMQ_HOST")            
MQTT_PORT = int(os.getenv("HIVEMQ_PORT", "8883"))
MQTT_USER = os.getenv("HIVEMQ_USER")
MQTT_PASS = os.getenv("HIVEMQ_PASS")
MQTT_TOPIC = os.getenv("HIVEMQ_TOPIC", "wol/commands")
MQTT_QOS = int(os.getenv("HIVEMQ_QOS", "1"))

def publish_to_hivemq(payload: str) -> None:
    if not MQTT_HOST:
        raise RuntimeError("Missing MQTT host (HIVEMQ_HOST)")

    client = mqtt.Client()
    if MQTT_USER:
        client.username_pw_set(MQTT_USER, MQTT_PASS)

    client.tls_set(tls_version=ssl.PROTOCOL_TLS)

    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    result = client.publish(MQTT_TOPIC, payload, qos=MQTT_QOS)
    result.wait_for_publish()
    client.disconnect()

    if result.rc != 0:
        raise RuntimeError(f"MQTT publish failed (rc={result.rc})")

@app.get("/wol")
async def wol():
    """
    Quando chiamato, pubblica il messaggio fisso '/wol' sul topic configurato.
    """
    try:
        publish_to_hivemq("/wol")
        return {"status": "sent", "topic": MQTT_TOPIC, "message": "/wol"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
