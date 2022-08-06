from datetime import timedelta
import pickle
import math
import re

class Features:
    class BWindow:
        pktsCount = 101
        pktsCount_SR_ratio = 102

        interArrivalTimeMean = 103

        packetSizeSum = 104

        packetSizeSum_SR_ratio = 105
        packetSizeMean = 106
        packetSizeStd = 107
        packetSizeRange = 108

        ALL = [
            pktsCount, pktsCount_SR_ratio,
            interArrivalTimeMean,
            packetSizeSum,
            packetSizeSum_SR_ratio, packetSizeMean, packetSizeStd, packetSizeRange
        ]
        DEFAULT = [
            pktsCount, pktsCount_SR_ratio,
            interArrivalTimeMean,
            packetSizeSum_SR_ratio, packetSizeMean, packetSizeStd, packetSizeRange
	]

    class Flow:
        pktsCount = 201
        interArrivalTimeStd = 202
        packetSizeStd = 203

        ALL = [pktsCount, interArrivalTimeStd, packetSizeStd]
        DEFAULT = []

    class CWindow:
        pktsCount = 301
        packetSizeSum = 302
        flowsCount = 303
        hostsCount = 304

        ALL = [pktsCount, packetSizeSum, flowsCount, hostsCount]
        DEFAULT = []

class CompactedPacket:
    def __init__(self, time, size, to_outside):
        self.time = time
        self.size = size
        self.to_outside = to_outside

    @staticmethod
    def fromPacket(packet, to_outside):
        return CompactedPacket(packet.time, packet.data_len, to_outside)

class DataStructure:
    # ONE FOR THE WHOLE DATASET
    # WILL KEEP TRACK OF EACH USER INVOLVED
    #一个用于整个数据集
    #将跟踪每个相关用户
    def __init__(self, intranetPattern, w1, w2):
        #(,CAPTURE_NET, CW_length, BW_length
        self.intranetPattern = re.compile(r"{}".format(intranetPattern))
        #编译正则表达式模式，返回一个对象。可以把常用的正则表达式编译成正则表达式对象，方便后续调用及提高效率。
        self.w1 = w1
        self.w2 = w2
        self.hosts = {}

    def add_packet(self, packet):
        completed_cw = None
        if self.intranetPattern.match(packet.ip_src):   #如果源IP地址和正则表达式匹配
            completed_cw = self.get_window_container(packet.ip_src).add_packet(
                c_packet = CompactedPacket.fromPacket(packet, to_outside = True),#c_packet(时间戳，负载，是否发出）
                port = packet.src_port, #port：源端口号
                other_host = packet.get_host(who = 'dst')  #其他主机：{IP}:{端口号}
            )
        if self.intranetPattern.match(packet.ip_dst):   #如果目的IP地址和正则表达式匹配
            completed_cw = self.get_window_container(packet.ip_dst).add_packet(
                c_packet = CompactedPacket.fromPacket(packet, to_outside = False),
                port = packet.dst_port,
                other_host = packet.get_host(who = 'src')
            )
        return completed_cw

    def get_window_container(self, host_ip):
        try: return self.hosts[host_ip]
        except KeyError:
            self.hosts[host_ip] = WindowContainer(self.w1, self.w2)
            return self.hosts[host_ip]

    def get_last_window(self, host_ip):
        try: return self.hosts[host_ip].get_last_window()
        except IndexError: return None

    def load_tmap(self, tmapfile):
        with open(tmapfile, 'r') as tmap:
            tmap.readline()
            for line in tmap:
                host, target = line.split('\n')[0].split(',')
                self.get_window_container(host).set_targets(target)

    def save(self, file):
        with open(file, 'wb') as f:
            pickle.dump(self, f)
    @staticmethod
    def load(file):
        return pickle.load(open(file, 'rb'))

