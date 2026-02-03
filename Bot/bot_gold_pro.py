from datetime import datetime
import threading
from telebot.types import BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from vnstock import Vnstock
import telebot
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import time
import json
import os
import logging

# Cấu hình Logging (Ghi log vào file để lọc/xem xét sau)
logging.basicConfig(
    filename='bot_activity.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ==========================================
# 1. CẤU HÌNH (User tự điền)
# ==========================================
API_TOKEN = "8288173761:AAEhh0Km0LVNZIel15flHEGGh3ixY-4v0Nw"
CHAT_ID = '1622117094'
DATA_FILE = 'bot_data.json'
VNSTOCK_API_KEY = "vnstock_66748eedeae48faaf4692adfbc3082dd" # API VIP

# Apply Config
try:
    import vnstock
    if 'change_api_key' in dir(vnstock):
        print(f"🔑 Applying VNStock API Key...")
        vnstock.change_api_key(VNSTOCK_API_KEY)
except Exception as e:
    print(f"⚠️ Could not set VNStock API Key: {e}")

# Khởi tạo Bot
bot = telebot.TeleBot(API_TOKEN)

# Symbol & Cài đặt
SYMBOL = 'GC=F'  # Vàng (Gold Futures)
INTERVAL = '15m'
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# Lưu trạng thái tín hiệu gần nhất để tránh spam
last_signal = None  # 'BUY', 'SELL', hoặc None

# ==========================================
# 2. DATA PERSISTENCE & HELPER FUNCTIONS
# ==========================================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"daily": [], "history": [], "last_clear": ""}
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"daily": [], "history": [], "last_clear": ""}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def format_volume(vol):
    """Rút gọn số Volume (VD: 1,200,000 -> 1.2M)"""
    if vol >= 1_000_000:
        return f"{vol/1_000_000:.2f}M"
    elif vol >= 1_000:
        return f"{vol/1_000:.2f}K"
    return str(int(vol))

def get_main_menu():
    """Tạo Menu nát phím bấm (Inline Keyboard)"""
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("💰 Check Vàng", callback_data="check_gold"),
        InlineKeyboardButton("🚀 List Breakout", callback_data="check_breakout"),
        InlineKeyboardButton("📅 Lịch sử 7 ngày", callback_data="check_history"),
        InlineKeyboardButton("🇻🇳 Check VN Stocks", callback_data="check_vn30_guide"),
        InlineKeyboardButton("ℹ️ Hướng dẫn", callback_data="help")
    )
    return markup

# ==========================================
# 3. LOGIC TÍNH TOÁN & FORMAT TIN NHẮN
# ==========================================
def format_message(signal_type, price, prev_price, vol, prev_vol):
    """
    Tạo tin nhắn theo format chuyên nghiệp
    """
    # 1. Tính TP / SL
    if signal_type == 'MUA':
        tp = price * (1 + 0.005)
        sl = price * (1 - 0.003)
    else:  # BÁN
        tp = price * (1 - 0.005)
        sl = price * (1 + 0.003)
    
    # 2. Tính % Thay đổi
    pct_price_change = ((price - prev_price) / prev_price) * 100
    if prev_vol == 0: pct_vol_change = 0.0
    else: pct_vol_change = ((vol - prev_vol) / prev_vol) * 100
        
    # 3. Format thời gian
    current_time = datetime.now().strftime("%d/%m/%Y")
    
    # 4. Xây dựng nội dung tin nhắn
    message = (
        f"#GOLD | {current_time} |\n"
        f"| RSI Signal | Type: {signal_type} | Price: {price:.1f} |\n"
        f"| TP: {tp:.1f} | SL: {sl:.1f} |\n"
        f"| % Price change: {pct_price_change:+.2f}% | % Vol change: {pct_vol_change:+.2f}% |"
    )
    return message

