import pytest

from pynetlinux import brctl
from tests.conftest import check_output


def bridge(request, name):
    br = brctl.addbr(name)
    def cleanup():
        br.delete()
    request.addfinalizer(cleanup)
    return br


@pytest.fixture
def br1(request):
    return bridge(request, 'br_test1')

@pytest.fixture
def br2(request):
    return bridge(request, 'br_test2')


def test_addbr_delete():
    br = brctl.addbr('br_test')
    try:
        check_output('brctl show', substr=[br.name])
    finally:
        br.delete()
    check_output('brctl show', not_substr=[br.name])


def test_findbridge(br1):
    br2 = brctl.findbridge(br1.name)
    assert br2 is not None
    assert br2.name == br1.name


def test_list_bridges(br1, br2):
    expected = {br1.name, br2.name}
    actual = set(br.name for br in brctl.list_bridges())
    assert expected <= actual


def test_iterbridges(br1, br2):
    expected = {br1.name, br2.name}
    actual = set(br.name for br in brctl.iterbridges())
    assert expected <= actual


def test_findif_existent(br1, br2):
    br1.addif('eth1')
    br2.addif('eth2')

    res = brctl.findif('eth1')
    assert res is not None
    assert res.name == br1.name

    res = brctl.findif('eth2')
    assert res is not None
    assert res.name == br2.name


def test_findif_nonexistent(br1, br2):
    br1.addif('eth1')
    br2.addif('eth2')
    res = brctl.findif('foobar')
    assert res is None


def test_addif(br1):
    cmd = 'brctl show {}'.format(br1.name)
    check_output(cmd, not_substr=['eth1', 'eth2'])
    br1.addif('eth1')
    check_output(cmd, substr=['eth1'], not_substr=['eth2'])
    br1.addif('eth2')
    check_output(cmd, substr=['eth1', 'eth2'])


def test_delif(br1):
    cmd = 'brctl show {}'.format(br1.name)
    br1.addif('eth1')
    check_output(cmd, substr=['eth1'])
    br1.delif('eth1')
    check_output(cmd, not_substr=['eth1'])


def test_listif(br1):
    br1.addif('eth1')
    br1.addif('eth2')
    expected = {'eth1', 'eth2'}
    actual = set(br1.listif())
    assert expected == actual


def test_iterifs(br1):
    br1.addif('eth1')
    br1.addif('eth2')
    expected = {'eth1', 'eth2'}
    actual = set(br1.iterifs())
    assert expected == actual


def test_set_forward_delay(br1):
    for value in [50, 100, 1000]:
        br1.set_forward_delay(value)
        check_output('brctl showstp {}'.format(br1.name),
                     regex=[r'forward delay\s+{}'.format(value)])


def test_get_ip(br1):
    assert br1.ip == '0.0.0.0'
    assert br1.get_ip() == '0.0.0.0'


def test_set_ip(br1):
    with pytest.raises(AttributeError):
        br1.ip = '1.1.1.1'
