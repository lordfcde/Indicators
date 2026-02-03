from vnstock import Vnstock

def test_market_cap():
    symbol = "HPG" 
    try:
        stock = Vnstock().stock(symbol=symbol, source='VCI')
        
        # 'finance' is a component
        print("Finance methods:", dir(stock.finance))
        
        # Try ratio if available
        if 'ratio' in dir(stock.finance):
            # Arguments might be distinct
            df = stock.finance.ratio(period='quarterly', lang='vi')
            print("\nColumns:", df.columns)
            # Look for values in the first row
            # Usually 'market_cap' or 'von hoa'
            print(df.iloc[0])
            
            # Check unit
            if 'market_cap' in df.columns:
                 val = df['market_cap'].iloc[0]
                 print(f"Market Cap: {val} (Check unit)")
                 
        # Also try valuation
        if 'valuation' in dir(stock.finance):
             print("\nValuation:")
             # print(stock.finance.valuation(period='quarterly'))
             
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_market_cap()
