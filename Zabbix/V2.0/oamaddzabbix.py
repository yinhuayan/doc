#!/usr/bin/python
#coding: utf-8

import MySQLdb
import os
import re
import time
import string
import smtplib
from email.mime.text import MIMEText
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

#获取时间
localtime = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))+""

print localtime

#创建监控项数据函数
def value( val ):
    a = val[0]
    b = a[0]
    return b

#创建Zabbix监控IP和端口列表函数
def value_zabbixportlist (val):
     a=list(val)
     l=len(a)
     b=0
     while b<l:
        c=a[b]
        g=list(c)
        d=g[1]
        e=re.findall(r'\d+',d,re.M)
        f=e[-1]
        g[1]=f
        a[b]=g
        b=b+1  
     return a		
#创建数据库数据转换列表函数
def value_list (val):
     a=list(val)
     l=len(a)
     b=0
     while b<l:
        c=a[b]
        g=list(c)
        a[b]=g
        b=b+1  
     return a

#创建发送邮件函数	 
def email (useremail,name,ip,port,status):
   a=useremail
   b=name
   c=ip
   d=port
   e=status
   
   #配置邮箱
   sender = 'POAM@fe.com'
   receiver = ''+a+',252491900@qq.com'
   receiver = string.splitfields(receiver, ",")
   subject = '产品端口监控'+e+'【' + localtime + '】'
   smtpserver = 'm.fe.com'
   username = 'POAM'
   password = '!@#2015'

   #文件内容
   msg = MIMEText("<html><p>产品名称："+str(b)+"</p><p>产品所在服务器IP："+str(c)+"</p><p>监控端口："+str(d)+"</p></html>",'html','utf-8')

  #邮件头显示
   msg['Subject'] = subject
   msg['from'] = sender
   msg['to'] =  ','.join(receiver)

   #发送邮件
   try:
      smtp = smtplib.SMTP()
      smtp.connect('m.fe.com')
      smtp.login(username, password)
      smtp.sendmail(sender, receiver, msg.as_string())
      smtp.quit()
      print "Successfully sent email"
   except Exception, e:  
      print str(e)

	 
#打开oam数据库连接
db1 = MySQLdb.connect("192.168.106.119","lyh","lyh","oam",charset="utf8" )	
# 使用cursor()方法获取操作游标 
cursor1 = db1.cursor() 

# 打开zabbix数据库连接
db2 = MySQLdb.connect("10.228.3.87","root","123","zabbix",charset="utf8" )
# 使用cursor()方法获取操作游标 
cursor2 = db2.cursor() 

#OAM
#获取OAM未下架产品需监控的端口和主机IP
sql12="SELECT ip,port from v_zabbix_zabbixinfo where entity_id not in(SELECT entity_id from v_zabbix_productdown)"
cursor1.execute(sql12)
b1=cursor1.fetchall()
b=value_list(b1)

#获取OAM未下架产品需监控的主机IP	 
sql14="SELECT DISTINCT ip from v_zabbix_zabbixinfo where entity_id not in(SELECT entity_id from v_zabbix_productdown) ORDER BY updated DESC"
cursor1.execute(sql14)
bip1=cursor1.fetchall()
bip=value_list(bip1)

#获取OAM下架产品需监控的端口和主机IP
sql15="SELECT ip,port from v_zabbix_zabbixinfo where entity_id in(SELECT entity_id from v_zabbix_productdown)"
cursor1.execute(sql15)
bd1=cursor1.fetchall()
bd=value_list(bd1)

#获取OAM下架产品需监控的主机IP	 
sql16="SELECT DISTINCT ip from v_zabbix_zabbixinfo where entity_id in(SELECT entity_id from v_zabbix_productdown) ORDER BY updated DESC"
cursor1.execute(sql16)
bipd1=cursor1.fetchall()
bipd=value_list(bipd1)

