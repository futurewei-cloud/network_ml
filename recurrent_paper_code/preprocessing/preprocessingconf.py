#INPUT OF PREPROCESSING SCRIPT
#	A set of csv files with the traffic of one activity
#	A mapping file with
#		the ip of the host that generates that traffic
#		the name of the file associated
#		the activity in that file

#OUTPUT OF PREPROCESSING SCRIPT
#	A single csv with all the traffic merged
#		Each of the input files will be asociated with a unique host ip in the same net
#	A mapping file with the host ip and it's activity

#预处理脚本的输入
#	具有一个活动流量的一组csv文件
#	映射文件
#		生成该流量的主机的ip
#		关联文件的名称
#		该文件中的活动
import os
import sys

#预处理脚本的输出
#	合并所有流量的单个csv
#		每个输入文件将与同一网络中的唯一主机ip关联
#	主机ip及其活动的映射文件


#Common path to the whole proyect
#整个项目的共同路径
main_path = os.path.dirname(os.getcwd())

#Path to the modules folder. Must be a full path
#模块文件夹的路径。必须是完整路径
MODULES_PATH = '{}/modules'.format(main_path)
#格式化字符串的函数 **str.format()，**它增强了字符串格式化的功能。
#基本语法是通过 {} 和 : 来代替以前的 % 。
#format 函数可以接受不限个参数，位置可以不按顺序。
#<模板字符串>.format(<逗号分隔的参数>)

#Path to the mapping file. The mapping consists in a csv with the host address, the trace name in csv and the activity
#映射文件的路径。映射包含在csv中，其中包含主机地址、csv中的跟踪名称和活动
mapping_file = '{}/data/raw/mapping.csv'.format(main_path)
###data_file = '{}/pcap2csv/213213.csv'.format(main_path)
#Read the mapping and and generate a list with one element per data file
#Each element is a dict with the values in the csv indexed by its field name
#Lines starting with # are ignored so we can place comments in the mapping file
#读取映射并生成一个列表，每个数据文件包含一个元素
#每个元素都是一个dict，csv中的值由其字段名索引
#忽略以#开头的行，以便我们可以在映射文件中放置注释

#traces = [{'host' : 192.168.1.49, 'file' : bulk_115s_01.csv, 'label' : 'bulk'}, {...}, ...]
with open(mapping_file) as f:
	header = f.readline()[:-1].split(',')   #末尾最后一个是\n，只读取了第一行
	traces = [{header[i] : v for i,v in enumerate(line[:-1].split(','))} for line in f if not line[0] == '#']

#rewrite the file fields with an absolute path.
#用绝对路径重写文件字段
for obj in traces: obj['file'] = '{}/{}/{}'.format(main_path, 'data/raw/csv', obj['file'])

#generate an array for the ip-address replacements.
#must be at least one ip for each host to monitorize (for each data file) in the dataset
#为ip地址替换生成数组。
#对于要监视数据集中（每个数据文件）的每个主机，必须至少有一个ip
HOSTS_POOL = ['10.0.{}.{}'.format(x, y) for x in range(1, 5) for y in range(1, 100)]

#Generate another array for the others hosts in the captured dataset.
#为捕获的数据集中的其他主机生成另一个数组。
OTHERS_POOL = ['20.{}.{}.{}'.format(x, y, z) for x in range(1, 5) for y in range(1, 200) for z in range(1, 200)]

#Define the paths to the exported files of the preprocessing script
#定义预处理脚本导出文件的路径
export_path = '{}/data/preprocessed'.format(main_path)
DATA_FILE = '{}/preprocessed.csv'.format(export_path)
TARGET_FILE = '{}/targetmap.csv'.format(export_path)

#Time compresion factor. Set 1 for no compression
#With a time compresion of 2. packets 1seg apart in the original file will be placed 0.5s apart
#时间压缩因子。设置1表示无压缩
#时间压缩为2。原始文件中相隔1秒的数据包将相隔0.5秒
COMPRESSION_FACTOR = 1

#Enable/disable output
#启用/禁用输出
VERBOSE = True
