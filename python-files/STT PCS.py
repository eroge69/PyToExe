//  By SIMPLE TRADING TECHNIQUES

//   	Arrow represent trade setup 
//   	Circle represent triggering of the trade
//--------------------------------------------------------------------

study(title="STT PULLBACK CANDLESTICK STRATEGY",overlay = true, shorttitle="STT PCS")
src = close, len = input(8, minval=1, title="Length")
up = rma(max(change(src), 0), len)
down = rma(-min(change(src), 0), len)
rsi = down == 0 ? 100 : up == 0 ? 0 : 100 - (100 / (1 + up / down))

//coloring method below

src1 = close, len1 = input(50, minval=1, title="UpLevel")
src2 = close, len2 = input(50, minval=1, title="DownLevel")
isup() => rsi > len1
isdown() => rsi < len2
barcolor(isup() ? green : isdown() ? red : na )

//study('buy/sell arrows', overlay=true)
lowest = lowest(low,(5))
highest = highest(high,(5))
pullbackB = (low == lowest) or (low[1] == lowest[1]) ? 1 : 0
pullbackS = (high == highest) or (high[1] == highest[1]) ? 1 : 0

value = (high - low) / 4
value1 = high - value
value2 = low + value

out = sma(close, 50)

data = (high > out ?  rsi > len1 ? pullbackB ? close >= value1 : na : na : na)  
data1 = (low < out ? rsi < len2 ? pullbackS ? close <= value2 : na : na : na)

plotchar(data, char='↑', location=location.belowbar, color=lime, text="PCS Buy")
plotchar(data1, char='↓', location=location.abovebar, color=red, text="PCS Sell")

//Trade Trigger
tiggerlongcandle = (data[1] == 1) and (high > high[1]) ? 1 : 0
tiggershortcandle = (data1[1] == 1) and (low < low[1]) ? 1 : 0
plotshape(tiggerlongcandle ? tiggerlongcandle : na, title="Triggered Long",style=shape.circle, location=location.belowbar, color=green, transp=0, offset=0, text="PCS")
plotshape(tiggershortcandle ? tiggershortcandle : na, title="Triggered Short",style=shape.circle, location=location.abovebar, color=red, transp=0, offset=0, text="PCS")

plot (out, color = black, linewidth = 3, title = "Trend - Long Term")