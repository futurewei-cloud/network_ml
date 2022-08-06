#!/usr/bin/env python3
import os
import sys

def main(config_module):
    from packet import Packet
    import dataStructure
    from easycolor import ecprint

    if config_module.VERBOSE : ecprint(
        ['Preparing data structure for:', config_module.CAPTURE_NET, config_module.CW_length, config_module.BW_length],
        c=['green', 'yellow', 'yellow', 'yellow'],
        template = '{}:\n\tNet pattern : {}\n\tCW Length : {}\n\tBW Length : {}'
    )
    dataStr = dataStructure.DataStructure(config_module.CAPTURE_NET, config_module.CW_length, config_module.BW_length)

    if config_module.VERBOSE : ecprint(config_module.TRAFFIC_FILE, c = 'blue', template = 'Reading traffic file : {}')
    
    with open(config_module.TRAFFIC_FILE, 'r') as src:
        #TRAFFIC_FILE：preprocessed.csv
        src.readline()
        for line in src:  #对每一行
            packet = Packet.from_csv_line(line)  
            #Packet.TCP_Packet/Packet.PROTO_UDP/Packet.IP_Packet
            if packet == None: continue
           
            dataStr.add_packet(packet)
            #key

    #dataStr.load_tmap(config_module.TARGETMAP_FILE)#targetmap.csv
    #key

    dataStr.save(config_module.RESTRUCTURED_FILE)  #将输出结果存储为pickle格式

    #data = pickle.load(open(config_module.DATASET, 'rb'))


    if config_module.VERBOSE : ecprint(config_module.RESTRUCTURED_FILE, c = 'blue', template = 'Restructured data saved at {}')





if __name__ == '__main__':
    if ('-h' in sys.argv):
        print('Usage:')
        print('python3 restructure.py <restructure_config_file>')
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

