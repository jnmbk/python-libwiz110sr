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
import struct
import thread
import time

WIZNET_REMOTE_UDP_PORT = 1460
WIZNET_REMOTE_TCP_PORT = 1461
WIZNET_LOCAL_UDP_PORT = 5001
WIZNET_SEARCH_COMMAND = "FIND"
WIZNET_SEARCH_RESPONSE = "IMIN"
WIZNET_SET_REQ_COMMAND = "SETT"
WIZNET_SET_RES_COMMAND = "SETC"
WIZNET_INT_FORMAT = "!H"
WIZNET_VERSION_FORMAT = "!BB"

class Device:
    data_positions = {
        "mac": (0, 6),
        "op": (6, 7),
        "ip": (7, 11),
        "subnet_mask": (11, 15),
        "gateway_ip": (15, 19),
        "port": (19, 21),
        "remote_ip": (21, 25),
        "remote_port": (25, 27),
        "baud": (27, 28),
        "d_bit": (28, 29),
        "p_bit": (29, 30),
        "s_bit": (30, 31),
        "flow": (31, 32),
        "char": (32, 33),
        "length": (33, 35),
        "interval": (35, 37),
        "inactivity": (37, 39),
        "dbug": (39, 40),
        "ver": (40, 42),
        "dhcp": (42, 43),
        "udp": (43, 44),
        "conn": (44, 45),
        "dflg": (45, 46),
        "dns_ip": (46, 50),
        "remote_domain": (50, 82),
        "scfg": (82, 83),
        "scfg_string": (83, 86),
        "pppoe_id": (86, 118),
        "pppoe_pass": (118, 150),
        "enp": (150, 151),
        "conn_pass": (151, 159),
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
        """writes current configuration to device"""
        s = socket.socket()
        s.connect((self.real_ip, WIZNET_REMOTE_TCP_PORT))
        s.send(WIZNET_SET_REQ_COMMAND + self.config_data)
        data = s.recv(1024)
        if data[:4] == WIZNET_SET_RES_COMMAND:
            self.config_data == data[4:]
        else:
            #This shouldn't happen
            pass
        s.close()

    def get_mac_address(self):
        """returns mac address in XX:XX:XX:XX:XX:XX format"""
        return ":".join(["%X" % ord(i) if ord(i) > 0xF else "0%X" % ord(i) for i in self._get_data("mac")])

    def set_mac_address(self, mac):
        """sets given mac address in XX:XX:XX:XX:XX:XX format"""
        self._set_data("mac", "".join(chr(int(i, 16)) for i in mac.split(":")))

    def get_operation_mode(self):
        """returns 1:client, 2:server, 3:mixed"""
        return ord(self._get_data("op"))

    def set_operation_mode(self, op):
        """op is an integer 1:client, 2:server, 3:mixed"""
        self._set_data("op", chr(op))

    def get_ip_address(self):
        """returns ip address in ddd.ddd.ddd.ddd format"""
        return ".".join([str(ord(i)) for i in self._get_data("ip")])

    def set_ip_address(self, ip):
        """ip is in ddd.ddd.ddd.ddd format"""
        self._set_data("ip", "".join(chr(int(i)) for i in ip.split(".")))

    def get_subnet_mask(self):
        """returns mask in ddd.ddd.ddd.ddd format"""
        return ".".join([str(ord(i)) for i in self._get_data("subnet_mask")])

    def set_subnet_mask(self, mask):
        """mask is in ddd.ddd.ddd.ddd format"""
        self._set_data("subnet_mask", "".join(chr(int(i)) for i in mask.split(".")))

    def get_gateway_ip(self):
        """returns ip address in ddd.ddd.ddd.ddd format"""
        return ".".join([str(ord(i)) for i in self._get_data("gateway_ip")])

    def set_gateway_ip(self, ip):
        """ip is in ddd.ddd.ddd.ddd format"""
        self._set_data("gateway_ip", "".join(chr(int(i)) for i in ip.split(".")))

    def get_port(self):
        """returns port number which is an unsigned short integer"""
        return struct.unpack(WIZNET_INT_FORMAT, self._get_data("port"))[0]

    def set_port(self, port):
        """port is an unsigned short integer"""
        self._set_data("port", struct.pack(WIZNET_INT_FORMAT, port))

    def get_remote_ip(self):
        """returns ip address in ddd.ddd.ddd.ddd format"""
        return ".".join([str(ord(i)) for i in self._get_data("remote_ip")])

    def set_remote_ip(self, ip):
        """ip is in ddd.ddd.ddd.ddd format"""
        self._set_data("remote_ip", "".join(chr(int(i)) for i in ip.split(".")))

    def get_remote_port(self):
        """returns port number which is an unsigned short integer"""
        return struct.unpack(WIZNET_INT_FORMAT, self._get_data("remote_port"))[0]

    def set_remote_port(self, port):
        """port is an unsigned short integer"""
        self._set_data("remote_port", struct.pack(WIZNET_INT_FORMAT, port))

    def get_baud_rate(self):
        """returns integer which in hex means:
        A0:1200, D0:2400, E8:4800, F4:9600, FA:19200, FD:38400, FE:57600, FF:115200, BB:230400"""
        return hex(ord(self._get_data("baud")))

    def set_baud_rate(self, baud):
        """baud is an integer which in hex means:
        A0:1200, D0:2400, E8:4800, F4:9600, FA:19200, FD:38400, FE:57600, FF:115200, BB:230400"""
        self._set_data("baud", chr(baud))

    def get_data_bit_length(self):
        """returns an integer which can be 7 or 8"""
        return ord(self._get_data("d_bit"))

    def set_data_bit_length(self, d_bit):
        """d_bit is an integer which can be 7 or 8"""
        self._set_data("d_bit", chr(d_bit))

    def get_parity_bit(self):
        """returns an integer which means 0:None, 1:Odd, 2:Even"""
        return ord(self._get_data("p_bit"))

    def set_parity_bit(self, p_bit):
        """p_bit is an integer which means 0:None, 1:Odd, 2:Even"""
        self._set_data("p_bit", chr(p_bit))

    def get_stop_bit(self):
        """returns an integer which can be 0 or 1"""
        return ord(self._get_data("s_bit"))

    def set_stop_bit(self, s_bit):
        """s_bit is an integer which can be 0 or 1"""
        self._set_data("s_bit", chr(s_bit))

    def get_flow(self):
        """returns an integer which means 0:None, 1:Xon/Xoff, 2:CTS/RTS"""
        return ord(self._get_data("flow"))

    def set_flow(self, flow):
        """flow is an integer which means 0:None, 1:Xon/Xoff, 2:CTS/RTS"""
        self._set_data("flow", chr(flow))

    def get_char(self):
        """returns a character, \0 means packing is not used"""
        return self._get_data("char")

    def set_char(self, char):
        """char is a character, \0 means packing is not used"""
        self._set_data("char", char)

    def get_length(self):
        """returns serial packing length which can be 255 max, 0 means packing is not used"""
        return struct.unpack(WIZNET_INT_FORMAT, self._get_data("length"))[0]

    def set_length(self, length):
        """length can be 255 max, 0 means packing is not used"""
        self._set_data("length", struct.pack(WIZNET_INT_FORMAT, length))

    def get_interval(self):
        """returns serial packing interval which is a short integer, 0 means packing is not used"""
        return struct.unpack(WIZNET_INT_FORMAT, self._get_data("interval"))[0]

    def set_interval(self, interval):
        """interval is a short integer, 0 means packing is not used"""
        self._set_data("interval", struct.pack(WIZNET_INT_FORMAT, interval))

    def get_inactivity(self):
        """returns TCP inactivity time in seconds which is a short integer, 0 means disabled"""
        return struct.unpack(WIZNET_INT_FORMAT, self._get_data("inactivity"))[0]

    def set_inactivity(self, inactivity):
        """TCP inactivity time in seconds is a short integer, 0 means disabled"""
        self._set_data("inactivity", struct.pack(WIZNET_INT_FORMAT, inactivity))

    def get_debug(self):
        """returns an integer which means 0:Enable, 1:Disable"""
        return ord(self._get_data("dbug"))

    def set_debug(self, dbug):
        """dbug is an integer which means 0:Enable, 1:Disable"""
        self._set_data("dbug", chr(dbug))

    def get_version(self):
        """returns version in d.d format"""
        return "%d.%d" % struct.unpack(WIZNET_VERSION_FORMAT, self._get_data("ver"))

    def set_version(self, ver):
        """ver is in d.d format"""
        self._set_data("ver", struct.pack(WIZNET_VERSION_FORMAT, *[int(i) for i in ver.split(".")]))

    def get_dhcp(self):
        """returns an integer which means 0:Static, 1:DHCP, 2:PPPoE"""
        return ord(self._get_data("dhcp"))

    def set_dhcp(self, dhcp):
        """dhcp is an integer which means 0:Static, 1:DHCP, 2:PPPoE"""
        self._set_data("dhcp", chr(dhcp))

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
        """sends a broadcast message to find all wiznet devices on network"""
        self.device_list = []
        self.socket.sendto(WIZNET_SEARCH_COMMAND, ("<broadcast>", WIZNET_REMOTE_UDP_PORT))

    def get_device_list(self):
        """returns a list of devices, you should call search method and wait a few seconds before using this"""
        return self.device_list

if __name__ == "__main__":
    f = DeviceFinder()
    f.search()
    time.sleep(1)
    print f.get_device_list()
    time.sleep(2)