#INPUT OF THE TEST SCRIPT
	#A trained model file
	#A test dataset file

#OUTPUT OF THE TEST SCRIPT
	#A csv with the testing results

#Common path to the whole proyect
import os
import sys
main_path = os.path.dirname(os.getcwd())

#Path to the modules folder. Must be a full path
MODULES_PATH = '{}/modules'.format(main_path)

#Path to the model & test dataset files
datapath =  '{}/data'.format(main_path)
MODEL_FILE = '{}/model/model.pickle'.format(datapath)
TESTING_SET = '{}/datasets/test.pickle'.format(datapath)

#Path to the results file
RESULTS_FILE = '{}/results/crossval_results.csv'.format(datapath)

#Code used to distinguish between multiple tests in the same file
#Used in "{}/scripts/helper/traintest.py".format(main_path)
#用于区分同一文件中多个测试的代码
#用于“{}/scripts/helper/traintest.py”.format(main_path)
TEST_CODE = 0

#Enable/disable output
VERBOSE = True
PRINT_RESULTS = True