def fetch_and_analyze():
    global last_signal
    try:
        df = yf.download(tickers=SYMBOL, period='5d', interval=INTERVAL, progress=False)
        if df.empty or len(df) < RSI_PERIOD + 2:
            print("⏳ Dữ liệu chưa đủ hoặc lỗi tải...")
            return

        try:
            close = df['Close']
            volume = df['Volume']
            if isinstance(close, pd.DataFrame): close = close.iloc[:, 0]
            if isinstance(volume, pd.DataFrame): volume = volume.iloc[:, 0]
        except Exception as e:
            print(f"Lỗi truy cập dữ liệu: {e}")
            return

        rsi = ta.rsi(close, length=RSI_PERIOD)
        current_rsi = rsi.iloc[-2]
        current_price = close.iloc[-2]
        prev_price = close.iloc[-3]
        current_vol = volume.iloc[-2]
        prev_vol = volume.iloc[-3]
        timestamp = df.index[-2]
        
        print(f"⏰ {timestamp} | Price: {current_price:.2f} | RSI: {current_rsi:.2f}")

        # Logic Tín hiệu
        signal_type = None
        if current_rsi < RSI_OVERSOLD: signal_type = 'MUA'
        elif current_rsi > RSI_OVERBOUGHT: signal_type = 'BÁN'
            
        if signal_type and signal_type != last_signal:
            print(f"🚀 PHÁT HIỆN TÍN HIỆU: {signal_type}")
            
            # Log tín hiệu Vàng
            logging.info(f"GOLD_SIGNAL: {signal_type} | Price: {current_price} | RSI: {current_rsi}")
            
            msg = format_message(signal_type, current_price, prev_price, current_vol, prev_vol)
            try:
                bot.send_message(CHAT_ID, msg)
                print("✅ Đã gửi tin nhắn Telegram thành công!")
                last_signal = signal_type
            except Exception as e:
                print(f"❌ Lỗi gửi Telegram: {e}")
                
        if 35 < current_rsi < 65:
            last_signal = None
            
    except Exception as e:
        print(f"❌ Lỗi phân tích: {e}")

# ==========================================
# 4. COMMAND HANDLERS & MENU
# ==========================================
@bot.message_handler(commands=['start', 'help', 'menu'])
def send_welcome(message):
    welcome_msg = (
        "🤖 **GOLD BOT PRO CONTROL** 🤖\n\n"
        "Chọn chức năng bên dưới hoặc gõ lệnh:\n"
        "• `/pricegold` : Check Vàng\n"
        "• `/vnstock <mã>` : Check CP Việt (VD: /vnstock FPT)\n"
    )
    bot.reply_to(message, welcome_msg, parse_mode='Markdown', reply_markup=get_main_menu())

# NEW DATA COMMANDS
@bot.message_handler(commands=['breakout', 'list'])
def check_breakout_list(message):
    data = load_data()
    daily = data.get('daily', [])
    
    if not daily:
        bot.reply_to(message, "📭 Danh sách Breakout hôm nay đang trống.", parse_mode='Markdown')
        return
        
    msg = "🚀 **DANH SÁCH BREAKOUT HÔM NAY** 🚀\n--------------------------\n"
    for item in daily:
        msg += f"• **{item['symbol']}** (Vol +{item['vol_pct']:.1f}%) - {item['time']}\n"
        
    bot.reply_to(message, msg, parse_mode='Markdown')

@bot.message_handler(commands=['history'])
def check_history_list(message):
    data = load_data()
    history = data.get('history', [])
    
    if not history:
        bot.reply_to(message, "📭 Lịch sử 7 ngày đang trống.", parse_mode='Markdown')
        return
        
    msg = "📅 **LỊCH SỬ ĐỘT BIẾN (7 NGÀY)**\n--------------------------\n"
    # Group theo ngày
    history_by_date = {}
    for item in history:
        d = item['date']
        if d not in history_by_date: history_by_date[d] = []
        if item['symbol'] not in history_by_date[d]:
            history_by_date[d].append(item['symbol'])
            
    for d, symbols in history_by_date.items():
        # Sắp xếp symbols A-Z
        symbols.sort()
        msg += f"🗓 `{d}`: {', '.join(symbols)}\n"
        
    bot.reply_to(message, msg, parse_mode='Markdown')

