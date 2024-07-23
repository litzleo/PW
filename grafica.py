try:
    import tkinter as tk
except:
    import pip
    pip.main(['install', 'python3-tk'])
    import tkinter as tk

from tkinter import messagebox
import aggregator
from main import beginBrowsing
from re import search


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("")
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
            
            pass_page_to_threads = lambda : self.start_threads(page)
            start_button = tk.Button(self.user_frame, text="Avvia", command=pass_page_to_threads, bg="#28a745", fg="#ffffff", font=label_font)
            start_button.pack(pady=10)
            start_button.config(anchor="w")
        else:
            messagebox.showwarning("Attenzione", "Seleziona un sito valido")

    def start_threads(self, page):
        comm = ' '.join(f"{user}:{entry.get().replace(' ', '')}" for user, entry in self.user_entries.items() if search('^ *[0-9]+ *$', entry.get()))

        if comm:
            beginBrowsing(comm, page)
        else:
            messagebox.showerror("Input invalido", "Inserire la quantità richiesta del tipo utente in numeri")

if __name__ == "__main__":
    app = App()
    app.mainloop()
