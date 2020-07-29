from toykoin.daemon.node import Node
from toykoin.daemon.connection import add_headers
from toykoin.core.utils import reset_blockchain

import time

def test_basic_connection():
    try:
        node1 = Node(10000, 'node1')
        node2 = Node(20000, 'node2')
        node1.start()
        node2.start()
        node1.connect('0.0.0.0', 20000)
        time.sleep(0.1)
        node1.connections[0].send(add_headers('version', b''))
        time.sleep(0.1)
        print(node1.connections)
        assert node2.connections[0].messages == [[b'version', b'']]
        node1.connections[0].send(add_headers('a', b'\x01'))
        time.sleep(0.1)
        assert node2.connections[0].messages == [[b'version', b''], [b'a', b'\x01']]
    finally:
        node1.stop()
        node2.stop()
        reset_blockchain('node1')
        reset_blockchain('node2')
