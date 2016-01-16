import binascii
import codecs
import pytest
import select
import socket
import struct


from pynetlinux import tap
from pynetlinux import ifconfig
from tests.conftest import check_output

# from linux/if_ether.h
ETH_P_ALL = 0x0003
# from linux/if_packet.h
PACKET_ADD_MEMBERSHIP = 1
PACKET_MR_PROMISC = 1
# from bits/socket.h
SOL_PACKET = 263


def test_tap_create():
    t = tap.Tap()
    assert ifconfig.findif(t.name, physical=False) is not None
    assert t.fd
    assert t.name


def test_tap_close():
    t = tap.Tap()
    t.close()
    assert ifconfig.findif(t.name, physical=False) is None


def test_tap_persistent():
    name = b'test_tap'

    t1 = tap.Tap(name)
    t1.persist()
    t1.close()
    assert ifconfig.findif(name, physical=False) is not None

    t2 = tap.Tap(name)
    t2.unpersist()
    t2.close()
    assert ifconfig.findif(name, physical=False) is None


def test_tap_write():
    t = tap.Tap()
    pre_stats = t.get_stats()
        
    tap_mac = b''.join(codecs.decode(i, 'hex') for i in t.mac.split(':'))
    # fake ethernet packet addressed to the tap interface
    packet = tap_mac + b'\x00\x11"3DU\x90\x00fake payload'
    t.write(packet)

    post_stats = t.get_stats()

    assert post_stats['rx_packets'] == pre_stats['rx_packets'] + 1
    assert post_stats['rx_bytes'] == pre_stats['rx_bytes'] + len(packet)


def test_tap_read():
    t = tap.Tap(blocking=False)
    t.up()

    # create raw layer 2 socket
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW,
                      socket.htons(ETH_P_ALL))
    s.bind((t.name.decode('ascii'), ETH_P_ALL))

    # fake ethernet packet
    packet = b'\xde\xad\xbe\xef\xde\xad\x00\x11"3DU\x90\x00fake payload'
    s.send(packet)

    while True:
        r, _, _ = select.select([t.fd], [], [], 3)
        assert r, 'did not receive expected packet - timed out'
        if t.fd.read(1500) == packet:
            break
