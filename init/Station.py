# encoding=utf-8

__author__ = 'liuqianchao'
class Staion:
    stationID=0#车站号
    parking=[]#正在服务的公交车车号,用于控制berth number
    berthnumber=1
    waitingtime=0#等待时间
    waitingpassenger=0#候车人员的数目
    passenger=[]
    stopstate=[]
    def __init__(self,id,berth_number):
        self.stationID=id
        self.passenger=[]
        self.parking=[]
        self.stopstate=[]
        self.berthnumber=berth_number
    def setwaitingpassenger(self,num):
        self.waitingpassenger=num
        self.waitingtime=int(self.waitingpassenger*1.5)

