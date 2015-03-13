#coding=utf-8
__author__ = 'liuqianchao'
import MySQLdb
import numpy
import csv
try:
    conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='test', port=3306)
    cur = conn.cursor()
    #每次模拟前 需要对数据库进行清零
    cur.execute('truncate table test.Statistic')
    conn.commit()
    cur.close()
    conn.close()
except MySQLdb.Error, e:
    print "Mysql Error %d: %s" % (e.args[0], e.args[1])
#get statistical result
f = open('/users/liuqianchao/desktop/simulation/stationinput.txt')
stopinfo = []
line = f.readline()
while line:
    stopinfo.append(line.split(','))
    line = f.readline()

#存储文件
#将结果写入csv
#1.创建文件
f=file('/users/liuqianchao/desktop/excel/demo.csv','wb')
#2.写文件
writer=csv.writer(f)
writer.writerow(['stop_id','routeline_id','servicetime_mean','servicetime_var','waitingtime_mean','waitingtime_var'])

#convert to int
stopmatrix=[]
for i in range(len(stopinfo)):
    templine=[]
    for j in range(len(stopinfo[i])):
        templine.append(int(stopinfo[i][j]))
    stopmatrix.append(templine)
#遍历十条线路
for routeline_num in range(10):
    for stop_num in range(len(stopmatrix[routeline_num])):
        servicetime_datalist=[]
        waitingtime_datalist=[]
        try:
            conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='test', port=3306)
            cur = conn.cursor()
            aa=cur.execute("select start_service_time,end_service_time from test.Bus where routeline_id=%d" % routeline_num)
            info1=cur.fetchmany(aa)
            for item in info1:
                if item[1].split(',')[stop_num]!='':
                    servicetime = int(item[1].split(',')[stop_num])-int(item[0].split(',')[stop_num])
                    servicetime_datalist.append(servicetime)
            bb=cur.execute("select arrive_stop_time,start_service_time from test.Bus where routeline_id=%d" % routeline_num)
            info2=cur.fetchmany(bb)
            for item in info2:
                if item[1].split(',')[stop_num]!='':
                    waitingtime = int(item[1].split(',')[stop_num])-int(item[0].split(',')[stop_num])
                    waitingtime_datalist.append(waitingtime)
            conn.close()
        except Exception,e:
            print e.args[0]
        narray_servicetime=numpy.array(servicetime_datalist)
        lenght_servicetime=len(narray_servicetime)
        mean_servicetime=narray_servicetime.sum()/float(lenght_servicetime)
        var_servicetime=((narray_servicetime*narray_servicetime).sum())/float(lenght_servicetime)-mean_servicetime**2

        narray_waitingtime=numpy.array(waitingtime_datalist)
        lenght_waitingtime=len(narray_waitingtime)
        mean_waitingtime=narray_waitingtime.sum()/float(lenght_waitingtime)
        var_waitingtime=((narray_waitingtime*narray_waitingtime).sum())/float(lenght_waitingtime)-mean_waitingtime**2

        data=(stopmatrix[routeline_num][stop_num],routeline_num,mean_servicetime,var_servicetime,mean_waitingtime,var_waitingtime)
        writer.writerow(data)
f.close()




















