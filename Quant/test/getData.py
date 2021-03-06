#-*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import tushare as ts
import datetime
import time
import tushare as ts
import os
  
data_dir = '/home/vnpy/share/'  #下载数据的存放路径
  
#ts.get_sz50s() #获取上证50成份股  返回值为DataFrame：code股票代码 name股票名称
  
#cal_dates = ts.trade_cal() #返回交易所日历，类型为DataFrame, calendarDate  isOpen
cal_dates = pd.read_csv(data_dir+'trade_cal.csv')
 
#本地实现判断市场开市函数
#@date: str类型日期 eg.'2017-11-23'
def is_open_day(date):
    if date in cal_dates['calendarDate'].values:
        return cal_dates[cal_dates['calendarDate']==date].iat[0,2]==1
    return False
  
  
#从TuShare获取tick data数据并保存到本地
#@symbol: str类型股票代码 eg.600030
#@date: date类型日期
def get_save_tick_data(symbol, date):
    global sleep_time,data_dir
    res=True
    sleep_time=2
    str_date=str(date)
    dir=data_dir+symbol+'/'+str(date.year)+'/'+str(date.month)
    file=dir+'/'+symbol+'_'+str_date+'.csv'
    if is_open_day(str_date):
        if not os.path.exists(dir):
            os.makedirs(dir)
        if not os.path.exists(file):
            try:
                d=ts.get_tick_data(symbol,str_date,pause=0.1)
            except IOError as msg:
                print str(msg).decode('UTF-8')
                sleep_time=min(sleep_time*2, 128)#每次下载失败后sleep_time翻倍，但是最大128s
                print 'Get tick data error: symbol: '+ symbol + ', date: '+str_date+', sleep time is: '+str(sleep_time)
                return res
            else:
                d.to_csv(file)
                #hdf5_file=pd.HDFStore(file, 'w',complevel=4, complib='blosc')
                #hdf5_file['data']=d
                #hdf5_file.close()
                sleep_time=max(sleep_time/2, 2) #每次成功下载后sleep_time变为一半，但是至少2s
                print "Successfully download and save file: "+file+', sleep time is: '+str(sleep_time)
                return res
        else:
            print "Data already downloaded before, skip " + file
            res=False
            return res
  
#获取从起始日期到截止日期中间的的所有日期，前后都是封闭区间
def get_date_list(begin_date, end_date):
    date_list = []
    while begin_date <= end_date:
        #date_str = str(begin_date)
        date_list.append(begin_date)
        begin_date += datetime.timedelta(days=1)
    return date_list
  
#获取感兴趣的所有股票信息，这里获取沪深全部股票
def get_all_stock_id():
    #stock_info=ts.get_hs300s()
    stock_info = pd.read_csv(data_dir+'stock_basics.csv')
    return stock_info['code'].values
 
# 补全股票代码(6位股票代码)
# input: int or string
# output: string
def getSixDigitalStockCode(code):
    strZero = ''
    for i in range(len(str(code)), 6):
        strZero += '0'
    return strZero + str(code)
 
#从TuShare下载感兴趣的所有股票的历史成交数据，并保存到本地HDF5压缩文件
#dates=get_date_list(datetime.date(2017,11,6), datetime.date(2017,11,12))
dates=get_date_list(datetime.date(2018,1,1), datetime.date(2018,7,9))
stocks=get_all_stock_id()
for stock in stocks:
    for date in dates:
       if get_save_tick_data(getSixDigitalStockCode(stock), date):
           time.sleep(sleep_time)