#Zabbix
#获取zabbix端口与IP监控信息
sql210="select b.host,a.key_ from items a,hosts b where a.hostid  in (SELECT hostid from hosts where host LIKE '10%' or host LIKE'192%') and a.key_ like 'net.tcp%' and a.hostid=b.hostid"
cursor2.execute(sql210)
a1=cursor2.fetchall()
a= value_zabbixportlist(a1) 
#获取zabbix端口监控ip信息
sql211="SELECT DISTINCT host from hosts where host LIKE '10%' or host LIKE'192%'"
cursor2.execute(sql211)
aip1=cursor2.fetchall()
aip= value_list(aip1)

#查询所有监控端口itemid已加到报警的itemid
sql219="select DISTINCT itemid from functions where itemid in (select itemid from items a where a.hostid  in (SELECT hostid from hosts where host LIKE '10%' or host LIKE'192%') and a.key_ like 'net.tcp%')"
cursor2.execute(sql219)
cid1=cursor2.fetchall()
cid= value_list(cid1)

#查询所有监控端口itemid已加到图表的itemid
sql223="select DISTINCT itemid from graphs_items where itemid in (select itemid from items a where a.hostid  in (SELECT hostid from hosts where host LIKE '10%' or host LIKE'192%') and a.key_ like 'net.tcp%')"
cursor2.execute(sql223)
did1=cursor2.fetchall()
did= value_list(did1)


#获取数据组数量
l1=len(a)
l2=len(b)
l3=len(aip)
l4=len(bip)
l5=len(bd)
l6=len(bipd)
#全局参数
i1=0
i2=0
i3=0
i4=0


