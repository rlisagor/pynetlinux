# See Vagrantfile for how the network layout

import pytest
import re

from pynetlinux import ifconfig
from tests.conftest import check_output


def test_list_all_ifs():
    ifs = ifconfig.list_ifs(physical=False)
    expected = set(['eth0', 'eth1', 'eth2', 'lo'])
    assert set(i.name for i in ifs) == expected


def test_list_ifs_physical_only():
    ifs = ifconfig.list_ifs()
    expected = set(['eth0', 'eth1', 'eth2'])
    assert set(i.name for i in ifs) == expected


def test_findif(if1, if2):
    for i in [if1, if2]:
        i2 = ifconfig.findif(i.name)
        assert i2 is not None
        assert i2.name == i.name


def test_up_down(if1):
    if1.down()
    assert not if1.is_up()
    check_output('ip link show {}'.format(if1.name),
                 regex=[r'{}: <.+>'.format(if1.name)], not_substr=['UP'])
    if1.up()
    assert if1.is_up()
    check_output('ip link show {}'.format(if1.name),
                 regex=[r'{}: <.+>'.format(if1.name)], substr=['UP'])


def test_get_mac(if1):
    assert re.match(r'[0-9A-F]{2}(:[0-9A-F]{2}){3}', if1.mac)


def test_set_mac(if1):
    if1.mac = '00:11:22:33:44:55'
    assert if1.mac == '00:11:22:33:44:55'
    check_output('ip link show {}'.format(if1.name),
                 substr=['link/ether 00:11:22:33:44:55'])


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
    check_output('ip addr show {}'.format(if1.name),
                 regex=[r'inet [0-9\.]+/16'])

    if1.netmask = 21
    assert if1.netmask == 21
    check_output('ip addr show {}'.format(if1.name),
                 regex=[r'inet [0-9\.]+/21'])


def test_get_index(if1, if2):
    for i in [if1, if2]:
        idx = i.index
        check_output('ip link show {}'.format(i.name),
                     substr=['{idx}: {name}:'.format(idx=idx, name=i.name)])


@pytest.mark.xfail
def test_set_netmask_invalid(if1):
    with pytest.raises(ValueError) as e:
        if1.netmask = 100
    assert 'invalid netmask' in str(e)


@pytest.mark.parametrize('thousand', [True, False])
@pytest.mark.parametrize('hundred', [True, False])
@pytest.mark.parametrize('ten', [True, False])
def test_set_link_auto(if1, ten, hundred, thousand):
    expected = r'Advertised link modes:\s+'
    if ten:
        expected += r'10baseT/Half 10baseT/Full\s+'
    if hundred:
        expected += r'100baseT/Half 100baseT/Full\s+'
    if thousand:
        expected += r'1000baseT/Full'

    if1.set_link_auto(ten, hundred, thousand)
    check_output('ethtool {}'.format(if1.name), regex=[expected])


def test_pause_param_autonegotiate(if1):
    if1.set_pause_param(True, True, True)
    check_output('ethtool -a {}'.format(if1.name),
                 regex=[r'Autonegotiate:\s+on'])

    if1.set_pause_param(False, True, True)
    check_output('ethtool -a {}'.format(if1.name),
                 regex=[r'Autonegotiate:\s+off'])

@pytest.mark.parametrize('tx', [True, False])
@pytest.mark.parametrize('rx', [True, False])
def test_pause_param_settings(if1, rx, tx):
    if1.set_pause_param(False, rx, tx)
    expected = [
        r'Autonegotiate:\s+off',
        r'RX:\s+' + ('on' if rx else 'off'),
        r'TX:\s+' + ('on' if tx else 'off'),
    ]
    check_output('ethtool -a {}'.format(if1.name), regex=expected)

