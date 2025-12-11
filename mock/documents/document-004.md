# Lập trình hướng đối tượng trong Python

## 1. Giới thiệu về Lập trình hướng đối tượng (OOP)

Lập trình hướng đối tượng (Object-Oriented Programming - OOP) là một mô hình lập trình dựa trên khái niệm "đối tượng", có thể chứa dữ liệu (thuộc tính) và mã (phương thức). OOP giúp tổ chức mã nguồn một cách rõ ràng, dễ bảo trì và tái sử dụng.

### Các nguyên tắc cơ bản của OOP:
-   **Đóng gói (Encapsulation):** Gói dữ liệu và các phương thức xử lý dữ liệu vào một đơn vị duy nhất (đối tượng), che giấu chi tiết triển khai bên trong.
-   **Kế thừa (Inheritance):** Cho phép một lớp (lớp con) kế thừa các thuộc tính và phương thức từ một lớp khác (lớp cha), giúp tái sử dụng mã.
-   **Đa hình (Polymorphism):** Cho phép các đối tượng thuộc các lớp khác nhau phản ứng khác nhau với cùng một thông điệp hoặc phương thức.
-   **Trừu tượng (Abstraction):** Tập trung vào những gì đối tượng làm thay vì cách nó làm, che giấu các chi tiết phức tạp không cần thiết.

## 2. Class và Object

### 2.1. Class (Lớp)

Class là một bản thiết kế (blueprint) hoặc khuôn mẫu để tạo ra các đối tượng. Nó định nghĩa các thuộc tính (variables) và phương thức (functions) mà các đối tượng được tạo từ lớp đó sẽ có.

Để định nghĩa một class, sử dụng từ khóa `class`:

```python
class Dog:
    # Thuộc tính lớp (class attribute)
    species = "Canis familiaris"

    def __init__(self, name, age):
        # Thuộc tính đối tượng (instance attributes)
        self.name = name
        self.age = age

    def bark(self):
        return f"{self.name} nói Gâu Gâu!"

    def description(self):
        return f"{self.name} là một chú chó {self.age} tuổi."
```

-   `__init__` là một phương thức khởi tạo (constructor). Nó được gọi tự động khi một đối tượng mới được tạo từ class. `self` là tham chiếu đến đối tượng hiện tại.
-   `self` là tham số đầu tiên của mọi phương thức trong class, đại diện cho instance của class đó.

### 2.2. Object (Đối tượng)

Object là một thể hiện (instance) cụ thể của một class. Khi bạn tạo một đối tượng từ một class, bạn đang tạo ra một thực thể cụ thể dựa trên bản thiết kế của class đó.

```python
# Tạo các đối tượng từ class Dog
my_dog = Dog("Buddy", 3)
your_dog = Dog("Lucy", 5)

# Truy cập thuộc tính của đối tượng
print(my_dog.name)    # Output: Buddy
print(your_dog.age)     # Output: 5
print(my_dog.species) # Output: Canis familiaris

# Gọi phương thức của đối tượng
print(my_dog.bark())      # Output: Buddy nói Gâu Gâu!
print(your_dog.description()) # Output: Lucy là một chú chó 5 tuổi.
```

## 3. Kế thừa (Inheritance)

Kế thừa cho phép một class (lớp con - child class) kế thừa các thuộc tính và phương thức từ một class khác (lớp cha - parent class). Điều này giúp tái sử dụng mã và tạo ra một hệ thống phân cấp các lớp.

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        raise NotImplementedError("Lớp con phải triển khai phương thức này")

class Cat(Animal):
    def __init__(self, name, breed):
        super().__init__(name) # Gọi constructor của lớp cha
        self.breed = breed

    def speak(self):
        return f"{self.name} nói Meo Meo!"

    def get_breed(self):
        return f"{self.name} là một con mèo giống {self.breed}."

