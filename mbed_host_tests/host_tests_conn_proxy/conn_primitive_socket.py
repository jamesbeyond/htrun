#!/usr/bin/env python
"""
mbed SDK
Copyright (c) 2011-2016 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


import time
import socket
from .conn_primitive import ConnectorPrimitive, ConnectorPrimitiveException


class SocketConnectorPrimitive(ConnectorPrimitive):
    # TBD is config necessary to pass over?
    def __init__(self, name, address, port):
        ConnectorPrimitive.__init__(self, name)
        self.address = address
        self.port = port
        self.read_timeout = 2
        self.target_id = None
        self.polling_timeout = 60
        self.socket = None

        # TBD DOSE this need function to check the socket port or address ???
        """
        socket_port = HostTestPluginBase().check_socket_port_ready(self.port, target_id=self.target_id, timeout=self.polling_timeout)
        if socket_port is None:
            #raise ConnectorPrimitiveException("Socket port not ready!")
        
        if socket_port != self.port:
            # socket port changed for given targetID
            self.logger.prn_inf("socket port changed from '%s to '%s')"% (self.port, socket_port))
            self.port = socket_port
        """

        startTime = time.time()
        self.logger.prn_inf("socket(address=%s, port=%s) read_timeout=%s"% (self.address, self.port, self.read_timeout))
        while time.time() - startTime < self.polling_timeout:
            try:
                # TBD what is TIMEOUT mean in socket condition
                # TIMEOUT: While creating Socket object timeout is delibrately passed as 0. Because blocking in socket.read
                # impacts thread and mutliprocess functioning in Python. Hence, instead in self.read() s delay (sleep()) is
                # inserted to let serial buffer collect data and avoid spinning on non blocking read().
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.address, int(self.port)))
                self.socket.settimeout(self.read_timeout)
            except socket.error as e:
                self.socket = None
                # TBD remove "SOCKET" in the error messsage
                self.LAST_ERROR = "SOCKET>>> connection lost, socket.connect(%s, %s)\nError: %s"% (self.address,
                    self.port,
                    str(e))
                self.logger.prn_err(str(e))
                self.logger.prn_err("SOCKET>>> Retry after 1 sec until %s seconds"% self.polling_timeout)
            else:
                break
            time.sleep(1)


    def read(self, count):
        """! Read data from socket buffer """
        # TIMEOUT: Since read is called in a loop, wait for self.timeout period before calling socket.read(). See
        # comment on self.socket() call above about timeout.
        # time.sleep(self.read_timeout)
        c = str()
        try:
            if self.connected():
                c = self.socket.recv(count)
        except socket.timeout as eto:
            #catch the timeout exception, when no data in the socket buffer. this will unblock the read()
            self.logger.prn_inf("SOCKET>>> socket read timeout: %s"% str(eto))
            return 0
        except socket.error as e:
            self.socket = None
            self.LAST_ERROR = "SOCKET READ>>> connection lost, socket.recv(%d): %s"% (count, str(e))
            self.logger.prn_err(str(e))
        return c

    def write(self, payload, log=False):
        """! Write data to socket buffer """
        try:
            if self.connected():
                self.socket.sendall(payload)
                if log:
                    self.logger.prn_txd(payload)
                return True
        except socket.error as e:
            self.socket = None
            self.LAST_ERROR = "SOCKET WRITE>>> connection lost, socket.sendall(%d bytes): %s"% (len(payload), str(e))
            self.logger.prn_err(str(e))
        return False

    def flush(self):
        if self.connected():
            self.logger.prn_inf("SOCKET>>> FLUSH SOCKET")
            self.socket.sendall('')

    def connected(self):
        return bool(self.socket)

    def finish(self):
        if self.connected():
            self.socket.close()
            self.logger.prn_inf("SOCKET>>> CLOSE SOCKET")
        self.socket = None

    def reset(self):
        self.logger.prn_inf("SOCKET>>> socket not support reset")

    def __del__(self):
        self.finish()

