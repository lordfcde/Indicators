from vnstock import Vnstock
from datetime import datetime, timedelta

symbol = 'FPT'
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')

print(f"Fetching data for {symbol} from {start_date} to {end_date} using Vnstock class...")

try:
    # Initialize Vnstock
    stock = Vnstock().stock(symbol=symbol, source='VCI')
    
    # Fetch history
    df = stock.quote.history(start=start_date, end=end_date, interval='1D')
    
    if not df.empty:
        print("✅ Data fetched successfully!")
        print(df.tail())
        print("\nColumns:", df.columns.tolist())
    else:
        print("❌ No data returned.")
        
except Exception as e:
    print(f"❌ Error: {e}")
