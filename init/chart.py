#coding=utf-8
from pylab import *
import matplotlib
import MySQLdb
import wx

#Passengers' waiting time
for j in range(24):
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='test', port=3306)
        cur = conn.cursor()
        aa=cur.execute("select arrive_stop_time,get_on_bus_time from test.Passenger where start_stop_id=%d" % (j+1))
        info=cur.fetchmany(aa)
        data=[]
        for ii in info:
           if ii[1]!=None:
                data.append(ii[1]-ii[0])
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    try:
        list=[]
        for i in range(100):
            list.append(0)
        for num in data:
            list[num/60]+=1
    except Exception,e:
        None
    #50组bar
    n = 100
    X = np.arange(n)
    Y = list
    axes([0.08,0.08,0.88,0.88])
    bar(X, Y, facecolor='#20B2AA', edgecolor='white',alpha=.8,width=1)

    for x,y in zip(X,Y):
        if y>0:
            text(x+0.6, y+0.01, y, ha='center', va='bottom',size=5)


    xlim(-.5,n), xticks(range(0,100,5),size=5)
    ylim(0,max(Y)+3), yticks(range(0,max(Y)+3,20),size=5)

    xlabel('waiting time of passengers /min',size=7)
    ylabel('number of passengers /person',size=7)
    title('Distribution Chart of Passengers\' waiting time at Shop%d' % (j+1),size=10)

    savefig('/users/liuqianchao/desktop/ans/passengers\'waitingtime/stop%d.png' % (j+1) ,dpi=480)
    clf()




#status chart of routeline
f = open('/users/liuqianchao/desktop/simulation/stationinput.txt')
stopinfo = []
line = f.readline()
while line:
    stopinfo.append(line.split(','))
    line = f.readline()
#convert to int
stopmatrix=[]
for i in range(len(stopinfo)):
    templine=[]
    for j in range(len(stopinfo[i])):
        templine.append(int(stopinfo[i][j]))
    stopmatrix.append(templine)



for routelinenum in range(len(stopmatrix)):
    n=len(stopmatrix[routelinenum])
    X=np.arange(n)
    Y1=[]#spare
    Y2=[]#service
    for i in range(n):
        Y1.append(0),Y2.append(0)
    statuslist=[]
    for id in stopmatrix[routelinenum]:
        try:
            conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='test', port=3306)
            cur = conn.cursor()
            aa=cur.execute("select stop_state from test.Stop where stop_id=%d" % (id))
            info=cur.fetchone()[0]
            statuslist.append(info)
            conn.commit()
            cur.close()
            conn.close()
        except Exception,e:
            print e.message
    for i in range(n):
        for j in statuslist[i].split(','):
            if j=='1':
                Y2[i]+=1
            elif j=='0':
                Y1[i]+=1
            else:
                None

    figure(figsize=(8,6))
    axes([0.08,0.08,0.88,0.86])
    bar(X-0.3, Y1, facecolor='#20B2AA', edgecolor='white',alpha=.8,width=0.3,label='status of spare')
    bar(X, Y2, facecolor='#ff9999', edgecolor='white',alpha=.8,width=0.3,label='status of service')

    for x,y in zip(X,Y1):
        text(x-0.15, y+0.01, y, ha='center', va='bottom',size=5)
    for x,y in zip(X,Y2):
        text(x+0.15, y+0.01, y, ha='center', va='bottom',size=5)
    xlim(-.5,n), xticks(range(n),stopmatrix[routelinenum],size=5)
    ylim(0,40000), yticks(range(0,20000,5000),size=5)

    legend(loc='upper right',fontsize=5)
    xlabel('Stop ID',size=7)
    ylabel('Time /s',size=7)
    title('Status Chart of Routeline%d'%(routelinenum+1),size=15)
    savefig('/users/liuqianchao/desktop/ans/stops\'status/routeline%d.png' % (routelinenum+1),dpi=480)
    clf()






