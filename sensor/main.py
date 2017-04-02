"""
This is a demo for Home Assistant's MQTT discovery.

Copyright (c) 2017 Fabian Affolter <fabian@affolter-engineering.ch>

Licensed under MIT. All rights reserved.
"""
import dht
import time
import machine

from umqtt.simple import MQTTClient

BROKER = 'xxxx'
DEVICE_ID = 'unit020' # Not useful for me: ubinascii.hexlify(machine.unique_id())
STATE_TOPIC = b"homeassistant/sensor/{0}_{1}/state"
CONFIG_TOPIC = b"homeassistant/sensor/{0}_{1}/config"
DHT_PIN = 5
SENSOR_PIN = 0
MIN_DEVIATION = 5

SENSOR_DETAILS = [
    [
        STATE_TOPIC.format(DEVICE_ID, 'temp'),
        CONFIG_TOPIC.format(DEVICE_ID, 'temp'),
        b'{"name": "temperature", "unit_of_measurement": "°C"}'
    ],
    [
        STATE_TOPIC.format(DEVICE_ID, 'hum'),
        CONFIG_TOPIC.format(DEVICE_ID, 'hum'),
        b'{"name": "humidity", "unit_of_measurement": "%"}'
    ],
    [
        STATE_TOPIC.format(DEVICE_ID, 'brig'),
        CONFIG_TOPIC.format(DEVICE_ID, 'brig'),
        b'{"name": "brightness", "unit_of_measurement": "ca"}'],
]

client = None
adc = machine.ADC(SENSOR_PIN)
d = dht.DHT22(machine.Pin(DHT_PIN))

def check_bound(new_value, previous_value, max_difference):
    if (new_value < previous_value - max_difference) or \
            (new_value > previous_value + max_difference):
        return True
    else:
        return False

def connect_and_subscribe():
    global client
    client = MQTTClient(DEVICE_ID, BROKER)
    client.connect()
    print("connected to mqtt broker {}".format(BROKER))
    for sensor in SENSOR_DETAILS:
        client.publish(sensor[1], sensor[2], retain=True)


def main():
    connect_and_subscribe()

    old_sensor_value = 0
    while True:
        d.measure()
        temp = d.temperature()
        hum = d.humidity()
        print("temperature:", temp)
        client.publish(SENSOR_DETAILS[0][0], str(temp))
        print("humidity", hum)
        client.publish(SENSOR_DETAILS[1][0], str(hum))

        sensor_value = adc.read()
        if check_bound(sensor_value, old_sensor_value, MIN_DEVIATION):
            old_sensor_value = sensor_value
            print("brightness:", old_sensor_value)
            client.publish(SENSOR_DETAILS[2][0], str(old_sensor_value))
        time.sleep(10)


if __name__ == '__main__':
    try:
        main()
    finally:
        try:
            client.disconnect()
            print("disconnecting...")
        except Exception:
            print("couldn't disconnect cleanly")


