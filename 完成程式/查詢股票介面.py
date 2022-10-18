#建立500x300的視窗
from tkinter import *
import time
import threading,三圖版


aaa=open('公司代號對照表.csv','r',encoding="utf-8")
bbb=aaa.read().split("\n")
公司清單與代號={}
for i in range(965):
    公司清單與代號[f'{bbb[i][:4]}']=bbb[i][4:]

def pr():
    代號=公司代號.get()
    try:
        stock_id=代號+'.TW'
        公司名稱=公司清單與代號[代號]
        localtime = time.localtime(time.time())
        開始=str(localtime.tm_year-2)+"-"+str(localtime.tm_mon)+"-"+str(localtime.tm_mday)
        終止=str(localtime.tm_year)+"-"+str(localtime.tm_mon)+"-"+str(localtime.tm_mday+1)
        三圖版.取得股票資料(公司名稱,stock_id,開始,終止)
    except:
        num1.set("請輸入正確代號")

        
    
def newtask():
    t = threading.Thread(target=pr)## 建立一個子執行緒
    t.start()# 執行該子執行緒

window = Tk() #呼叫TK( )函式建立視窗，T大寫，k小寫
window.title('股市查詢')#視窗標題
window.geometry('320x50')#寬*高

label=Label(window,text='請輸入公司代號:',font=14)#(顯示視窗,文字,顏色,字型與大小,文字語塞框之間的距離x,y)

label.pack(side='left')
num1=IntVar()
num1.set("請輸入代號")#將文字盒1設定預設文字
公司代號=Entry(window, width=20, textvariable=num1)#文字盒1
公司代號.pack(side='left')
btn=Button(window, width=5, text='go',command=newtask)#按鈕直接呼叫複雜的函數會死機，所以先呼叫平行執行的模組

btn.pack(side='left')
window.mainloop() #呼叫mainloop( )函式讓程式運作直到關閉視窗為止
#pyinstaller -w -F --icon=avwpt-ykoq7-002.ico 查詢股票介面.py