# Xử lý ngoại lệ và File I/O trong Python

## 1. Xử lý ngoại lệ (Exception Handling)

Ngoại lệ là các lỗi xảy ra trong quá trình thực thi chương trình, làm gián đoạn luồng hoạt động bình thường của chương trình. Python cung cấp cơ chế xử lý ngoại lệ để chương trình có thể phục hồi một cách duyên dáng hoặc thông báo lỗi một cách rõ ràng.

### 1.1. Khối `try-except`

Cấu trúc cơ bản để xử lý ngoại lệ là khối `try-except`:

```python
try:
    # Khối mã có thể gây ra ngoại lệ
    result = 10 / 0
except ZeroDivisionError:
    # Khối mã được thực thi nếu ngoại lệ ZeroDivisionError xảy ra
    print("Lỗi: Không thể chia cho 0!")
except TypeError:
    # Khối mã được thực thi nếu ngoại lệ TypeError xảy ra
    print("Lỗi: Kiểu dữ liệu không hợp lệ!")
except Exception as e:
    # Khối mã được thực thi cho bất kỳ ngoại lệ nào khác
    print(f"Một lỗi không xác định đã xảy ra: {e}")
else:
    # Khối mã được thực thi nếu không có ngoại lệ nào xảy ra trong khối try
    print("Phép tính thành công!")
finally:
    # Khối mã luôn được thực thi, dù có ngoại lệ hay không
    print("Kết thúc khối try-except.")
```

-   **`try`:** Chứa mã có thể gây ra ngoại lệ.
-   **`except`:** Bắt và xử lý các ngoại lệ cụ thể. Bạn có thể có nhiều khối `except` để xử lý các loại ngoại lệ khác nhau. `Exception as e` bắt tất cả các ngoại lệ và gán đối tượng ngoại lệ cho biến `e`.
-   **`else`:** (Tùy chọn) Mã trong khối này sẽ được thực thi nếu khối `try` hoàn thành mà không có bất kỳ ngoại lệ nào.
-   **`finally`:** (Tùy chọn) Mã trong khối này luôn được thực thi, bất kể có ngoại lệ xảy ra hay không. Thường dùng để dọn dẹp tài nguyên (đóng file, kết nối database).

### 1.2. `raise` Ngoại lệ

Bạn có thể tự tạo và ném (raise) một ngoại lệ bằng từ khóa `raise`.

```python
def validate_age(age):
    if not isinstance(age, int):
        raise TypeError("Tuổi phải là số nguyên.")
    if age < 0 or age > 120:
        raise ValueError("Tuổi phải nằm trong khoảng 0 đến 120.")
    print(f"Tuổi hợp lệ: {age}")

try:
    validate_age(30)
    validate_age(-5)
except (TypeError, ValueError) as e:
    print(f"Lỗi xác thực: {e}")
```

## 2. File I/O (Input/Output)

Python cung cấp các hàm tích hợp sẵn để làm việc với file, cho phép bạn đọc và ghi dữ liệu vào file trên hệ thống.

### 2.1. Mở và đóng File

Để làm việc với file, bạn cần mở nó bằng hàm `open()`. Hàm này trả về một đối tượng file.

```python
# Mở file để đọc (read mode - 'r')
file = open("my_file.txt", "r")
# ... làm việc với file ...
file.close() # Luôn đóng file sau khi sử dụng
```

Các chế độ mở file phổ biến:
-   `'r'` (read): Mở file để đọc (mặc định). File phải tồn tại.
-   `'w'` (write): Mở file để ghi. Nếu file tồn tại, nội dung sẽ bị xóa. Nếu không, file mới sẽ được tạo.
-   `'a'` (append): Mở file để ghi. Dữ liệu mới sẽ được thêm vào cuối file. Nếu không, file mới sẽ được tạo.
-   `'x'` (create): Tạo file mới. Nếu file đã tồn tại, sẽ gây lỗi `FileExistsError`.
-   `'t'` (text): Chế độ văn bản (mặc định).
-   `'b'` (binary): Chế độ nhị phân.

### 2.2. Đọc File

```python
# Giả sử có file my_file.txt với nội dung:
# Dòng 1
# Dòng 2
# Dòng 3

try:
    with open("my_file.txt", "r") as file:
        content = file.read() # Đọc toàn bộ nội dung
        print("Nội dung file:")
        print(content)

    with open("my_file.txt", "r") as file:
        first_line = file.readline() # Đọc một dòng
        print("Dòng đầu tiên:", first_line.strip()) # .strip() để loại bỏ ký tự xuống dòng

    with open("my_file.txt", "r") as file:
        lines = file.readlines() # Đọc tất cả các dòng vào một list
        print("Tất cả các dòng:", [line.strip() for line in lines])

    with open("my_file.txt", "r") as file:
        print("Đọc từng dòng qua vòng lặp:")
        for line in file:
            print(line.strip())

except FileNotFoundError:
    print("Lỗi: File không tồn tại.")
```

### 2.3. Ghi File

```python
try:
    with open("new_file.txt", "w") as file:
        file.write("Đây là dòng đầu tiên.\n")
        file.write("Đây là dòng thứ hai.")
    print("Đã ghi vào new_file.txt")

    with open("new_file.txt", "a") as file:
        file.write("\nĐây là dòng được thêm vào.")
    print("Đã thêm vào new_file.txt")

except IOError as e:
    print(f"Lỗi I/O khi ghi file: {e}")
```

### 2.4. Sử dụng `with` statement

Việc sử dụng `with open(...) as file:` là cách được khuyến nghị để làm việc với file. Nó đảm bảo rằng file sẽ tự động được đóng ngay cả khi có lỗi xảy ra, giúp tránh rò rỉ tài nguyên.

```python
# Ví dụ với with statement
with open("another_file.txt", "w") as f:
    f.write("Nội dung được ghi bằng with statement.")
# File f tự động đóng khi thoát khỏi khối with
```

Việc nắm vững xử lý ngoại lệ và File I/O là rất quan trọng để xây dựng các ứng dụng Python mạnh mẽ và đáng tin cậy, có khả năng tương tác với dữ liệu bên ngoài và xử lý các tình huống không mong muốn.