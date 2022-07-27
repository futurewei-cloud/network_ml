from random import random
from os.path import isfile

class Splitter:
    def __init__(self, train_percent, filter, store_statistics = False, store_file = None):
                       #训练集占比0.6，过滤
        self.train_percent = train_percent
        self.filter = filter
        self.store_statistics = store_statistics
        self.store_file = store_file
        self.statistics = None

    def split(self, data):
        if self.store_statistics: return self._storesplit(data)
        else : return self._split(data)

    def _split(self, data):
        train,test = [],[]
        for host in data.hosts.values():
            if random() <= self.train_percent: train.append(host)  #random() 方法返回随机生成的一个实数，它在[0,1)范围内。
            else : test.append(host)
        train = [w for h in train for w in h.windows if self.filter(w)]
        #for h in train
            #for w in h.windows
                #if self.filter(w)：w
        test = [w for h in test for w in h.windows if self.filter(w)]
        return train, test

    def _storesplit(self, data):
        self.statistics = {'train' : {}, 'test' : {}}
        activities = self._get_activities(data)
        train,test = [],[]

        for host in data.hosts.values():
            if random() <= self.train_percent: train.append(host)
            else : test.append(host)

        self.statistics['train']['traces'] = self._count_traces(train, activities)
        self.statistics['test']['traces'] = self._count_traces(test, activities)

        train = [w for h in train for w in h.windows]
        test = [w for h in test for w in h.windows]

        self.statistics['train']['pre-cw'] = self._count_cw(train, activities)
        self.statistics['test']['pre-cw'] = self._count_cw(test, activities)
        self.statistics['train']['pre-fw'] = self._count_fw(train, activities)
        self.statistics['test']['pre-fw'] = self._count_fw(test, activities)
        self.statistics['train']['pre-bw'] = self._count_bw(train, activities)
        self.statistics['test']['pre-bw'] = self._count_bw(test, activities)

        train = [w for w in train if self.filter(w)]
        test = [w for w in test if self.filter(w)]

        self.statistics['train']['post-cw'] = self._count_cw(train, activities)
        self.statistics['test']['post-cw'] = self._count_cw(test, activities)
        self.statistics['train']['post-fw'] = self._count_fw(train, activities)
        self.statistics['test']['post-fw'] = self._count_fw(test, activities)
        self.statistics['train']['post-bw'] = self._count_bw(train, activities)
        self.statistics['test']['post-bw'] = self._count_bw(test, activities)

        if isfile(self.store_file) == False:
            with open(self.store_file, 'w') as sf:
                sf.write(self._header())
                sf.write(self._as_line())
        else:
            with open(self.store_file, 'a') as sf:
                sf.write(self._as_line())

        return train, test

    def _get_activities(self, data):
        return list({hc.windows[0].target : 0 for hc in data.hosts.values() if len(hc.windows) > 0}.keys())
    def _count_traces(self, arr, activities):
        c = {a : 0 for a in activities}
        for hc in arr:
            if len(hc.windows) < 1: continue
            c[hc.windows[0].target] += 1
        return c
    def _count_cw(self, arr, activities):
        c = {a : 0 for a in activities}
        for cw in arr: c[cw.target] += 1
        return c
    def _count_fw(self, arr, activities):
        c = {a : 0 for a in activities}
        for cw in arr: c[cw.target] += len(cw.flows)
        return c
    def _count_bw(self, arr, activities):
        c = {a : 0 for a in activities}
        for cw in arr:
            for fw in cw.flows.values(): c[cw.target] += len(fw.windows)
        return c
    def _header(self):
        keys = [(t, v, c) for t,tv in self.statistics.items() for v,vv in tv.items() for c,cv in vv.items()]
        return '{}\n'.format(','.join(70*['{}'])).format(*['{}_{}_{}'.format(*k) for k in keys])
    def _as_line(self):
        values = [cv for tv in self.statistics.values() for vv in tv.values() for cv in vv.values()]
        return '{}\n'.format(','.join(70*['{}'])).format(*values)
