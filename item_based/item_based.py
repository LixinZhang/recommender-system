#!/usr/bin/python
import math
import sys
import time
import heapq


class Item_based :
    def __init__(self) :
        self.itemMat = {}
        self.similarityMat = {}
        self.similarityTop = {}
        self.below = {}
        self.user2item = {}
        self.itemset = set()

    def ItemSimilarity(self, item1, item2, item_id1,item_id2) :
        upon = 0.0
        for u_id in item1 :
            if u_id in item2 :
                upon += item1[u_id] * item2[u_id]
        below1 = self.below[item_id1]
        below2 = self.below[item_id2]
        if upon == 0.0 or below1 == 0.0 or below2 == 0.0 : return 0.0
        return upon * 1.0 / (below1 * below2)
    
    def prepareFromFile(self, trainfile) :
        datafile = file(trainfile, 'r')
        for line in datafile :
            item_id, user_id, rating = line.split('\x01')
            rating = float(rating.split()[0])
            self.itemset.add(item_id)
            if item_id not in self.itemMat :
                self.itemMat[item_id] = {}
            if user_id not in self.itemMat[item_id] :
                self.itemMat[item_id][] = rating
            
            '''user -> item , sets'''
            if user_id not in self.user2item :
                self.user2item[user_id] = set()
            self.user2item[user_id].add(item_id)

        for item_id in self.itemMat :
            tmp = 0.0
            for u_id in self.itemMat[item_id] :
                tmp += self.itemMat[item_id][u_id] ** 2
            self.below[item_id] = math.sqrt(tmp)

    def generateSimilarityMat(self) :
        item_ids = self.itemMat.keys()
        for id1 in range(len(item_ids)) :
            for id2 in range(id1, len(item_ids)) :
                item_id1 = item_ids[id1]
                if item_id1 not in self.similarityMat :
                    self.similarityMat[item_id1] = {}
                item_id2 = item_ids[id2]
                if item_id2  in self.similarityMat[item_id1] :
                    continue
                if item_id2 not in self.similarityMat :
                    self.similarityMat[item_id2] = {}
                sim = self.ItemSimilarity(self.itemMat[item_id1], self.itemMat[item_id2], item_id1, item_id2)
                self.similarityMat[item_id1][item_id2] = sim
                self.similarityMat[item_id2][item_id1] = sim
        self.__generateTopSimilarity()

    def dumpRes2File(self, dumpFile, Top = 100) :
        dumpF = file(dumpFile, 'w')
        line_format = '%s -> %s -----%f\n'
        for item_id1 in self.itemMat :
            arr = [ (self.similarityMat[item_id1][item_id2], item_id2) for item_id2 in self.similarityMat[item_id1] ]
            arr = heapq.nlargest(Top, arr)
            for t in range(min(Top, len(arr))) :
                dumpF.write(line_format % (item_id1, arr[t][1], arr[t][0]))
        dumpF.close()

    def __generateTopSimilarity(self, Top = 100) :
        for item_id1 in self.itemMat :
            arr = [ (self.similarityMat[item_id1][item_id2], item_id2) for item_id2 in self.similarityMat[item_id1] ]
            arr = heapq.nlargest(Top, arr)
            self.similarityTop[item_id1] = set()
            for rating, item_id in arr :
                self.similarityTop[item_id1].add(item_id)

    def pred(self, user_id, item_id, isTop = True) :
        item_ids = self.user2item[user_id]
        upon = 0.0
        below = 0.0
        for item_id_cmp in item_ids :
            if isTop and (item_id_cmp not in self.similarityTop[item_id]) :
                continue
            print self.similarityMat[item_id][item_id_cmp], self.itemMat[item_id_cmp][user_id], item_id_cmp
            upon += self.similarityMat[item_id][item_id_cmp] * self.itemMat[item_id_cmp][user_id]
            below += self.similarityMat[item_id][item_id_cmp]
        if upon == 0.0 : return 0.0
        return upon * 1.0 /  below
    
    def generateRecommendationList(self, user_id, Top = 10) :
        user_item_ids = self.user2item[user_id]
        new_item_ids = self.itemset - user_item_ids
        score_list = []
        for item_id in new_item_ids :
            score_list.append((self.pred(user_id, item_id), item_id))
        res = heapq.nlargest(Top, score_list)
        return res

    def loadSimilarityMatFromFile(self, matFile = 'out.res') :
        for line in file(matFile, 'r') :
            arr = line.split()
            item1 = arr[0]
            item2 = arr[2]
            rating = float(arr[3][5:])

            
if __name__ == '__main__' :
    start_time = time.time()
    trainfile = 'test.dat'
    trainfile = sys.argv[1]
    ib = Item_based()
    ib.prepareFromFile(trainfile)
    ib.generateSimilarityMat()
    ib.dumpRes2File('out.res.bak')
    print 'Time Cost: ', time.time() - start_time
    
    while True :
        user_id = raw_input('User_id :')
        res = ib.generateRecommendationList(user_id)
        for score, item in res :
            print item, '-->', score
    
    exit(0)

    testfile = 'ml-100k/u1.test' 
    limit = 10
    for line in file(testfile) :
        limit -= 1
        if (limit < 0) : break
        user_id, item_id, rating, timestamps = line.split()
        print user_id,item_id,rating,'---->',
        print ib.pred(user_id,item_id)
        print '*' * 100
