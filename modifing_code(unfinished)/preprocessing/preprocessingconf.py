#预处理脚本的输入
#	具有按时间排序的混合所有流量的csv文件
#	生成该流量的主机的ip list

#预处理脚本的输出
#	匿名化的csv文件
#	主机ip及其匿名化的映射文件


#Common path to the whole proyect
#整个项目的共同路径
main_path = 'G:/Anaconda/2'  

#Path to the modules folder. Must be a full path
#模块文件夹的路径。必须是完整路径
MODULES_PATH = '{}/modules'.format(main_path)
#格式化字符串的函数 **str.format()，**它增强了字符串格式化的功能。
#基本语法是通过 {} 和 : 来代替以前的 % 。
#format 函数可以接受不限个参数，位置可以不按顺序。
#<模板字符串>.format(<逗号分隔的参数>)

D_FILE = '{}/pcap2csv/1.csv'.format(main_path)
MAP_FILE = '{}/pcap2csv/map.csv'.format(main_path)

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

#Time compresion factor. Set 1 for no compression
#With a time compresion of 2. packets 1seg apart in the original file will be placed 0.5s apart
#时间压缩因子。设置1表示无压缩
#时间压缩为2。原始文件中相隔1秒的数据包将相隔0.5秒
COMPRESSION_FACTOR = 1

#Enable/disable output
#启用/禁用输出
VERBOSE = True
