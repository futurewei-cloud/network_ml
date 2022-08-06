#!/usr/bin/env python3
import sys
import pickle
from os.path import isfile

def main(config_module, test = None, model = None):
    import clsModel
    import dataStructure
    from easycolor import ecprint

    #Load testing set
    if test == None:
        if config_module.VERBOSE: ecprint(config_module.TESTING_SET, c = 'blue', template = 'Loading testing set : {}')
        test = pickle.load(open(config_module.TESTING_SET, 'rb'))

    #Load and test the model
    if model == None:
        if config_module.VERBOSE: ecprint('Loading model', c='green')
        model = pickle.load(open(config_module.MODEL_FILE, 'rb'))
    if config_module.VERBOSE: ecprint('Performing evaluation', c='green')

    res = model.test(test)     #key

    #Save the results
    if config_module.VERBOSE: ecprint(config_module.RESULTS_FILE, c = 'blue', template = 'Saving results : {}')
    if isfile(config_module.RESULTS_FILE) == False:
        with open(config_module.RESULTS_FILE, 'w') as rfile:
            rfile.write('code,target,pred\n')
            for r in res: rfile.write('{},{},{}\n'.format(config_module.TEST_CODE, r['target'], r['pred']))
    else :
        with open(config_module.RESULTS_FILE, 'a') as rfile:
            for r in res: rfile.write('{},{},{}\n'.format(config_module.TEST_CODE, r['target'], r['pred']))

    if config_module.PRINT_RESULTS:
        cls = list(set([x['target'] for x in res]))
        results = {k : {'correct' : 0, 'total' : 0} for k in cls}
        for r in res:
            results[r['target']]['total'] += 1
            if r['target'] == r['pred']: results[r['target']]['correct'] += 1
        for c in results: ecprint('{:.3f}'.format(results[c]['correct'] / results[c]['total']), c = 'yellow', template = '{} : {}'.format(c, '{}'))


if __name__ == '__main__':
    try:
        config_path = '/'.join(sys.argv[1].split('/')[:-1])     #Get all the path without the file
        config_file = sys.argv[1].split('/')[-1].split('.')[0]  #Get the file without extension
    except IndexError: sys.exit('This scripts needs the absolute path to the config file as argument')

    sys.path.insert(0, config_path)
    CONFIG = __import__(config_file)
    sys.path.insert(0, CONFIG.MODULES_PATH)

    main(config_module = CONFIG)
