# Python version for the program to work: 3.9.13 and below.
# For the program to work, you need to connect the database that is in the repository.
#

import pytesseract
import mysql.connector
import re
import customtkinter as ctk

from PIL import Image
from tkinter import filedialog
from customtkinter import *
from tkinter import messagebox

current_dir = os.path.dirname(os.path.abspath(__file__))
tesseract_path = os.path.join(current_dir, "DigiCertGlobalRootCA.crt.pem")
config = {
    'user': 'NikMine',
    'password': 'Misa21122017',
    'host': 'o4kodev.mysql.database.azure.com',
    'database': 'Languages',
    'port': '3306',
    'ssl_ca': f'{tesseract_path}',
    'ssl_disabled': False,
}


ctk.set_appearance_mode("black")
ctk.set_default_color_theme("blue")

class Research_image_Text(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, height=1250, corner_radius=0, width=450)
        self.grid(row=0, column=0, sticky="nsew", padx=(260, 20), pady=10)
        self.grid_rowconfigure(0, weight=1)

        # Button to choose an image
        self.button = ctk.CTkButton(self, text="Choose Image", command=self.start_procces)
        self.button.grid(row=1, column=1, ipadx=200, pady=10, padx=10)

        # Label to display the text
        self.entry_text = ctk.CTkLabel(self, text="", width=700, height=500)
        self.entry_text.grid(row=0, column=1, padx=20)

        # Frame to display the results
        self.results_frame = ctk.CTkScrollableFrame(self, width=180, height=500)
        self.results_frame.grid(row=0, column=2, sticky="nsew", pady=35)

        # Label for the results
        self.result_text = ctk.CTkLabel(self.results_frame, text="Results")
        self.result_text.grid(row=0, column=2)

    def start_procces(self):
        # Ask user to choose an image file
        filepath = filedialog.askopenfilename()

        # Set the path to the Tesseract OCR executable
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tesseract_path = os.path.join(current_dir, "Tesseract-OCR", "tesseract.exe")
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

        # Open the image
        image = Image.open(filepath)

        # Connect to the MySQL database
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # Execute SQL query to retrieve language names and codes
        sql = "SELECT lang_full_name, lang_code FROM lang_list;"
        cursor.execute(sql)
        result = cursor.fetchone()
        i = 1
        while result:
            lang_name = result[0]
            lang_c = result[1]

            # Perform text recognition using Tesseract OCR
            # text = pytesseract.image_to_string(image, lang_c)
            text = pytesseract.image_to_string(image, lang_c)
            # Perform research on the extracted text
            research_text = Research_Text(text, lang_c)
            score = research_text.count
            word_count = research_text.count_word

            # Display the language and detection score
            lang_button = ctk.CTkLabel(self.results_frame, text=(f"{lang_name} = Score {round((score / word_count * 100), 2)}%"))
            lang_button.grid(row=i, column=2, ipadx=20, pady=2)
            i += 1
            result = cursor.fetchone()

        cnx.commit()
        messagebox.showinfo("Process", "The detection is completed, the percentage of the language detection is also displayed.")


class Research_Text():
    def __init__(self, text, lang_c):
        super().__init__()
        try:
            self.count = 0 
            self.count_word = 0
            if text is None:
                messagebox.showinfo("No data", "Text field is empty")
            
            # Establish a connection to the database
            cnx_insert = mysql.connector.connect(**config)
            cursor_insert = cnx_insert.cursor()
            
            # Find all words in the text using regular expression
            words = re.findall(r'\b\w+\b', text)
            for word in words:
                if not word.isdigit() and word.isalpha():
                    self.count_word += 1
                    
                    # Check if the word exists in the database
                    sql = f"SELECT COUNT(*) FROM `{lang_c}` WHERE `word`=%s"
                    cursor_insert.execute(sql, (word,))
                    result_insert = cursor_insert.fetchone()
                    if result_insert[0] == 1 or result_insert[0] == 2:
                        self.count += 1
            
            cursor_insert.close()
            cnx_insert.close()
        except:
            self.count = 0
            self.count_word = 0

