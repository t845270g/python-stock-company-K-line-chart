import yfinance as yf 
import pandas
import plotly.graph_objects as go

import talib
from plotly import subplots

def 取得股票資料(公司名稱,stock_id,start,end):
    #-------------------------------整理查詢表格(目前有6屬性)--------------------------------#
    stock1=yf.download(stock_id,start,end)
    stock1.columns=['開盤價','最高價','最低價','收盤價','還原股價','成交量']
    #此時的索引值為日期格式，因為視pandas的時間序列為連續的，會造成繪製出來產生無開盤日期的空白

    #----重新設定索引值reset_index()，並新增欄位(目前有8屬性，索引值更換了，原本日期索引會變成屬性，又增加成交量顏色的屬性)----# 

    stock=stock1.reset_index()
    stock['成交量顏色']=""#新增一個屬性，顯示成交量的顏色
    
    #-------------------------------------------均線(目前有14屬性)-------------------------------------------# 
    #新增移動平均線屬性，值為rolling會將指定的表格數量的值，mean會計算這些資料的平均
    #所以如果rolling(5)時，前四天是無資料的，第五天才會有往前推五筆資料的平均，也就是五日均線
    #如果要知道指定天數中的最高點價格，就把mean()改成max()函式
    for ma in [5,10,20,60,120,240]:
        stock[f'{ma}MA']=stock['收盤價'].rolling(ma).mean()
    #-------------------------------------------KD值(目前有16屬性)-------------------------------------------# 
    stock['k'], stock['d'] = talib.STOCH(stock['最高價'], stock['最低價'], stock['收盤價'],fastk_period=9, slowk_period=3,slowd_period=3)
    stock['k'].fillna(value=0, inplace=True)
    stock['d'].fillna(value=0, inplace=True)
    #-------------------處理日期轉成字串/成交量顯示的顏色(目前有16屬性，多日期屬性，刪除原本時間型態的Date屬性)------------------------#  
    lll=[]#建立列表來放改成字串的日期
    for color in range(stock.shape[0]):#遍歷所有資料
        lll.append("/".join(str(stock.iloc[color,0])[:10].split("-")))#將時間型態的日期改成字串存到列表中
        if stock.iloc[color-1,4]<stock.iloc[color,4]:#如果前一天收盤價<當天收盤價，設定紅色>>上漲
            stock.iloc[color,7]='rgba(255, 212, 175,0.5)'
        elif stock.iloc[color-1,4]==stock.iloc[color,4]:
            stock.iloc[color,7]='rgba(201, 206, 243,0.5)'
        else: #如果開盤>收盤價，設定綠色>>下跌
            stock.iloc[color,7]='rgba(201, 242, 175,0.5)'

    stock.insert(0, "日期", lll)#最前面增加日期屬性，值為列表的資料
    stock=stock.drop(['Date'],axis=1)#刪除Date屬性
    del lll#刪除暫存的列表，因為值已經存到表格了

    for ema in [12,26]:
        stock[f'EMA_{ema}'] = stock['收盤價'].ewm(span=ema).mean()
    stock['DIF']=stock['EMA_12']-stock['EMA_26'] 
    stock['DEM']=stock['DIF'].ewm(span=9).mean()
    stock['OSC']=stock['DIF']-stock['DEM']#柱狀圖值
    macd_cilor=[]
    for r in stock['OSC']:
        if r>=0:
            macd_cilor.append('rgb(255,0,0)')
        else:
            macd_cilor.append('rgb(0,255,0)')
    stock['OSC_color']=macd_cilor
    del macd_cilor
    #-------------------------------------------設定子圖數量-------------------------------------------#  
    #設定繪製的子圖數量，上下2個，左右1個，並共用X軸
    fig = subplots.make_subplots(rows=3, cols=1,shared_xaxes=True,specs=[[{"secondary_y": True}],[{"secondary_y": False}],[{"secondary_y":True}]])

    #-------------------------------------------1.K線-均線-成交量-------------------------------------------#
    #畫K線蠟燭圖
    fig.add_trace(go.Candlestick(x =  stock['日期'],open = stock['開盤價'], 
                                        high = stock['最高價'],
                                        low = stock['最低價'],
                                        close = stock['收盤價'], 
                                        increasing_line_color= 'rgb(255,0,0)', 
                                        decreasing_line_color= 'rgb(0,255,0)',
                                        name='K線'), row=1, col=1, secondary_y=False)

    #畫均線折線圖                                 
    fig.add_trace(go.Scatter(x =  stock['日期'], y = stock['5MA'], name = '5 MA', line = dict(width=1,color ='rgb(255,255,0)')), row=1, col=1, secondary_y=False)
    fig.add_trace(go.Scatter(x =  stock['日期'], y = stock['20MA'], name = '20 MA', line = dict(width=1,color ='rgb(255,130,0)')), row=1, col=1, secondary_y=False)
    fig.add_trace(go.Scatter(x =  stock['日期'], y = stock['60MA'], name = '60 MA', line = dict(width=1,color ='rgb(0,0,255)')), row=1, col=1, secondary_y=False)
    fig.add_trace(go.Scatter(x =  stock['日期'], y = stock['240MA'], name = '240 MA', line = dict(width=1,color ='rgb(255,0,255)')), row=1, col=1, secondary_y=False)
    
    #畫成交量長條圖
    fig.add_trace(go.Bar(x = stock['日期'], y = stock['成交量'], name = '成交量',marker_color=stock['成交量顏色']), row=1, col=1, secondary_y=True) #看右邊刻度

    網格色="rgb(223, 225, 225)"
    表格色="rgb(255, 255, 240)"
    fig.update_yaxes(title_text="成交量                指數",title_font_size=20, row=1, col=1,gridcolor=網格色, secondary_y=False)#左邊的y設定排版更新
    fig.update_yaxes(showgrid=False, secondary_y=True)#右邊刻度對照的y輔助線拿掉
    
    #-------------------------------------------2.KD線折線圖-------------------------------------------#

    fig.add_trace(go.Scatter(x =  stock['日期'], y = stock['k'], name = 'K', line = dict(width=2,color ='rgb(255,150,0)')), row=2, col=1, secondary_y=False)
    fig.add_trace(go.Scatter(x =  stock['日期'], y = stock['d'], name = 'D', line = dict(width=1.5,color ='rgb(0,0,255)')), row=2, col=1, secondary_y=False)#慢
    for color in range(stock.shape[0]):#遍歷所有資料
        #判斷黃金交叉(k>d，前一天的k<d，k值<30)，5ma<10ma，5ma>60ma，收盤比前一天高(可能是紅的也可能是綠的)
        if stock.iloc[color,14]>stock.iloc[color,15] and stock.iloc[color-1,14]<stock.iloc[color-1,15] and stock.iloc[color,14]<30 and stock.iloc[color,8]<stock.iloc[color,9]and stock.iloc[color,8]>stock.iloc[color,11]and stock.iloc[color,7]=='rgba(255, 212, 175,0.5)':
            a=stock['日期'][color]
            b=stock['收盤價'][color]
            fig.add_annotation(x=a, y=b,text="買點",showarrow=True,arrowhead=1,arrowcolor='black',arrowsize=1,arrowwidth=2,ax=0,ay=-100, bordercolor='red',bgcolor='yellow')
    


    fig.update_yaxes(title_text="KD值",title_font_size=20, row=2, col=1,showgrid=False)#子圖2新增y軸標題
    fig.update_xaxes(showgrid=False)
    #-------------------------------------------3.macd-------------------------------------------#
    fig.add_trace(go.Bar(x = stock['日期'], y = stock['OSC'], name = '信號柱',marker_color=stock['OSC_color']), row=3, col=1, secondary_y=False)
    fig.add_trace(go.Scatter(x =  stock['日期'], y = stock['DEM'], name = 'DEM', line = dict(width=1,color ='rgb(0,0,255)')), row=3, col=1, secondary_y=True)
    fig.add_trace(go.Scatter(x =  stock['日期'], y = stock['DIF'], name = 'DIF', line = dict(width=1,color ='rgb(255,150,0)')), row=3, col=1, secondary_y=True)
    

    #fig.update_yaxes(row=3, col=1,showgrid=True)#隱藏MACD右邊的刻度，還沒寫好
    fig.update_yaxes(title_text="MACD",title_font_size=20, row=3, col=1,showgrid=False)#子圖2新增y軸標題
    fig.update_xaxes(showgrid=False)
    fig.update_xaxes(showspikes=True, spikemode='toaxis', spikesnap='data', spikecolor='grey',spikethickness=1, spikedash='dot')  
    fig.update_yaxes(showspikes=True,spikemode='toaxis',spikesnap='data', spikecolor='grey',spikethickness=1, spikedash='dot')
    fig.update_layout(spikedistance=-1,hoverdistance=-1, hovermode = "x unified",showlegend= False) 
    layout = dict( title_x=0.5,title_font_size=25, # title居中
                    font=dict(family="Arial",size=20,color="RebeccaPurple"),# 字体设置
                    coloraxis_colorbar=dict(xanchor="left",ticks="inside"),# 颜色条设置
                    margin=dict(b= 40,l=40, r=40, t= 40),# 大小设置
                    xaxis_rangeslider_visible=False,
                    yaxis1= {"domain": [0.4,1]},
                    yaxis3= {"domain": [0.2,0.4]} ,
                    yaxis4= {"domain": [0,0.2]} )#子圖顯示?
    fig.update_layout(layout,title_text=f"{公司名稱}:K線、均線、kd值、買點推薦",plot_bgcolor=表格色,paper_bgcolor=表格色 )
    
    """
    #表格
    paper_bgcolor='#EE0000'  設定表格外的底色
    plot_bgcolor='black'     表格的背景色
    width=1000               表格寬度

    #圖例
    legend_title='我是图例'  縮圖的名稱，默認沒有名稱
    legend_title_font_color='red'縮圖的名稱文字顏色

    #標題
    title='我是标题',   標題名稱
    title_font_size=22,  標體字大小
    title_font_color='red',  標題字顏色
    title_x=0.4  標題字在視窗多少比例處放置

    #子圖
    xaxis_rangeslider_visible=False
    """

    fig.show()#印出圖像
    return fig

#取得股票資料(輸入的代號資料,開始,終止)
# 取得股票資料("中鋼","2002.TW","2020-05-27","2022-05-27")