class WindowContainer:
    # ONE FOR EACH HOST
    # WILL KEEP TRACK OF EACH CLASSIFICATION WINDOW
    #每个主机一个
    #将跟踪每个分类窗口
    def __init__(self, w1, w2):
        self.w1 = w1
        self.w2 = w2
        self.w1_index = 0
        self.initTime = None
        self.windows = []

    def add_packet(self, c_packet, port, other_host):
        if self.initTime == None: self.initTime = c_packet.time
        w1_offset = self.initTime + timedelta(milliseconds = 1000 * (self.w1_index + 1) * self.w1)
        #分类窗口cw的时间间隔
        #milliseconds毫秒
        #timedelta()方法的意义在于给数字附上相应的单位，
        #比如30，使用days=30，就可以直接表示30天，minutes= 30，直接表示为30min，并且这个值可以直接参与日期的计算

        if c_packet.time < w1_offset:  #如果小于说明在这个窗口中
            self.get_window(self.w1_index).add_packet(c_packet, port, other_host)
        else :
            completed_window_index = self.w1_index  #记录已经完成的窗口大小
            while c_packet.time >= w1_offset:     #大于就弄下一个窗口
                self.w1_index += 1
                w1_offset = self.initTime + timedelta(milliseconds = 1000 * (self.w1_index + 1) * self.w1)
                tmpwindow = self.get_window(self.w1_index)
            self.get_window(self.w1_index).add_packet(c_packet, port, other_host)
            return self.windows[completed_window_index]
        return None

    def get_window(self, w1_index):
        try : return self.windows[w1_index]
        except IndexError:
            self.windows.append(ClassificationWindow(
                w2_len = self.w2,   #BW行为窗口的长度
                w2_amount = int(self.w1 / self.w2) + (0 if (self.w1 / self.w2 == int(self.w1 / self.w2)) else 1),
                initTime = self.initTime + timedelta(milliseconds = 1000 * self.w1_index * self.w1)
            ))
            return self.windows[w1_index]

    def get_last_window(self):
        try : return self.windows[self.w1_index]
        except IndexError: return None

    def set_targets(self, target):
        for clswindow in self.windows:
            clswindow.set_target(target)

class ClassificationWindow:
    # WILL KEEP TRACK OF EACH FLOW INSIDE
    def __init__(self, w2_len, w2_amount, initTime):
        self.w2_len = w2_len
        self.w2_amount = w2_amount   #5.0/0.5=10
        self.initTime = initTime   #当前时刻/当前时刻+1000*1*5/当前时刻+1000*2*5...e.g.0/5/10/15s...
        self.flows = {}
        self.target = None

    def add_packet(self, c_packet, port, other_host):
        self.get_flow(port, other_host).add_packet(c_packet)

    def get_flow(self, port, other_host):
        key = '{}:{}'.format(port if port is not None else '', other_host)  #key='{port/''}:{other_host}'
        try : return self.flows[key]
        except KeyError:
            self.flows[key] = FlowStructure(self.initTime, self.w2_len, self.w2_amount)
            return self.flows[key]

    def export_features(self, f = Features.CWindow.ALL):
        #ALL = [pktsCount 数据包数量, packetSizeSum 数据包大小总和, flowsCount 流量计数, hostsCount 主机计数]
        if f == []: return []

        _pktsCount_s = sum([flow.get_pktsCount('s') for flow in self.flows.values()])
        _pktsCount_r = sum([flow.get_pktsCount('r') for flow in self.flows.values()])
        _packetSizeSum_s = sum([flow.get_pktSizeSum('s') for flow in self.flows.values()])
        _packetSizeSum_r = sum([flow.get_pktSizeSum('r') for flow in self.flows.values()])

        _features = []

        if Features.CWindow.pktsCount in f : _features += [_pktsCount_s, _pktsCount_r]
        if Features.CWindow.packetSizeSum in f : _features += [_packetSizeSum_s, _packetSizeSum_r]
        if Features.CWindow.flowsCount in f : _features += [len(self.flows.keys())]#不同流量的总数
        if Features.CWindow.hostsCount in f : _features += [len(set([k.split(':')[1] for k in self.flows.keys()]))]

        return _features

    def get_pktSizeSum(self, key = 'both'):
        if key == 'both': return (sum([f.get_pktSizeSum('s') for f in self.flows.values()]) + sum([f.get_pktSizeSum('r') for f in self.flows.values()]))
        return sum([f.get_pktSizeSum(key) for f in self.flows.values()])

    def get_pktCountSum(self, key = 'both'):
        if key == 'both': return (sum([flow.get_pktsCount('s') for flow in self.flows.values()]) + sum([flow.get_pktsCount('r') for flow in self.flows.values()]))
        return sum([flow.get_pktsCount(key) for flow in self.flows.values()])

    def set_target(self, target):
        self.target = target