def browse_image():
    filepath = filedialog.askopenfilename()
    text_from_image = Research_image_Text(filepath)

class TextDeterminant(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, height=1250, corner_radius=0, width=450)
        self.grid(row=0, column=0, sticky="nsew", padx=(260, 20), pady=10)
        self.grid_rowconfigure(0, weight=1)
        
        # Start determination button
        self.button = ctk.CTkButton(self, text="Start determination", command=self.start_process)
        self.button.grid(row=1, column=1, ipadx=200, pady=10, padx=10)
        
        # Text entry
        self.entry_text = ctk.CTkTextbox(self, width=700, height=500)
        self.entry_text.grid(row=0, column=1, padx=20)
        
        # Results frame
        self.results_frame = ctk.CTkScrollableFrame(self, width=180, height=500)
        self.results_frame.grid(row=0, column=2, sticky="nsew", pady=35)
        
        # Result label
        self.result_text = ctk.CTkLabel(self.results_frame, text="Results")
        self.result_text.grid(row=0, column=2)

    def start_process(self):
        i = 1
        
        # Establish a connection to the database
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        
        # Fetch language names and codes from the database
        sql = "SELECT lang_full_name, lang_code FROM lang_list;"
        cursor.execute(sql)
        result = cursor.fetchone()
        
        # Get the text from the entry
        text = self.entry_text.get("1.0", "end-1c")
        word_count = len(re.findall(r'\b\w+\b', text))
        
        # Process each language
        while result:
            lang_name = result[0]
            lang_c = result[1]
            
            # Perform research on the text for the current language
            research_text = Research_Text(text, lang_c)
            score = research_text.count
            word_count = research_text.count_word
            final_score = round((score / word_count * 100), 2)
            
            # Perform learning if the final score is above 80
            if final_score > 80:
                learn_Text(text, lang_c)
            
            # Display the language and its score in the results frame
            lang_button = ctk.CTkLabel(self.results_frame, text=(f"{lang_name} = Score {final_score}%"))
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
        
        # Create entry text box
        self.entry_text = ctk.CTkTextbox(self, width=700, height=500)
        self.entry_text.grid(row=0, column=1, padx=20)
        
        # Create button to start training
        self.button = ctk.CTkButton(self, text=(f"Start Training language = {lang}"), state="disabled", command=self.start_process)
        self.button.grid(row=1, column=1, ipadx=200, pady=10, padx=10)
        
        # Enable button if language is selected
        if lang != "Not selected":
            self.button.configure(state="normal")
        
        # Create frame for displaying results
        self.results_frame = ctk.CTkScrollableFrame(self, width=180, height=500)
        self.results_frame.grid(row=0, column=2, sticky="nsew", pady=35)
        
        # Create label for displaying languages
        self.result_text = ctk.CTkLabel(self.results_frame, text="Languages")
        self.result_text.grid(row=0, column=2)
        
        # Insert languages into the results frame
        lang = self.insert_languages(self.result_text)

    def insert_languages(self, results_frame):
        i = 1
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        sql = "SELECT lang_full_name, lang_code FROM lang_list;"
        cursor.execute(sql)
        result = cursor.fetchone()
        while result:
            lang_name = result[0]
            lang_c = result[1]
            
            # Define button callback for selecting a language
            def button_callback(language=lang_name, lang_code=lang_c):
                self.update_lang(language, lang_code)
            
            # Create button for each language
            lang_button = ctk.CTkButton(results_frame, text=result[0], command=button_callback)
            lang_button.grid(row=i, column=0, ipadx=20, pady=2)
            
            i += 1
            result = cursor.fetchone()

    def update_lang(self, language, lang_c):
        global lang_code
        lang_code = lang_c
        lang = language 
        self.button.configure(text=f"Start Training language = {lang}")
        self.button.configure(state="normal")

    def start_process(self):
        text = self.entry_text.get("1.0", "end-1c")
        learn_Text(text, lang_code)
        messagebox.showinfo("Process", "Training completed")


