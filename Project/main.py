# Python version for the program to work: 3.9.13 and below.
# For the program to work, you need to connect the database that is in the repository.
#
#
#
#
# 
# 
#

import pytesseract
import mysql.connector
import re
import customtkinter as ctk

from PIL import Image
from tkinter import filedialog
from customtkinter import *
from tkinter import messagebox

config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'languages',
}

ctk.set_appearance_mode("black")
ctk.set_default_color_theme("blue")

class Research_image_Text(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, height=1250, corner_radius=0, width=450)
        self.grid(row=0, column=0, sticky="nsew", padx=(260, 20), pady=10)
        self.grid_rowconfigure(0, weight=1)
        self.button = ctk.CTkButton(self, text="Chose Image", command=self.start_procces)
        self.button.grid(row=1, column=1, ipadx=200, pady=10, padx=10)
        self.entry_text = ctk.CTkLabel(self, text= "", width=700, height=500)
        self.entry_text.grid(row=0, column=1, padx=20)
        self.results_frame = ctk.CTkScrollableFrame(self, width=180, height=500)
        self.results_frame.grid(row=0, column=2, sticky="nsew", pady=35)
        self.result_text = ctk.CTkLabel(self.results_frame, text="Results")
        self.result_text.grid(row=0, column=2)

    def start_procces(self):
        filepath = filedialog.askopenfilename()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tesseract_path = os.path.join(current_dir, "Tesseract-OCR", "tesseract.exe")
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        image = Image.open(filepath)
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        sql = "SELECT lang_full_name, lang_code FROM lang_list;"
        cursor.execute(sql)
        result = cursor.fetchone()
        i = 1
        while result:    
            lang_name = result[0]  # Получение названия языка
            lang_c = result[1]
            text = pytesseract.image_to_string(image, lang_c)
            research_text = Research_Text(text, lang_c)  # Создание экземпляра класса Research_Text
            score = research_text.count  # Получение значения атрибута count
            word_count = research_text.count_word
            lang_button = ctk.CTkLabel(self.results_frame, text=(f"{lang_name} = Score {round((score / word_count * 100), 2)}%"))
            lang_button.grid(row=i, column=2, ipadx=20, pady=2)
            i += 1
            result = cursor.fetchone()
        cnx.commit()
        messagebox.showinfo("Process", "The detection is completed, the percentage of the language detection is also displayed.")

class Research_Text():
    def __init__(self, text, lang_c):
        super().__init__()  # Вызов конструктора родительского класса
        try:
            self.count = 0  # Сохраняем значение в атрибуте экземпляра
            self.count_word = 0
            if text is None:
                messagebox.showinfo("No data", "Text field is empty")
            cnx_insert = mysql.connector.connect(**config)
            cursor_insert = cnx_insert.cursor()
            words = re.findall(r'\b\w+\b', text)
            for word in words:
                if not word.isdigit() and word.isalpha():
                    self.count_word += 1
                    sql = f"SELECT COUNT(*) FROM `{lang_c}` WHERE `word`=%s"
                    # sql = f"SELECT COUNT(*) FROM `eng` WHERE `word`=%s"
                    cursor_insert.execute(sql, (word,))
                    result_insert = cursor_insert.fetchone()
                    if result_insert[0] == 1 or result_insert[0] == 2 :
                        self.count += 1
            cursor_insert.close()
            cnx_insert.close()
        except:
            self.count = 0
            self.count_word = 0  # Установка значения по умолчанию в случае ошибки

def browse_image():
    filepath = filedialog.askopenfilename()
    text_from_image = Research_image_Text(filepath)

class TextDeterminant(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, height=1250, corner_radius=0, width=450)
        self.grid(row=0, column=0, sticky="nsew", padx=(260, 20), pady=10)
        self.grid_rowconfigure(0, weight=1)
        self.button = ctk.CTkButton(self, text="Start determination", command=self.start_process)
        self.button.grid(row=1, column=1, ipadx=200, pady=10, padx=10)
        self.entry_text = ctk.CTkTextbox(self, width=700, height=500)
        self.entry_text.grid(row=0, column=1, padx=20)
        self.results_frame = ctk.CTkScrollableFrame(self, width=180, height=500)
        self.results_frame.grid(row=0, column=2, sticky="nsew", pady=35)
        self.result_text = ctk.CTkLabel(self.results_frame, text="Results")
        self.result_text.grid(row=0, column=2)

    def start_process(self):
        i = 1
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        sql = "SELECT lang_full_name, lang_code FROM lang_list;"
        cursor.execute(sql)
        result = cursor.fetchone()
        text = self.entry_text.get("1.0", "end-1c")
        word_count = len(re.findall(r'\b\w+\b', text))
        while result:    
            lang_name = result[0]  # Получение названия языка
            lang_c = result[1]
            # Получить текст из поля ввода
            research_text = Research_Text(text, lang_c)  # Создание экземпляра класса Research_Text
            score = research_text.count  # Получение значения атрибута count
            word_count = research_text.count_word
            lang_button = ctk.CTkLabel(self.results_frame, text=(f"{lang_name} = Score {round((score / word_count * 100), 2)}%")) # 
            lang_button.grid(row=i, column=2, ipadx=20, pady=2)
            i += 1
            result = cursor.fetchone()
        cnx.commit()
        messagebox.showinfo("Process", "The detection is completed, the percentage of the language detection is also displayed.")

