# 📊 RS Rating Module - Hướng Dẫn Sử Dụng

## 🎯 Giới thiệu
Module **RS Rating (IBD Style)** tính toán sức mạnh tương đối của cổ phiếu so với thị trường chung theo phương pháp của William O'Neil (Investor's Business Daily).

---

## 🚀 Cách Sử Dụng

### Bước 1: Thêm vào Indicator hiện tại
Copy toàn bộ nội dung file [`rs_rating_module.pine`](file:///Users/vinhh/Documents/tradeIndicators/rs_rating_module.pine) và paste vào **cuối file** indicator hiện tại của bạn (sau tất cả code đã có).

### Bước 2: Tùy chỉnh Settings (TradingView)
Trong TradingView Settings, bạn sẽ thấy section mới **"📊 RS Rating (IBD)"**:

| Setting | Mô tả | Giá trị mặc định |
|---------|-------|------------------|
| **Hiện RS Rating** | Bật/tắt hiển thị | ✅ ON |
| **Benchmark Index** | Mã chỉ số so sánh | `VN:VNINDEX` |
| **Vị trí Dashboard** | Góc hiển thị bảng | Bottom Left |

**Lưu ý Benchmark:**
- Việt Nam: `VN:VNINDEX`, `VN:VN30`
- Mỹ: `SP:SPX` (S&P 500), `NASDAQ:NDX`
- Crypto: `BITSTAMP:BTCUSD`

---

## 📐 Công Thức RS Rating (IBD Method)

### 1. Tính Hiệu Suất (Performance)
Tính % thay đổi giá trong 4 khoảng thời gian:

```
Perf_3m  = (Giá hiện tại - Giá 63 phiên trước) / Giá 63 phiên trước × 100%
Perf_6m  = (Giá hiện tại - Giá 126 phiên trước) / Giá 126 phiên trước × 100%
Perf_9m  = (Giá hiện tại - Giá 189 phiên trước) / Giá 189 phiên trước × 100%
Perf_12m = (Giá hiện tại - Giá 252 phiên trước) / Giá 252 phiên trước × 100%
```

### 2. Tính Weighted Score
Áp dụng trọng số IBD:

```
Stock Score = (Perf_3m × 40%) + (Perf_6m × 20%) + (Perf_9m × 20%) + (Perf_12m × 20%)
Market Score = (Benchmark_3m × 40%) + (Benchmark_6m × 20%) + ...
```

### 3. Tính RS Rating (1-99)
```
RS Diff = Stock Score - Market Score
RS Rating = 50 + (RS Diff × 0.8)
```

- **50** = Ngang bằng thị trường
- **> 50** = Outperform (mạnh hơn thị trường)
- **< 50** = Underperform (yếu hơn thị trường)

Cuối cùng, giới hạn kết quả trong khoảng **1-99**.

---

## 🎨 Ý Nghĩa Màu Sắc

| RS Rating | Màu sắc | Ý nghĩa | Hành động |
|-----------|---------|---------|-----------|
| **91-99** | 🟣 Tím (#9C27B0) | **SIÊU MẠNH 🔥** | Cổ phiếu dẫn đầu thị trường, tiềm năng cao |
| **80-90** | 🟢 Xanh lá | **LEADER 💪** | Cổ phiếu mạnh, đáng chú ý |
| **60-79** | 🟠 Cam | **TRUNG BÌNH ⚠️** | Không nổi bật, quan sát |
| **1-59** | 🔴 Đỏ | **YẾU 📉** | Kém hơn thị trường, tránh |

---

## 📊 Dashboard Hiển Thị

Bảng mini sẽ hiển thị tại góc màn hình (tùy chỉnh được):

```
┌─────────────┬──────────────────┐
│ RS RATING   │ 85               │
│             │ LEADER 💪        │
└─────────────┴──────────────────┘
```

**Vị trí có thể chọn:**
- Top Left (Góc trên trái)
- Top Right (Góc trên phải)
- **Bottom Left** (Góc dưới trái - mặc định)
- Bottom Right (Góc dưới phải)

---

## 🔧 Tùy Chỉnh Nâng Cao

### 1. Vẽ đường RS Line (Optional)
Nếu muốn xem biểu đồ RS Rating theo thời gian, uncomment dòng 121:

```pine
plot(rs_rating, "RS Rating", color=color.new(color.purple, 0), linewidth=2)
```

### 2. Điều chỉnh Scale Factor
Nếu muốn RS Rating nhạy hơn/chậm hơn, sửa dòng 76:

```pine
// Nhạy hơn: 0.8 → 1.0
// Chậm hơn: 0.8 → 0.5
rs_raw = 50 + (rs_diff * 0.8)
```

### 3. Thay đổi Trọng Số
Nếu muốn ưu tiên hiệu suất ngắn hạn, sửa dòng 58-61:

```pine
// Ví dụ: Tăng trọng số 3 tháng lên 60%
weight_3m = 0.60
weight_6m = 0.15
weight_9m = 0.15
weight_12m = 0.10
```

---

## ✅ Ví Dụ Thực Tế

**Scenario 1: VNM (Vinamilk)**
- 3 tháng: +15%
- 6 tháng: +10%
- 9 tháng: +8%
- 12 tháng: +12%
- **VNINDEX**:
  - 3 tháng: +5%
  - 6 tháng: +3%
  - 9 tháng: +2%
  - 12 tháng: +4%

**Tính toán:**
```
Stock Score = (15 × 0.4) + (10 × 0.2) + (8 × 0.2) + (12 × 0.2) = 12%
Market Score = (5 × 0.4) + (3 × 0.2) + (2 × 0.2) + (4 × 0.2) = 3.8%
RS Diff = 12 - 3.8 = 8.2%
RS Rating = 50 + (8.2 × 0.8) = 56.56 ≈ 57
```

**Kết quả:** RS = **57** → Màu 🟠 Cam (Trung Bình)

---

**Scenario 2: HPG (Hòa Phát)**
- 3 tháng: +45%
- 6 tháng: +50%
- 9 tháng: +40%
- 12 tháng: +55%
- **VNINDEX**: Giữ nguyên như trên

**Tính toán:**
```
Stock Score = (45 × 0.4) + (50 × 0.2) + (40 × 0.2) + (55 × 0.2) = 47%
RS Diff = 47 - 3.8 = 43.2%
RS Rating = 50 + (43.2 × 0.8) = 84.56 ≈ 85
```

**Kết quả:** RS = **85** → Màu 🟢 Xanh lá (LEADER)

---

## 🎓 Cách Dùng RS Rating (IBD Strategy)

### Quy tắc William O'Neil:
1. **Chỉ mua cổ phiếu có RS ≥ 80** - Đây là các Leader dẫn dắt thị trường
2. **Tránh RS < 70** - Cổ phiếu yếu, ít tiềm năng tăng trưởng
3. **Kết hợp với các yếu tố khác:**
   - EPS Growth (tăng trưởng lợi nhuận)
   - Institutional Sponsorship (tổ chức nắm giữ)
   - Cup & Handle pattern (mô hình giá)

### Chiến lược CANSLIM:
- **C** = Current Quarterly Earnings
- **A** = Annual Earnings Growth
- **N** = New Product/Service
- **S** = Supply & Demand
- **L** = Leader (RS > 80) ← **Module này**
- **I** = Institutional Sponsorship
- **M** = Market Direction

---

## 🐛 Xử Lý Lỗi

**Lỗi:** Dashboard không hiển thị
- **Nguyên nhân:** Cổ phiếu mới IPO, chưa đủ 252 phiên
- **Giải pháp:** RS Rating sẽ hiển thị 0 nếu không đủ dữ liệu. Module tự động xử lý bằng check `bar_index >= lookback`

**Lỗi:** RS Rating luôn = 50
- **Nguyên nhân:** Benchmark symbol sai hoặc không có dữ liệu
- **Giải pháp:** Kiểm tra lại symbol benchmark (ví dụ: `VN:VNINDEX` cho HOSE)

---

## 📚 Tài Liệu Tham Khảo

- **Sách:** "How to Make Money in Stocks" - William J. O'Neil
- **IBD RS Rating:** https://www.investors.com/ibd-university/find-evaluate-stocks/exclusive-ratings/
- **CANSLIM Strategy:** https://www.investopedia.com/terms/c/canslim.asp

---

## ⚡ Performance Note

Module này chạy **hoàn toàn độc lập**, không ảnh hưởng đến logic indicator hiện tại. Nếu muốn tắt, chỉ cần uncheck **"Hiện RS Rating"** trong settings.

**Tài nguyên sử dụng:**
- 1 `request.security()` call (lấy benchmark data)
- 8 tính toán performance (4 stock + 4 benchmark)
- 1 mini table (2 cells)

Hoàn toàn nhẹ và không gây lag! 🚀
