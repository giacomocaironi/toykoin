from toykoin.daemon.node import Node
from toykoin.daemon.messages import add_headers, Debug
from toykoin.core.utils import reset_blockchain

import time


def test_basic_connection():
    try:
        node1 = Node(10000, "node1")
        node2 = Node(20000, "node2")
        node1.start()
        node2.start()
        node1.connect("0.0.0.0", 20000)
        time.sleep(0.2)
        node1.connections[0].send(Debug(payload=b"").serialize())
        time.sleep(0.2)
        assert node2.connections[0].messages == [["debug", b""]]
        node1.connections[0].send(Debug(payload=b"\x01").serialize())
        time.sleep(0.2)
        assert node2.connections[0].messages == [["debug", b""], ["debug", b"\x01"]]
        assert node2.connections[0].buffer == b""
    finally:
        node1.stop()
        node2.stop()
        reset_blockchain("node1")
        reset_blockchain("node2")


def test_invalid_headers():
    try:
        node1 = Node(10000, "node1")
        node2 = Node(20000, "node2")
        node1.start()
        node2.start()
        node1.connect("0.0.0.0", 20000)
        time.sleep(0.2)
        node1.connections[0].send(Debug(payload=b"").serialize() + b"\x01")
        time.sleep(0.2)
        assert node2.connections[0].messages == []
        assert node2.connections[0].buffer != b""
        node1.connections[0].send(Debug(payload=b"").serialize())
        time.sleep(0.2)
        assert node2.connections[0].messages == [["debug", b""]]
        assert node2.connections[0].buffer == b""
    finally:
        node1.stop()
        node2.stop()
        reset_blockchain("node1")
        reset_blockchain("node2")


def test_split_message():
    try:
        node1 = Node(10000, "node1")
        node2 = Node(20000, "node2")
        node1.start()
        node2.start()
        node1.connect("0.0.0.0", 20000)
        time.sleep(0.2)
        msg = b"regtest" + add_headers("debug", b"")
        node1.connections[0].socket.sendall(msg[:4])
        time.sleep(0.2)
        assert node2.connections[0].buffer != b""
        node1.connections[0].socket.sendall(msg[4:])
        time.sleep(0.2)
        assert node2.connections[0].messages == [["debug", b""]]
        assert node2.connections[0].buffer == b""
    finally:
        node1.stop()
        node2.stop()
        reset_blockchain("node1")
        reset_blockchain("node2")


def test_split_message_2():
    try:
        node1 = Node(10000, "node1")
        node2 = Node(20000, "node2")
        node1.start()
        node2.start()
        node1.connect("0.0.0.0", 20000)
        time.sleep(0.2)
        node1.sendall(Debug(payload=b"\x01" * 8192).serialize())
        time.sleep(0.2)
        assert node2.connections[0].messages == [["debug", b"\x01" * 8192]]
        assert node2.connections[0].buffer == b""
    finally:
        node1.stop()
        node2.stop()
        reset_blockchain("node1")
        reset_blockchain("node2")


def test_shutdown():
    try:
        node1 = Node(10000, "node1")
        node2 = Node(20000, "node2")
        node1.start()
        node2.start()
        node1.connect("0.0.0.0", 20000)
        time.sleep(0.2)
        node2.connections[0].stop()
        time.sleep(0.2)
        assert node2.connections == []
    finally:
        node1.stop()
        node2.stop()
        reset_blockchain("node1")
        reset_blockchain("node2")
