#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011, Uğur Çetin <ugur@ugurcetin.com.tr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import socket
import thread
import time

WIZNET_REMOTE_UDP_PORT = 1460
WIZNET_REMOTE_TCP_PORT = 1461
WIZNET_LOCAL_UDP_PORT = 5001
WIZNET_SEARCH_COMMAND = "FIND"
WIZNET_SEARCH_RESPONSE = "IMIN"
WIZNET_SET_COMMAND = "SET"

class Device:
    data_positions = {
        "mac": (0, 6),
        "op": (6, 7),
        "ip": (7, 11),
    }
    def __init__(self, config_data, real_ip):
        self.config_data = config_data
        self.real_ip = real_ip

    def __repr__(self):
        return self.get_mac_address()

    def _get_data(self, name):
        return self.config_data.__getslice__(*self.data_positions[name])

    def _set_data(self, name, data):
        data_list = list(self.config_data)
        data_list.__setslice__(*self.data_positions[name] + (tuple(data),))
        self.config_data = "".join(data_list)

    def save_config(self):
        "not implemented"
        self.socket = socket.socket()
        self.socket.connect((self.real_ip, WIZNET_REMOTE_TCP_PORT))
        self.socket.send("")
        self.socket.close()

    def get_mac_address(self):
        "returns mac address in XX:XX:XX:XX:XX:XX format"
        return ":".join(["%X" % ord(i) if ord(i) > 0xF else "0%X" % ord(i) for i in self._get_data("mac")])

    def set_mac_address(self, mac):
        "sets given mac address in XX:XX:XX:XX:XX:XX format"
        self._set_data("mac", "".join(chr(int(i, 16)) for i in mac.split(":")))

    def get_operation_mode(self):
        "returns 1: client, 2: server, 3:mixed"
        return ord(self._get_data("op"))

    def set_operation_mode(self, op):
        "op is an integer 1: client, 2: server, 3:mixed"
        self._set_data("op", chr(op))

    def get_ip_address(self):
        "returns ip address in ddd.ddd.ddd.ddd format"
        return ".".join([str(ord(i)) for i in self._get_data("ip")])

    def set_ip_address(self, ip):
        "ip is in ddd.ddd.ddd.ddd format"
        self._set_data("ip", "".join(chr(int(i)) for i in ip.split(".")))

class DeviceFinder:
    device_list = []

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        self.socket.bind(("", WIZNET_LOCAL_UDP_PORT))
        thread.start_new_thread(self._listen, ())

    def __del__(self):
        self.socket.close()

    def _listen(self):
        while True:
            data, address = self.socket.recvfrom(1024)
            if data[:4] == WIZNET_SEARCH_RESPONSE:
                self.device_list.append(Device(data[4:], address[0]))

    def search(self):
        "sends a broadcast message to find all wiznet devices on network"
        self.device_list = []
        self.socket.sendto(WIZNET_SEARCH_COMMAND, ("<broadcast>", WIZNET_REMOTE_UDP_PORT))

    def get_device_list(self):
        return self.device_list

if __name__ == "__main__":
    f = DeviceFinder()
    f.search()
    time.sleep(1)
    print f.get_device_list()
