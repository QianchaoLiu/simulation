#coding=utf-8
from pylab import *
import matplotlib
import MySQLdb
for j in range(24):
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='test', port=3306)
        cur = conn.cursor()
        aa=cur.execute("select arrive_stop_time,get_on_bus_time from test.Passenger where start_stop_id=%d" % (j+1))
        info=cur.fetchmany(aa)
        data=[]
        for ii in info:
           #print ii[1]-ii[0]
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

    savefig('/users/liuqianchao/desktop/pic/%d.png' % (j+1) ,dpi=480)
    clf()
