import pytest
import re
import subprocess

from pynetlinux import ifconfig


def interface(request, name):
    i = ifconfig.Interface(name)
    ip = i.ip
    mac = i.mac
    netmask = i.netmask
    i.up()

    def cleanup():
        i.ip = ip
        i.mac = mac
        i.netmask = netmask
        i.up()
    request.addfinalizer(cleanup)

    return i


@pytest.fixture
def if1(request):
    return interface(request, 'eth1')


@pytest.fixture
def if2(request):
    return interface(request, 'eth2')


def check_output(shell_cmd, regex=[], substr=[], not_regex=[], not_substr=[],
                 debug=False):
    assert regex or substr or not_regex or not_substr
    output = subprocess.check_output(shell_cmd, stderr=subprocess.STDOUT,
                                     shell=True)
    if debug:
        print regex, substr, not_regex, not_substr
        print output
    for s in substr:
        assert s in output
    for r in regex:
        assert re.search(r, output, re.MULTILINE)
    for s in not_substr:
        assert s not in output
    for r in not_regex:
        assert not re.search(r, output, re.MULTILINE)
