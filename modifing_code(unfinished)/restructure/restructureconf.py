#INPUT OF THE RESTRUCTURE SCRIPT
#	Both output files from preprocessing.py

#OUTPUT OF RESTRUCTURE SCRIPT
#	A single binary file storing the whole dataset
#		in the hierarchical window structure
#重组脚本的输入
#   所有输出文件都来自preprocessing.py

#重组脚本的输出
#   存储整个数据集的单个二进制文件
#       在分层窗口结构中

import os
import sys
main_path = os.path.dirname(os.getcwd())


#Path to the modules folder. Must be a full path
MODULES_PATH = '{}/modules'.format(main_path)

#Paths to the csv traffic and mapping files generated with preprocessing.py
#使用生成的csv流量和映射文件的路径
datapath =  '{}/data'.format(main_path)
TRAFFIC_FILE = '{}/pcap2csv/preprocessed.csv'.format(main_path)
#213213.csv
#TARGETMAP_FILE = '{}/preprocessed/targetmap.csv'.format(datapath)

#Regex to decide whether or not the host is from the monitoring net
#We are only monitoring traffic from hosts in that net
#MUST MATCH THE NET GENERATED FOR HOSTS_POOL IN preprocessingconf.py
#Regex决定主机是否来自监控网络
#我们只监视来自该网络中主机的流量
#必须在preprocessingconf.py中为HOSTS_POOL生成的网络匹配
CAPTURE_NET = '^10\\.0\\.\\d{1,3}\\.\\d{1,3}'    #改
#括号是捕获组的意思。也就是你要捕获的内容。
#正则表达  IP地址匹配  \\.表示“.” d{1,3}匹配1-3位数字

#CW and BW sizes in seconds. In some modules they are also called w1 and w2 respectively
#CW和BW大小（秒）。在某些模块中，它们分别也称为w1和w2
CW_length = 5.0
BW_length = 0.5

#Path to the restructured dataset file
RESTRUCTURED_FILE = '{}/restructured/restructured.pickle'.format(datapath)

#Enable/disable output
VERBOSE = True
