# Giới thiệu Python và Cài đặt

## 1. Python là gì?

Python là một ngôn ngữ lập trình bậc cao, thông dịch, đa năng và dễ học. Nó được tạo ra bởi Guido van Rossum và phát hành lần đầu vào năm 1991. Python nổi tiếng với cú pháp rõ ràng, dễ đọc và khả năng mở rộng mạnh mẽ, phù hợp cho nhiều lĩnh vực từ phát triển web, phân tích dữ liệu, trí tuệ nhân tạo đến tự động hóa.

### Các đặc điểm nổi bật của Python:
- **Dễ học và dễ sử dụng:** Cú pháp đơn giản, gần gũi với ngôn ngữ tự nhiên.
- **Đa nền tảng:** Chạy được trên Windows, macOS, Linux và nhiều hệ điều hành khác.
- **Mã nguồn mở và miễn phí:** Cộng đồng lớn mạnh, nhiều thư viện và framework hỗ trợ.
- **Đa năng:** Hỗ trợ nhiều mô hình lập trình (hướng đối tượng, hướng thủ tục, hướng chức năng).
- **Thư viện phong phú:** Có hàng ngàn thư viện và framework giúp giải quyết hầu hết các vấn đề lập trình.

## 2. Cài đặt Python

Để bắt đầu lập trình Python, bạn cần cài đặt trình thông dịch Python trên máy tính của mình.

### 2.1. Tải xuống Python

Truy cập trang web chính thức của Python: [python.org](https://www.python.org/downloads/)

Chọn phiên bản Python mới nhất (khuyến nghị phiên bản 3.x) phù hợp với hệ điều hành của bạn.

### 2.2. Hướng dẫn cài đặt trên Windows

1.  **Chạy trình cài đặt:** Sau khi tải xuống, nhấp đúp vào file `.exe` để chạy trình cài đặt.
2.  **Chọn tùy chọn:**
    -   **RẤT QUAN TRỌNG:** Đảm bảo bạn chọn tùy chọn "Add Python X.Y to PATH" (trong đó X.Y là phiên bản Python của bạn) ở cuối cửa sổ cài đặt. Điều này sẽ giúp bạn chạy Python từ bất kỳ thư mục nào trong Command Prompt hoặc PowerShell.
    -   Chọn "Install Now" để cài đặt với các tùy chọn mặc định hoặc "Customize installation" nếu bạn muốn tùy chỉnh.
3.  **Hoàn tất cài đặt:** Chờ quá trình cài đặt hoàn tất.

### 2.3. Hướng dẫn cài đặt trên macOS

1.  **Tải xuống:** Tải file `.pkg` từ trang web Python.
2.  **Chạy trình cài đặt:** Nhấp đúp vào file `.pkg` và làm theo hướng dẫn trên màn hình.
3.  **Kiểm tra cài đặt:** macOS thường đi kèm với Python 2.x. Để đảm bảo bạn đang sử dụng Python 3.x, hãy mở Terminal và gõ:
    ```bash
    python3 --version
    ```

### 2.4. Hướng dẫn cài đặt trên Linux

Hầu hết các bản phân phối Linux đều đã cài đặt sẵn Python. Bạn có thể kiểm tra phiên bản bằng cách mở Terminal và gõ:
```bash
python3 --version
```
Nếu bạn cần cài đặt hoặc cập nhật, bạn có thể sử dụng trình quản lý gói của hệ thống:
-   **Debian/Ubuntu:**
    ```bash
    sudo apt update
    sudo apt install python3 python3-pip
    ```
-   **Fedora/CentOS:**
    ```bash
    sudo dnf install python3 python3-pip
    ```

## 3. Kiểm tra cài đặt

Sau khi cài đặt, bạn có thể kiểm tra xem Python đã được cài đặt thành công hay chưa bằng cách mở Command Prompt (Windows) hoặc Terminal (macOS/Linux) và gõ:

```bash
python --version
```
hoặc
```bash
python3 --version
```

Bạn cũng có thể mở trình thông dịch Python bằng cách gõ `python` hoặc `python3` và thử một lệnh đơn giản:

```python
print("Hello, Python!")
```
Nếu bạn thấy "Hello, Python!" được in ra, nghĩa là Python đã sẵn sàng để sử dụng.

## 4. Môi trường ảo (Virtual Environment)

Khi làm việc với các dự án Python, việc sử dụng môi trường ảo là một thực hành tốt. Môi trường ảo giúp cô lập các gói thư viện của từng dự án, tránh xung đột phiên bản giữa các dự án khác nhau.

### 4.1. Tạo môi trường ảo

Mở terminal tại thư mục dự án của bạn và chạy lệnh:
```bash
python -m venv venv
```
Lệnh này sẽ tạo một thư mục `venv` chứa môi trường ảo.

### 4.2. Kích hoạt môi trường ảo

-   **Trên Windows (Command Prompt):**
    ```bash
    venv\Scripts\activate.bat
    ```
-   **Trên Windows (PowerShell):**
    ```bash
    .\venv\Scripts\Activate.ps1
    ```
-   **Trên macOS/Linux:**
    ```bash
    source venv/bin/activate
    ```

Sau khi kích hoạt, bạn sẽ thấy tên môi trường ảo (thường là `(venv)`) xuất hiện ở đầu dòng lệnh.

### 4.3. Hủy kích hoạt môi trường ảo

Để thoát khỏi môi trường ảo, chỉ cần gõ:
```bash
deactivate
```

## 5. Trình soạn thảo mã (Code Editor)

Mặc dù bạn có thể viết mã Python bằng bất kỳ trình soạn thảo văn bản nào, nhưng việc sử dụng một trình soạn thảo mã chuyên dụng sẽ giúp tăng năng suất với các tính năng như tô sáng cú pháp, tự động hoàn thành, gỡ lỗi, v.v.

Một số trình soạn thảo mã phổ biến cho Python:
-   **VS Code:** Miễn phí, mạnh mẽ, nhiều tiện ích mở rộng.
-   **PyCharm:** IDE chuyên nghiệp cho Python (có phiên bản Community miễn phí).
-   **Sublime Text:** Nhanh, nhẹ, tùy biến cao.
-   **Jupyter Notebook:** Tuyệt vời cho phân tích dữ liệu và học máy.

Bạn nên cài đặt một trong số chúng để có trải nghiệm lập trình tốt nhất.
