"""
Copyright (c) 2017 Fabian Affolter <fabian@affolter-engineering.ch>

Licensed under MIT. All rights reserved.
"""
# This file is executed on every boot (including wake-boot from deepsleep)
import esp
#esp.osdebug(None)
import gc
import webrepl
import os
import machine
import ubinascii
import network

import configuration

gc.collect()

def connect():
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)
    if ap_if.active():
        ap_if.active(False)
    if not sta_if.isconnected():
        print("connecting to network...")
        sta_if.active(True)
        sta_if.connect(configuration.DEFAULT_WIFI_SSID,
                       configuration.DEFAULT_WIFI_PASSWORD)
        while not sta_if.isconnected():
            pass
    print("ip address:", sta_if.ifconfig()[0])
    print("netmask:", sta_if.ifconfig()[1])
    print("gateway:", sta_if.ifconfig()[2])

    mac_address = network.WLAN().config('mac')
    binaryToAscii = ubinascii.hexlify(mac_address, ':')
    print("mac address:", binaryToAscii.decode())

    if not sta_if.isconnected():
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(essid=configuration.CONFIG_WIFI_SSID,
                  authmode=network.AUTH_WPA_WPA2_PSK,
                  password=configuration.CONFIG_WIFI_PASSWORD)

connect()
webrepl.start()
print("files:", os.listdir())
print("frequency:", machine.freq())
print("device id:", ubinascii.hexlify(machine.unique_id()).decode())
print("flash id:", esp.flash_id())
print("sleep mode:", esp.sleep_type())
