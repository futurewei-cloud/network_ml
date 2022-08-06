#!/usr/bin/env python3
import os
import sys
import pickle
#import pandas as pd

def main(config_module, save = True):
    import dataStructure
    from easycolor import ecprint
    from splitter import Splitter

    #Load the dataset
    if config_module.VERBOSE: ecprint(config_module.DATASET, c = 'blue', template = 'Loading dataset : {}')


    data = pickle.load(open(config_module.DATASET, 'rb'))
    #df = pd.DataFrame(data)
    #df.to_csv(r'2.csv')

    #Split by trace
    if config_module.VERBOSE:
        ecprint('Splitting data', c = 'green')
        ecprint(config_module.TRAIN_RATE, c = 'yellow', template = '\tTRAINING RATE : {}')
        ecprint(1 - config_module.TRAIN_RATE, c = 'yellow', template = '\tTESTING RATE : {}')
        ecprint(config_module.WINDOW_FILTER, c = 'yellow', template = '\tWINDOW FILTER : {}')

    train, test = Splitter(
        config_module.TRAIN_RATE,
        config_module.WINDOW_FILTER,
        store_statistics = config_module.STORE_SPLIT_STATISTICS,   #Store split statistics#存储拆分统计信息
        store_file = config_module.SPLIT_FILE
    ).split(data)

    #Save the splitted sets
    if save == True:
        if config_module.VERBOSE: ecprint(['Saving datasets', config_module.TRAIN_FILE, config_module.TEST_FILE], c = ['green', 'blue', 'blue'], template = '{}\n\tTrain: {}\n\tTest: {}')
        pickle.dump(train, open(config_module.TRAIN_FILE, 'wb'))
        pickle.dump(test, open(config_module.TEST_FILE, 'wb'))
    else: return train,test


if __name__ == '__main__':
    if ('-h' in sys.argv):
        print('Usage:')
        print('python3 split.py <split_config_file>')
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