class Training(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, height=1250, corner_radius=0, width=450)
        lang = "Not selected"
        self.grid(row=0, column=0, sticky="nsew", padx=(260, 20), pady=10)
        self.grid_rowconfigure(0, weight=1)
        self.entry_text = ctk.CTkTextbox(self, width=700, height=500)
        self.entry_text.grid(row=0, column=1, padx=20)
        self.button = ctk.CTkButton(self, text=(f"Start Training language = {lang}"), state= "disabled", command= self.start_process)
        self.button.grid(row=1, column=1, ipadx=200, pady=10, padx=10)
        if lang != "Not selected":
            self.button.configure(state = "normal")
        self.results_frame = ctk.CTkScrollableFrame(self, width=180, height=500)
        self.results_frame.grid(row=0, column=2, sticky="nsew", pady=35)
        self.result_text = ctk.CTkLabel(self.results_frame, text="Languages")
        self.result_text.grid(row=0, column=2)
        lang = self.inseart_lng(self.result_text)

    def inseart_lng(self, results_frame):
        i = 1
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        sql = "SELECT lang_full_name, lang_code FROM lang_list;"
        cursor.execute(sql)
        result = cursor.fetchone()
        while result:
            lang_name = result[0]  # Получение названия языка
            lang_c = result[1]
            def button_callback(language=lang_name, lang_code = lang_c):
                self.update_lang(language, lang_code)  # Обновление переменной lang
            lang_button = ctk.CTkButton(results_frame, text=result[0], command=button_callback)
            lang_button.grid(row=i, column=0, ipadx=20, pady=2)
            i += 1
            result = cursor.fetchone()

    def update_lang(self, language, lang_c):
        global lang_code
        lang_code = lang_c
        lang = language  # Обновление переменной lang
        self.button.configure(text=f"Start Training language = {lang}")  # Обновление текста кнопки
        self.button.configure(state="normal")  # Включение кнопки

    def start_process(self):
        text = self.entry_text.get("1.0", "end-1c")
        learn_Text(text, lang_code)
        messagebox.showinfo("Process", "Training completed")

class learn_Text:
    def __init__(self, text, lang):
        try:
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()
            if text is None:
                messagebox.showinfo("No data", "Text field is empty")
            cnx_insert = mysql.connector.connect(**config)
            cursor_insert = cnx_insert.cursor()
                # Разделение строки на слова
            words = re.findall(r'\b\w+\b', text)
            unique_words = set()
            for word in words:
                # Проверка, является ли слово числом или символом
                if not word.isdigit() and word.isalpha():
                    sql = f"SELECT COUNT(*) FROM `{lang}`"" WHERE `word`=%s"
                    cursor.execute(sql, (word,))
                    result = cursor.fetchone()
                    # Добавление слова в базу данных, если его еще нет
                    if result[0] == 0 and word not in unique_words:
                        unique_words.add(word)
                        sql = f"INSERT INTO `{lang}` (`word`)"" VALUES (%s)"
                        cursor_insert.execute(sql, (word,))
                        cnx_insert.commit()  # Фиксация изменений в базе данных
        finally:
            cursor.close()
            cnx.close()
            cursor_insert.close()
            cnx_insert.close()

class Correction_Words:
    def __init__(self, text, lang_c):
        try:
            global corrected_text
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()
            sql = f"SELECT word FROM {lang_c};"
            cursor.execute(sql)
            results = cursor.fetchall()
            corrected_text = self.correct_text(text, results)
            print(corrected_text)
        except Exception as e:  # Обработка ошибки
            print("Error:", str(e))

    def sort_word(self, word):
        return ''.join(sorted(word))

    def correct_word(self, word, word_list):
        word_letters = [char for char in word if char.isalpha()]  # Разделение слова на буквы
        sorted_word_letters = self.sort_word(word_letters)
        for db_word_tuple in word_list:

            db_word = db_word_tuple[0]  # Извлечение слова из кортежа
            db_letters = [char for char in db_word]  # Разделение слова из базы данных на буквы
            sorted_db_letters = self.sort_word(db_letters)
            if len(db_letters) != len(word_letters):
                continue
            if sorted_db_letters == sorted_word_letters:
                return db_word
        return word

    def correct_text(self, text, word_list):
        # Разбиваем текст на слова
        words = text.split()
        # Исправляем каждое слово
        corrected_words = [self.correct_word(word, word_list) or word for word in words]
        # Собираем исправленный текст
        corrected_text = " ".join(corrected_words)
        return corrected_text
    
