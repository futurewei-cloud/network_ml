from sklearn.preprocessing import StandardScaler
from sklearn.multiclass import OneVsRestClassifier
from sklearn.cluster import KMeans, Birch
from sklearn import svm
from sklearn.neural_network import MLPClassifier
from sklearn.mixture import GaussianMixture
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime as dt

SUPPORTED_MODELS = {

    #lambda 参数列表 ： 表达式
    #lambda表达式的参数可有可⽆，函数的参数在lambda表达式中完全适⽤。
    #lambda表达式能接收任何数量的参数但只能返回⼀个表达式的值
    #可变参数：**kwargs
	#Layers 1 & 2
	'KMeans' : lambda args : KMeans(**args),
	'Birch' : lambda args : Birch(**args),
	'GM' : lambda args : GaussianMixture(**args),

	#Layer 3
	'SVM' : lambda args : OneVsRestClassifier(svm.SVC(**args)),
	'MLP' : lambda args : MLPClassifier(**args),
	'RF' : lambda args : RandomForestClassifier(**args)
}

class clsModel:
    def __init__(self, config):
        self.layer1_features = config['layer1_features']  #Features.BWindow.ALL
        self.layer1_scaler = StandardScaler()  #去均值和方差归一化
        self.k1 = config['layer1_params']['n_clusters'] if 'n_clusters' in config['layer1_params'] else config['layer1_params']['n_components']
        self.layer1_model = SUPPORTED_MODELS[config['layer1_model']](config['layer1_params'])

        # self.layer2_encoding = 'binary'编码二进制
        self.layer2_features = config['layer2_features']
        self.layer2_scaler = StandardScaler()
        self.k2 = config['layer2_params']['n_clusters'] if 'n_clusters' in config['layer2_params'] else config['layer2_params']['n_components']
        self.layer2_model = SUPPORTED_MODELS[config['layer2_model']](config['layer2_params'])

        # self.layer3_encoding = 'binary'
        self.layer3_features = config['layer3_features']
        self.layer3_scaler = StandardScaler()
        self.layer3_model = SUPPORTED_MODELS[config['layer3_model']](config['layer3_params'])

    def pull_layer1(self, w1_arr):
        
        numapp = 0
        dst = open(r'G:\Anaconda\2\data\results\layer1.csv', 'w', newline="")
        dst.write('pktsCount_s,pktsCount_r,pktsCount_SR_ratio,interArrivalTimeMean_s,interArrivalTimeMean_r,\
packetSizeSum_s,packetSizeSum_r,packetSizeSum_SR_ratio,packetSizeMean_s,packetSizeMean_r,\
packetSizeStd_s,packetSizeStd_r,packetSizeRange_s,packetSizeRange_r\n')

        data = []
        for clsWindow in w1_arr:
            for flowkey, flowStruct in clsWindow.flows.items():
                #items() 主要用于提取词典中的key: value对
                #flowkey：键(流的对应关系port:other_host）  flowStruct：值
                
                #if numapp < 10:
                   #print(flowkey,flowstruct)

                for behavWindow in flowStruct.windows:   #BW                   
                    tmp = behavWindow.export_features(f = self.layer1_features)
                    if tmp is not None: 
                        data.append(tmp)
                        if numapp < 50:
                            dst.write('{}\n'.format('\n'.join('%s' %i for i in data)))
                            numapp = numapp + 1
        print("layer1 OK!")

        return data

    def set_layer1(self, w1_arr, w2_pred):
        index = 0
        for clsWindow in w1_arr:
            for flowkey, flowStruct in clsWindow.flows.items():  
                for behavWindow in flowStruct.windows:
                    tmp = behavWindow.export_features(f = self.layer1_features) #self.layer1_features = config['layer1_features']  #Features.BWindow.ALL
                    if tmp is not None:
                        behavWindow.set_cluster(w2_pred[index] + 1)
                        index += 1
                    else: behavWindow.set_cluster(0)


    def pull_layer2(self, w1_arr):

        numapp = 0
        dst = open(r'G:\Anaconda\2\data\results\layer2.csv', 'w', newline="")
        dst.write('pktsCount_s,pktsCount_r,interArrivalTimeStd_s,interArrivalTimeStd_r,\
packetSizeStd_s,packetSizeStd_r,BW_cluster_binary_encoding\n')

        data = []
        for clsWindow in w1_arr:
            for flowkey, flowStruct in clsWindow.flows.items():

                binary_encoding = [0] * (self.k1 + 1)   #列一个1*16的0/1矩阵表示第一轮矩阵结果
                for bw in flowStruct.windows:
                    binary_encoding[bw.cluster] = 1
                    #print(binary_encoding)
                data.append(flowStruct.export_features(f = self.layer2_features) + binary_encoding)
                if numapp < 50:
                    dst.write('{}\n'.format('\n'.join('%s' %i for i in data)))
                    numapp = numapp + 1
        print("layer2 OK!")       

        return data

    def set_layer2(self, w1_arr, flow_pred):
        index = 0
        for clsWindow in w1_arr:
            for flowkey, flowStruct in clsWindow.flows.items():
                flowStruct.set_cluster(flow_pred[index])
                index += 1

    def pull_layer3(self, w1_arr):

        ###numapp = 0
        dst1 = open(r'g:\anaconda\2\data\results\layer3.csv', 'w', newline="")
        dst1.write('pktscount_s,pktscount_r,packetsizesum_s,packetsizesum_r,flowscount,hostscount,fw_cluster_binary_encoding\n')


        data = []
        for clswindow in w1_arr:
            binary_encoding = [0] * self.k2
            for flow in clswindow.flows.values(): 
                binary_encoding[flow.cluster] = 1
            data.append(clswindow.export_features(f = self.layer3_features) + binary_encoding)
            ###if numapp < 2:
            dst1.write('{}\n'.format('\n'.join('%s' %i for i in data)))
                ###numapp = numapp + 1
        print("layer3 OK!")
        return data

    def train(self, w1_arr):    #key
        #w1_arr=train = pickle.load(open(config_module.TRAINING_SET, 'rb'))   #载入训练集
        layer1_in = self.pull_layer1(w1_arr)

        self.layer1_scaler.fit(layer1_in)  #用于计算训练数据的均值和方差
        self.layer1_model.fit(self.layer1_scaler.transform(layer1_in))#再用scaler中的均值和方差来转换X，使X标准化
        #layer1_model.fit=kmeans.fit找质心

        self.set_layer1(w1_arr, self.layer1_model.predict(self.layer1_scaler.transform(layer1_in)))
        #预测部分，输入新的数据点，来进行预测，用的是predict()方法  kmeans.predict([[0, 0], [4, 4]])
        


        layer2_in = self.pull_layer2(w1_arr)
        self.layer2_scaler.fit(layer2_in)
        self.layer2_model.fit(self.layer2_scaler.transform(layer2_in))
        self.set_layer2(w1_arr, self.layer2_model.predict(self.layer2_scaler.transform(layer2_in)))

        layer3_in = self.pull_layer3(w1_arr)
        #self.layer3_scaler.fit(layer3_in['x'])
        #self.layer3_model.fit(self.layer3_scaler.transform(layer3_in['x']), layer3_in['y'])


    def test(self, w1_arr):
        self.set_layer1(w1_arr, self.layer1_model.predict(self.layer1_scaler.transform(self.pull_layer1(w1_arr))))
        self.set_layer2(w1_arr, self.layer2_model.predict(self.layer2_scaler.transform(self.pull_layer2(w1_arr))))
        layer3_in = self.pull_layer3(w1_arr)
        layer3_pred = self.layer3_model.predict(self.layer3_scaler.transform(layer3_in['x']))
        return [{'target' : layer3_in['y'][i], 'pred' : layer3_pred[i]} for i in range(len(layer3_pred))]