# Class to learn text and update the language database
class learn_Text:
    def __init__(self, text, lang):
        try:
            # Connect to the database
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()

            # Check if the text is empty
            if text is None:
                messagebox.showinfo("No data", "Text field is empty")

            # Connect to the database for inserting new words
            cnx_insert = mysql.connector.connect(**config)
            cursor_insert = cnx_insert.cursor()

            # Extract words from the text
            words = re.findall(r'\b\w+\b', text)
            unique_words = set()

            # Iterate over the words
            for word in words:
                if not word.isdigit() and word.isalpha():
                    # Check if the word already exists in the language database
                    sql = f"SELECT COUNT(*) FROM `{lang}` WHERE `word`=%s"
                    cursor.execute(sql, (word,))
                    result = cursor.fetchone()

                    # If the word does not exist and is not a duplicate, add it to the language database
                    if result[0] == 0 and word not in unique_words:
                        unique_words.add(word)
                        sql = f"INSERT INTO `{lang}` (`word`) VALUES (%s)"
                        cursor_insert.execute(sql, (word,))
                        cnx_insert.commit()

        finally:
            # Close the database connections
            cursor.close()
            cnx.close()
            cursor_insert.close()
            cnx_insert.close()

# Class to correct words in a text using a language database
class Correction_Words:
    def __init__(self, text, lang_c):
        try:
            global corrected_text
            # Connect to the database
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()

            # Retrieve all words from the language database
            sql = f"SELECT word FROM {lang_c};"
            cursor.execute(sql)
            results = cursor.fetchall()

            # Correct the text using the language database
            corrected_text = self.correct_text(text, results)
            print(corrected_text)

        except Exception as e:
            print("Error:", str(e))

    # Helper function to sort the letters in a word
    def sort_word(self, word):
        return ''.join(sorted(word))

    # Correct a single word using the language database
    def correct_word(self, word, word_list):
        word_letters = [char for char in word if char.isalpha()]
        sorted_word_letters = self.sort_word(word_letters)

        for db_word_tuple in word_list:
            db_word = db_word_tuple[0]
            db_letters = [char for char in db_word]
            sorted_db_letters = self.sort_word(db_letters)

            # Skip words with different lengths
            if len(db_letters) != len(word_letters):
                continue

            # Check if the sorted letters match
            if sorted_db_letters == sorted_word_letters:
                return db_word

        # Return the original word if no correction is found
        return word

    # Correct the entire text using the language database
    def correct_text(self, text, word_list):
        words = text.split()
        corrected_words = [self.correct_word(word, word_list) or word for word in words]
        corrected_text = " ".join(corrected_words)
        return corrected_text

