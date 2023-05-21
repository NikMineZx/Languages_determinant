def correct_word(word, word_list):
    word_letters = list(word)  # Разделение слова на буквы

    for db_word in word_list:
        db_letters = db_word # Разделение слова из базы данных на буквы
        print(db_letters, word_letters)
        print(len(db_letters), len(word_letters))
        if len(db_letters) != len(word_letters):
            continue

        matched = True
        for letter in word_letters:
            if letter not in db_letters:
                matched = False
                break

        if matched:
            return db_word

    return None

def correct_text(text, word_list):
    # Разбиваем текст на слова
    words = text.split()

    # Исправляем каждое слово
    corrected_words = [correct_word(word, word_list) or word for word in words]

    # Собираем исправленный текст
    corrected_text = " ".join(corrected_words)

    return corrected_text

# Пример использования
word_list = ["home", "apple", "banana", "car"]
text = "This is an hmeo"
corrected_text = correct_text(text, word_list)
print(corrected_text)