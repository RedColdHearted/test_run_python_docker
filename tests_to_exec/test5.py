def rabin_karp(text, pattern):
    d = 256
    q = 101  # Простое число

    n = len(text)
    m = len(pattern)

    h = 1
    for _ in range(m-1):
        h = (h * d) % q

    p = 0  # Хеш для шаблона
    t = 0  # Хеш для текста

    for i in range(m):
        p = (d * p + ord(pattern[i])) % q
        t = (d * t + ord(text[i])) % q

    for i in range(n - m + 1):
        if p == t:
            if text[i:i+m] == pattern:
                return i  # Подстрока найдена

        if i < n - m:
            t = (d * (t - ord(text[i]) * h) + ord(text[i + m])) % q
            t = (t + q) % q

    return -1  # Подстрока не найдена

# Пример
print(rabin_karp("hello world", "world"))  # Вывод: 6