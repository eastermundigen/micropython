"""
This is a demo for Home Assistant's MQTT discovery of switches.
ESP8266 dev board with on-board LED.

Copyright (c) 2017 Fabian Affolter <fabian@affolter-engineering.ch>

Licensed under MIT. All rights reserved.
"""
import machine

from umqtt.simple import MQTTClient

import configuration

BUTTON_PIN = 0
CONFIG_TOPIC = b"homeassistant/switch/{0}_{1}/config"
CONTROL_TOPIC = b"homeassistant/switch/{0}_{1}/set"
DEFAULT_PAYLOAD_OFF = 'OFF'
DEFAULT_PAYLOAD_ON = 'ON'
GREEN_PIN = 13
RED_PIN = 14
RELAY_PIN = 12
STATE_TOPIC = b"homeassistant/switch/{0}_{1}/state"

SWITCH_DETAILS = [
    [
        # This pin is controlled with the button.
        STATE_TOPIC.format(configuration.DEVICE_ID, 'relay'),
        CONFIG_TOPIC.format(configuration.DEVICE_ID, 'relay'),
        CONTROL_TOPIC.format(configuration.DEVICE_ID, 'relay'),
        b'{"name": "relay", "command_topic": "%s"}' % CONTROL_TOPIC.format(configuration.DEVICE_ID, 'relay')
    ],
    [
        STATE_TOPIC.format(configuration.DEVICE_ID, 'red'),
        CONFIG_TOPIC.format(configuration.DEVICE_ID, 'red'),
        CONTROL_TOPIC.format(configuration.DEVICE_ID, 'red'),
        b'{"name": "red", "command_topic": "%s"}' % CONTROL_TOPIC.format(configuration.DEVICE_ID, 'red')
    ],
]

client = None


def button_callback(pin):
    client.publish(SWITCH_DETAILS[0][0], b'{}'.format("OFF" if relay.value() else "ON"))
    relay.low() if relay.value() else relay.high()
    led_green.low() if led_green.value() else led_green.high()

def message_callback(topic, msg):
    print("mqtt message on topic with payload:", topic.decode('utf-8'), msg.decode('utf-8'))
    if topic.decode('utf-8') == SWITCH_DETAILS[0][2]:
        if msg.decode('utf-8') == DEFAULT_PAYLOAD_ON:
            relay.high()
            led_green.high()
            publish_state(SWITCH_DETAILS[0][0])
        elif msg.decode('utf-8') == DEFAULT_PAYLOAD_OFF:
            relay.low()
            led_green.low()
            publish_state(SWITCH_DETAILS[0][0])
        else:
            print("unknown mqtt message payload, ignoring...")
    if topic.decode('utf-8') == SWITCH_DETAILS[1][2]:
        if msg.decode('utf-8') == DEFAULT_PAYLOAD_ON:
            led_red.high()
            publish_state(SWITCH_DETAILS[1][0])
        elif msg.decode('utf-8') == DEFAULT_PAYLOAD_OFF:
            led_red.low()
            publish_state(SWITCH_DETAILS[1][0])
        else:
            print("unknown mqtt message payload, ignoring...")

def publish_state(topic):
    if relay.value() or led_green.value() or led_red.value():
        client.publish(topic, b"ON")
    else:
        client.publish(topic, b"OFF")

def connect_and_subscribe():
    global client
    client = MQTTClient(configuration.DEVICE_ID, configuration.MQTT_BROKER)
    client.set_callback(message_callback)
    client.connect()
    print("connected to {}".format(configuration.MQTT_BROKER))

    for switch in SWITCH_DETAILS:
        client.publish(switch[1], switch[3], retain=True)
        client.subscribe(switch[2])
        print("subscribed to {}".format(switch[2]))

print("start setup of pins...")
relay = machine.Pin(RELAY_PIN, machine.Pin.OUT, value=0)
led_green = machine.Pin(GREEN_PIN, machine.Pin.OUT, value=0)
led_red = machine.Pin(RED_PIN, machine.Pin.OUT, value=0)
button = machine.Pin(BUTTON_PIN, machine.Pin.IN)
button.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_callback)

def main():
    connect_and_subscribe()
    while True:
        client.wait_msg()

if __name__ == '__main__':
    try:
        main()
    finally:
        try:
            client.disconnect()
            print("disconnecting...")
        except Exception:
            print("couldn't disconnect cleanly")
