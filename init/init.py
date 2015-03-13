# encoding=utf-8
__author__ = 'liuqianchao'
from Bus import Bus
from Station import Staion
from RouteLine import RouteLine
from Passenger import Passenger
import random
import math
import MySQLdb
import time

import threading

#to do:add berth number
def poisson(u):#泊松函数
    p = 1.0
    k = 0
    e = math.exp(-u)
    while p >= e:
        u = random.random()
        p *= u
        k += 1
    return k - 1


def clock(routeinstancelist, stationinstancelist):
    #先遍历公交线路，后遍历线路上run的车,随机因素包括
    passengerid = 0#乘客计数
    targettime = input('请输入要查询的时间距公交系统开始营运时间（6：00）的秒数,比如7：00为3600:')
    for clock in range(targettime):
        #一、更新车站候车信息、每隔5min设置下5min更新站点乘客信息

        #一.1 确定下十分钟各可能路线的总需求，写入需求矩阵
        if (clock % 600 == 0):
            for routeline in routeinstancelist:
                f = open('/users/liuqianchao/desktop/simulation/matrix/%s.txt' % routeline.routelineID, 'w')
                for i in range(len(routeline.stoplist)):
                    for j in range(len(routeline.stoplist)):
                        if j == len(routeline.stoplist) - 1:
                            if i >= j:
                                f.write('0')
                            else:
                                f.write('%s' % poisson(2))  #10分钟a➡b人数
                        else:
                            if i >= j:
                                f.write('0,')
                            else:
                                f.write('%s,' % poisson(2))
                    f.write('\n')
                f.close()


        #一.2读取需求矩阵，逐秒钟创建乘客
        mats = []#mat保存各可能线路乘客到达间隔
        for routeline in routeinstancelist:
            temp = []
            f = open('/users/liuqianchao/desktop/simulation/matrix/%s.txt' % routeline.routelineID, 'r')
            line = f.readline()
            while line:
                temp.append(line.split(','))
                line = f.readline()
            mats.append(temp)
        #获取间隔
        datalist = []
        for i in range(len(mats)):
            for j in range(len(mats[i])):
                for z in range(len(mats[i][j])):
                    if int(mats[i][j][z]) > 0:
                        mats[i][j][z] = 600 / int(mats[i][j][z])
                        temp = []
                        temp.append(routeinstancelist[i].stoplist[j])
                        temp.append(routeinstancelist[i].stoplist[z])
                        temp.append(mats[i][j][z])
                        datalist.append(temp)
        try:
            conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='test', port=3306)
            cur = conn.cursor()
            for data in datalist:
                if (clock % 600) % data[2] == 0:
                    for station in stationinstancelist:
                        if station.stationID == data[0]:
                            passengerid += 1
                            station.passenger.append(Passenger(passengerid, data[0], data[1], clock))
                            cur.execute("insert into test.Passenger(passenger_id,start_stop_id,end_stop_id,arrive_stop_time) values(%d,%d,%d,%d)" % (passengerid,data[0], data[1], clock))
            conn.commit()
            cur.close()
            conn.close()
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])


        intervaltime = 1200#发车间隔
        #二、更新公交车
        for routeline in routeinstancelist:
            #1、在每一秒首先判断该route是否有新车发出，每隔20min（1200s）每条线路发出一辆新车active→true
            if (clock % intervaltime == 0):
                for car in routeline.buslist:
                    if (car.active == False and car.forestation == routeline.stoplist[0] and car.rundistance == 0):
                        car.active = True
                        break#break使只激活候发车中的第一辆车

            #2、update (routeline)上的busonrun
            busonrun = []
            for car in routeline.buslist:
                if (car.active == True):
                    busonrun.append(car)
            routeline.updatebusrunning(busonrun)


            #3、判断是否到达新站，如果到达，设置为候车。每次到站该子语句只执行一次
            for car in routeline.busrunning:
                indexofforeshop = routeline.stoplist.index(car.forestation)
                if ((car.rundistance!=0 and car.rundistance >= int(routeline.distancelist[indexofforeshop]) * 100) or (car.forestation == routeline.stoplist[0] and car.rundistance == 0 and clock % intervaltime == 0)):
                    car.arrive_stop_time.append(clock)
                    if (car.forestation == routeline.stoplist[len(routeline.stoplist) - 2]):
                        #到达终点
                        car.forestation = routeline.stoplist[indexofforeshop + 1]
                        car.rundistance = 0
                        car.parkwaitingtime=1#开始候车，等待服务
                    else:
                        #到达非终点车站，先更新车辆位置信息
                        if car.rundistance >= int(routeline.distancelist[indexofforeshop]) * 100:
                            car.forestation = routeline.stoplist[indexofforeshop + 1]
                            car.rundistance = 0
                            car.parkwaitingtime=1#开始候车，等待服务
                        #始发点
                        else:
                            car.parkwaitingtime=1#开始候车，等待服务



            #4、进行服务，服务完毕离开车站，腾出泊位（只要检测该car处于候车状态（处于终点stop的car即使active属于false也要进行服务--对应＃5）就执行该子模块）
            for car in routeline.busrunning:
                indexofforeshop = routeline.stoplist.index(car.forestation)#前一站的车站序号
                indexofpreshop = indexofforeshop + 1
                #泊车等待处理
                if car.rundistance == 0 and car.parkwaitingtime != 0:#在候车
                    for station in stationinstancelist:
                        if station.stationID == car.forestation:
                            #如果有车位，进入车位，开始乘客服务
                            if (len(station.parking) < station.berthnumber):
                                #泊车等待结束
                                car.parkwaitingtime = 0
                                car.start_service_time.append(clock)
                                station.parking.append(car.busID)
                                #开启服务
                                #下车
                                leavenum = 0

                                #在某一秒时乘客进行下车操作，实际情况时同时下车的，纪录进数据库中时
                                for passenger in car.passengers:
                                    if passenger.terminus_Staion==station.stationID:
                                        passenger.getout_finishtime=clock+1*leavenum
                                        leavenum+=1
                                        #--update数据库--#
                                        try:

                                            conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='test', port=3306)
                                            cur = conn.cursor()
                                            cur.execute("update test.Passenger set get_off_bus_time=%d where passenger_id=%d" % (clock + 1 * leavenum,passenger.passenger_id))
                                            conn.commit()
                                            cur.close()
                                            conn.close()
                                        except MySQLdb.Error, e:
                                            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
                                        #---------------#
                                #删
                                car.passengers = [passenger for passenger in car.passengers if passenger.terminus_Staion!=station.stationID]
                                #上车
                                boardnum = 0
                                for i in range(len(routeline.stoplist) - (indexofforeshop + 1)):
                                    for nextstation in stationinstancelist:
                                        if nextstation.stationID == routeline.stoplist[i + indexofforeshop + 1]:
                                            for passenger in station.passenger:
                                                if passenger.terminus_Staion == nextstation.stationID:#车站中的这个顾客可以选择该条线路
                                                    if len(car.passengers) < car.capacity:#乘客未满
                                                        passenger.board_finishtime = clock + boardnum * 2#最终上车时间
                                                        car.passengers.append(passenger)#乘客上车
                                                        station.passenger.remove(passenger)#乘客离开站点
                                                        #--update数据库--#
                                                        try:

                                                            conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='test', port=3306)
                                                            cur = conn.cursor()
                                                            cur.execute("update test.Passenger set get_on_bus_time=%d,bus_id=%d,routeline_id=%d where passenger_id=%d" % (passenger.board_finishtime,car.busID,routeline.routelineID,passenger.passenger_id))
                                                            conn.commit()
                                                            cur.close()
                                                            conn.close()
                                                        except MySQLdb.Error, e:
                                                            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
                                                        #---------------#
                                                        boardnum += 1
                                    #设置等待时间
                                car.waitingtime = max(leavenum*1,boardnum*2)
                                car.passenger_get_on_number.append(boardnum)
                                car.passenger_get_off_number.append(leavenum)
                            #如果没车位，继续等待
                            else:
                                car.parkwaitingtime = 1#继续等待



            #6、对每一辆busonrun(bus),判断是否在原地等待，如果不是，更新距离距离信息（更新rundistance）
            for car in routeline.busrunning:
                if car.parkwaitingtime == 0:#没有在候车
                    #在服务
                    if car.waitingtime != 0:
                        car.waitingtime -= 1
                        if car.waitingtime == 0:#服务完毕，腾出泊位
                            car.end_service_time.append(clock)
                            #如果是在终点站完成服务，active设为false
                            if car.forestation == routeline.stoplist[len(routeline.stoplist) - 1]:
                                car.active=False
                            for station in stationinstancelist:
                                if station.stationID == car.forestation:
                                    station.parking.remove(car.busID)
                    #在行驶
                    else:
                        speed = random.gauss(1, 0.1)#!!汽车行驶速度，需要导入数据
                        car.rundistance += speed

            #5、updata busonrun
            busonrun = []
            for car in routeline.buslist:
                if (car.active == True):
                    busonrun.append(car)
            routeline.updatebusrunning(busonrun)

        #update stops'state
        for station in stationinstancelist:
            station.stopstate.append(len(station.parking))

