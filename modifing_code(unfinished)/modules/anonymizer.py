from random import shuffle, randint
import re as regex
import ipaddress

class Anonymizer:
    def __init__(self, hosts_pool, other_pool):
        #两个下划线开头的函数是声明该属性为私有，不能在类的外部被使用或访问
        #_init__函数（方法）支持带参数类的初始化，也可为声明该类的属性（类中的变量）
        ##__init__函数（方法）的第一个参数必须为self，后续参数为自己定义,__init__()方法又被称为构造器（constructor）
        self.hpool = hosts_pool
        self.opool = other_pool
        self.map = {}
        shuffle(self.hpool)
        #anonym = Anonymizer(config_module.HOSTS_POOL, config_module.OTHERS_POOL)

    def add_host(self, original):   #随机生成了一个ip对应关系
        IP_map = {}
        new_addr = self.hpool.pop()
        #pop()将列表指定位置的元素移除，不填写位置参数则默认删除最后一位
        self.map[original] = {'new' : new_addr, 'omap' : {}, 'pool' : [x for x in self.opool]}
        shuffle(self.map[original]['pool'])
        #print(original,self.map[original]['new'])
        IP_map[original] = self.map[original]['new']
        return IP_map  

    def anonimize(self, packet, host_list):   #anonimize：匿名化

        IP_map = {}

        host_list = set(host_list)
        if(packet.ip_src in host_list):
            original = packet.ip_src
            try :hostmap = self.map[original]
            except IndexError: raise ValueError('The host must be added before trying to anonimize')
                                                    #在尝试anonimize之前，必须添加主机
            packet.ip_src = hostmap['new']
            try : packet.ip_dst = hostmap['omap'][packet.ip_dst]
            except KeyError: # The other_host has not been seen for this host  说明之前没用过 new
                other = hostmap['pool'].pop()
                hostmap['omap'][packet.ip_dst] = other
                IP_map[packet.ip_dst] = other
                packet.ip_dst = other
                

        elif(packet.ip_dst in host_list):
            original = packet.ip_dst
            try :hostmap = self.map[original]
            except IndexError: raise ValueError('The host must be added before trying to anonimize')
                                                    #在尝试anonimize之前，必须添加主机
            packet.ip_dst = hostmap['new']
            try : packet.ip_src = hostmap['omap'][packet.ip_src]
            except KeyError: # The other_host has not been seen for this host
                other = hostmap['pool'].pop()
                hostmap['omap'][packet.ip_src] = other
                IP_map[packet.ip_src] = other
                packet.ip_src = other

        return IP_map



class IpAnonymizer:
    def __init__(self, anonimize_private = False):
        self.map = {}
        self.anon_private = anonimize_private

    @staticmethod
    def generate_ip():
        new_addr = '.'.join([str(randint(1, 254)) for x in range(4)])
        ip_addr = ipaddress.ip_address(new_addr)
        while ip_addr.is_private or ip_addr.is_multicast or ip_addr.is_link_local:
            new_addr = '.'.join([str(randint(1, 254)) for x in range(4)])
            ip_addr = ipaddress.ip_address(new_addr)

        return new_addr

    def anonimize(self, addr):
        ipaddr = ipaddress.ip_address(addr)

        if ipaddr.is_multicast or ipaddr.is_link_local:
            return addr
        if self.anon_private == False and ipaddr.is_private:
            return addr

        if addr in self.map:
            return self.map[addr]


        new_addr = IpAnonymizer.generate_ip()
        while new_addr in self.map.values():
            new_addr = IpAnonymizer.generate_ip()

        self.map[addr] = new_addr
        return new_addr
