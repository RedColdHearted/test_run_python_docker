def is_palindrome(s):
    s = ''.join(filter(str.isalnum, s)).lower()  # Удаляем пробелы и приводим к нижнему регистру
    return s == s[::-1]

# Пример
print(is_palindrome("A man, a plan, a canal: Panama"))  # Вывод: True