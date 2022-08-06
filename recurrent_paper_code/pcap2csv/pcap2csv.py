#!/usr/bin/env python3
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, epilog = '{}\n{}'.format(
	'example : pcap2csv.py file.pcap file.csv',
	'example : pcap2csv.py -v -vb 10000 -wb 25000 -se on file.pcap file.csv'
))
parser.add_argument('pcap', help = 'pcap file to read')
parser.add_argument('csv', help = 'csv file to save')
parser.add_argument('-v', '--verbose', help = 'print the progress to stdout', action = 'store_true', default=False)
parser.add_argument('-vb', '--vbuffer', help = 'print progress every n packets.\nshould be used with -v option.\ndefault 5000', type=int, metavar ='n', default=5000)
parser.add_argument('-wb', '--wbuffer', help = 'write to output file every n packets.\ndefault 5000', type=int, metavar='n', default=5000)
parser.add_argument('-se', '--skip_empty', help = 'ignore packets with empty payload.\ndefault on', choices=['off', 'on'], default = 'on')
args = parser.parse_args()
'''
pcap 要读取的pcap文件
csv 要保存的csv文件
-v 将进度打印到标准输出
-vb 每n个数据包打印一次进度 \n应与-v选项一起使用 \ndefault 5000
-wb 每n个数据包写入输出文件 \ndefault 5000
-se 忽略负载为空的数据包 \ndefault 开启
'''


#Get required args 获取所需参数
srcfile, dstfile = args.pcap, args.csv

#Get optional args 获取可选参数
verbose, vbuffer, wbuffer = args.verbose, args.vbuffer, args.wbuffer
skip_empty = True if (args.skip_empty == 'on') else False

#Required internal vars 所需的内部变量
pkt_count = 0
buffer_count = 0
verbose_count = 0
data_buffer = []

#Imports
from scapy.utils import RawPcapReader
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP, UDP

#MAIN

#pre_pkt = None
with open(dstfile, 'w') as dst:
	dst.write('time,proto,data_len,ip_src,ip_dst,src_port,dst_port\n')

	new = 1

	#READ THE PCAP FILE
	jmp = 0
	pre_id = []
	for (pkt_data, pkt_metadata,) in RawPcapReader(srcfile):
		ether_pkt = Ether(pkt_data)
		
		
		#FILTER NON RELEVANT PACKETS  过滤不相关的数据包
		if 'type' not in ether_pkt.fields: 
			new=new+1
			continue		# LLC frames will have 'len' instead of 'type'.
		if ether_pkt.type != 0x0800: 
			new=new+1
			continue			# disregard non-IPv4 packets 忽略非IPv4数据包

		ip_pkt = ether_pkt[IP]
		
		

		#print(ip_pkt.flags)
		#if(ip_pkt.id in pre_id):
		#	if(ip_pkt.flags == "MF"):
		#		pre_id.append(ip_pkt.id)
		#	#pre_id.remove(ip_pkt.id)
		#	continue
		if ip_pkt.proto == 6 or ip_pkt.proto == 17:		# if UDP or TCP
			pkt = ip_pkt[TCP if ip_pkt.proto == 6 else UDP]
			data_len = (len(pkt) - (pkt.dataofs * 4)) if (ip_pkt.proto == 6) else len(pkt)
			#数据载荷长度=IP数据包总长度（50）-IP头部长度（5）4-TCP首部长度（5）4，因为IP与TCP首部长度字段的单位为4字节，因此需乘4

			sport, dport = ip_pkt.payload.sport, ip_pkt.payload.dport

			#print(ip_pkt.proto,data_len,sport,dport,new)
			#new=new+1
			#if(ip_pkt.flags == "MF"):
			#	print("here")
			#	pre_id.append(ip_pkt.id)

		else :							# if other IP packet
			new=new+1
			continue 					# filter non TCP-UDP packets
			#data_len = len(ip_pkt)
			#sport, dport = '', ''

		if skip_empty and data_len == 0: 
			continue		# Skip packets with an empty payload跳过负载为空


		#GET THE CSV LINE FOR THE ACTUAL PACKET 获取实际数据包的CSV行
		pkt_timestamp = (pkt_metadata.sec) + (pkt_metadata.usec / 1000000)
		pkt_line = '{},{},{},{},{},{},{}'.format(
		    pkt_timestamp, ip_pkt.proto, data_len,
		    ip_pkt.src, ip_pkt.dst,
			sport, dport
		)

		#REFRESH INTERNAL VARIABLES 刷新内部变量
		pkt_count += 1
		verbose_count += 1
		buffer_count += 1
		data_buffer.append(pkt_line) #下一行

		#PRINT THE PROGRESS AND RESET THE COUNTER 打印进度并重置计数器
		if verbose and verbose_count >= vbuffer:
			print('Parsed packets : {}'.format(pkt_count), end='\r')
			verbose_count = 0

		#WRITE TO THE CSV FILE AND RESET COUNTER AND BUFFER 写入CSV文件并重置计数器和缓冲区
		if buffer_count >= wbuffer:
			dst.write('{}\n'.format('\n'.join(data_buffer)))
			buffer_count = 0
			data_buffer = []
		'''
		new=new+1
		if new == 2052:
			break
		'''

	#PUSH THE LAST LINES IF THEY DID NOT REACH THE BUFFER WRITTING THRESHOLD 如果最后几行未达到缓冲区写入阈值，则推送它们
	if buffer_count > 0:
		dst.write('{}\n'.format('\n'.join(data_buffer)))
		if verbose: print('Parsed packets : {}'.format(pkt_count))

if verbose: print('Parse finished, csv file in {}'.format(dstfile))

