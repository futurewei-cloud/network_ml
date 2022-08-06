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
    random.shuffle(config_module.TRACES)            #REORDENAMOS ALEATORIAMENTE LAS TRAZAS随机重排轨迹
    #random.shuffle()用于将一个列表中的元素打乱顺序，不生成新列表，只将原列表次序打乱
    #TRACES = [{'host' : 192.168.1.49, 'file' : bulk_115s_01.csv, 'label' : 'bulk'}, {...}, ...]
    
    anonym = Anonymizer(config_module.HOSTS_POOL, config_module.OTHERS_POOL)

    readed_traces = []

    cf = config_module.COMPRESSION_FACTOR
    #时间压缩因子。设置1表示无压缩

    #First pass : write each pcap as a temporal csv file 
    #第一步：将每个pcap写入临时csv文件

    for trace_index, trace in enumerate(config_module.TRACES):

        tmpfile = '{}/{}_{}'.format('/'.join(trace['file'].split('/')[:-1]), dt.timestamp(dt.now()), trace['file'].split('/')[-1])
        #e.g. /bulk_115s_01.csv/当前时间的时间戳_bulk_115s_01.csv

        #split('/')[:-1]:以/为界限，将最后一块切割出来
        #timestamp返回对应于 datetime 实例的 POSIX 时间戳

        readed_traces.append({'target' : trace['label'], 'host' : anonym.add_host(trace['host']), 'tmpfile' : tmpfile})
        #已经读过的路径
        trace_time = None

        if config_module.VERBOSE : ecprint(trace['file'], c='blue', template = 'reading trace : {}')

        with open(trace['file'], 'r') as f, open(tmpfile, 'w') as dstf:
            f.readline()								#ignoramos la cabecera del csv 忽略CSV标头
            for line in f:
                packet = Packet.from_csv_line(line)
                if packet == None: continue						#error en el parser解析器错误

                if trace_time == None: trace_time = packet.time				#guardamos el tiempo de inicio de la traza保存跟踪开始时间
                packet.time = common_time + ((1/cf) * (packet.time - trace_time))  	#Trasladamos temporalmente el paquete我们暂时转移了包裹。

                anonym.anonimize(packet, original = trace['host'])      		#Anonimizamos las ips我们匿名的PSU
                #用新的ip数组代替了原来的 完成匿名化
                dstf.write(packet.as_csv_line())					#Append packets to the tmp file将数据包附加到tmp文件


    if config_module.VERBOSE : ecprint('Saving preprocessing results', c='green')

    #Second pass : merge the csv files. --> Made in 2 iterations to avoid having to keep all the packets in memory simultaneously
    #第二步：合并csv文件。-->在2次迭代中进行，以避免同时将所有数据包保留在内存中
    tmp_files = [open(r['tmpfile'], 'r') for r in readed_traces]				#Open all the files
    tmp_packets = [Packet.from_csv_line(f.readline()) for f in tmp_files]			#Get the first packet of each file
    with open(config_module.DATA_FILE, 'w') as f:
        f.write(Packet.csv_header())
        while len(tmp_packets) > 0:
            tmp_times = [p.time for p in tmp_packets]						#Get an array with the packet times 获取包含数据包时间的数组
            next_packet = tmp_times.index(min(tmp_times))					#Find first packet in time 及时找到第一个数据包
            f.write(tmp_packets[next_packet].as_csv_line())					#Write to output file
            next_line = tmp_files[next_packet].readline()					#Read next line
            if next_line != '': tmp_packets[next_packet] = Packet.from_csv_line(next_line)	#If not EOF: override the readed packet with the next one in that file#如果不是EOF：用该文件中的下一个数据包覆盖读取的数据包
            else :										#else:
                tmp_packets = tmp_packets[:next_packet] + tmp_packets[next_packet + 1:]		#   pop the readed packet
                tmp_files[next_packet].close()							#   close the file
                tmp_files = tmp_files[:next_packet] + tmp_files[next_packet + 1:]		#   pop the full readed file

    for r in readed_traces: os.remove(r['tmpfile'])						#Remove the tmp files

    if config_module.VERBOSE : ecprint(config_module.DATA_FILE, c='blue', template = 'saved merged traces : {}')

    #Save the target map --> address - activity
    if config_module.VERBOSE : ecprint('Saving targetmap', c='green')
    with open(config_module.TARGET_FILE, 'w') as f:
        f.write('host,target\n')
        for t in readed_traces:
            f.write('{},{}\n'.format(t['host'], t['target']))
    if config_module.VERBOSE : ecprint(config_module.TARGET_FILE, c='blue', template = 'saved targets : {}')


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