#OAM运维平台新添加及变更产品端口监控添加到Zabbix
if l4<=l3:
 while i2<l4:
  if bip[i2] in aip:
   if l2<l1:
     while i1<l2:
      if b[i1] in a:
             c=b[i1]
             port=c[1]
             hostname=c[0]
             #获取OAM未下架产品名称
             sql17="select name from v_zabbix_zabbixinfo where ip like '"+str(hostname)+"' and port like '"+str(port)+"'"
             cursor1.execute(sql17)
             name_value=cursor1.fetchall()
             name=value(name_value)
             #获取端口监控项itemid
             sql213="select  a.itemid from items a ,hosts b where b.host like '"+str(hostname)+"' and b.hostid=a.hostid and (a.key_ like concat('net.tcp.port[','"+str(hostname)+"',',','"+str(port)+"',']') or  a.key_ like concat('net.tcp.listen[','"+str(port)+"',']') or a.key_ like concat('net.tcp.listen[,','"+str(port)+"',']')) "
             cursor2.execute(sql213)
             id = cursor2.fetchall()
             itemid = value(id)
             graph1=id[0]
             graph=list(graph1)
             if graph in cid and graph in did:
               #更新端口监控项名称
               sql214="update items set name = concat('"+name+"port',"+str(port)+") where itemid like '"+str(itemid)+"'"
               cursor2.execute(sql214)
                #获取触发器triggerid
               sql215="select triggerid from functions where itemid like '"+str(itemid)+"'" 
               cursor2.execute(sql215)
               id = cursor2.fetchall()
               triggerid = value(id)
               #更新端口报警名称
               sql216="update triggers a,functions b,items c set a.description=concat( c.name,'is not runnning') where a.triggerid like '"+str(triggerid)+"' and a.triggerid=b.triggerid and b.itemid=c.itemid"
               cursor2.execute(sql216)
               #获取图表graphid
               sql218="select graphid from graphs_items where itemid like '"+str(itemid)+"'"
               cursor2.execute(sql218)
               id = cursor2.fetchall()
               graphid = value(id)
               #更新图表名称
               sql217="update graphs a,graphs_items b,items c set a.name=c.name where a.graphid like '"+str(graphid)+"' and a.graphid=b.graphid and b.itemid=c.itemid"
               cursor2.execute(sql217)
               db2.commit()
             else:
                 print "未添加监控端口触发器",name,c[0],c[1]
                 sql222="DELETE a.* from items a ,hosts b where b.host like '"+str(hostname)+"' and b.hostid=a.hostid and (a.key_ like concat('net.tcp.port[','"+str(hostname)+"',',','"+str(port)+"',']') or  a.key_ like concat('net.tcp.listen[','"+str(port)+"',']') or a.key_ like concat('net.tcp.listen[,','"+str(port)+"',']'))"
                 #获取hostid数据
                 sql224="SELECT `hostid` from `hosts` where `host` like  '" +hostname +"'"
                 cursor2.execute(sql224)
                 id = cursor2.fetchall()
                 hostid = value(id)
				 #获取itemid数据
                 sql232="select  itemid from items  order by itemid desc LIMIT 0,1"
                 cursor2.execute(sql232)
                 id = cursor2.fetchall()
                 itemid1 = value(id)
                 itemid=itemid1+1
                 #插入端口监控
                 sql225="insert into `items` (`itemid`,`hostid`,`name`,`key_`,`delay`,`formula`,`interfaceid`)values("+str(itemid)+","+str(hostid)+",concat('"+name+"port',"+str(port)+"),concat('net.tcp.port[','"+str(hostname)+"',',','"+str(port)+"',']'),'30','1','27')"
                 #新建triggerid模板
                 sql226="insert into triggers(triggerid)(select triggerid+'1' from triggers  order by triggerid desc LIMIT 0,1)"
                 #插入表达式
                 sql227="insert into functions(functionid,itemid,triggerid,function,parameter) (select a.functionid +'1',b.itemid,c.triggerid,'last','0' from functions as a ,items as b,triggers as c where b.itemid like '"+str(itemid)+"' and c.triggerid in (select c1.triggerid from ( select triggerid from triggers order by triggerid desc LIMIT 0,1)as c1) and a.functionid in (select a1.functionid from (select functionid from functions order by functionid desc LIMIT 0,1) as a1))"
                 #更新报警
                 sql228="update triggers a, functions b ,items as c set a.expression=concat('{',b.functionid, '}=0' ),a.priority= '5', a.description=concat( c.name,'is not runnning') where a.triggerid =b.triggerid and a.triggerid in (select c1.triggerid from ( select triggerid from triggers order by triggerid desc LIMIT 0,1)as c1) and c.itemid =b.itemid and c.itemid in (select c1.itemid from (SELECT itemid from items where itemid like '"+str(itemid)+"') as c1)"
                 #新建报表graphs模板
                 sql229="insert into graphs(graphid) (select graphid+'1' from graphs  order by graphid desc LIMIT 0,1)"
                 #插入报表数据
                 sql230="insert into graphs_items(gitemid,graphid,itemid)(select a.gitemid +'1',b.graphid,c.itemid from graphs_items a,graphs b,items c where a.gitemid in  (select a1.gitemid from ( select gitemid from graphs_items order by gitemid desc LIMIT 0,1)as a1) and b.graphid in  (select b1.graphid from ( select graphid from graphs order by graphid desc LIMIT 0,1)as b1) and c.itemid in (select c1.itemid from (SELECT itemid from items where itemid like '"+str(itemid)+"') as c1) )"
                 #更新报表graphs名称
                 sql231="update graphs_items a,graphs b,items c set b.name =c.name where b.graphid=a.graphid and a.itemid =c.itemid and c.itemid in (select c1.itemid from (SELECT itemid from items where itemid like '"+str(itemid)+"') as c1)"
                  #执行sql语句
                 cursor2.execute(sql222)
                 cursor2.execute(sql225)
                 cursor2.execute(sql226)
                 cursor2.execute(sql227)
                 cursor2.execute(sql228)
                 cursor2.execute(sql229)
                 cursor2.execute(sql230)
                 cursor2.execute(sql231)
                 db2.commit()

      else:
         c=b[i1]
         print "未添加监控主机和端口",  c[0],c[1]
         port=c[1]
         hostname=c[0]
		 #获取zabbbix监控端口产品名称
         sql13="select name from v_zabbix_zabbixinfo where ip like '"+str(hostname)+"' and port like '"+str(port)+"'"
         cursor1.execute(sql13)
         name_value=cursor1.fetchall()
         name=value(name_value)
		 #获取产品运维责任人邮箱
         sql18="SELECT email from v_zabbix_userinfo where entity_id in (SELECT entity_id from v_zabbix_zabbixinfo where ip like '"+str(hostname)+"' and port like '"+str(port)+"')"
         cursor1.execute(sql18)
         mail_value=cursor1.fetchall()
         mail=value(mail_value)		 
		 #获取hostid数据
         sql21="SELECT `hostid` from `hosts` where `host` like  '" +hostname +"'"
         cursor2.execute(sql21)
         id = cursor2.fetchall()
         hostid = value(id)
		 #获取itemid数据
         sql22="select  itemid from items  order by itemid desc LIMIT 0,1"
         cursor2.execute(sql22)
         id = cursor2.fetchall()
         itemid1 = value(id)
         itemid=itemid1+1
         #插入端口监控
         sql23="insert into `items` (`itemid`,`hostid`,`name`,`key_`,`delay`,`formula`,`interfaceid`)values("+str(itemid)+","+str(hostid)+",concat('"+name+"port',"+str(port)+"),concat('net.tcp.port[','"+str(hostname)+"',',','"+str(port)+"',']'),'30','1','27')"
         #新建triggerid模板
         sql24="insert into triggers(triggerid)(select triggerid+'1' from triggers  order by triggerid desc LIMIT 0,1)"
         #插入表达式
         sql25="insert into functions(functionid,itemid,triggerid,function,parameter) (select a.functionid +'1',b.itemid,c.triggerid,'last','0' from functions as a ,items as b,triggers as c where b.itemid in (select b1.itemid from (SELECT itemid from items where itemid like '"+str(itemid)+"') as b1) and c.triggerid in (select c1.triggerid from ( select triggerid from triggers order by triggerid desc LIMIT 0,1)as c1) and a.functionid in (select a1.functionid from (select functionid from functions order by functionid desc LIMIT 0,1) as a1))"
         #更新报警
         sql26="update triggers a, functions b ,items as c set a.expression=concat('{',b.functionid, '}=0' ),a.priority= '5', a.description=concat( c.name,'is not runnning') where a.triggerid =b.triggerid and a.triggerid in (select c1.triggerid from ( select triggerid from triggers order by triggerid desc LIMIT 0,1)as c1) and c.itemid =b.itemid and c.itemid like '"+str(itemid)+"'"
         #新建报表graphs模板
         sql27="insert into graphs(graphid) (select graphid+'1' from graphs  order by graphid desc LIMIT 0,1)"
         #插入报表数据
         sql28="insert into graphs_items(gitemid,graphid,itemid)(select a.gitemid +'1',b.graphid,c.itemid from graphs_items a,graphs b,items c where a.gitemid in  (select a1.gitemid from ( select gitemid from graphs_items order by gitemid desc LIMIT 0,1)as a1) and b.graphid in  (select b1.graphid from ( select graphid from graphs order by graphid desc LIMIT 0,1)as b1) and c.itemid in (select c1.itemid from (SELECT itemid from items where itemid like '"+str(itemid)+"' ) as c1) )"
         #更新报表graphs名称
         sql29="update graphs_items a,graphs b,items c set b.name =c.name where b.graphid=a.graphid and a.itemid =c.itemid and c.itemid like '"+str(itemid)+"'"
         #执行sql语句
         cursor2.execute(sql23)
         cursor2.execute(sql24)
         cursor2.execute(sql25)
         cursor2.execute(sql26)
         cursor2.execute(sql27)
         cursor2.execute(sql28)
         cursor2.execute(sql29)
         db2.commit()
         print "已添加监控产品、主机和端口", name,c[0],c[1]
         status="正常"
         email(mail,name,hostname,port,status) 		 
      i1=i1+1
   else:
    print "OAM平台监控端口数量过多"
  else:
   d=bip[i2]
   hostname=d[0]
   #获取zabbbix监控端口产品名称
   sql110="select name from v_zabbix_zabbixinfo where ip like '"+str(hostname)+"'"
   cursor1.execute(sql110)
   name_value=cursor1.fetchall()
   name=value(name_value)
   #获取zabbix监控端口
   sql111="select port from v_zabbix_zabbixinfo where ip like '"+str(hostname)+"'" 
   cursor1.execute(sql111)
   port_value=cursor1.fetchall()
   port=value(port_value)
   #获取产品运维责任人邮箱
   sql19="SELECT email from v_zabbix_userinfo where entity_id in (SELECT entity_id from v_zabbix_zabbixinfo where ip like '"+str(hostname)+"')"
   cursor1.execute(sql19)
   mail_value=cursor1.fetchall()
   mail=value(mail_value)
   print "OAM平台监控ip未添加到zabbix:",d[0]
   hostname1=hostname+"该ip服务器未添加到zabbix监控，没有请添加，错误请修改。"
   status="异常"
   email(mail,name,hostname1,port,status)
   break
  i2=i2+1
