#!/usr/bin/env python3
import os
import sys
import random
from datetime import datetime as dt

def main(config_module):
    from packet import Packet
    from easycolor import ecprint
    from anonymizer import Anonymizer

    common_time = dt.now()                          #OBTENEMOS UN TIEMPO COMÚN AL QUE TRASLADAR LAS TRAZAS我们有一个共同的时间来移动轨迹
    #datetime.now()：读取的时间是系统的本地时间
    
    anonym = Anonymizer(config_module.HOSTS_POOL, config_module.OTHERS_POOL)

    host_list = {}

    cf = config_module.COMPRESSION_FACTOR
    #时间压缩因子。设置1表示无压缩

    #第一步：将每个pcap写入临时csv文件
    with open(config_module.MAP_FILE, 'r') as f:
        f.readline()								#ignoramos la cabecera del csv 忽略CSV标头
        for line in f:
            p_data = line.split('\n')[0].split(',')
            host_list['host_ip'] = p_data[0]

    anonym.add_host(host_list['host_ip'])


    with open(config_module.D_FILE, 'r') as f, open(config_module.DATA_FILE, 'w') as dstf:
        f.readline()								#ignoramos la cabecera del csv 忽略CSV标头
        for line in f:
            packet = Packet.from_csv_line(line)    #返回一个提取出来的数组TCP_Packet、UDP_Packet、IP_Packet
            if packet == None: continue						#error en el parser解析器错

            anonym.anonimize(packet, original = host_list['host_ip'])      		#Anonimizamos las ips我们匿名的PSU
            #用新的ip数组代替了原来的 完成匿名化
            dstf.write(packet.as_csv_line())					#Append packets to the tmp file将数据包附加到tmp文件

    if config_module.VERBOSE : ecprint(config_module.DATA_FILE, c='blue', template = 'saved merged traces : {}')

    ##Save the target map --> address - activity
    #if config_module.VERBOSE : ecprint('Saving targetmap', c='green')
    #with open(config_module.TARGET_FILE, 'w') as f:
    #    f.write('host,target\n')
    #    for t in readed_traces:
    #        f.write('{},{}\n'.format(t['host'], t['target']))
    #if config_module.VERBOSE : ecprint(config_module.TARGET_FILE, c='blue', template = 'saved targets : {}')


if __name__ == '__main__':
    if ('-h' in sys.argv):
        print('Usage:')
        print('python3 preprocessing.py <preprocessing_config_file>')
        sys.exit()

    try:
        if not os.path.isfile(sys.argv[1]) : sys.exit('Could not find the config file at {}'.format(sys.argv[1]))
        config_path = '/'.join(sys.argv[1].split('/')[:-1])     #Get all the path without the file
        config_file = sys.argv[1].split('/')[-1].split('.')[0]  #Get the file without extension
    except IndexError: sys.exit('This scripts needs the absolute path to the config file as argument')

    sys.path.insert(0, config_path)
    CONFIG = __import__(config_file)
    sys.path.insert(0, CONFIG.MODULES_PATH)

    main(config_module = CONFIG)