# Xử lý khi bấm nút trên Menu
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "check_gold":
        do_check_gold(call.message)
    elif call.data == "check_breakout":
        check_breakout_list(call.message)
    elif call.data == "check_history":
        check_history_list(call.message)
    elif call.data == "check_vn30_guide":
        bot.answer_callback_query(call.id, "💡 Gõ: /vnstock <mã> để xem chi tiết!")
        bot.send_message(call.message.chat.id, "🇻🇳 **HƯỚNG DẪN VNSTOCK**\n\n- Gõ `/vnstock FPT` để xem FPT\n- Bot tự động quét Vol đột biến các mã HOT hàng ngày.")
    elif call.data == "help":
        bot.answer_callback_query(call.id, "Đang mở hướng dẫn...")
        send_welcome(call.message)

def do_check_gold(message):
    try:
        msg_wait = bot.reply_to(message, "⏳ Đang lấy dữ liệu Vàng...")
        df = yf.download(tickers=SYMBOL, period='5d', interval=INTERVAL, progress=False)
        
        if df.empty:
            bot.edit_message_text("❌ Lỗi dữ liệu.", chat_id=message.chat.id, message_id=msg_wait.message_id)
            return

        try:
            close = df['Close']
            if isinstance(close, pd.DataFrame): close = close.iloc[:, 0]
        except: return

        rsi = ta.rsi(close, length=RSI_PERIOD)
        current_price = close.iloc[-1]
        current_rsi = rsi.iloc[-1]
        
        rsi_status = "Trung tính 😐"
        if current_rsi > 70: rsi_status = "QUÁ MUA 🔴"
        elif current_rsi < 30: rsi_status = "QUÁ BÁN 🟢"
        
        reply_msg = (
            f"💰 **GOLD UPDATE** 💰\n"
            f"Price: `{current_price:.2f}` | RSI: `{current_rsi:.2f}`\n"
            f"Status: {rsi_status}\n"
            f"Time: `{datetime.now().strftime('%H:%M %d/%m')}`"
        )
        
        bot.delete_message(chat_id=message.chat.id, message_id=msg_wait.message_id)
        bot.send_message(message.chat.id, reply_msg, parse_mode='Markdown')
        
    except Exception as e:
        print(f"Lỗi Gold: {e}")

@bot.message_handler(commands=['pricegold', 'gold', 'price'])
def check_price_command(message):
    do_check_gold(message)

