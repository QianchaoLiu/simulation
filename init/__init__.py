# encoding=utf-8
__author__ = 'liuqianchao'
from Bus import Bus
from Station import Staion
from RouteLine import RouteLine
from Passenger import Passenger
import random
import math

if __name__=="__main__":
    #读入stationlist,共10条公交线路
    f1=open('/users/liuqianchao/desktop/simulation/stationinput.txt')
    stoplist=[]
    line1=f1.readline()
    while line1:
        stoplist.append(line1.split(','))
        line1=f1.readline()

    #读入distancelist
    f2=open('/users/liuqianchao/desktop/simulation/distanceinput.txt')
    distancelist=[]
    line2=f2.readline()
    while line2:
        distancelist.append(line2.split(','))
        line2=f2.readline()


#初始化公交线路
    routeinstancelist=[]
    for i in range(10):
        newroute=RouteLine(i,stoplist[i],distancelist[i])
        routeinstancelist.append(newroute)


#初始化公交汽车，每一个条公交线路分配10辆车,一号线路分配1-10号车，二号线路分配11-20号车...
    for i in range(10):
        buslist=[]
        for j in range(10):
            buslist.append(Bus(i*10+j+1,i,routeinstancelist[i].stoplist[0]))#车号，公交线路ID，起始位置公交车站号
        routeinstancelist[i].setbuslist(buslist)#将各线路上的车分别分配到十条线路上，之后再操作公交车通过线路操作

#初始化公交车站,Station:1,2.3,4,5,6,7,8,10,11,12,13,15,16,17,18,19,20,21,22,24,Stastioninstancelist[1]表示第一个公交车站
    stationinstancelist=[]
    for i in range(24):
        if(i+1!=9 and i+1!=14):
            stationinstancelist.append(Staion(i+1))



#先遍历公交线路，后遍历线路上run的车,随机因素包括
    targettime=input('请输入要查询的时间距公交系统开始营运时间（6：00）的秒数,比如7：00为3600:')
    for clock in range(targettime):
        for routeline in routeinstancelist:

            #1、在每一秒首先判断该route是否有新车发出，每隔10min（600s）每条线路发出一辆新车active→true
            if(clock%600==0):
                for car in routeline.buslist:
                    if(car.active==False and car.forestation==routeline.stoplist[0] and car.rundistance==0):
                        car.active=True
                        break

            #2、update (routeline)上的busonrun
            busonrun=[]
            for car in routeline.buslist:
                if(car.active==True):
                    busonrun.append(car)
            routeline.updatebusrunning(busonrun)
            #3、对每一辆busonrun(bus),判断是否在车站，如果不是，更新距离距离信息
            for car in routeline.busrunning:
                if car.waitingtime!=0:
                    car.waitingtime-=1
                else:
                    speed=random.gauss(1,0.1)#!!汽车行驶速度，需要导入数据
                    car.rundistance+=speed
            #4、判断是否到达新站，如果到达，设定等待时间
            for car in routeline.busrunning:
                indexofshop=routeline.stoplist.index(car.forestation)
                if(car.rundistance>=int(routeline.distancelist[indexofshop])*100):
                    if(car.forestation==routeline.stoplist[len(routeline.stoplist)-2]):
                        #到达终点
                        car.active=False
                        car.forestation=routeline.stoplist[indexofshop+1]
                        car.rundistance=0
                    else:
                        #不是到达终点
                        car.forestation=routeline.stoplist[indexofshop+1]
                        car.rundistance=0
                        #!!车站停车时间，需要导入需求,此时到达的车站id为routeline.stoplist[indexofshop+1]
                        for station in stationinstancelist:
                            if station.stationID==routeline.stoplist[indexofshop+1]:
                                car.waitingtime=station.waitingtime
            #5、updata busonrun
            busonrun=[]
            for car in routeline.buslist:
                if(car.active==True):
                    busonrun.append(car)
            routeline.updatebusrunning(busonrun)

    for routeline in routeinstancelist:
        print('routeID:'+str(routeline.routelineID))
        for car in routeline.buslist:
            car.information()
        print('----------------')

def creatpassenger():#产生需求
    for routeline in routeinstancelist:
        for stop in routeline.stoplist:


    #在站点产生需求
    #产生需求时：
        #1、遍历所有可选的路线 随机选择下游终点（同时可选路线锁定）
        #2、
    #遍历时间时：
        #1、判断是否有可乘坐的车
        #2、


def poisson(u):
    p = 1.0
    k = 0
    e = math.exp(-u)
    while p >= e:
        u = random.random()  #generate a random floating point number in the range [0.0, 1.0)
        p *= u
        k += 1
    return k-1