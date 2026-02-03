import time
from vnstock import Listing, Vnstock
import pandas as pd
from datetime import datetime, timedelta

def test_liquidity_filter():
    print("--- Getting All Symbols ---")
    l = Listing(source='VCI')
    df_sym = l.all_symbols()
    all_symbols = df_sym['symbol'].tolist()
    print(f"Total: {len(all_symbols)}")
    
    # Test batch of 10
    test_batch = all_symbols[:10]
    print(f"Testing batch: {test_batch}")
    
    start = time.time()
    qualified = []
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d') # ~3 months

    for sym in test_batch:
        try:
            stock = Vnstock().stock(symbol=sym, source='VCI')
            df = stock.quote.history(start=start_date, end=end_date, interval='1D')
            
            if len(df) < 20: continue
            
            vol = df['volume']
            ma20 = vol.tail(20).mean()
            ma60 = vol.tail(60).mean() # Approximate 3 months
            
            # User Criteria:
            # MA20 > 100,000
            # MA60 > 50,000
            
            print(f"{sym}: MA20={ma20:,.0f}, MA60={ma60:,.0f}")
            
            if ma20 > 100000 and ma60 > 50000:
                qualified.append(sym)
                
        except Exception as e:
            print(f"Error {sym}: {e}")
            
    elapsed = time.time() - start
    print(f"Time for 10 stocks: {elapsed:.2f}s")
    print(f"Estimated time for 1700: {(elapsed/10)*1700/60:.1f} minutes")
    print(f"Qualified: {qualified}")

if __name__ == "__main__":
    test_liquidity_filter()


