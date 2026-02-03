from vnstock import Vnstock
import pandas as pd
from datetime import datetime, timedelta
import time

# 1. DANH SÁCH THEO DÕI (VN30 + Hot Stocks)
# List mẫu, sẽ bổ sung đầy đủ khi tích hợp vào bot
WATCHLIST = [
    "HPG", "SSI", "VND", "DIG", "CEO", "MWG", "FPT", "VCB", "STB", "NVL", "PDR",
    "VIC", "VHM", "TCB", "VPB", "MBB", "ACB", "MSN", "GAS", "VNM"
]

def check_volume_breakout(symbol):
    try:
        # Lấy dữ liệu 10 ngày gần nhất để tính MA5
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d')
        
        stock = Vnstock().stock(symbol=symbol, source='VCI')
        df = stock.quote.history(start=start_date, end=end_date, interval='1D')
        
        if df.empty or len(df) < 6:
            return None

        # Lấy Volume
        # df['volume'] confirm lại tên cột
        vol = df['volume']
        
        # Volume phiên hiện tại (nến cuối cùng)
        current_vol = vol.iloc[-1]
        
        # Volume 5 phiên TRƯỚC ĐÓ (không tính phiên hiện tại để so sánh đột biến vs trung bình quá khứ)
        # Ma_Vol_5 = Average(Vol[-6] -> Vol[-2])
        # Hoặc ý user là MA5 bao gồm cả phiên nay? 
        # Thường breakout là so với trung bình 5 phiên gần nhất (moving average).
        # Ta dùng 5 phiên trước đó (MA5 Previous) để chuẩn bài breakout.
        
        avg_vol_5 = vol.iloc[-6:-1].mean()
        
        # Điều kiện 1: Thanh khoản > 100k
        if avg_vol_5 < 100000:
            return None
            
        # Điều kiện 2: Đột biến > 20% ( > 1.2 lần)
        if current_vol > (avg_vol_5 * 1.2):
            return {
                "symbol": symbol,
                "current_vol": current_vol,
                "avg_vol_5": avg_vol_5,
                "upline": (current_vol / avg_vol_5)
            }
            
        return None

    except Exception as e:
        print(f"Lỗi {symbol}: {e}")
        return None

print(f"🔥 Bắt đầu quét {len(WATCHLIST)} mã...")
found_stocks = []

for symbol in WATCHLIST:
    print(f"Scanning {symbol}...", end="\r")
    result = check_volume_breakout(symbol)
    if result:
        found_stocks.append(result)
        print(f"✅ DETECTED: {symbol} (Vol: {result['current_vol']:,.0f} > MA5: {result['avg_vol_5']:,.0f})")

print("\n--- KẾT QUẢ QUÉT ---")
if found_stocks:
    for item in found_stocks:
        print(f"📢 {item['symbol']} - Vol đột biến {item['upline']:.2f} lần")
else:
    print("Không tìm thấy mã nào thỏa mãn.")
