#!/usr/bin/env python3
import sys
import pickle

def main(config_module, train = None, save = True):
    import clsModel
    import dataStructure
    from easycolor import ecprint

    if config_module.VERBOSE:
        ecprint('Model parameters', c = 'green')
        ecprint([config_module.MODEL_CONFIG['layer1_model'], config_module.MODEL_CONFIG['layer1_features'], config_module.MODEL_CONFIG['layer1_params']], c = 'yellow', template = '\tLayer1\n\t\tModel : {}\n\t\tFeatures : {}\n\t\tParams : {}')
        ecprint([config_module.MODEL_CONFIG['layer2_model'], config_module.MODEL_CONFIG['layer2_features'], config_module.MODEL_CONFIG['layer2_params']], c = 'yellow', template = '\tLayer2\n\t\tModel : {}\n\t\tFeatures : {}\n\t\tParams : {}')
        ecprint([config_module.MODEL_CONFIG['layer3_model'], config_module.MODEL_CONFIG['layer3_features'], config_module.MODEL_CONFIG['layer3_params']], c = 'yellow', template = '\tLayer3\n\t\tModel : {}\n\t\tFeatures : {}\n\t\tParams : {}')

    #Load training set
    if train == None:
        if config_module.VERBOSE: ecprint(config_module.TRAINING_SET, c = 'blue', template = 'Loading training set : {}')

        train = pickle.load(open(config_module.TRAINING_SET, 'rb'))   #载入训练集

    #Configure and compile the model 配置和编译模型
    if config_module.VERBOSE: ecprint('Compiling model', c = 'green')
    model = clsModel.clsModel(config_module.MODEL_CONFIG)
    '''
    MODEL_CONFIG = {
    'layer1_features' : Features.BWindow.ALL,
    'layer1_model' : 'KMeans',
    'layer1_params' : {
        'n_clusters' : 15
    },

    'layer2_features' : Features.Flow.ALL,
    'layer2_model' : 'KMeans',
    'layer2_params' : {
        'n_clusters': 20        #n_簇
    },

    'layer3_features' : Features.CWindow.ALL,
    'layer3_model' : 'RF',
    'layer3_params' : {
        'n_estimators' : 1000    #n_估计量
    }
}
    '''
    #key

    #Train the model
    if config_module.VERBOSE: ecprint('Training model', c='green')
    model.train(train)
    #key

    ##Save the model
    #if save == True:
    #    if config_module.VERBOSE: ecprint('Saving model', c='green')
    #    pickle.dump(model, open(config_module.MODEL_FILE, 'wb'))
    #    if config_module.VERBOSE: ecprint(config_module.MODEL_FILE, c='blue', template = 'Model saved at : {}')
    #else : return model


if __name__ == '__main__':
    if ('-h' in sys.argv):
        print('Usage:')
        print('python3 train.py <train_config_file>')
        sys.exit()

    try:
        config_path = '/'.join(sys.argv[1].split('/')[:-1])     #Get all the path without the file
        config_file = sys.argv[1].split('/')[-1].split('.')[0]  #Get the file without extension
    except IndexError: sys.exit('This scripts needs the absolute path to the config file as argument')

    sys.path.insert(0, config_path)
    CONFIG = __import__(config_file)
    sys.path.insert(0, CONFIG.MODULES_PATH)

    main(config_module = CONFIG)
