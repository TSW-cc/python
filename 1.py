import requests
import re
import urllib.parse as parse
import xlsxwriter
import threading
import sys
#设置登录百度贴吧账号后的请求头，如果失效，请登录自己的百度账号，重新设置一下下面的cookie
headers = {'content-type': 'application/json',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
           'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
           'Accept-Encoding':'gzip, deflate, br',
           'cookie':''    #为了隐私安全，这里就不展示登录状态后的cookie了
           }

url_main = 'http://tieba.baidu.com/'
user_all = []

fans_list = []
user_list = []
zhuye_list = []
public_q = ''
forbidden = 0
#正则匹配 获取中间文本
def get_midstring(buff,w1,w2):
    if '\n' in buff :
        buff = buff.replace('\n', '')
    pat = re.compile(w1 + '(.*?)' + w2, re.S)
    result = pat.findall(buff)
    return result

#超时重试，防止由于超时，导致爬虫卡死
def gethtml(url):
  i = 0
  while i < 3:
    try:
      html = requests.get(url, timeout=5 , headers = headers).text
      return html
    except requests.exceptions.RequestException:
      i += 1
  return '0'


#获取n个,评论数>m的贴子的楼主用户信息
import time
state = [0,0,0,0,0]

def get_tiezi(n,m,list,name,i,symbol):
    if len(user_list) == public_n :
        return
    index = i

    try:
        url = 'https://tieba.baidu.com/f?kw=hpv&ie=utf-8&pn=' + str(list[index] * 50)
        print(name + '   ' + url)
    except:
        state[symbol] = 1
        print(name + '   ' + '已完成任务，已获取楼主数量：' + str(len(user_list)))
        return

    private_respond = gethtml(url)
    if private_respond  == '0':
        print('连接错误-1，可能ip被屏蔽了...')
        return
    #print(private_respond.text)
    data_all = get_midstring(private_respond,r'<ul id="thread_list"',r'thread_list_bottom clearfix')[0]

    num_pinglun = get_midstring(data_all,r'title="回复">',r'</span>')
    num_url=get_midstring(data_all,r'/p/',r'"')
    private_str = get_midstring(data_all,r'主题作者',r'创建时间')
    num_user = []
    name_user = []
    print(name + '   初步过滤，贴子评论数不足' + str(m) + '的楼主...')
    for i in range(len(private_str)):
        try:
            if int(num_pinglun[i]) < m:
                continue;
            str_user = url_main + get_midstring(private_str[i],r'href="','"')[0]
            str_name = get_midstring(private_str[i],r':',r'"')[0]
            num_url[i] = url_main + 'p/'+num_url[i]
            num_user.append(str_user)
            name_user.append(str_name)
        except:
            print(len(private_str))
            print(len(num_pinglun))
            print('错误代码 000')


    if len(user_list) == public_n :
        return
    print(name + '   剩余' + str(len(num_user)) + '名楼主，开始判断是否关注hpv吧...')

    if len(num_user) ==0 :
        print(name + '   开始获取下一页贴子')
        index += 1
        get_tiezi(n, m,list,name,index,symbol)
        return

    for j in range(len(num_user)):
        b = get_gztb(num_user[j],name,name_user[j])
        if b == 'none':
            print('任务已完成，终止线程操作.')
            return

        if b >= n :
            print( name + '   ' + str(n) + '名符合条件的楼主已经获取完成..')
            break
            return
        elif j == len(num_user) - 1:
            print(name + '   开始获取下一页贴子')
            index += 1
            get_tiezi(n, m,list,name,index,symbol)
            break
        else:
            continue


#判断楼主是否关注贴吧,如果是，则获取粉丝ID，否则过滤掉该楼主
def get_gztb(user,name,name_user):
    private_respond = gethtml(user)

    if private_respond  == '0':
        print(name + '   连接错误-2，可能ip被屏蔽了...')
        return 0

    if len(user_list) == public_n:
        return 'none'

    if r'/f?kw=hpv&fr=home' in private_respond and '关注的吧' in private_respond:
        user_name =  name_user
        user_id = get_midstring(user,'&id=','&')[0]
        if user_name in user_list:
            print(name + '   ' + user_name + '已经获取过该楼主用户信息，自动跳过.')
            return len(user_list)
        print(name + '   正在获取用户：' + user_name + '的粉丝')
        zhuye_list.append(user)
        get_fans_id(user_id,user_name,name)
    else:
        print(name + '   未关注hpv吧，自动过滤.....')
        pass

    return len(user_list)