# ==========================================
# 5. VNSTOCK COMMAND
# ==========================================
@bot.message_handler(commands=['vnstock', 'vni'])
def check_vnstock(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Vui lòng nhập mã cổ phiếu. Ví dụ: `/vnstock FPT`", parse_mode='Markdown')
            return
        
        symbol = parts[1].upper()
        msg_wait = bot.reply_to(message, f"⏳ Đang lấy dữ liệu **{symbol}**...")
        
        from datetime import timedelta
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')

        try:
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            df = stock.quote.history(start=start_date, end=end_date, interval='1D')
            
            if df.empty:
                bot.edit_message_text(f"❌ Không tìm thấy mã **{symbol}**.", chat_id=message.chat.id, message_id=msg_wait.message_id)
                return
                
            rsi = ta.rsi(df['close'], length=RSI_PERIOD)
            current_price = df['close'].iloc[-1] * 1000 
            current_rsi = rsi.iloc[-1]
            
            raw_close = df['close'].iloc[-1]
            raw_prev = df['close'].iloc[-2]
            pct_change = ((raw_close - raw_prev) / raw_prev) * 100
            
            rsi_status = "Trung tính 😐"
            if current_rsi > 70: rsi_status = "QUÁ MUA 🔴"
            elif current_rsi < 30: rsi_status = "QUÁ BÁN 🟢"

            reply_msg = (
                f"🇻🇳 **{symbol} UPDATE** 🇻🇳\n"
                f"Price: `{raw_close:.2f}K` ({pct_change:+.2f}%)\n"
                f"RSI (14 Daily): `{current_rsi:.2f}`\n"
                f"Status: {rsi_status}\n"
                f"Time: `{datetime.now().strftime('%H:%M:%S %d/%m/%Y')}`"
            )
            
            bot.delete_message(chat_id=message.chat.id, message_id=msg_wait.message_id)
            bot.reply_to(message, reply_msg, parse_mode='Markdown')
            
        except Exception as e:
            bot.edit_message_text(f"❌ Lỗi: {e}", chat_id=message.chat.id, message_id=msg_wait.message_id)
            
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi hệ thống: {e}")

# ==========================================
# 6. SCANNER THREAD (New format + Persistence)
# ==========================================

def get_market_symbols():
    try:
        from vnstock import Listing
        l = Listing(source='VCI')
        df = l.all_symbols()
        return df['symbol'].tolist()
    except:
        return []

def scan_liquidity():
    """Scan toàn bộ thị trường để lọc mã thanh khoản cao (Chạy 1 lần đầu ngày)"""
    print("🔄 Đang quét thanh khoản toàn thị trường (có thể mất 15 phút)...")
    symbols = get_market_symbols()
    qualified = []
    
    from datetime import timedelta
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d') # 3 tháng
    
    count = 0
    total = len(symbols)
    
    for sym in symbols:
        try:
            # Lấy data
            stock = Vnstock().stock(symbol=sym, source='VCI')
            df = stock.quote.history(start=start_date, end=end_date, interval='1D')
            
            if len(df) < 60: continue # Ít nhất 3 tháng dữ liệu
            
            vol = df['volume']
            ma20 = vol.tail(20).mean()
            ma60 = vol.tail(60).mean()
            
            # Điều kiện thanh khoản:
            # 1. TB 20 phiên > 100k
            # 2. TB 3 tháng > 50k
            if ma20 > 100000 and ma60 > 50000:
                qualified.append(sym)
                
        except: pass
        
        count += 1
        if count % 100 == 0: print(f"   -> Đã quét {count}/{total} mã...")
        
    print(f"✅ Quét xong! Tìm thấy {len(qualified)} mã đủ thanh khoản.")
    return qualified

def check_volume_breakout(symbol):
    try:
        from datetime import timedelta
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d')
        
        stock = Vnstock().stock(symbol=symbol, source='VCI')
        df = stock.quote.history(start=start_date, end=end_date, interval='1D')
        
        if df.empty or len(df) < 6: return None

        vol = df['volume']
        current_vol = vol.iloc[-1]
        avg_vol_5 = vol.iloc[-6:-1].mean()
        
        if avg_vol_5 < 100000: return None
        if current_vol > (avg_vol_5 * 1.2):
            # Lấy thông tin giá
            price_close = df['close'].iloc[-1]
            price_prev = df['close'].iloc[-2]
            pct_change = ((price_close - price_prev) / price_prev) * 100
            
            return {
                "symbol": symbol,
                "current_vol": current_vol,
                "avg_vol_5": avg_vol_5,
                "ratio": (current_vol / avg_vol_5),
                "price": price_close,
                "pct_change": pct_change
            }
        return None
    except: return None

def run_vnstock_scanner():
    print("⏰ VNStock Scanner Thread Started...")
    alerted_stocks = {} 
    
    # Load watchlist từ file nếu có
    data = load_data()
    watchlist = data.get('liquid_watchlist', [])
    
    # Nếu chưa có watchlist (lần đầu chạy), quét ngay
    if not watchlist:
        watchlist = scan_liquidity()
        data['liquid_watchlist'] = watchlist
        save_data(data)
    else:
        print(f"✅ Đã load {len(watchlist)} mã từ cache.")
    
    while True:
        try:
            now = datetime.now()
            current_hour = now.hour
            today_str = now.strftime('%Y-%m-%d')
            time_str = now.strftime('%H:%M:%S')

            # --- AUTO CLEAR & RESCAN LOGIC (8:50 AM, Mon-Fri) ---
            if now.weekday() < 5 and current_hour == 8 and now.minute >= 45: # Sớm hơn tí để quét kịp
                 data = load_data()
                 if data['last_clear'] != today_str:
                     print("🧹 Starting New Day & Re-scanning Liquidity...")
                     data['daily'] = [] 
                     data['last_clear'] = today_str
                     
                     # Rescan Liquidity
                     watchlist = scan_liquidity()
                     data['liquid_watchlist'] = watchlist
                     
                     # Clean history > 7 days
                     from datetime import timedelta
                     cutoff_date = (now - timedelta(days=7)).strftime('%Y-%m-%d')
                     data['history'] = [h for h in data['history'] if h['date'] > cutoff_date]
                     
                     save_data(data)
                     alerted_stocks = {} 

            # --- SCANNER LOGIC (9h - 15h) ---
            if 9 <= current_hour <= 15:
                # Loop through dynamic wathclist
                for symbol in watchlist:
                    if symbol in alerted_stocks and alerted_stocks[symbol] == today_str:
                        continue
                        
                    result = check_volume_breakout(symbol)
                    
                    if result:
                        print(f"📢 BREAKOUT: {symbol}")
                        
                        vol_str = format_volume(result['current_vol'])
                        ma5_str = format_volume(result['avg_vol_5'])
                        price_display = result['price'] * 1000
                        vol_increase_pct = (result['ratio'] - 1) * 100
                        
                        # Logging
                        logging.info(f"VNSTOCK_BREAKOUT: {symbol} | Vol: {result['current_vol']} | Incr: +{vol_increase_pct:.1f}%")
                        
                        # Save to JSON
                        data = load_data()
                        data['daily'].append({
                            "symbol": symbol,
                            "time": time_str,
                            "vol_pct": vol_increase_pct
                        })
                        
                        history_exists = any(h['symbol'] == symbol and h['date'] == today_str for h in data['history'])
                        if not history_exists:
                            data['history'].append({
                                "symbol": symbol,
                                "date": today_str
                            })
                            
                        save_data(data)

                        msg = (
                            f"🚨 VOL ĐỘT BIẾN | {time_str} |\n"
                            f"| 🔴 **{symbol}** 🔴 | Breakout | Vol đột biến: **+{vol_increase_pct:.1f}%** 🚀 |\n"
                            f"| Price: `{price_display:,.0f}` | Change: `{result['pct_change']:+.2f}%` |\n"
                            f"| Vol: {vol_str} | MA5: {ma5_str} |"
                        )
                        
                        try:
                            bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
                            alerted_stocks[symbol] = today_str
                        except Exception as e:
                            logging.error(f"Send Error: {e}")
                    time.sleep(1) # Faster check since we have many stocks
                time.sleep(120) # 2 mins check loop
            else:
                time.sleep(600)
        except Exception as e:
            print(f"Scanner Error: {e}")
            time.sleep(60)

# ==========================================
# 7. GOLD ALERT THREAD
# ==========================================
def run_alert_schedule():
    print("⏰ Alert Thread Started...")
    while True:
        try:
            fetch_and_analyze()
            time.sleep(60) 
        except Exception as e:
            print(f"⚠️ Alert Thread Error: {e}")
            time.sleep(10)

# ==========================================
# 8. MAIN RUN
# ==========================================
if __name__ == "__main__":
    print("🤖 Bot Gold Pro đang chạy... (Ctrl+C để dừng)")
    print(f"Theo dõi: {SYMBOL} | Khung: {INTERVAL} | RSI({RSI_PERIOD})")
    print("✅ Đã kích hoạt Menu Inline & Scanner v2 (Persistence)")

    try:
        commands = [
            BotCommand("menu", "🎛 Mở Menu điều khiển"),
            BotCommand("breakout", "🚀 Xem List Breakout hôm nay"),
            BotCommand("history", "📅 Xem Lịch sử 7 ngày"),
            BotCommand("pricegold", "💰 Xem giá Vàng"),
            BotCommand("vnstock", "🇻🇳 Check CP Việt"),
            BotCommand("start", "🚀 Khởi động")
        ]
        bot.set_my_commands(commands)
    except: pass

    # Chạy luồng quét tín hiệu Vàng
    t1 = threading.Thread(target=run_alert_schedule)
    t1.daemon = True
    t1.start()
    
    # Chạy luồng quét tín hiệu Chứng khoán VN
    t2 = threading.Thread(target=run_vnstock_scanner)
    t2.daemon = True
    t2.start()
    
    bot.infinity_polling()