#service time of bus at stops
for stop_id in range(24):
    stop_id+=1
    routelinelist=[]
    for i in range(len(stopmatrix)):
        for j in range(len(stopmatrix[i])):
            if stopmatrix[i][j]==stop_id:
                temp=[]
                temp.append(i)#i,j第i个routeline的第j个元素为该stop
                temp.append(j)
                routelinelist.append(temp)
                break
    datalist=[]
    #通过routeline_id找到车并存储下来相关数据
    for routeline_id in routelinelist:
        try:
            conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='test', port=3306)
            cur = conn.cursor()
            aa=cur.execute("select start_service_time,end_service_time from test.Bus where routeline_id=%d" % (routeline_id[0]))
            info=cur.fetchmany(aa)
            for item in info:
                datalist.append(int(item[1].split(',')[routeline_id[1]])-int(item[0].split(',')[routeline_id[1]]))
                #findbug
            conn.commit()
            cur.close()
            conn.close()
        except Exception,e:
            print e.message
    print min(datalist),max(datalist)

    X=range(0,max(datalist)+2,2)
    n=len(X)
    Y=[]
    for i in range(n):
        Y.append(0)
    for i in datalist:
        Y[i/2]+=1

    axes([0.08,0.08,0.88,0.88])
    bar(X, Y, facecolor='#20B2AA',edgecolor='white',alpha=.8,width=2)

    #for x,y in zip(X,Y):
    #text(x, y+0.01, '%.2f' % y, ha='center', va='bottom')

    #if max(datalist)>400:
    #    xlim(-.5,100), xticks(range(0,100,100/10))
    #else:
    xlim(-.5,max(datalist)+2), xticks(range(0,max(datalist),5))
    ylim(0,max(Y)+1), yticks(range(0,max(Y)))
    title('Service Time of Bus at Stop%d' % stop_id,size=15)
    xlabel('Service time /s',size=7)
    ylabel('Number of Bus',size=7)
    savefig('/users/liuqianchao/desktop/ans/buses\'servicetime/stop%d.png' % stop_id,dpi=480)
    clf()


#waiting time of bus at stops
for stop_id in range(24):
    stop_id+=1
    routelinelist=[]
    for i in range(len(stopmatrix)):
        for j in range(len(stopmatrix[i])):
            if stopmatrix[i][j]==stop_id:
                temp=[]
                temp.append(i)#i,j第i个routeline的第j个元素为该stop
                temp.append(j)
                routelinelist.append(temp)
                break
    datalist=[]
    #通过routeline_id找到车并存储下来相关数据
    for routeline_id in routelinelist:
        try:
            conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='test', port=3306)
            cur = conn.cursor()
            aa=cur.execute("select arrive_stop_time,start_service_time from test.Bus where routeline_id=%d" % (routeline_id[0]))
            info=cur.fetchmany(aa)
            for item in info:
                datalist.append(int(item[1].split(',')[routeline_id[1]])-int(item[0].split(',')[routeline_id[1]]))
            conn.commit()
            cur.close()
            conn.close()
        except Exception,e:
            print e.message
    print min(datalist),max(datalist)

    X=range(0,max(datalist)+2,2)
    n=len(X)
    Y=[]
    for i in range(n):
        Y.append(0)
    for i in datalist:
        Y[i/2]+=1

    axes([0.08,0.08,0.88,0.88])
    bar(X, Y, facecolor='#20B2AA',edgecolor='white',alpha=.8,width=2)

    #for x,y in zip(X,Y):
    #text(x, y+0.01, '%.2f' % y, ha='center', va='bottom')

    if max(datalist)<20:
        xlim(-.5,100), xticks(range(0,100,5))
    else:
        xlim(-.5,max(datalist)+2), xticks(range(0,max(datalist),max(datalist)/10))
    ylim(0,max(Y)+1), yticks(range(0,max(Y),max(Y)/10))
    title('Waiting Time of Bus at Stop%d' % stop_id,size=15)
    xlabel('Waiting time /s',size=7)
    ylabel('Number of Bus',size=7)
    savefig('/users/liuqianchao/desktop/ans/buses\'waitingtime/stop%d.png' % stop_id,dpi=480)
    clf()