class Text_Correction(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, height=1250, corner_radius=0, width=450)
        lang = "Not selected"
        self.grid(row=0, column=0, sticky="nsew", padx=(260, 20), pady=10)
        self.grid_rowconfigure(0, weight=1)
        self.entry_text = ctk.CTkTextbox(self, width=700, height=250)
        self.entry_text.grid(row=0, column=1, padx=20, pady = 20)
        self.correction_text = ctk.CTkTextbox(self, width=700, height=250)
        self.correction_text.grid(row=1, column=1, padx=20, )
        self.button = ctk.CTkButton(self, text=(f"Start Correction language = {lang}"), state= "disabled", command=self.start_process)
        self.button.grid(row=2, column=1, ipadx=200, pady=10, padx=10)
        if lang != "Not selected":
            self.button.configure(state = "normal")
        self.button_frame = ctk.CTkScrollableFrame(self, width=180, height=500)
        self.button_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", pady=35)
        self.result_text = ctk.CTkLabel(self.button_frame, text="Languages")
        self.result_text.grid(row=0, column=2)
        lang = self.inseart_lng(self.result_text)

    def inseart_lng(self, results_frame):
        i = 1
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        sql = "SELECT lang_full_name, lang_code FROM lang_list;"
        cursor.execute(sql)
        result = cursor.fetchone()
        while result:
            lang_name = result[0]  # Получение названия языка
            lang_c = result[1]
            def button_callback(language=lang_name, lang_code = lang_c):
                self.update_lang(language, lang_code)  # Обновление переменной lang
            lang_button = ctk.CTkButton(results_frame, text=result[0], command=button_callback)
            lang_button.grid(row=i, column=0, ipadx=20, pady=2)
            i += 1
            result = cursor.fetchone()
            
    def update_lang(self, language, lang_c):
        global lang_code
        lang_code = lang_c
        lang = language  # Обновление переменной lang
        self.button.configure(text=f"Start Correction language = {lang}")  # Обновление текста кнопки
        self.button.configure(state="normal")  # Включение кнопки
        
    def start_process(self):
        self.correction_text.delete("1.0", "end")
        text = self.entry_text.get("1.0", "end-1c")
        Correction_Words(text, lang_code)
        self.correction_text.insert("1.0", corrected_text)
        messagebox.showinfo("Process", "Correction completed")
        
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Language determinant")
        self.geometry("1250x640")
        self.resizable(0, 0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.menu_frame = ctk.CTkFrame(self, height=1250, corner_radius=0)
        self.menu_frame.grid(row=0, column=0, sticky="nsw")
        self.menu_frame.grid_rowconfigure(4, weight=1)
        self.title_frame = ctk.CTkLabel(self.menu_frame, text="Language determinant", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_frame.grid(row=0, column=0, padx=10, pady=10)
        self.button_text_frame = ctk.CTkButton(self.menu_frame, text="Text determinant", command=self.show_text_frame)
        self.button_text_frame.grid(row=1, column=0, padx=10, pady=(10, 10))  # Добавлено pady=(10, 0) для отступа сверху
        self.button_image_frame = ctk.CTkButton(self.menu_frame, text="Image determinant", command=self.show_image_frame)
        self.button_image_frame.grid(row=2, column=0, padx=10, pady=(10, 10))  # Добавлено pady=(0, 10) для отступа снизу
        self.button_training_frame = ctk.CTkButton(self.menu_frame, text="Training", command=self.show_traing_frame)
        self.button_training_frame.grid(row=5, column=0, padx=10, pady=(10, 10))
        self.button_text_correction_frame = ctk.CTkButton(self.menu_frame, text="Text correction", command=self.show_text_correction_frame)
        self.button_text_correction_frame.grid(row=3, column=0, padx=10, pady=(10, 10))
        self.text_frame = None
        self.training_frame = None
        self.image_frame = None
        self.text_correction_frame = None
    def show_text_frame(self):
        if self.text_frame is not None:
            self.text_frame.destroy()
        self.text_frame = TextDeterminant(self)
    
    def show_traing_frame(self):
        if self.training_frame is not None:
            self.training_frame.destroy()
        self.training_frame = Training(self)

    def show_image_frame(self):
        if self.image_frame is not None:
            self.image_frame.destroy()
        self.image_frame = Research_image_Text(self)
    
    def show_text_correction_frame(self):
        if self.text_correction_frame is not None:
            self.text_correction_frame.destroy()
        self.text_correction_frame = Text_Correction(self)
        
if __name__ == "__main__":
    app = App()
    app.mainloop()