# GUI class for text correction
class Text_Correction(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, height=1250, corner_radius=0, width=450)
        lang = "Not selected"
        self.grid(row=0, column=0, sticky="nsew", padx=(260, 20), pady=10)
        self.grid_rowconfigure(0, weight=1)

        # Text input box
        self.entry_text = ctk.CTkTextbox(self, width=700, height=250)
        self.entry_text.grid(row=0, column=1, padx=20, pady=20)

        # Corrected text output box
        self.correction_text = ctk.CTkTextbox(self, width=700, height=250)
        self.correction_text.grid(row=1, column=1, padx=20)

        # Start correction button
        self.button = ctk.CTkButton(self, text=(f"Start Correction language = {lang}"), state="disabled", command=self.start_process)
        self.button.grid(row=2, column=1, ipadx=200, pady=10, padx=10)

        # Language selection buttons
        if lang != "Not selected":
            self.button.configure(state="normal")
        self.button_frame = ctk.CTkScrollableFrame(self, width=180, height=500)
        self.button_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", pady=35)

        # Result text label
        self.result_text = ctk.CTkLabel(self.button_frame, text="Languages")
        self.result_text.grid(row=0, column=2)

        # Insert language buttons
        lang = self.insert_lang(self.result_text)

    # Insert language buttons into the GUI
    def insert_lang(self, results_frame):
        i = 1
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        sql = "SELECT lang_full_name, lang_code FROM lang_list;"
        cursor.execute(sql)
        result = cursor.fetchone()

        while result:
            lang_name = result[0]
            lang_c = result[1]

            # Callback function for language button
            def button_callback(language=lang_name, lang_code=lang_c):
                self.update_lang(language, lang_code)

            # Create and place language button
            lang_button = ctk.CTkButton(results_frame, text=result[0], command=button_callback)
            lang_button.grid(row=i, column=0, ipadx=20, pady=2)
            i += 1
            result = cursor.fetchone()

    # Update the selected language
    def update_lang(self, language, lang_c):
        global lang_code
        lang_code = lang_c
        lang = language
        self.button.configure(text=f"Start Correction language = {lang}")
        self.button.configure(state="normal")

    # Start the correction process
    def start_process(self):
        self.correction_text.delete("1.0", "end")
        text = self.entry_text.get("1.0", "end-1c")
        Correction_Words(text, lang_code)
        self.correction_text.insert("1.0", corrected_text)
        messagebox.showinfo("Process", "Correction completed")

# Main application class
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Language determinant")
        self.geometry("1250x640")
        self.resizable(0, 0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Menu frame
        self.menu_frame = ctk.CTkFrame(self, height=1250, corner_radius=0)
        self.menu_frame.grid(row=0, column=0, sticky="nsw")
        self.menu_frame.grid_rowconfigure(4, weight=1)

        # Title label
        self.title_frame = ctk.CTkLabel(self.menu_frame, text="Language determinant", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_frame.grid(row=0, column=0, padx=10, pady=10)

        # Buttons for different frames
        self.button_text_frame = ctk.CTkButton(self.menu_frame, text="Text determinant", command=self.show_text_frame)
        self.button_text_frame.grid(row=1, column=0, padx=10, pady=(10, 10))
        self.button_image_frame = ctk.CTkButton(self.menu_frame, text="Image determinant", command=self.show_image_frame)
        self.button_image_frame.grid(row=2, column=0, padx=10, pady=(10, 10))
        self.button_training_frame = ctk.CTkButton(self.menu_frame, text="Training", command=self.show_training_frame)
        self.button_training_frame.grid(row=5, column=0, padx=10, pady=(10, 10))
        self.button_text_correction_frame = ctk.CTkButton(self.menu_frame, text="Text correction", command=self.show_text_correction_frame)
        self.button_text_correction_frame.grid(row=3, column=0, padx=10, pady=(10, 10))

        # Frames for different sections
        self.text_frame = None
        self.training_frame = None
        self.image_frame = None
        self.text_correction_frame = None
        
    # Show the text determinant frame
    def show_text_frame(self):
        if self.text_frame is not None:
            self.text_frame.destroy()
        self.text_frame = TextDeterminant(self)
    
    # Show the training frame
    def show_training_frame(self):
        if self.training_frame is not None:
            self.training_frame.destroy()
        self.training_frame = Training(self)

    # Show the image determinant frame
    def show_image_frame(self):
        if self.image_frame is not None:
            self.image_frame.destroy()
        self.image_frame = Research_image_Text(self)
    
    # Show the text correction frame
    def show_text_correction_frame(self):
        if self.text_correction_frame is not None:
            self.text_correction_frame.destroy()
        self.text_correction_frame = Text_Correction(self)
        
# Main entry point of the application
if __name__ == "__main__":
    app = App()
    app.mainloop()