def get_fans_id(userid,username,name):
    if len(user_list) == public_n :
        return
    page = 1
    fans_id = []

    while 1:
        #print('正在获取第'+ str(page) +'页粉丝列表....')

        url = url_main + '/i/i/fans?u=' + userid + '&pn=' + str(page)
        private_respond = gethtml(url)
        if private_respond  == '0':
            print(name + '   连接错误-3，可能ip被屏蔽了...')
            return

        b= get_midstring(private_respond,r'name_show="',r'"')
        fans_id +=b

        if len(b) == 20:
            page = page + 1
            if d == 999 :
                pass
            elif  len(fans_id) > d :
                print(name + '   ' + username + ' 的粉丝数超过'+ str(d) +'人，过滤剩余粉丝....')
                user_list.append(username)
                fans_list.append(fans_id)
                print(name + '   ' + username + '粉丝获取完成')
                print(name + '   已经完成' + str(len(user_list)) + '个')
                break

        else:
            if len(b) == 0 :
                print('该楼主没有粉丝，或cookie已失效...')

            if len(user_list) == public_n:
                print(name + '   任务已完成，终止线程操作.')
                break

            user_list.append(username)
            fans_list.append(fans_id)

            print(name + '   ' + username + '粉丝获取完成')
            print(name + '   已经完成' + str(len(user_list)) + '个')
            break

#导出为Excel

def daochu():

    workbook = xlsxwriter.Workbook( public_q +'.xlsx')  # 新建excel表

    worksheet = workbook.add_worksheet('sheet1')  # 新建sheet（sheet的名称为"sheet1"）

    headings = ['楼主用户名','主页地址','粉丝数量','粉丝用户名']  # 设置表头

    worksheet.write_row('A1', headings)

    x = user_list
    y = fans_list

    for i in range(len(x)):
        a=[]
        a.append(x[i])
        a.append(zhuye_list[i])
        a.append(len(y[i]))

        user_data = a + y[i]
        worksheet.write_row('A' + str(i+2), user_data)

    workbook.close()
    print('导出成功')

#给每个线程url列表
list = {}
t=5
for i in  range(5):
    list[i] = []

for j in range(1,195):
    if j % t == 0:
        list[0].append(j)
    if j % t == 1:
        list[1].append(j)
    if j % t == 2:
        list[2].append(j)
    if j % t == 3:
        list[3].append(j)
    if j % t == 4:
        list[4].append(j)

#多线程操作
public_n = 0
class Messy:
    def main(self,n,m,q):
        self.n=n
        self.m=m
        global public_n,public_q
        public_n=n
        public_q=q

        Threads = []
        # 将会启动5个线程,满足条件的用户数达到n时，全部线程终止！
        if n ==0:
            print('线程已退出')
            return
        for i in range(5):
            t = threading.Thread(target=get_tiezi,args=(n,m,list[i],'线程' + str(i),0,i))
            t.daemon = 1
            Threads.append(t)
        # 启动所有线程
        for i in Threads:
            i.start()
        # 满足条件的用户数达到n时所有多线程结束
        while 1:
            if state[0] == state[1] == state[2] == state[3] == state[4]== 1:
                print('所有的主题帖已经爬取完了')
                break

            if len(user_list) == n :
                break
        print('线程退出!')

n = int(sys.argv[1]) #获取命令行第一个参数
m= int(sys.argv[2]) #获取命令行第二个参数
d= int(sys.argv[3]) #获取命令行第三个参数
q= sys.argv[4] #获取命令行第四个参数

Messy().main(n,m,q)

time.sleep(3)
print('开始导出Excel,请稍等....')
time.sleep(1)
daochu()

