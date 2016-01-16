# See Vagrantfile for how the network layout

import pytest
import re

from pynetlinux import ifconfig
from tests.conftest import check_output


def test_list_all_ifs():
    ifs = ifconfig.list_ifs(physical=False)
    expected = set([b'eth0', b'eth1', b'eth2', b'lo'])
    assert expected <= set(i.name for i in ifs)


def test_list_ifs_physical_only():
    ifs = ifconfig.list_ifs()
    expected = set([b'eth0', b'eth1', b'eth2'])
    assert set(i.name for i in ifs) == expected


def test_findif(if1, if2):
    for i in [if1, if2]:
        i2 = ifconfig.findif(i.name)
        assert i2 is not None
        assert i2.name == i.name


def test_up_down(if1):
    if1.down()
    assert not if1.is_up()
    check_output(b'ip link show ' + if1.name,
                 regex=[if1.name + br': <.+>'], not_substr=[b'UP'])
    if1.up()
    assert if1.is_up()
    check_output(b'ip link show ' + if1.name,
                 regex=[if1.name + br': <.+>'], substr=[b'UP'])


def test_get_mac(if1):
    assert re.match(r'[0-9A-F]{2}(:[0-9A-F]{2}){3}', if1.mac)


def test_set_mac(if1):
    if1.mac = '00:11:22:33:44:55'
    assert if1.mac == '00:11:22:33:44:55'
    check_output(b'ip link show ' + if1.name,
                 substr=[b'link/ether 00:11:22:33:44:55'])


@pytest.mark.xfail
def test_set_mac_invalid(if1):
    with pytest.raises(ValueError) as e:
        if1.mac = 'invalid mac address'
    assert 'invalid mac address format' in str(e)


def test_get_netmask(if1):
    assert (8 < if1.netmask <= 30)


def test_set_netmask(if1):
    if1.netmask = 16
    assert if1.netmask == 16
    check_output(b'ip addr show ' + if1.name,
                 regex=[br'inet [0-9\.]+/16'])

    if1.netmask = 21
    assert if1.netmask == 21
    check_output(b'ip addr show ' + if1.name,
                 regex=[br'inet [0-9\.]+/21'])


def test_get_index(if1, if2):
    for i in [if1, if2]:
        idx = str(i.index).encode('ascii')
        check_output(b'ip link show ' + i.name,
                     substr=[idx + b': ' + i.name + b':'])


@pytest.mark.xfail
def test_set_netmask_invalid(if1):
    with pytest.raises(ValueError) as e:
        if1.netmask = 100
    assert 'invalid netmask' in str(e)


@pytest.mark.parametrize('thousand', [True, False])
@pytest.mark.parametrize('hundred', [True, False])
@pytest.mark.parametrize('ten', [True, False])
def test_set_link_auto(if1, ten, hundred, thousand):
    expected = br'Advertised link modes:\s+'
    if ten:
        expected += br'10baseT/Half 10baseT/Full\s+'
    if hundred:
        expected += br'100baseT/Half 100baseT/Full\s+'
    if thousand:
        expected += br'1000baseT/Full'

    if1.set_link_auto(ten, hundred, thousand)
    check_output(b'ethtool ' + if1.name, regex=[expected])


def test_pause_param_autonegotiate(if1):
    if1.set_pause_param(True, True, True)
    check_output(b'ethtool -a ' + if1.name,
                 regex=[br'Autonegotiate:\s+on'])

    if1.set_pause_param(False, True, True)
    check_output(b'ethtool -a ' + if1.name,
                 regex=[br'Autonegotiate:\s+off'])

@pytest.mark.parametrize('tx', [True, False])
@pytest.mark.parametrize('rx', [True, False])
def test_pause_param_settings(if1, rx, tx):
    if1.set_pause_param(False, rx, tx)
    expected = [
        br'Autonegotiate:\s+off',
        br'RX:\s+' + (b'on' if rx else b'off'),
        br'TX:\s+' + (b'on' if tx else b'off'),
    ]
    check_output(b'ethtool -a ' + if1.name, regex=expected)

