def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n+1):
        a, b = b, a + b
    return b

# Пример
print(fibonacci(10))  # Вывод: 55
print(eval("5+5"))