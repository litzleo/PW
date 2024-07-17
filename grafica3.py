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


# crea una prima finestra con dimesioni prestabilite e la chiamo "Web interactions" 
#  (sto nome mi è venuto completamente a caso, si può ovviamente cambiare)
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Web Interactions")
        self.geometry("600x400")
        self.configure(bg="#f0f0f0")
        self.pages = aggregator.getPages()
        self.users = []
        self.create_widgets()
        self.bind("<Configure>", self.on_resize) # on_resize è il metodo di rimensionamento 

 # crea i widget ed i bottoni. Listbox è quello che restituisce i siti in chiaro da selezionare
# grid sarebbe quello che garantisce il ridimensionamento (sticky=ew dovrebbe tenerlo centrale)       
    def create_widgets(self):
        self.title_font = ("Tahoma", 16)
        self.label_font = ("Tahoma", 12)
        self.button_font = ("Tahoma", 12)

        self.container = tk.Frame(self, bg="#f0f0f0")
        self.container.grid(sticky="nsew")

        self.container.grid_rowconfigure(1, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.title_label = tk.Label(self.container, text="Siti disponibili:", font=self.title_font, bg="#f0f0f0", fg="#333333")
        self.title_label.grid(row=0, column=0, pady=10, padx=10)

        self.page_listbox = tk.Listbox(self.container, font=self.label_font, bg="#ffffff", fg="#333333")
        for page in self.pages:
            self.page_listbox.insert(tk.END, page)
        self.page_listbox.grid(row=1, column=0, pady=5, padx=10, sticky="ew")

        self.select_button = tk.Button(self.container, text="Seleziona", command=self.select_page, bg="#007acc", fg="#ffffff", font=self.button_font)
        self.select_button.grid(row=1, column=1, pady=5, padx=10)

        self.user_frame = tk.Frame(self.container, bg="#f0f0f0")
        self.user_frame.grid(row=3, column=0, pady=10, padx=10, sticky="nsew")

    def select_page(self):
        selected_index = self.page_listbox.curselection()
        if selected_index:
            page = self.page_listbox.get(selected_index)
            self.users = aggregator.getKindOfUsers(page)
            for widget in self.user_frame.winfo_children():
                widget.destroy()

            user_label = tk.Label(self.user_frame, text="Tipi di utenti:", font=self.title_font, bg="#f0f0f0", fg="#333333")
            user_label.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

            self.user_entries = {}
            for index, user in enumerate(self.users):
                frame = tk.Frame(self.user_frame, bg="#f0f0f0")
                frame.grid(row=index+1, column=0, pady=5, padx=10, sticky="ew")

                user_label = tk.Label(frame, text=user, font=self.label_font, bg="#f0f0f0", fg="#333333")
                user_label.pack(side="left", padx=5, anchor="w")

                entry = tk.Entry(frame, font=self.label_font, bg="#ffffff", fg="#333333")
                entry.pack(side="left", padx=5, expand=True, fill="x")
                self.user_entries[user] = entry

            start_button = tk.Button(self.user_frame, text="Avvia", command=self.start_threads, bg="#28a745", fg="#ffffff", font=self.label_font)
            start_button.grid(row=len(self.users)+1, column=0, pady=10, padx=10, sticky="ew")

        # se vogliamo dare un feedback anche alla selezione del sito web, 
        # ma questo implicherebbe la possibilità di far fare dei click altrove nella schermata 
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
                    threading.Thread(target=visitPage, args=(self.page_listbox.get(self.page_listbox.curselection()), aggregator.getInstructions(self.page_listbox.get(self.page_listbox.curselection()), userType))).start()
        else:
            messagebox.showerror("Input invalido", "Inserire la quantità richiesta del tipo utente in numeri")

    # ritorna on_resize per le dimesioni
    def on_resize(self, event):
        new_width = event.width
        new_height = event.height

         # dovrebbe aggiustare le dimesioni del font in base a quelle della finestra
        self.title_font = ("Tahoma", max(10, int(new_width / 40)))
        self.label_font = ("Tahoma", max(8, int(new_width / 50)))
        self.button_font = ("Tahoma", max(8, int(new_width / 50)))

        self.title_label.config(font=self.title_font)
        self.page_listbox.config(font=self.label_font)
        self.select_button.config(font=self.button_font)

        for child in self.user_frame.winfo_children():
            if isinstance(child, tk.Label):
                child.config(font=self.label_font)
            if isinstance(child, tk.Entry):
                child.config(font=self.label_font)
            if isinstance(child, tk.Button):
                child.config(font=self.button_font)

if __name__ == "__main__":
    app = App()
    app.mainloop()