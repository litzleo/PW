import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import threading
import aggregator
import random

random.seed()

def visitPage(page, instructions):
    def getFilter(f):
        if f == 'id':
            return By.ID
        if f == 'tag':
            return By.TAG_NAME
        if f == 'path':
            return By.XPATH
        if f == 'name':
            return By.NAME
    
    def getElement(i):
        return driver.find_element(by=getFilter(i[2]), value=i[1])

    driver = webdriver.Chrome()
    driver.get(page)
    
    for i in instructions:
        if i[0] == 'type':
            el = getElement(i)
            el.send_keys(i[3])

        if i[0] == 'click':
            el = getElement(i)
            el.click()

        if i[0] == 'wait':
            waitTime = int(i[1] + random.random() * (i[2] - i[1]))
            time.sleep(waitTime / 1000)
    
    driver.quit()

def isValidUserQuantityList(comm, users):
    s = ''
    if not comm:
        return False
    
    user_list = list(users)
    for i in range(len(user_list)):
        user_list[i] = user_list[i].lower()

    state = 'user'
    num = False
    user = ''
    quantity = 0
    
    for c in comm.lower():
        ascii = ord(c)
        if state == 'user':
            if ord('a') <= ascii <= ord('z'):
                user += c
            elif c == ':':
                if user not in user_list:
                    return False
                user_list.remove(user)
                s += user + ':'
                user = ''
                state = 'quantity'
                num = False
            elif c == ' ':
                pass
            else:
                return False
        elif state == 'quantity':
            if ord('0') <= ascii <= ord('9'):
                quantity *= 10
                quantity += int(c)
                s += c
                num = True
            elif c == ' ':
                if num:
                    state = 'user'
                    s += ' '
            elif c != '\0':
                return False
    
    return s

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Web Interaction")
        self.geometry("600x400")
        self.configure(bg="#f0f0f0")
        self.pages = aggregator.getPages()
        self.users = []
        self.create_widgets()

    def create_widgets(self):
        title_font = ("Tahoma", 16)
        label_font = ("Tahoma", 12)
        #entry_font = ("Tahoma", 12)
        button_font = ("Tahoma", 12)

        title_label = tk.Label(self, text="Siti disponibili:", font=title_font, bg="#f0f0f0", fg="#333333")
        title_label.pack(pady=10)
        title_label.config(anchor="w")

        self.page_var = tk.StringVar(self)
        self.page_var.set("Seleziona un sito")
        self.page_menu = tk.OptionMenu(self, self.page_var, *self.pages)
        self.page_menu.config(bg="#ffffff", fg="#333333", font=label_font)
        self.page_menu["menu"].config(bg="#ffffff", fg="#333333", font=label_font)
        self.page_menu.pack(pady=5)

        select_button = tk.Button(self, text="Seleziona Utente", command=self.select_page, bg="#007acc", fg="#ffffff", font=button_font)
        select_button.pack(pady=5)
        select_button.config(anchor="w")

        self.user_frame = tk.Frame(self, bg="#f0f0f0")
        self.user_frame.pack(pady=10)

    def select_page(self):
        page = self.page_var.get()
        if page and page != "Seleziona un sito":
            self.users = aggregator.getKindOfUsers(page)
            for widget in self.user_frame.winfo_children():
                widget.destroy()

            title_font = ("Tahoma", 16)
            label_font = ("Tahoma", 12)

            user_label = tk.Label(self.user_frame, text="Tipi di utenti:", font=title_font, bg="#f0f0f0", fg="#333333")
            user_label.pack(pady=10)
            user_label.config(anchor="w")

            self.user_entries = {}
            for user in self.users:
                frame = tk.Frame(self.user_frame, bg="#f0f0f0")
                frame.pack(pady=5, fill="x")

                user_label = tk.Label(frame, text=user, font=label_font, bg="#f0f0f0", fg="#333333")
                user_label.pack(side="left", padx=5)
                user_label.config(anchor="w", width=20)

                entry = tk.Entry(frame, font=label_font, bg="#ffffff", fg="#333333")
                entry.pack(side="left", padx=5, expand=True, fill="x")
                self.user_entries[user] = entry

            start_button = tk.Button(self.user_frame, text="Avvia", command=self.start_threads, bg="#28a745", fg="#ffffff", font=label_font)
            start_button.pack(pady=10)
            start_button.config(anchor="w")
        else:
            messagebox.showwarning("Attenzione", "Seleziona un sito valido")

    def start_threads(self):
        comm = ' '.join(f"{user}:{entry.get()}" for user, entry in self.user_entries.items() if entry.get().isdigit())
        comm = isValidUserQuantityList(comm, self.users)

        if comm:
            quantities = comm.split()
            for q in quantities:
                userType, amount = q.split(':')
                for i in range(int(amount)):
                    time.sleep(0.1)
                    threading.Thread(target=visitPage, args=(self.page_var.get(), aggregator.getInstructions(self.page_var.get(), userType))).start()
        else:
            messagebox.showerror("Input invalido", "Inserire la quantità richiesta del tipo utente in numeri")

if __name__ == "__main__":
    app = App()
    app.mainloop()