class FlowStructure:
    # WILL KEEP TRACK OF EACH BEHAVIOUR WINDOW  #将跟踪每个行为窗口
    def __init__(self, initTime, w2_len, w2_amount):
        self.initTime = initTime
        self.w2_len = w2_len
        self.w2_amount = w2_amount
        self.w2_index = 0
        self.windows = [BehaviourWindow() for i in range(self.w2_amount)]  #w2_amount  5.0/0.5=10
        self.cluster = None

    def add_packet(self, c_packet):
        w2_offset = self.initTime + timedelta(milliseconds = 1000 * (self.w2_index + 1) * self.w2_len)
        #在一个CW窗口里面分的更细

        if c_packet.time < w2_offset:
            self.get_window(self.w2_index).add_packet(c_packet)
        else :
            while c_packet.time >= w2_offset:
                self.w2_index += 1
                w2_offset = self.initTime + timedelta(milliseconds = 1000 * (self.w2_index + 1) * self.w2_len)
            self.get_window(self.w2_index).add_packet(c_packet)

    def get_window(self, w2_index):
        return self.windows[w2_index]

    def get_pktsCount(self, key = 'both'):
        if key == 'both': return (sum([w2.pktsCount['s'] for w2 in self.windows]) + sum([w2.pktsCount['r'] for w2 in self.windows]))
        return sum([w2.pktsCount[key] for w2 in self.windows])

    def get_pktSizeSum(self, key = 'both'):
        if key == 'both': return (sum([w2.packetSizeSum['s'] for w2 in self.windows]) + sum([w2.packetSizeSum['r'] for w2 in self.windows]))
        return sum([w2.packetSizeSum[key] for w2 in self.windows])

    def export_features(self, f = Features.Flow.ALL):
        #ALL = [pktsCount 数据包计数， interArrivalTimeStd 分组到达间隔时间标准差, packetSizeStd 数据包大小标准偏差4]
        if f == []: return []

        _pktsCount_s = sum([w2.pktsCount['s'] for w2 in self.windows])
        _pktsCount_r = sum([w2.pktsCount['r'] for w2 in self.windows])
        _interTimeSum_s = sum([w2.interTimesSum['s'] for w2 in self.windows])
        _interTimeSum_r = sum([w2.interTimesSum['r'] for w2 in self.windows])
        _interTimeSquaredSum_s = sum([w2.interTimesSquaredSum['s'] for w2 in self.windows])
        _interTimeSquaredSum_r = sum([w2.interTimesSquaredSum['r'] for w2 in self.windows])
        _packetSizeSum_s = sum([w2.packetSizeSum['s'] for w2 in self.windows])
        _packetSizeSum_r = sum([w2.packetSizeSum['r'] for w2 in self.windows])
        _packetSizeSquaredSum_s = sum([w2.packetSizeSquaredSum['s'] for w2 in self.windows])
        _packetSizeSquaredSum_r = sum([w2.packetSizeSquaredSum['r'] for w2 in self.windows])

        _interTimeMean_s = (_interTimeSum_s / _pktsCount_s) if (_pktsCount_s > 1) else 0
        _interTimeMean_r = (_interTimeSum_r / _pktsCount_r) if (_pktsCount_r > 1) else 0
        _packetSizeSquaredSum_s = (_packetSizeSum_s / _pktsCount_s) if (_pktsCount_s > 0) else 0
        _packetSizeMean_r = (_packetSizeSum_r / _pktsCount_r) if (_pktsCount_r > 0) else 0

        _interTimeStd_s = ((_interTimeSquaredSum_s / (_pktsCount_s - 1)) - (_interTimeMean_s ** 2)) if (_pktsCount_s > 1) else 0
        _interTimeStd_r = ((_interTimeSquaredSum_r / (_pktsCount_r - 1)) - (_interTimeMean_r ** 2)) if (_pktsCount_r > 1) else 0
        _packetSizeStd_s = ((_packetSizeSquaredSum_s / (_pktsCount_s - 1)) - (_packetSizeSquaredSum_s ** 2)) if (_pktsCount_s > 1) else 0
        _packetSizeStd_r = ((_packetSizeSquaredSum_r / (_pktsCount_r - 1)) - (_packetSizeSquaredSum_r ** 2)) if (_pktsCount_r > 1) else 0

        _features = []

        if Features.Flow.pktsCount in f: _features += [_pktsCount_s, _pktsCount_r]
        if Features.Flow.interArrivalTimeStd in f: _features += [_interTimeStd_s, _interTimeStd_r]
        if Features.Flow.packetSizeStd in f: _features += [_packetSizeStd_s, _packetSizeStd_r]

        return _features

    def set_cluster(self, cluster):
        self.cluster = cluster