if __name__ == "__main__":
    start = time.clock()
    #清空数据库
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='test', port=3306)
        cur = conn.cursor()
        #每次模拟前 需要对数据库进行清零
        cur.execute('truncate table test.Passenger')
        cur.execute('truncate table test.Bus')
        cur.execute('truncate table test.Stop')
        cur.execute('truncate table test.Statistic')
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    #读入stationlist,共10条公交线路
    f1 = open('/users/liuqianchao/desktop/simulation/stationinput.txt')
    stoplist = []
    line1 = f1.readline()
    while line1:
        stoplist.append(line1.split(','))
        line1 = f1.readline()

    #读入distancelist
    f2 = open('/users/liuqianchao/desktop/simulation/distanceinput.txt')
    distancelist = []
    line2 = f2.readline()
    while line2:
        distancelist.append(line2.split(','))
        line2 = f2.readline()


    #初始化公交线路
    routeinstancelist = []
    for i in range(10):
        newroute = RouteLine(i, stoplist[i], distancelist[i])
        routeinstancelist.append(newroute)

    bus_num_per_routeline=30
    #初始化公交汽车，每一个条公交线路分配10辆车,一号线路分配1-10号车，二号线路分配11-20号车...
    for i in range(10):
        buslist = []
        for j in range(bus_num_per_routeline):
            buslist.append(Bus(i * bus_num_per_routeline + j + 1, i, routeinstancelist[i].stoplist[0]))#车号，公交线路ID，起始位置公交车站号
        routeinstancelist[i].setbuslist(buslist)#将各线路上的车分别分配到十条线路上，之后再操作公交车通过线路操作
        #----写入数据库
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='test', port=3306)
        cur = conn.cursor()
        for i in range(10):
            for j in range(bus_num_per_routeline):
                cur.execute("insert into test.Bus(bus_id,routeline_id) values(%d,%d)" %(i * bus_num_per_routeline + j + 1,i))
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    #初始化公交车站,Station:1,2.3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,24,Stastioninstancelist[1]表示第一个公交车站
    stationinstancelist = []
    for i in range(24):
        stationinstancelist.append(Staion(i + 1,2))#ID,Berthnumber
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='test', port=3306)
        cur = conn.cursor()
        for i in range(24):
            cur.execute("insert into test.Stop(stop_id) values(%d)" %(i+1))
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    #调用
    clock(routeinstancelist, stationinstancelist)

    #insert data of Bus into database

    for routeline in routeinstancelist:
        for car in routeline.buslist:
            try:
                conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='test', port=3306,use_unicode=1, charset='utf8')
                cur = conn.cursor()

                arrive_stop_time=''
                for item in car.arrive_stop_time:
                    arrive_stop_time+=str(item)+','

                start_service_time=''
                for item in car.start_service_time:
                    start_service_time+=str(item)+','

                end_service_time=''
                for item in car.end_service_time:
                    end_service_time+=str(item)+','

                passenger_get_on_number=''
                for item in car.passenger_get_on_number:
                    passenger_get_on_number+=str(item)+','

                passenger_get_off_number=''
                for item in car.passenger_get_off_number:
                    passenger_get_off_number+=str(item)+','

                passengernumber=0
                for i in range(len(car.passenger_get_on_number)):
                    passengernumber+=car.passenger_get_on_number[i]
                    passengernumber-=car.passenger_get_off_number[i]
                    car.passenger_number.append(passengernumber)
                for i in range(len(car.arrive_stop_time)-1):
                    car.running_time.append(car.arrive_stop_time[i+1]-car.end_service_time[i])


                running_time=''
                for item in car.running_time:
                    running_time+=str(item)+','

                passenger_number=''
                for item in car.passenger_number:
                    passenger_number+=str(item)+','

                cur.execute("update test.Bus set arrive_stop_time='%s',start_service_time='%s',end_service_time='%s',passenger_get_on_number='%s',passenger_get_off_number='%s',running_time='%s',passenger_number='%s' where bus_id=%d" %(arrive_stop_time,start_service_time,end_service_time,passenger_get_on_number,passenger_get_off_number,running_time,passenger_number,car.busID))
                conn.commit()
                cur.close()
                conn.close()
            except MySQLdb.Error, e:
                print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    # insert stops'state into database
    for station in stationinstancelist:
        try:
            conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='test', port=3306)
            cur = conn.cursor()
            text=''
            for item in station.stopstate:
                text+=str(item)+','
            cur.execute("update test.Stop set stop_state='%s' where stop_id=%d" %(text,station.stationID))
            conn.commit()
            cur.close()
            conn.close()
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])


    #输出运行结果
    for routeline in routeinstancelist:
        print('routeID:' + str(routeline.routelineID))
        for car in routeline.buslist:
            car.information()
        print('----------------------------------------------------------------')

    execfile('chart.py')
    execfile('Statistic.py')
    elapsed = (time.clock() - start)
    print("Time used:",elapsed)