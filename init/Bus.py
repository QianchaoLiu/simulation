# encoding=utf-8
__author__ = 'liuqianchao'
class Bus:
    busID=0#公交车车号
    capacity=80#容量
    active=False
    forestation=0#在公交线路上前一个车站的站号
    rundistance=0#较上一个车站行驶的距离
    busLineID=0#目前所属交通线路
    waitingtime=0#停车时间
    parkwaitingtime=0
    passengers=[]#实时数据信息

    #---database信息
    arrive_stop_time=[]
    start_service_time=[]
    end_service_time=[]
    passenger_get_on_number=[]
    passenger_get_off_number=[]
    running_time=[]
    passenger_number=[]

    def __init__(self,id,buslineid,forestation):
        self.busID=id
        self.busLineID=buslineid
        self.forestation=int(forestation)
        self.passengers=[]
        self.waitingtime=0

        self.arrive_stop_time=[]
        self.start_service_time=[]
        self.end_service_time=[]
        self.passenger_get_on_number=[]
        self.passenger_get_off_number=[]
        self.running_time=[]
        self.passenger_number=[]
    def information(self):
        print('当前公交车车号为:'+str(self.busID)+';隶属'+str(self.busLineID)+'号公交线路;Active:'+str(self.active)+'前一站为:'+str(self.forestation)+';较前一站已行驶:'+str(self.rundistance)+'米,waitingtime'+str(self.waitingtime)+',  parkingwaitingtime'+str(self.parkwaitingtime)+'       实载：'+str(len(self.passengers))+'人')