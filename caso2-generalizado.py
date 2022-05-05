#!/usr/bin_/python

from ast import Num
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

NUM_SUC = range(6)
router_list = []
host_list = []
s_wan_list = []
s_lan_list = []

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    info( '*** Add switches\n')
    for i in NUM_SUC:
        s_wan = net.addSwitch('s{}_wan'.format(i), cls=OVSKernelSwitch, failMode='standalone')
        s_wan_list.append(s_wan)

    for i in NUM_SUC:
        s_lan = net.addSwitch('s{}_lan'.format(i), cls=OVSKernelSwitch, failMode='standalone')
        s_lan_list.append(s_lan)
      
    r_central = net.addHost('r_central', cls=Node, ip='')
    for i in NUM_SUC:
        r = net.addHost('r' + str(i), cls=Node, ip='')
        router_list.append(r)

    r_central.cmd('sysctl -w net.ipv4.ip_forward=1')
    for i in router_list:
        i.cmd('sysctl -w net.ipv4.ip_forward=1')

    info( '*** Add hosts\n')
    for i in NUM_SUC:
        h = net.addHost('h' + str(i), cls=Host, ip='10.0.{}.254/24'.format(i+1), defaultRoute='via 10.0.{}.1'.format(i+1))
        host_list.append(h)

    info( '*** Add links\n')
    #Links router central a switches WAN
    j = 0
    k = 6
    for i in s_wan_list:
        net.addLink(r_central, i, intfName1='r_central-eth{}'.format(j), params1={ 'ip' : '192.168.100.{}/29'.format(k)})
        k += 8
        j += 1

    #Links router a switches WAN
    k = 1
    for i in NUM_SUC:
        net.addLink(router_list[i], s_wan_list[i], intfName1='r{}-eth0'.format(i), params1={ 'ip' : '192.168.100.{}/29'.format(k) })
        k += 8

    #Links router a switches LAN
    for i in NUM_SUC:
        net.addLink(router_list[i], s_lan_list[i], intfName1='r{}-eth1'.format(i), params1={ 'ip' : '10.0.{}.1/24'.format(i+1)})
    
    #Links hosts a switches LAN
    for i in NUM_SUC:
        net.addLink(host_list[i], s_lan_list[i])

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    #info( '*** Starting switches\n')
    net.start()

    info( '*** Post configure switches and hosts\n')
    j = 1
    for i in NUM_SUC:
        net['r_central'].cmd('ip route add 10.0.{}.0/24 via 192.168.100.{}'.format(i+1, j))
        for k in NUM_SUC:
            net['r{}'.format(i)].cmd('ip route add 10.0.{}.0/24 via 192.168.100.{}'.format(k+1, j+5))
            print(j)
        j += 8





    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()