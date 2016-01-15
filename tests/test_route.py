import pytest
import subprocess
import re

from pynetlinux import route


def test_route():
    cmd = 'ip route show'
    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    match = re.search(r'default via ([^ ]+) dev ([^ ]+)', output)
    assert match, 'this test requires a default route to be present'
    assert match.group(1) == route.get_default_gw()
    assert match.group(2) == route.get_default_if()
