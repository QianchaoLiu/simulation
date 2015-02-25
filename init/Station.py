# encoding=utf-8

__author__ = 'liuqianchao'
class Staion:
    stationID=0#车站号
    parking=0#正在服务的公交车车号
    waitingtime=0#等待时间
    waitingpassenger=0#候车人员的数目
    passenger=[]
    stopstate=[]
    def __init__(self,id):
        self.stationID=id
        self.passenger=[]
        self.parking=0
        self.stopstate=[]
    def setwaitingpassenger(self,num):
        self.waitingpassenger=num
        self.waitingtime=int(self.waitingpassenger*1.5)

