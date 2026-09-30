import logging

import paho.mqtt.client as mqtt

from slide-utils import apply_command

# --------------------------------------------------
# Configuration
# --------------------------------------------------

MQTT_BROKER = "192.168.0.123"       # Change to your MQTT broker
MQTT_PORT = 1883
MQTT_TOPIC = "slideshow/cmd"

logging.basicConfig(
    filename="/home/pi/slideshow/mqtt-slideshow.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

log = logging.getLogger("mqtt-slideshow")


def handle_command(command):
    command = command.strip().lower()
    log.info("MQTT command: %s", command)

    if not apply_command(command):
        log.warning("Unknown command: %s", command)


# --------------------------------------------------
# MQTT callbacks
# --------------------------------------------------

def on_connect(client, userdata, flags, rc):

    if rc == 0:
        log.info("Connected to MQTT broker")

        client.subscribe(MQTT_TOPIC)

        log.info("Subscribed to %s", MQTT_TOPIC)

    else:
        log.error("MQTT connection failed: %s", rc)


def on_message(client, userdata, msg):

    try:

        payload = msg.payload.decode("utf-8").strip()

        log.info(
            "MQTT [%s] -> %s",
            msg.topic,
            payload
        )

        handle_command(payload)

    except Exception as e:
        log.error("MQTT message error: %s", e)


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION1,
        client_id="raspi-slideshow"
    )

    client.on_connect = on_connect
    client.on_message = on_message

    log.info(
        "Connecting to MQTT %s:%s",
        MQTT_BROKER,
        MQTT_PORT
    )

    client.connect(
        MQTT_BROKER,
        MQTT_PORT,
        60
    )

    client.loop_forever()


if __name__ == "__main__":
    main()
