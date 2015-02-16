# encoding=utf-8

__author__ = 'liuqianchao'
class RouteLine:
    routelineID=0
    stoplist=[]
    distancelist=[]
    busrunning=[]
    buslist=[]#存放bus对象
    def __init__(self,id,stoplist,distancelist):
        self.routelineID=id
        #stoplist
        tempstoplist=[]
        for i in stoplist:
            tempstoplist.append(int(i))
        self.stoplist=tempstoplist
        #distancelist
        tempdistancelist=[]
        for i in distancelist:
            tempdistancelist.append(int(i))
        self.distancelist=tempdistancelist
    def setbuslist(self,buslist):
        self.buslist=buslist
    def updatebusrunning(self,list):
        self.busrunning=list