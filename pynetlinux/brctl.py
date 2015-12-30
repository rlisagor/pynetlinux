import array
import fcntl
import struct

import os

import ifconfig

SYSFS_NET_PATH = "/sys/class/net"

# From linux/sockios.h
SIOCBRADDBR = 0x89a0
SIOCBRDELBR = 0x89a1
SIOCBRADDIF = 0x89a2
SIOCBRDELIF = 0x89a3

SIOCDEVPRIVATE = 0x89F0

# From bridge-utils if_bridge.h
BRCTL_SET_BRIDGE_FORWARD_DELAY = 8
BRCTL_SET_BRIDGE_STP_STATE = 14
BRCTL_GET_BRIDGE_INFO = 6

if not os.path.isdir(SYSFS_NET_PATH):
    raise ImportError("Path %s not found. This module requires sysfs." % SYSFS_NET_PATH)


class Bridge(ifconfig.Interface):
    ''' Class representing a Linux Ethernet bridge. '''

    def __init__(self, name):
        ifconfig.Interface.__init__(self, name)

    def iterifs(self):
        ''' Iterate over all the interfaces in this bridge. '''
        if_path = os.path.join(SYSFS_NET_PATH, self.name, "brif")
        net_files = os.listdir(if_path)
        for iface in net_files:
            yield iface

    def listif(self):
        ''' List interface names. '''
        return [p for p in self.iterifs()]

    def addif(self, iface):
        ''' Add the interface with the given name to this bridge. Equivalent to
            brctl addif [bridge] [interface]. '''
        if type(iface) == ifconfig.Interface:
            devindex = iface.index
        else:
            devindex = ifconfig.Interface(iface).index
        ifreq = struct.pack('16si', self.name, devindex)
        fcntl.ioctl(ifconfig.sockfd, SIOCBRADDIF, ifreq)
        return self

    def delif(self, iface):
        ''' Remove the interface with the given name from this bridge.
            Equivalent to brctl delif [bridge] [interface]'''
        if type(iface) == ifconfig.Interface:
            devindex = iface.index
        else:
            devindex = ifconfig.Interface(iface).index
        ifreq = struct.pack('16si', self.name, devindex)
        fcntl.ioctl(ifconfig.sockfd, SIOCBRDELIF, ifreq)
        return self

    def set_stp_mode(self, status):
        '''Set the status of spanning tree on bridge. Called using bridge.set_stp_mode([True,False])'''
        if status is True:
            status = 1
        else:
            status = 0
        data = array.array('L', [BRCTL_SET_BRIDGE_STP_STATE, status, 0, 0])
        buffer, _items = data.buffer_info()
        ifreq = struct.pack('16sP', self.name, buffer)
        fcntl.ioctl(ifconfig.sockfd, SIOCDEVPRIVATE, ifreq)
        return True

    def set_forward_delay(self, delay):
        ''' Set the given bridge forward delay (in seconds). '''
        # delay is passed to kernel in "jiffies" (100ths of a second)
        jiffies = int(delay * 100)
        data = array.array('L', [BRCTL_SET_BRIDGE_FORWARD_DELAY, jiffies, 0, 0])
        buffer, _items = data.buffer_info()
        ifreq = struct.pack('16sP', self.name, buffer)
        fcntl.ioctl(ifconfig.sockfd, SIOCDEVPRIVATE, ifreq)
        return self

    def delete(self):
        ''' Brings down the bridge interface, and removes it. Equivalent to
        ifconfig [bridge] down && brctl delbr [bridge]. '''
        self.down()
        fcntl.ioctl(ifconfig.sockfd, SIOCBRDELBR, self.name)
        return self

    def get_ip(self):
        ''' Bridges don't have IP addresses, so this always returns 0.0.0.0. '''
        return "0.0.0.0"

    ip = property(get_ip)

    def iterfdb(self):
        ''' Iterate over all client addresses in the FDB of this bridge. '''
        interfaces = dict()
        for (index, iface) in enumerate(self.iterifs(), start=1):
            interfaces[index] = iface
        fdb_path = os.path.join(SYSFS_NET_PATH, self.name, "brforward")
        with open(fdb_path, "r") as f:
            fdb = f.read()  # proc file only works if read all at once
            offset = 0
            while offset < len(fdb):
                (m1, m2, m3, m4, m5, m6, port, local, age_timer,
                 port_hi, pad1, pad2) = struct.unpack(
                        "BBBBBBBBIBBH", fdb[offset:offset + 16])
                mac = "%02x:%02x:%02x:%02x:%02x:%02x" % (m1, m2, m3, m4, m5, m6)
                iface = interfaces.get(port, "unknown")
                is_local = True if local else False
                yield (mac, iface, is_local, age_timer)
                offset += 16


def shutdown():
    ''' Shut down bridge library '''
    ifconfig.shutdown()


def iterbridges():
    ''' Iterate over all the bridges in the system. '''
    net_files = os.listdir(SYSFS_NET_PATH)
    for d in net_files:
        path = os.path.join(SYSFS_NET_PATH, d)
        if not os.path.isdir(path):
            continue
        if os.path.exists(os.path.join(path, "bridge")):
            yield Bridge(d)


def list_bridges():
    ''' Return a list of the names of the bridge interfaces. '''
    return [br for br in iterbridges()]


def addbr(name):
    ''' Create new bridge with the given name '''
    fcntl.ioctl(ifconfig.sockfd, SIOCBRADDBR, name)
    return Bridge(name)


def findif(name):
    ''' Find the given interface name within any of the bridges. Return the
        Bridge object corresponding to the bridge containing the interface, or
        None if no such bridge could be found. '''
    for br in iterbridges():
        if name in br.iterifs():
            return br
    return None


def findbridge(name):
    ''' Find the given bridge. Return the Bridge object, or None if no such
        bridge could be found. '''
    for br in iterbridges():
        if br.name == name:
            return br
    return None
