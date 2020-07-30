#!/usr/bin/env python3

# Copyright (C) 2017-2020 The btclib developers
#
# This file is part of btclib. It is subject to the license terms in the
# LICENSE file found in the top-level directory of this distribution.
#
# No part of btclib including this file, may be copied, modified, propagated,
# or distributed except according to the terms contained in the LICENSE file.

from toykoin.daemon.connection import Connection
from toykoin.daemon.mempool import Mempool
from toykoin.core.blockchain import Blockchain

import socket
import threading
import time


class Node(threading.Thread):
    def __init__(self, port=18888, name="regtest", network="regtest"):
        super().__init__()

        self.blockchain = Blockchain(name)
        self.mempool = Mempool(name)

        self.network = network
        self.connections = []

        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("0.0.0.0", self.port))
        self.server_socket.listen()
        self.server_socket.settimeout(0.0)

        self.lock = threading.Lock()
        self.terminate_flag = threading.Event()

    def run(self):
        while not self.terminate_flag.is_set():
            try:
                conn, address = self.server_socket.accept()
                new_connection = Connection(conn, address, self)
                new_connection.start()
                self.connections.append(new_connection)
            except socket.error:
                pass
            with self.lock:
                for conn in self.connections:
                    if not conn.is_alive():
                        self.connections.remove(conn)
            time.sleep(0.1)

    def stop(self):
        self.terminate_flag.set()
        self.server_socket.close()
        for conn in self.connections:
            conn.stop()
        for conn in self.connections:
            conn.join()
            self.connections.remove(conn)

    def connect(self, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        new_connection = Connection(sock, (ip, port), self)
        new_connection.start()
        self.connections.append(new_connection)

    def sendall(self, data):
        for conn in self.connections:
            conn.send(data)


BUFFER_SIZE = 1024