else:
  print "OAM平台监控ip数量过多" 

#下架产品删除zabbix端口监控
if l6<=l3:
 while i4<l6:
  if bipd[i4] in aip:
   if l5<l1:
     while i3<l5:
      if bd[i3] in a:
             c=bd[i3]
             port=c[1]
             hostname=c[0]
             print "下架产品需删除的监控主机和端口",  c[0],c[1]
             sql212="DELETE a.* from items a ,hosts b where b.host like '"+str(hostname)+"' and b.hostid=a.hostid and (a.key_ like concat('net.tcp.port[','"+str(hostname)+"',',','"+str(port)+"',']') or  a.key_ like concat('net.tcp.listen[','"+str(port)+"',']') or a.key_ like concat('net.tcp.listen[,','"+str(port)+"',']'))"
             cursor2.execute(sql212)
             db2.commit()
            #获取zabbbix监控端口产品名称
             sql112="select name from v_zabbix_zabbixinfo where ip like '"+str(hostname)+"' and port like '"+str(port)+"'"
             cursor1.execute(sql112)
             name_value=cursor1.fetchall()
             name=value(name_value)
            #获取产品运维责任人邮箱
             sql113="SELECT email from v_zabbix_downinfo where entity_id in (SELECT entity_id from v_zabbix_zabbixinfo where ip like '"+str(hostname)+"' and port like '"+str(port)+"')"
             cursor1.execute(sql113)
             mail_value=cursor1.fetchall()
             mail=value(mail_value)
             status="已删除"
             port1=port+ "已删除"
             email(mail,name,hostname,port1,status)			 
             print "已删除监控主机和端口",  name,c[0],c[1]			 
      else:
	     #获取zabbbix监控端口产品名称
         sql114="select name from v_zabbix_zabbixinfo where ip like '"+str(hostname)+"' and port like '"+str(port)+"'"
         cursor1.execute(sql114)
         name_value=cursor1.fetchall()
         c=bd[i3]		 
         print "下架产品已删除的监控产品主机和端口", name,c[0],c[1]          				 
      i3=i3+1
   else:
    print "OAM平台监控端口数量过多"
  else:
   d=bipd[i4]
   print "OAM平台监控ip未添加到zabbix,不用删除监控的ip:",d[0]
   break
  i4=i4+1
else:
  print "OAM平台监控ip数量过多" 
  
print "Zabbix在线监控端口总数:",l1
print "OAM在线监控端口总数:",l2 
print "zabbix在线监控ip总数:",l3 
print "OAM在线监控ip总数:",l4 
print "OAM需下架监控端口总数:",l5 

# 关闭数据库连接
db1.close()
db2.close()
