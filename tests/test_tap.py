import binascii
import pytest
import types
from scapy.all import sendp, Ether

from pynetlinux import tap
from pynetlinux import ifconfig
from tests.conftest import check_output


def test_tap_create():
    t = tap.Tap()
    assert ifconfig.findif(t.name, physical=False) is not None
    assert isinstance(t.fd, types.FileType)
    assert t.name


def test_tap_close():
    t = tap.Tap()
    t.close()
    assert ifconfig.findif(t.name, physical=False) is None


def test_tap_persistent():
    name = 'test_tap'

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

    packet = str(Ether(dst=t.mac, src='00:11:22:33:44:55') / "fake payload")
    t.write(packet)

    post_stats = t.get_stats()

    assert post_stats['rx_packets'] == pre_stats['rx_packets'] + 1
    assert post_stats['rx_bytes'] == pre_stats['rx_bytes'] + len(packet)


def test_tap_read():
    t = tap.Tap()
    t.up()

    packet = str(Ether(dst='de:ad:be:ef:de:ad', src='00:11:22:33:44:55') /
                 "fake payload")
    
    sendp(packet, iface=t.name, verbose=False)
    received = t.read(len(packet))

    assert received == packet
