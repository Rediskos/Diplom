import tkinterDb
from eprocessor import *
import nltk
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font

import sqlite3


class Application:
    DB_NAME = "test_keeper.db"
    TASKS_TABLE = "tasks_history"

    def __init__(self, root):
        root.title("Автоматический конструктор тестов по английскому")
        root.resizable(False, False)
        # asd
        self.myFont = Font(family="Verdana", size=12)
        self.root = root
        self.eprocessor = EngProcessor()
        self.blueprint_converter = BlueprintConverter()
        self.app_tabs = ttk.Notebook(root)
        self.app_tabs.grid(row=0, column=0)
        self.app_tabs.enable_traversal()

        self.tab_test_creation = tk.Frame(root)
        self.tab_test_creation.columnconfigure(0, weight=1)

        self.tab_test_execute =tk.Frame(root)

        self.app_tabs.add(self.tab_test_creation, text="Создание задания")
        self.app_tabs.add(self.tab_test_execute, text="Выполнение задания")

        self.conn = sqlite3.connect(self.DB_NAME)
        self._create_tables_if_needed()

        self._tab_test_creation()
        self._tab_test_execute_creation()
       # self.tab_checker()

    def _create_tables_if_needed(self):
        cursor = self.conn.cursor()

        sql_create_tasks_tab = """CREATE TABLE IF NOT EXISTS tasks_history (answer txt, blueprint txt);"""

        cursor.execute(sql_create_tasks_tab)

    def _process_text(self, inserted_text, preview_text, hard_level_counter, pack_level_counter):
        processed = self.eprocessor.process_text(inserted_text.get("1.0", tk.END))
        blueprinted = self.eprocessor.make_blueprint(processed, hard_level_counter["text"],
                                                     pack_level_counter["text"])
        str_blueprint = blueprinted["to_contester"]
        str_to_bd_blueprint = blueprinted["to_data_base"]

        cursor = self.conn.cursor()

        sql = "INSERT INTO "+self.TASKS_TABLE+" VALUES (:answer, :blueprint)"
        cursor.execute(sql, (str_to_bd_blueprint, str_blueprint))

        self.conn.commit()

        sql = "SELECT oid FROM "+self.TASKS_TABLE+" WHERE answer=?"
        cursor.execute(sql, (str_to_bd_blueprint, ))
        answer_index = cursor.fetchall()
        preview_text["state"] = "normal"
        preview_text.delete("1.0", tk.END)
        preview_text.insert("1.0", "###"+str(answer_index[0][0]) + "###\n"+ str_blueprint)
        preview_text["state"] = "disabled"

    def _check_button_pressed(self, inserted_text, preview_text):
        target_text = inserted_text.get("1.0", tk.END)
        splited_text_and_id = target_text.split("###")
        id = splited_text_and_id[1]
        target_text = nltk.word_tokenize(splited_text_and_id[2].strip())

        cursor = self.conn.cursor()

        sql = "SELECT * FROM " + self.TASKS_TABLE + " WHERE oid=" + id
        cursor.execute(sql)

        cursor.execute(sql)
        sql_answer = cursor.fetchall()
        etalon = nltk.word_tokenize(sql_answer[0][0])

        length_text = len(target_text)
        length_etalon = len(etalon)

        checked_answer = ""

        target_shift = 0
        etalon_shift = 0

        for i in range(min(length_etalon, length_text)):

            target_i = i + target_shift
            etalon_i = i + etalon_shift

            if target_i >= length_text or etalon_i >= length_etalon:
                break

            target_tmp = target_text[target_i]
            etalon_tmp = etalon[etalon_i]

            if target_tmp == '``':
                target_tmp = "''"

            if etalon_tmp == '``':
                etalon_tmp = "''"


            if target_i + 1 < length_text and target_text[target_i + 1] in string.punctuation + '’':
                target_tmp += target_text[target_i + 1]

                if target_text[target_i + 1] == '’':
                    target_tmp += target_text[target_i + 2]
                    target_text[target_i + 2] = ""
                    target_shift += 1

                target_text[target_i + 1] = ""
                target_shift += 1

            if etalon_i + 1 < length_etalon and etalon[etalon_i + 1] in string.punctuation + '’':
                etalon_tmp += etalon[etalon_i + 1]

                if etalon[etalon_i + 1] == '’':
                    etalon_tmp += etalon[etalon_i + 2]
                    etalon[etalon_i + 2] = ""
                    etalon_shift += 1

                etalon[etalon_i + 1] = ""
                etalon_shift += 1


            if target_tmp == etalon_tmp:

                if target_tmp not in string.punctuation + '’':
                    checked_answer += " "

                if target_tmp != "ничего":
                    checked_answer += target_tmp
            else:
                checked_answer += " <<Ответ: " + target_tmp + " Правильный ответ: " + etalon_tmp + ">>"

        preview_text["state"] = "normal"
        preview_text.delete("1.0", tk.END)
        preview_text.insert("1.0", checked_answer)
        preview_text["state"] = "disabled"


    def _tab_test_creation(self):

        action_buttons =tk.Frame(self.tab_test_creation)
        action_buttons.grid(row=0, column=0, rowspan=2, sticky="we")

        check_text = tk.Button(action_buttons, text="Проверить текст", width=33,
                               command=lambda :self._check_button_pressed(inserted_text, preview_text))
        prew_tasks = tk.Button(action_buttons, text="Предыдущие задания", width=33)

        check_text.grid(row=1, column=0, padx=5, pady=2, sticky="ew")
        prew_tasks.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        options_frame = tk.Frame(self.tab_test_creation)
        options_frame.grid(row=0, column=1, rowspan=2, sticky="ew")

        hard_level = tk.Label(options_frame, text="Уровень сложности")
        pack_level = tk.Label(options_frame, text="Плотность")

        hard_level_counter =tk.Label(options_frame, text="1")
        pack_level_counter =tk.Label(options_frame, text="1")

        hard_level.grid(row=0, column=0, padx=2, pady=2)
        pack_level.grid(row=1, column=0, padx=2, pady=2)
        hard_level_counter.grid(row=0, column=1, padx=50, pady=2)
        pack_level_counter.grid(row=1, column=1, padx=10, pady=2)

        process_text = tk.Button(action_buttons, text="Обработать текст",
                                 command=lambda: self._process_text(inserted_text, preview_text,
                                                                    hard_level_counter, pack_level_counter))

        process_text.grid(row=0, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        hard_level_1 =tk.Button(options_frame, text="1", padx=3, width=10,
                                command=lambda :hard_level_counter.config(text='1') )
        hard_level_2 =tk.Button(options_frame, text="2", padx=3, width=10,
                                command=lambda :hard_level_counter.config(text='2') )
        hard_level_3 =tk.Button(options_frame, text="3", padx=3, width=10,
                                command=lambda :hard_level_counter.config(text='3') )

        hard_level_1.grid(row=0, column=2, sticky="ew")
        hard_level_2.grid(row=0, column=3, sticky="ew")
        hard_level_3.grid(row=0, column=4, sticky="ew")

        pack_level_1 =tk.Button(options_frame, text="1", padx=3, width=10,
                                command=lambda :pack_level_counter.config(text='1') )
        pack_level_2 =tk.Button(options_frame, text="2", padx=3, width=10,
                                command=lambda :pack_level_counter.config(text='2') )
        pack_level_3 =tk.Button(options_frame, text="3", padx=3, width=10,
                                command=lambda :pack_level_counter.config(text='3') )

        pack_level_1.grid(row=1, column=2, sticky="ew")
        pack_level_2.grid(row=1, column=3, sticky="ew")
        pack_level_3.grid(row=1, column=4, sticky="ew")

        inserted_text =tk.Text(self.tab_test_creation, height=30, width=60)
        preview_text =tk.Text(self.tab_test_creation, height=30, width=60, state="disabled")

        inserted_text.configure(font=self.myFont)
        preview_text.configure(font=self.myFont)

        inserted_text.grid(row=2, column=0, sticky="nsew")
        preview_text.grid(row=2, column=1, sticky="nsew")

    def _end_test_button_pressed(self, user_answer, window, bottom_frame, upper_frame):

        answer = ""

        for item in user_answer:

            if isinstance(item, tk.Label):
                text = item["text"].strip()
                answer += " " + text

                if len(item["text"]) > 1 and item["text"][1] == '#':
                    answer += '\n'

            elif isinstance(item, tk.StringVar):
                word = item.get().strip()
                if word != "":
                    answer += " " + word
            elif isinstance(item, tk.Entry):
                word = item.get().split()
                answer += " " + word[0]

        self.blueprint_converter.clear_elements()
        bottom_frame.destroy()
        upper_frame.destroy()

        answer_text = tk.Text(window)
        answer_text.pack()
        answer_text.insert("1.0", answer)
        answer_text.config(state="disabled", font = self.myFont)



    def _execute_text_button_pressed(self, text):

        go_window = tk.Toplevel(self.root, width = 300, height = 300)
        FrameTop = tk.Frame(go_window)
        FrameTop.pack()

        FrameBottom = tk.Frame(go_window)
        FrameBottom.pack()

        end_test_button = tk.Button(FrameTop, text="Завершить тестирование",
                                    command=lambda: self._end_test_button_pressed(answer, go_window, FrameBottom, FrameTop))
        end_test_button.pack()

        answer = self.blueprint_converter.make_test(FrameBottom, text.get("1.0", tk.END))

    def _tab_test_execute_creation(self):
        myFont = Font(family="Verdana", size=12)
        test_text = tk.Text(self.tab_test_execute, width=125)

        test_text.configure(font=self.myFont)
        execute_text = tk.Button(self.tab_test_execute, text="Выполнить загруженный тест",
                                 command=lambda :self._execute_text_button_pressed(test_text))

        execute_text.grid(row=0, column=0)
        test_text.grid(row=1, column=0)



root = tk.Tk()
GUI = Application(root)

root.mainloop()


# root.geometry("400x400")


# Create table

'''
c.execute("""CREATE TABLE adresses(
    first_name text,
    last_name text,
    address text,
    city text,
    state text,
    zipcode integer    
)
""")
'''


# place db into new window
def new_win_table():
    with tkinterDb.drawDBinTkinter('addres_book.db') as draw_db:
        # conn = sqlite3.connect('addres_book.db')

        new_window = Toplevel(root)

        # draw_db = tkinterDb.drawDBinTkinter(db=conn)

        draw_db.draw_table(new_window, "adresses")

        # commit changes
        # conn.commit()

        # Close connection
        # conn.close()


# create function tu delete a record
def delete():
    # Create a database or connect to one
    conn = sqlite3.connect('addres_book.db')

    # Create cursor
    c = conn.cursor()

    # Delete a Record
    c.execute("DELETE from adresses WHERE oid= " + delete_oid.get())

    # commit changes
    conn.commit()

    # Close connection
    conn.close()


# Create submit fucntion for db
def submit():
    # Create a database or connect to one
    conn = sqlite3.connect('addres_book.db')

    # Create cursor
    c = conn.cursor()

    # Insert Into Table
    c.execute("INSERT INTO adresses VALUES (:f_name, :l_name, :address, :city, :state, :zipcode)",
              {
                  'f_name': f_name.get(),
                  'l_name': l_name.get(),
                  'address': address.get(),
                  'city': city.get(),
                  'state': state.get(),
                  'zipcode': zipcode.get()
              })

    # commit changes
    conn.commit()

    # Close connection
    conn.close()


def quary():
    # Create a database or connect to one
    conn = sqlite3.connect('addres_book.db')

    # Create cursor
    c = conn.cursor()

    # Query Into Table
    c.execute("SELECT *, oid FROM adresses")
    tab_all = c.fetchall()

    print_records = ""
    for record in tab_all:
        for item in record:
            print_records += str(item) + "\t"
        print_records += "\n"

    quary_label =tk.Label(root, text=print_records)
    quary_label.grid(row=11, column=0, columnspan=2)

    # commit changes
    conn.commit()

    # Close connection
    conn.close()

    # Clear The Text Boxes
    f_name.delete(0, END)
    l_name.delete(0, END)
    address.delete(0, END)
    city.delete(0, END)
    state.delete(0, END)
    zipcode.delete(0, END)
