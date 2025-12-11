# Cấu trúc dữ liệu cơ bản trong Python

## 1. Biến và Kiểu dữ liệu

Trong Python, biến được sử dụng để lưu trữ dữ liệu. Python là ngôn ngữ kiểu động, nghĩa là bạn không cần khai báo kiểu dữ liệu cho biến. Kiểu dữ liệu sẽ được xác định tự động dựa trên giá trị mà bạn gán cho biến.

### 1.1. Khai báo và gán giá trị

```python
# Khai báo biến số nguyên
age = 30

# Khai báo biến số thực
price = 19.99

# Khai báo biến chuỗi
name = "Alice"

# Khai báo biến boolean
is_student = True

print(f"Tên: {name}, Tuổi: {age}, Giá: {price}, Là sinh viên: {is_student}")
```

### 1.2. Các kiểu dữ liệu cơ bản

-   **Số (Numbers):** `int` (số nguyên), `float` (số thực), `complex` (số phức).
-   **Chuỗi (Strings):** `str` (chuỗi ký tự).
-   **Boolean:** `bool` (True/False).

## 2. Cấu trúc dữ liệu Collection

Python cung cấp một số cấu trúc dữ liệu tích hợp sẵn để lưu trữ các tập hợp dữ liệu.

### 2.1. List (Danh sách)

List là một tập hợp có thứ tự, có thể thay đổi (mutable) và cho phép các phần tử trùng lặp. List được định nghĩa bằng cách đặt các phần tử trong dấu ngoặc vuông `[]` và phân tách bằng dấu phẩy.

```python
# Tạo một list
my_list = [1, 2, 3, "apple", "banana", True]
print("List ban đầu:", my_list)

# Truy cập phần tử (indexing)
print("Phần tử đầu tiên:", my_list[0]) # Output: 1
print("Phần tử cuối cùng:", my_list[-1]) # Output: True

# Cắt list (slicing)
print("Cắt list (từ index 1 đến 3):", my_list[1:4]) # Output: [2, 3, 'apple']

# Thay đổi phần tử
my_list[0] = 100
print("List sau khi thay đổi phần tử đầu tiên:", my_list)

# Thêm phần tử
my_list.append("orange")
print("List sau khi thêm 'orange':", my_list)

# Xóa phần tử
my_list.remove("banana")
print("List sau khi xóa 'banana':", my_list)

# Độ dài của list
print("Độ dài của list:", len(my_list))
```

### 2.2. Tuple (Bộ)

Tuple là một tập hợp có thứ tự, không thể thay đổi (immutable) và cho phép các phần tử trùng lặp. Tuple được định nghĩa bằng cách đặt các phần tử trong dấu ngoặc đơn `()` và phân tách bằng dấu phẩy.

```python
# Tạo một tuple
my_tuple = (1, 2, 3, "apple", "banana", True)
print("Tuple ban đầu:", my_tuple)

# Truy cập phần tử
print("Phần tử thứ hai:", my_tuple[1]) # Output: 2

# Cắt tuple
print("Cắt tuple (từ index 0 đến 2):", my_tuple[0:3]) # Output: (1, 2, 3)

# Tuple không thể thay đổi
# my_tuple[0] = 100 # Sẽ gây lỗi TypeError

# Độ dài của tuple
print("Độ dài của tuple:", len(my_tuple))
```

### 2.3. Set (Tập hợp)

Set là một tập hợp không có thứ tự, không thể thay đổi (immutable) các phần tử của nó (nhưng set có thể thay đổi kích thước - mutable) và không cho phép các phần tử trùng lặp. Set được định nghĩa bằng cách đặt các phần tử trong dấu ngoặc nhọn `{}` hoặc sử dụng hàm `set()`.

```python
# Tạo một set
my_set = {1, 2, 3, "apple", "banana", 2}
print("Set ban đầu (phần tử trùng lặp bị loại bỏ):", my_set) # Output: {1, 2, 3, 'banana', 'apple'}

# Thêm phần tử
my_set.add("orange")
print("Set sau khi thêm 'orange':", my_set)

# Xóa phần tử
my_set.remove(1)
print("Set sau khi xóa 1:", my_set)

# Các phép toán trên set
set1 = {1, 2, 3}
set2 = {3, 4, 5}
print("Hợp của hai set:", set1.union(set2)) # Output: {1, 2, 3, 4, 5}
print("Giao của hai set:", set1.intersection(set2)) # Output: {3}
print("Hiệu của hai set:", set1.difference(set2)) # Output: {1, 2}
```

### 2.4. Dictionary (Từ điển)

Dictionary là một tập hợp không có thứ tự, có thể thay đổi (mutable) và lưu trữ dữ liệu dưới dạng cặp khóa-giá trị (key-value pairs). Khóa phải là duy nhất và không thể thay đổi (immutable), trong khi giá trị có thể là bất kỳ kiểu dữ liệu nào. Dictionary được định nghĩa bằng cách đặt các cặp khóa-giá trị trong dấu ngoặc nhọn `{}`.

```python
# Tạo một dictionary
my_dict = {"name": "Alice", "age": 30, "city": "New York"}
print("Dictionary ban đầu:", my_dict)

# Truy cập giá trị bằng khóa
print("Tên:", my_dict["name"]) # Output: Alice

# Thay đổi giá trị
my_dict["age"] = 31
print("Dictionary sau khi thay đổi tuổi:", my_dict)

# Thêm cặp khóa-giá trị mới
my_dict["email"] = "alice@example.com"
print("Dictionary sau khi thêm email:", my_dict)

# Xóa cặp khóa-giá trị
del my_dict["city"]
print("Dictionary sau khi xóa thành phố:", my_dict)

# Lấy tất cả các khóa
print("Các khóa:", my_dict.keys())

# Lấy tất cả các giá trị
print("Các giá trị:", my_dict.values())

# Lấy tất cả các cặp khóa-giá trị
print("Các cặp khóa-giá trị:", my_dict.items())
```

## 3. So sánh các cấu trúc dữ liệu

| Đặc điểm          | List           | Tuple          | Set            | Dictionary     |
| :---------------- | :------------- | :------------- | :------------- | :------------- |
| Có thứ tự         | Có             | Có             | Không          | Không          |
| Có thể thay đổi   | Có             | Không          | Có (kích thước)| Có             |
| Cho phép trùng lặp | Có             | Có             | Không          | Khóa không, giá trị có |
| Cú pháp           | `[]`           | `()`           | `{}` hoặc `set()` | `{key: value}` |

Việc lựa chọn cấu trúc dữ liệu phù hợp sẽ giúp bạn viết mã hiệu quả và dễ bảo trì hơn. Hãy cân nhắc các yêu cầu về thứ tự, khả năng thay đổi và tính duy nhất của dữ liệu khi lựa chọn.