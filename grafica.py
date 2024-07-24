import os
import tkinter as tk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.ie.service import Service as IEService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager, IEDriverManager
from tkinter import messagebox
import aggregator
from main import beginBrowsing
from re import search

def check_installed_browsers():
    paths = {
        "Chrome": [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        ],
        "Firefox": [
            "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
            "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe",
            "/usr/bin/firefox",
            "/Applications/Firefox.app/Contents/MacOS/firefox"
        ],
        "Edge": [
            "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
            "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
            "/usr/bin/microsoft-edge",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
        ],
        "IE": [
            "C:\\Program Files\\Internet Explorer\\iexplore.exe",
            "C:\\Program Files (x86)\\Internet Explorer\\iexplore.exe"
        ]
    }

    installed_browsers = []
    for browser, paths in paths.items():
        for path in paths:
            if os.path.exists(path):
                installed_browsers.append(browser)
                break

    return installed_browsers

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("")
        self.geometry("600x450")  # cgeometry cambia dimensione a seconda del browser scelto
        self.configure(bg="#e0f7fa")
        self.pages = aggregator.getPages()
        self.browsers = check_installed_browsers()
        self.users = []
        self.create_widgets()

    def create_widgets(self):
        title_font = ("Tahoma", 16)
        label_font = ("Tahoma", 12)
        button_font = ("Tahoma", 12)

        title_label = tk.Label(self, text="Siti disponibili:", font=title_font, bg="#e0f7fa", fg="#333333")
        title_label.pack(pady=10)
        title_label.config(anchor="w")

        self.page_var = tk.StringVar(self)
        self.page_var.set("Seleziona un sito")
        self.page_menu = tk.OptionMenu(self, self.page_var, *self.pages)
        self.page_menu.config(bg="#ffffff", fg="#333333", font=label_font)
        self.page_menu["menu"].config(bg="#ffffff", fg="#333333", font=label_font)
        self.page_menu.pack(pady=5)

    
        browser_label = tk.Label(self, text="Browser disponibili:", font=title_font, bg="#e0f7fa", fg="#333333")
        browser_label.pack(pady=10)
        browser_label.config(anchor="w")

        self.browser_var = tk.StringVar(self)
        self.browser_var.set("Seleziona un browser")
        self.browser_menu = tk.OptionMenu(self, self.browser_var, *self.browsers)
        self.browser_menu.config(bg="#ffffff", fg="#333333", font=label_font)
        self.browser_menu["menu"].config(bg="#ffffff", fg="#333333", font=label_font)
        self.browser_menu.pack(pady=5)

        select_button = tk.Button(self, text="Seleziona Utente", command=lambda: self.animate_button(select_button, self.select_page), bg="#afeeee", fg="#000000", font=button_font)
        select_button.pack(pady=5)
        select_button.config(anchor="w")

        self.user_frame = tk.Frame(self, bg="#afeeee")
        self.user_frame.pack(pady=10)

    def animate_button(self, button, command):
        original_color = button.cget("bg")
        button.config(bg="#b0e0e6")  # Cambia il colore del pulsante al clic (azzurro chiaro)
        self.after(200, lambda: button.config(bg=original_color))  # Ripristina il colore originale dopo 200ms
        command()

    def start_threads(self, page):
        comm = ''
        comm += ' '.join(f"{user}:{entry.get().replace(' ', '')}" for user, entry in self.user_entries.items() if search('^ *[0-9]+ *$', entry.get()))
        
        browser = self.browser_var.get()

        if not comm:
            messagebox.showerror("Input invalido", "Inserire la quantità richiesta del tipo utente in numeri.")
            return
        if not (browser and browser != "Seleziona un browser"):
            messagebox.showerror("Input invalido", "Selezionare prima un browser, poi procedere.")
            return
        beginBrowsing(comm, page, browser)

    def select_page(self):
        page = self.page_var.get()
        browser = self.browser_var.get()
        if page and page != "Seleziona un sito":
            self.users = aggregator.getKindOfUsers(page)
            for widget in self.user_frame.winfo_children():
                widget.destroy()

            title_font = ("Tahoma", 16)
            label_font = ("Tahoma", 12)

            user_label = tk.Label(self.user_frame, text="Tipi di utente:", font=title_font, bg="#afeeee", fg="#333333")
            user_label.pack(pady=10)
            user_label.config(anchor="w")

            self.user_entries = {}
            for user in self.users:
                frame = tk.Frame(self.user_frame, bg="#afeeee")
                frame.pack(pady=5, fill="x")

                user_label = tk.Label(frame, text=user, font=label_font, bg="#f0f0f0", fg="#333333")
                user_label.pack(side="left", padx=5)
                user_label.config(anchor="w", width=20)

                entry = tk.Entry(frame, font=label_font, bg="#ffffff", fg="#333333")
                entry.pack(side="left", padx=5, expand=True, fill="x")
                self.user_entries[user] = entry
            
            pass_page_to_threads = lambda : self.start_threads(page)
            start_button = tk.Button(self.user_frame, text="Avvia", command=lambda: self.animate_button(start_button, pass_page_to_threads), bg="#28a745", fg="#ffffff", font=label_font)
            start_button.pack(pady=10)
            start_button.config(anchor="w")
        else:
            messagebox.showwarning("Attenzione", "Selezionare prima un sito, poi procedere.")

if __name__ == "__main__":
    app = App()
    app.mainloop()
