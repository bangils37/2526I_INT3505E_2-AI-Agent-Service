# Hàm và Module trong Python

## 1. Hàm (Functions)

Hàm là một khối mã được tổ chức, có thể tái sử dụng, thực hiện một tác vụ cụ thể. Hàm giúp chia nhỏ chương trình thành các phần nhỏ hơn, dễ quản lý hơn, và tránh lặp lại mã.

### 1.1. Định nghĩa hàm

Trong Python, hàm được định nghĩa bằng từ khóa `def`, theo sau là tên hàm, dấu ngoặc đơn `()` chứa các tham số (nếu có), và dấu hai chấm `:`. Khối mã của hàm được thụt lề.

```python
def greet(name):
    """Hàm này dùng để chào hỏi một người."""
    print(f"Xin chào, {name}!")

# Gọi hàm
greet("Alice")
```

### 1.2. Tham số và đối số

-   **Tham số (Parameters):** Là các biến được liệt kê bên trong dấu ngoặc đơn trong định nghĩa hàm.
-   **Đối số (Arguments):** Là các giá trị được truyền vào hàm khi gọi hàm.

#### 1.2.1. Tham số bắt buộc

Các tham số phải được truyền vào khi gọi hàm.

```python
def add(a, b):
    return a + b

result = add(5, 3)
print(f"Tổng là: {result}") # Output: Tổng là: 8
```

#### 1.2.2. Tham số mặc định

Bạn có thể gán giá trị mặc định cho tham số. Nếu đối số không được truyền vào, giá trị mặc định sẽ được sử dụng.

```python
def say_hello(name="Guest"):
    print(f"Hello, {name}!")

say_hello()        # Output: Hello, Guest!
say_hello("Bob")   # Output: Hello, Bob!
```

#### 1.2.3. Tham số từ khóa (Keyword Arguments)

Bạn có thể truyền đối số bằng cách chỉ định tên tham số, giúp mã dễ đọc hơn và không cần quan tâm đến thứ tự.

```python
def describe_person(name, age):
    print(f"Tên: {name}, Tuổi: {age}")

describe_person(age=25, name="Charlie") # Output: Tên: Charlie, Tuổi: 25
```

#### 1.2.4. Tham số tùy biến (`*args` và `**kwargs`)

-   `*args`: Cho phép hàm chấp nhận một số lượng đối số không xác định dưới dạng tuple.
-   `**kwargs`: Cho phép hàm chấp nhận một số lượng đối số từ khóa không xác định dưới dạng dictionary.

```python
def calculate_sum(*numbers):
    total = 0
    for num in numbers:
        total += num
    return total

print(calculate_sum(1, 2, 3))       # Output: 6
print(calculate_sum(10, 20, 30, 40)) # Output: 100

def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="David", age=40, city="London")
# Output:
# name: David
# age: 40
# city: London
```

### 1.3. Giá trị trả về (Return Value)

Hàm có thể trả về một giá trị bằng từ khóa `return`. Nếu không có `return` hoặc `return` không có giá trị, hàm sẽ trả về `None`.

```python
def multiply(x, y):
    return x * y

product = multiply(4, 6)
print(f"Tích là: {product}") # Output: Tích là: 24
```

## 2. Module (Mô-đun)

Module là một file Python (`.py`) chứa các định nghĩa và câu lệnh Python. Module giúp tổ chức mã nguồn thành các đơn vị logic, dễ quản lý và tái sử dụng.

### 2.1. Tạo một Module

Giả sử bạn có một file `my_module.py` với nội dung sau:

```python
# my_module.py
def hello(name):
    return f"Hello from my_module, {name}!"

PI = 3.14159
```

### 2.2. Import Module

Để sử dụng các hàm và biến từ một module khác, bạn cần `import` nó.

#### 2.2.1. Import toàn bộ Module

```python
# main.py
import my_module

print(my_module.hello("Eve")) # Output: Hello from my_module, Eve!
print(my_module.PI)          # Output: 3.14159
```

#### 2.2.2. Import các thành phần cụ thể

Bạn có thể import trực tiếp các hàm hoặc biến cụ thể từ module.

```python
# main.py
from my_module import hello, PI

print(hello("Frank")) # Output: Hello from my_module, Frank!
print(PI)            # Output: 3.14159
```

#### 2.2.3. Đổi tên khi Import

Bạn có thể đổi tên module hoặc các thành phần khi import để tránh xung đột tên hoặc để mã ngắn gọn hơn.

```python
# main.py
import my_module as mm
from my_module import hello as greet_func

print(mm.hello("Grace"))    # Output: Hello from my_module, Grace!
print(greet_func("Heidi")) # Output: Hello from my_module, Heidi!
```

### 2.3. Package (Gói)

Package là một cách để tổ chức các module liên quan thành một cấu trúc thư mục. Một package là một thư mục chứa file `__init__.py` (có thể trống) và các module hoặc sub-package khác.

Cấu trúc ví dụ:

```
my_package/
├── __init__.py
├── module_a.py
└── sub_package/
    ├── __init__.py
    └── module_b.py
```

Để import từ package:

```python
# main.py
from my_package import module_a
from my_package.sub_package import module_b

# Giả sử module_a có hàm func_a và module_b có hàm func_b
# module_a.func_a()
# module_b.func_b()
```

Việc sử dụng hàm và module là nền tảng để xây dựng các ứng dụng Python lớn và có cấu trúc tốt. Chúng giúp tăng khả năng tái sử dụng mã, dễ bảo trì và làm việc nhóm hiệu quả hơn.