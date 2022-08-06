#INPUT OF THE TRAIN SCRIPT
	#The training set file generated with split.py

#OUTPUT OF THE TRAIN SCRIPT
	#A trained model stored in a file
#列车脚本的输入
    #使用split.py生成的训练集文件
#列车脚本的输出
    #存储在文件中的经过训练的模型


#Common path to the whole proyect
import os
import sys
main_path = os.path.dirname(os.getcwd())

#Path to the modules folder. Must be a full path
MODULES_PATH = '{}/modules'.format(main_path)

#Path to the training dataset file
datapath =  '{}/data'.format(main_path)
TRAINING_SET = '{}/datasets/train.pickle'.format(datapath)

#Import the modules to have access to the Features class #导入模块以访问Features类
import sys
sys.path.insert(0, MODULES_PATH)  #把MODULES_PATH添加成python可识别的文件夹
from dataStructure import Features

#Configuration of the model #模型的配置
MODEL_CONFIG = {
    'layer1_features' : Features.BWindow.ALL,
    'layer1_model' : 'KMeans',
    'layer1_params' : {
        'n_clusters' : 15
    },

    'layer2_features' : Features.Flow.ALL,
    'layer2_model' : 'KMeans',
    'layer2_params' : {
        'n_clusters': 20
    },

    'layer3_features' : Features.CWindow.ALL,
    'layer3_model' : 'RF',
    'layer3_params' : {
        'n_estimators' : 1000
    }
}

#Output file where to save the trained model
MODEL_FILE = '{}/model/model.pickle'.format(datapath)

#Enable/disable output
VERBOSE = True
