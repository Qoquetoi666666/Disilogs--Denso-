# Digi-Logs

**Nhật ký số cho máy CNC.** Mỗi máy có một hồ sơ riêng gồm thông tin máy, lịch sử bảo trì và tài liệu. Chọn máy là thấy toàn bộ hồ sơ của máy đó.

- Phiên bản: `0.1.0`
- Chế độ: `LOCAL` (chạy trên máy cá nhân)
- Backend: FastAPI (cổng `8000`)
- Giao diện: Streamlit (cổng `8501`)

> Đây là bản demo. Dữ liệu và tài liệu trong repo là dữ liệu mẫu.

---

## Tính năng

- Chọn máy ở thanh bên (ví dụ `CNC-001`, `CNC-003`)
- Hồ sơ Digi-Log riêng cho từng máy
- Theo dõi bảo trì
- Quản lý tài liệu theo máy (upload, xem)
- Scan mã QR / nameplate để mở nhanh hồ sơ máy (có OCR)

---

## Yêu cầu

- Python 3.10 trở lên
- Git
- Linux hoặc macOS (khuyên dùng). Windows xem phần cuối.
- Tesseract OCR, chỉ cần nếu dùng tính năng đọc ảnh/nameplate:

```bash
# Ubuntu / Debian
sudo apt install tesseract-ocr
```

---

## Cài đặt

### 1. Tải code

Repo ở chế độ riêng tư, bạn cần được chủ repo mời và bấm **Accept** trong email GitHub trước.

```bash
git clone https://github.com/Qoquetoi666666/Disilogs--Denso-.git
cd Disilogs--Denso-
```

Khi Git hỏi mật khẩu, hãy dán **Personal Access Token** của chính bạn (không dùng mật khẩu GitHub).
Tạo token tại: *GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)*, tick quyền `repo`.

### 2. Tạo môi trường Python và cài thư viện

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Tạo dữ liệu demo

```bash
python -m scripts.seed_demo
```

Nếu lệnh trên báo lỗi, thử `python scripts/seed_demo.py`.

Các script tạo dữ liệu mẫu khác (không bắt buộc):

| Script | Tác dụng |
|---|---|
| `scripts/generate_qr_demo.py` | Tạo mã QR mẫu cho máy |
| `scripts/generate_nameplate_demo.py` | Tạo ảnh nameplate mẫu |
| `scripts/generate_demo_manual.py` | Tạo tài liệu hướng dẫn mẫu |
| `scripts/test_ocr.py` | Kiểm tra OCR có hoạt động không |

---

## Chạy hệ thống

Cần **2 Terminal riêng biệt**. Cả hai phải để chạy liên tục: không bấm `Ctrl+C`, không đóng cửa sổ.

**Terminal 1: Backend (FastAPI)**

```bash
cd Disilogs--Denso-
source .venv/bin/activate
uvicorn app.main:app --reload
```

Khi thấy hai dòng sau là thành công:

```
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

**Terminal 2: Giao diện (Streamlit)**

```bash
cd Disilogs--Denso-
source .venv/bin/activate
streamlit run ui/app.py
```

Trình duyệt sẽ tự mở. Nếu không, vào: **http://localhost:8501**

> Luôn bật **backend trước**, giao diện sau.

### Kiểm tra backend

Mở http://127.0.0.1:8000, bạn phải thấy:

```json
{
  "system": "Digi-Logs",
  "version": "0.1.0",
  "status": "online",
  "mode": "LOCAL"
}
```

Hoặc dùng lệnh:

```bash
curl http://127.0.0.1:8000/health
```

---

## Cách dùng nhanh

1. Mở http://localhost:8501
2. Ở thanh bên, chọn máy (ví dụ `CNC-001`)
3. Xem thông tin máy và lịch sử bảo trì
4. Vào mục **Tài liệu** để xem hoặc tải tài liệu của máy đang chọn
5. Dùng mục **Scan** để mở hồ sơ bằng mã QR hoặc ảnh nameplate
6. Đổi sang máy khác (ví dụ `CNC-003`) để thấy hồ sơ đổi theo

---

## Cấu trúc thư mục

```
.
├── app/                 # Backend FastAPI (API, router)
├── ui/                  # Giao diện Streamlit (app.py là file chính)
├── scripts/             # Script tạo dữ liệu demo, test OCR
├── data/samples/        # Dữ liệu mẫu (ví dụ mã QR)
├── uploads/documents/   # Tài liệu được tải lên
├── requirements.txt     # Danh sách thư viện Python
└── README.md
```

Các file `ui/app_before_*.py` và `ui/app_m3_stable.py` là bản sao lưu trong quá trình phát triển, bạn không cần dùng đến.

---

## Xử lý sự cố

| Triệu chứng | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|
| Giao diện báo đỏ, `Connection refused` ở `127.0.0.1:8000` | Backend đã tắt | Chạy lại Terminal 1, rồi nhấn `Ctrl+Shift+R` trên trình duyệt |
| `address already in use` khi chạy uvicorn/streamlit | Cổng 8000/8501 đang bị chiếm | Tắt tiến trình cũ, hoặc đổi cổng: `uvicorn app.main:app --port 8001` |
| `ModuleNotFoundError` | Chưa kích hoạt venv hoặc chưa cài thư viện | `source .venv/bin/activate` rồi `pip install -r requirements.txt` |
| Scan/OCR không đọc được | Thiếu Tesseract | `sudo apt install tesseract-ocr` |
| `Repository not found` khi clone | Chưa được mời hoặc chưa Accept, hoặc token thiếu quyền `repo` | Nhờ chủ repo mời lại, kiểm tra token |
| Danh sách máy trống | Chưa tạo dữ liệu demo | Chạy `python -m scripts.seed_demo` |

---