# Tạo đối tượng từ lớp con
my_cat = Cat("Whiskers", "Siamese")
print(my_cat.name)      # Output: Whiskers
print(my_cat.speak())     # Output: Whiskers nói Meo Meo!
print(my_cat.get_breed()) # Output: Whiskers là một con mèo giống Siamese.
```

-   `super().__init__(name)`: Gọi phương thức `__init__` của lớp cha để khởi tạo các thuộc tính của lớp cha.

## 4. Đa hình (Polymorphism)

Đa hình cho phép các đối tượng thuộc các lớp khác nhau phản ứng khác nhau với cùng một phương thức. Điều này thường được thể hiện thông qua kế thừa và ghi đè phương thức.

```python
class Duck:
    def speak(self):
        return "Quạc Quạc"

class Dog:
    def speak(self):
        return "Gâu Gâu"

class Cat:
    def speak(self):
        return "Meo Meo"

def make_sound(animal):
    print(animal.speak())

duck = Duck()
dog = Dog()
cat = Cat()

make_sound(duck) # Output: Quạc Quạc
make_sound(dog)  # Output: Gâu Gâu
make_sound(cat)  # Output: Meo Meo
```

Trong ví dụ trên, hàm `make_sound` có thể chấp nhận bất kỳ đối tượng nào có phương thức `speak()` và nó sẽ gọi phương thức `speak()` tương ứng của đối tượng đó.

## 5. Đóng gói (Encapsulation)

Đóng gói là việc giới hạn quyền truy cập trực tiếp vào các thuộc tính và phương thức của đối tượng, thay vào đó cung cấp các phương thức công khai để tương tác với chúng. Trong Python, không có từ khóa `private` hay `protected` rõ ràng như các ngôn ngữ khác, nhưng có các quy ước:

-   **Thuộc tính công khai (Public):** Có thể truy cập trực tiếp từ bên ngoài class.
    ```python
    class MyClass:
        def __init__(self):
            self.public_var = "Tôi là công khai"
    ```
-   **Thuộc tính được bảo vệ (Protected):** Bắt đầu bằng một dấu gạch dưới (`_`). Quy ước cho biết thuộc tính này chỉ nên được truy cập trong class và các lớp con.
    ```python
    class MyClass:
        def __init__ (self):
            self._protected_var = "Tôi được bảo vệ"
    ```
-   **Thuộc tính riêng tư (Private):** Bắt đầu bằng hai dấu gạch dưới (`__`). Python sẽ đổi tên thuộc tính này (name mangling) để làm cho việc truy cập từ bên ngoài class khó khăn hơn, nhưng không hoàn toàn ngăn chặn.
    ```python
    class MyClass:
        def __init__(self):
            self.__private_var = "Tôi là riêng tư"

    obj = MyClass()
    # print(obj.__private_var) # Sẽ gây lỗi AttributeError
    print(obj._MyClass__private_var) # Có thể truy cập nhưng không khuyến khích
    ```

### Getters và Setters

Để kiểm soát việc truy cập và sửa đổi thuộc tính, bạn có thể sử dụng các phương thức getter và setter, hoặc sử dụng decorator `@property`.

```python
class Person:
    def __init__(self, name, age):
        self._name = name # Quy ước protected
        self._age = age

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        if isinstance(new_name, str) and len(new_name) > 0:
            self._name = new_name
        else:
            print("Tên không hợp lệ!")

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, new_age):
        if isinstance(new_age, int) and 0 < new_age < 150:
            self._age = new_age
        else:
            print("Tuổi không hợp lệ!")

p = Person("John", 30)
print(p.name) # Output: John
p.name = "Jane"
print(p.name) # Output: Jane
p.name = ""    # Output: Tên không hợp lệ!
print(p.age)  # Output: 30
p.age = 35
print(p.age)  # Output: 35
p.age = 200 # Output: Tuổi không hợp lệ!
```

Lập trình hướng đối tượng là một kỹ thuật mạnh mẽ giúp xây dựng các ứng dụng Python phức tạp một cách có tổ chức và hiệu quả.