# 🐋 Coder Stock - Trinity Master VSA

> Hệ thống chỉ báo "All-in-One" kết hợp **Money Flow Analysis** + **Wyckoff VSA** cho TradingView

---

## 📦 Files

| File | Loại | Mô tả |
|------|------|-------|
| `money_flow_trinity.pine` | Indicator | Phân tích + Hiển thị tín hiệu |
| `money_flow_trinity_strategy.pine` | Strategy | Backtest + Thống kê hiệu suất |
| `ultimate_ma_overlay.pine` | Indicator | EMA Overlay riêng |

---

## 🎯 Tính năng chính

### 1. Money Flow Analysis
- **CMF (Chaikin Money Flow)**: Dòng tiền trung hạn
- **Chaikin Oscillator**: Dòng tiền ngắn hạn
- **EOM (Ease of Movement)**: Độ thoáng của giá

### 2. Wyckoff VSA (Volume Spread Analysis)

#### Candle Coloring (Màu nến theo Volume)
| Màu | Ý nghĩa |
|-----|---------|
| 🟡 Vàng | **Tiền mạnh vào** - Volume Climax + Bullish + Close gần đỉnh |
| 🔵 Aqua | **Absorption** - Volume cao + Bearish nhưng có mua vào |
| 🟢 Teal | Volume cao + Bullish |
| 🔴 Maroon | Volume cao + Bearish |
| ⚫ Xám | **Volume cạn** - Dry volume |

#### Warning Icons
| Icon | Tên | Ý nghĩa |
|------|-----|---------|
| 🟡 ○ | Volume Climax | Volume > 2x trung bình - có thể đỉnh/đáy |
| ⚡ ◇ | Spring/Shakeout | Điểm đảo chiều tiềm năng |
| 💰 △ | Accumulation | Tích lũy - có mua vào trong nến đỏ |
| ⚠️ ▽ | Hidden Distribution | Phân phối ẩn - Volume cao nhưng không tăng |
| ❌ X | Upthrust | Đẩy lên giả - Breakout thất bại |

### 3. EMA System
- **EMA 50**: Lướt sóng (ngắn hạn)
- **EMA 144**: Trung hạn
- **EMA 233**: Dài hạn

Màu sắc thay đổi: 🟢 Xanh = Giá trên EMA | 🔴 Đỏ = Giá dưới EMA

---

## 📊 Tín hiệu Mua/Bán

### 💎 Tín hiệu MUA

| Nhãn | Màu | Điều kiện |
|------|-----|-----------|
| 💎 | Vàng | **Super Buy** - Wyckoff confirm + Tất cả indicator hội tụ |
| MÚC | Xanh | **Safe Buy** - CMF+ + EMA hỗ trợ + Chaikin cross up |
| SỚM | Cam | **Early Buy** - Spring/Shakeout/Accumulation detected |

### 🔴 Tín hiệu BÁN

| Nhãn | Màu | Điều kiện |
|------|-----|-----------|
| BÁN | Đỏ | CMF âm 3 phiên + Mất hỗ trợ EMA |
| THOÁT | Đỏ | Death Cross hoặc Hidden Distribution |

---

## ⚙️ Strategy Settings

| Tham số | Mặc định | Mô tả |
|---------|----------|-------|
| Stop Loss | 8% | Cắt lỗ cứng |
| Take Profit 1 | 15% | Chốt 50% vị thế |
| Trailing Stop | 5% | Cho 50% còn lại |
| Initial Capital | 100M VND | Vốn ban đầu |
| Commission | 0.15% | Phí giao dịch |

---

## 📈 Dashboard

### Indicator Dashboard
- Dòng tiền: VÀO MẠNH / VÀO NHẸ / RA NHẸ / RA MẠNH
- Volume: CLIMAX / CAO / CẠN / BÌNH THƯỜNG
- Wyckoff: SPRING / SHAKEOUT / TÍCH LŨY / PHÂN PHỐI
- Lướt sóng: OK / DƯỚI (so với EMA50)
- Trung hạn: UPTREND / DOWNTREND (so với EMA233)
- Cản trên: 0-3 EMA

### Strategy Dashboard
- Vị thế: ĐANG GIỮ / ---
- Win Rate: %
- Trades: Số lệnh đóng
- P&L: Lợi nhuận %
- PF: Profit Factor

---

## 🚀 Cách sử dụng

### Indicator
1. Mở TradingView → Pine Editor
2. Copy code từ `money_flow_trinity.pine`
3. Click "Add to Chart"
4. Indicator sẽ hiển thị histogram + overlay EMAs + tín hiệu

### Strategy
1. Copy code từ `money_flow_trinity_strategy.pine`
2. Add to Chart
3. Vào tab "Strategy Tester" để xem kết quả backtest

---

## 📚 Lý thuyết Wyckoff áp dụng

### Luật Nhân Quả (Cause & Effect)
- **Spring**: Giá chọc xuống support rồi đóng trên → Bullish
- **Shakeout**: Phá đáy cũ với volume thấp, đóng gần đỉnh → Rũ bỏ tay yếu
- **Upthrust**: Phá đỉnh rồi đóng thấp → Bearish trap

### Effort vs Result
- Volume cao + Spread hẹp → Cảnh báo (không đi được)
- Volume thấp + Spread rộng → Easy move (cạn cung/cầu)

---

## 👨‍💻 Author

**Vinh** - Coder Stock

---

## 📝 Changelog

### v2.0.0 (2026-01-31)
- ✅ Tích hợp Wyckoff VSA
- ✅ Candle coloring by volume
- ✅ Spring/Shakeout/Upthrust detection
- ✅ Hidden Distribution warning
- ✅ Strategy với 8% SL + Partial TP
- ✅ Dashboard cải tiến

### v1.0.0
- Initial release với CMF + Chaikin + EOM