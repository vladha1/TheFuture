import yfinance as yf


response={}
ticker="^FCHI"
stock = yf.Ticker(ticker)

data1= stock.info
last=data1.get('regularMarketPrice')
pcChange=5#round((last/data1.get('previousClose')-1)*100,2)
response={'indexName':ticker,'last':data1.get('regularMarketPrice'),'pcChange':pcChange}

print(response)