class BehaviourWindow:
    # WILL KEEP TRACK OF THE REQUIRED DATA TO EXPORT THE FEATURES
    #将跟踪导出功能所需的数据

    def __init__(self):
        self.pktsCount = {'s' : 0, 'r' : 0}

        self.prevTime = {'s':None, 'r':None}
        self.interTimesSum = {'s' : 0, 'r' : 0}
        self.interTimesSquaredSum = {'s' : 0, 'r' : 0}

        self.packetSizeSum = {'s':0, 'r':0}
        self.packetSizeSquaredSum = {'s':0, 'r':0}
        self.packetSizeLimits = {
            's': {'max' : 0, 'min' : 1514},
            'r': {'max' : 0, 'min' : 1514}
        }
        self.cluster = None

    def add_packet(self, c_packet):
        key = 's' if (c_packet.to_outside == True) else 'r'  #键值对

        self.pktsCount[key] += 1

        if self.prevTime[key] == None: self.prevTime[key] = c_packet.time  #第一个初始化这个时间
        else:
            _interTime = (c_packet.time - self.prevTime[key]).total_seconds()  #total_seconds()是获取两个时间之间的总差
            self.interTimesSum[key] += _interTime    #差值的总和
            self.interTimesSquaredSum[key] += (_interTime * _interTime)  #差值平方的总和
            self.prevTime[key] = c_packet.time  #改为当前算完的这个时间

        self.packetSizeSum[key] += c_packet.size  #有效负载的总和
        self.packetSizeSquaredSum[key] += (c_packet.size * c_packet.size)  #有效负载平方的总和
        if c_packet.size > self.packetSizeLimits[key]['max']: self.packetSizeLimits[key]['max'] = c_packet.size
        if c_packet.size < self.packetSizeLimits[key]['min']: self.packetSizeLimits[key]['min'] = c_packet.size

    def export_features(self, f = Features.BWindow.ALL):
        #        ALL = [
        #   pktsCount 数据包计数, pktsCount_SR_ratio 数据包计数发送-接收比率,
        #   interArrivalTimeMean 数据包到达时间平均值,
        #   packetSizeSum 数据包大小总和,
        #   packetSizeSum_SR_ratio 数据包大小和发送接收比, packetSizeMean 数据包大小平均值,
        #   packetSizeStd 数据包大小标准偏差, packetSizeRange 数据包大小范围

        if self.pktsCount['s'] == 0 and self.pktsCount['r'] == 0: return None
        if f == []: return []

        _pktsCountSum = self.pktsCount['s'] + self.pktsCount['r']   #数据包个数总和
        _packetSizeSum = self.packetSizeSum['s'] +  self.packetSizeSum['r']  #有效载荷总和

        _interTime_mean_s = (self.interTimesSum['s'] / self.pktsCount['s']) if (self.pktsCount['s'] > 1) else 0
        _interTime_mean_r = (self.interTimesSum['r'] / self.pktsCount['r']) if (self.pktsCount['r'] > 1) else 0

        _packetSize_mean_s = (self.packetSizeSum['s'] / self.pktsCount['s']) if (self.pktsCount['s'] > 0) else 0
        _packetSize_mean_r = (self.packetSizeSum['r'] / self.pktsCount['r']) if (self.pktsCount['r'] > 0) else 0
        #方差
        _packetSize_std_s = ((self.packetSizeSquaredSum['s'] / self.pktsCount['s']) - (_packetSize_mean_s ** 2)) if (self.pktsCount['s'] > 0) else 0
        _packetSize_std_r = ((self.packetSizeSquaredSum['r'] / self.pktsCount['r']) - (_packetSize_mean_r ** 2)) if (self.pktsCount['r'] > 0) else 0

        _features = []

        if Features.BWindow.pktsCount in f: _features += [self.pktsCount['s'], self.pktsCount['r']]
        if Features.BWindow.pktsCount_SR_ratio in f: _features += [self.pktsCount['s'] / _pktsCountSum]   #发送的包/总包
        if Features.BWindow.interArrivalTimeMean in f: _features += [_interTime_mean_s, _interTime_mean_r]#[发送平均，接收平均]
        if Features.BWindow.packetSizeSum in f: _features += [self.packetSizeSum['s'], self.packetSizeSum['r']]
        if Features.BWindow.packetSizeSum_SR_ratio in f: _features += [self.packetSizeSum['s'] / _packetSizeSum]
        if Features.BWindow.packetSizeMean in f: _features += [_packetSize_mean_s, _packetSize_mean_r]
        if Features.BWindow.packetSizeStd in f: _features += [_packetSize_std_s, _packetSize_std_r]
        if Features.BWindow.packetSizeRange in f: _features += [
            ((self.packetSizeLimits['s']['max'] - self.packetSizeLimits['s']['min']) / 1514) if (self.pktsCount['s'] > 0) else 0,
            ((self.packetSizeLimits['r']['max'] - self.packetSizeLimits['r']['min']) / 1514) if (self.pktsCount['r'] > 0) else 0
        ]

        return _features

    def set_cluster(self, cluster):
        self.cluster = cluster
