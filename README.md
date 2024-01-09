# Project I - Resources Allocation

## Mô tả
Repository gồm:
- Thư mục `datasets`: chứa các bộ dữ liệu benchmark Taillard và Demirkol, cùng với file `Data.xlsx` chứa dữ liệu để lập lịch cho bài toán biến thể của Job Shop Scheduling
- Thư mục `jobshop`: chứa source code của bài toán Job Shop Scheduling cổ điển
- Thư mục `jobshop_v2`: chứa mô tả bài toán biến thể của Job Shop Scheduling, cùng với source code giải quyết bài toán này
- Thư mục `notebooks`: chứa các notebook demo
- Thư mục `results`: chứa kết quả chạy thử nghiệm

## Cài đặt
Clone repository, sau đó chạy lệnh sau để cài đặt các thư viện cần thiết:
```
pip install -r requirements.txt
```

## Cách dùng
### 1. Job Shop Scheduling cổ điển
Vào thư mục `notebooks`:

- `jssp-cp_sat.ipynb`: Demo giải bài toán bằng phương pháp **Lập trình ràng buộc (Constraint Programming)**
- `jssp-mip.ipynb`: Demo giải bài toán bằng phương pháp **Quy hoạch nguyên (Mixed Integer Programming)**

Thư mục `results` chứa kết quả chạy thử nghiệm trước đó của các phương pháp trên trên các bộ dữ liệu benchmark Taillard và Demirkol.
### 2. Job Shop Scheduling biến thể
Truy cập vào thư mục `jobshop_v2`:
- Phát biểu bài toán: `problem.pdf`
- Mở notebook `app.ipynb` để xem chi tiết hướng dẫn sử dụng