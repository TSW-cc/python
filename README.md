# python
一、使用方法
用法：
Python 1.py n m d q

选项：
n为需要获取的楼主数量
m为评论数
d 为限制获取楼主粉丝的最大数（最小为20，999为不限制粉丝最大数）
q 为导出时的文件名 (不要带后缀名，以及目录)

示例：
python 1.py 1000 20 50 user_data

解释：获取主题帖中评论数大于20的1000个楼主及粉丝,楼主粉丝数大于50时自动忽略超出50的部分，任务结束后，导出数据为当前目录下的user_data.xlsx文件
二、环境配置
Python版本 3.6.8
引用模块：
Reques
Re
Urllib
Xlswriter
Threading
