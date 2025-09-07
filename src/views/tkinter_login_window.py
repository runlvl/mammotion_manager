"""
Robustes Login-Fenster mit Tkinter

Tkinter ist zuverlässiger als Qt und hat keine Größenprobleme.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import logging
from typing import Optional, Callable


class TkinterLoginWindow:
    """
    Robustes Login-Fenster mit Tkinter
    
    Garantiert große, gut sichtbare UI-Elemente ohne Qt-Probleme.
    """
    
    def __init__(self, on_login: Optional[Callable] = None, on_cancel: Optional[Callable] = None):
        self.logger = logging.getLogger(__name__)
        self.on_login = on_login
        self.on_cancel = on_cancel
        
        # Hauptfenster erstellen
        self.root = tk.Tk()
        self.root.title("Mammotion Mähroboter - Anmeldung")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Fenster zentrieren
        self._center_window()
        
        # Variablen
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.remember_var = tk.BooleanVar()
        self.is_logging_in = False
        
        # UI erstellen
        self._setup_styles()
        self._create_ui()
        
        # Fenster-Events
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel_clicked)
        
    def _center_window(self):
        """Zentriert das Fenster auf dem Bildschirm"""
        self.root.update_idletasks()
        width = 600
        height = 700
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def _setup_styles(self):
        """Konfiguriert die Styles"""
        # Hintergrundfarbe
        self.root.configure(bg='#f8f9fa')
        
        # Schriftarten definieren
        self.title_font = font.Font(family="Arial", size=32, weight="bold")
        self.subtitle_font = font.Font(family="Arial", size=18, weight="normal")
        self.label_font = font.Font(family="Arial", size=16, weight="bold")
        self.input_font = font.Font(family="Arial", size=16, weight="normal")
        self.button_font = font.Font(family="Arial", size=16, weight="bold")
        self.checkbox_font = font.Font(family="Arial", size=14, weight="normal")
        
    def _create_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # Hauptcontainer
        main_frame = tk.Frame(self.root, bg='white', relief='raised', bd=2)
        main_frame.pack(fill='both', expand=True, padx=40, pady=40)
        
        # === HEADER ===
        self._create_header(main_frame)
        
        # Abstand
        tk.Frame(main_frame, height=40, bg='white').pack()
        
        # === FORMULAR ===
        self._create_form(main_frame)
        
        # Abstand
        tk.Frame(main_frame, height=30, bg='white').pack()
        
        # === OPTIONEN ===
        self._create_options(main_frame)
        
        # Abstand
        tk.Frame(main_frame, height=20, bg='white').pack()
        
        # === PROGRESS ===
        self._create_progress(main_frame)
        
        # Abstand
        tk.Frame(main_frame, height=30, bg='white').pack()
        
        # === BUTTONS ===
        self._create_buttons(main_frame)
        
    def _create_header(self, parent):
        """Erstellt den Header-Bereich"""
        header_frame = tk.Frame(parent, bg='white')
        header_frame.pack(fill='x', pady=(30, 0))
        
        # Titel
        title_label = tk.Label(
            header_frame,
            text="Mammotion",
            font=self.title_font,
            fg='#2c3e50',
            bg='white'
        )
        title_label.pack()
        
        # Untertitel
        subtitle_label = tk.Label(
            header_frame,
            text="Mähroboter-Verwaltung",
            font=self.subtitle_font,
            fg='#6c757d',
            bg='white'
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Beschreibung
        desc_label = tk.Label(
            header_frame,
            text="Melden Sie sich mit Ihren Mammotion-Zugangsdaten an,\num Ihren Mähroboter zu verwalten.",
            font=font.Font(family="Arial", size=14),
            fg='#6c757d',
            bg='white',
            justify='center'
        )
        desc_label.pack(pady=(10, 0))
        
        # Trennlinie
        separator = tk.Frame(header_frame, height=2, bg='#dee2e6')
        separator.pack(fill='x', pady=(20, 0))
        
    def _create_form(self, parent):
        """Erstellt das Formular"""
        form_frame = tk.Frame(parent, bg='white')
        form_frame.pack(fill='x', padx=40)
        
        # E-Mail-Bereich
        email_frame = tk.Frame(form_frame, bg='white')
        email_frame.pack(fill='x', pady=(0, 25))
        
        email_label = tk.Label(
            email_frame,
            text="E-Mail-Adresse",
            font=self.label_font,
            fg='#495057',
            bg='white',
            anchor='w'
        )
        email_label.pack(fill='x', pady=(0, 8))
        
        self.email_entry = tk.Entry(
            email_frame,
            textvariable=self.email_var,
            font=self.input_font,
            relief='solid',
            bd=3,
            highlightthickness=0,
            fg='#495057',
            bg='white',
            insertbackground='#495057'
        )
        self.email_entry.pack(fill='x', ipady=15)  # ipady macht das Feld höher!
        self.email_entry.insert(0, "ihre.email@mammotion.com")
        self.email_entry.configure(fg='#adb5bd')  # Placeholder-Farbe
        
        # Placeholder-Funktionalität
        self._setup_placeholder(self.email_entry, "ihre.email@mammotion.com")
        
        # Passwort-Bereich
        password_frame = tk.Frame(form_frame, bg='white')
        password_frame.pack(fill='x')
        
        password_label = tk.Label(
            password_frame,
            text="Passwort",
            font=self.label_font,
            fg='#495057',
            bg='white',
            anchor='w'
        )
        password_label.pack(fill='x', pady=(0, 8))
        
        self.password_entry = tk.Entry(
            password_frame,
            textvariable=self.password_var,
            font=self.input_font,
            relief='solid',
            bd=3,
            highlightthickness=0,
            fg='#495057',
            bg='white',
            insertbackground='#495057',
            show='*'
        )
        self.password_entry.pack(fill='x', ipady=15)  # ipady macht das Feld höher!
        
        # Enter-Taste für Login
        self.email_entry.bind('<Return>', lambda e: self._on_login_clicked())
        self.password_entry.bind('<Return>', lambda e: self._on_login_clicked())
        
    def _setup_placeholder(self, entry, placeholder_text):
        """Richtet Placeholder-Funktionalität ein"""
        def on_focus_in(event):
            if entry.get() == placeholder_text:
                entry.delete(0, tk.END)
                entry.configure(fg='#495057')
                
        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder_text)
                entry.configure(fg='#adb5bd')
                
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)
        
    def _create_options(self, parent):
        """Erstellt den Optionen-Bereich"""
        options_frame = tk.Frame(parent, bg='white')
        options_frame.pack(fill='x', padx=40)
        
        self.remember_checkbox = tk.Checkbutton(
            options_frame,
            text="Zugangsdaten sicher speichern",
            variable=self.remember_var,
            font=self.checkbox_font,
            fg='#6c757d',
            bg='white',
            activebackground='white',
            activeforeground='#495057',
            selectcolor='white',
            anchor='w'
        )
        self.remember_checkbox.pack(fill='x')
        
    def _create_progress(self, parent):
        """Erstellt die Progress-Bar"""
        self.progress_frame = tk.Frame(parent, bg='white')
        self.progress_frame.pack(fill='x', padx=40)
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode='indeterminate',
            length=400
        )
        # Progress-Bar ist initial versteckt
        
    def _create_buttons(self, parent):
        """Erstellt die Buttons"""
        button_frame = tk.Frame(parent, bg='white')
        button_frame.pack(fill='x', padx=40, pady=(0, 30))
        
        # Button-Container für zentrierte Anordnung
        button_container = tk.Frame(button_frame, bg='white')
        button_container.pack()
        
        # Abbrechen-Button
        self.cancel_button = tk.Button(
            button_container,
            text="Abbrechen",
            font=self.button_font,
            fg='#6c757d',
            bg='#f8f9fa',
            activeforeground='#495057',
            activebackground='#e9ecef',
            relief='solid',
            bd=3,
            width=12,
            pady=10,
            command=self._on_cancel_clicked
        )
        self.cancel_button.pack(side='left', padx=(0, 15))
        
        # Anmelden-Button
        self.login_button = tk.Button(
            button_container,
            text="Anmelden",
            font=self.button_font,
            fg='white',
            bg='#198754',
            activeforeground='white',
            activebackground='#157347',
            relief='solid',
            bd=0,
            width=12,
            pady=10,
            command=self._on_login_clicked
        )
        self.login_button.pack(side='left')
        
    def _on_login_clicked(self):
        """Behandelt Login-Button-Klick"""
        if self.is_logging_in:
            return
            
        email = self.email_var.get().strip()
        password = self.password_var.get()
        remember = self.remember_var.get()
        
        # Placeholder-Text ignorieren
        if email == "ihre.email@mammotion.com":
            email = ""
            
        # Validierung
        if not email:
            messagebox.showerror("Fehler", "Bitte geben Sie Ihre E-Mail-Adresse ein.")
            self.email_entry.focus()
            return
            
        if not password:
            messagebox.showerror("Fehler", "Bitte geben Sie Ihr Passwort ein.")
            self.password_entry.focus()
            return
            
        # Login-Prozess starten
        self.set_login_in_progress(True)
        
        if self.on_login:
            self.on_login(email, password, remember)
            
    def _on_cancel_clicked(self):
        """Behandelt Abbrechen-Button-Klick"""
        if self.on_cancel:
            self.on_cancel()
        self.root.destroy()
        
    def set_login_in_progress(self, in_progress: bool):
        """Setzt den Login-Status"""
        self.is_logging_in = in_progress
        
        # UI-Elemente deaktivieren/aktivieren
        state = 'disabled' if in_progress else 'normal'
        self.email_entry.configure(state=state)
        self.password_entry.configure(state=state)
        self.remember_checkbox.configure(state=state)
        self.login_button.configure(state=state)
        
        # Progress Bar anzeigen/verstecken
        if in_progress:
            self.progress_bar.pack(fill='x', pady=(10, 0))
            self.progress_bar.start(10)
            self.login_button.configure(text="Verbinde mit Mammotion...")
        else:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.login_button.configure(text="Anmelden")
            
    def show_error(self, message: str):
        """Zeigt eine Fehlermeldung"""
        self.set_login_in_progress(False)
        messagebox.showerror("Anmeldung fehlgeschlagen", message)
        
    def show_success(self, message: str):
        """Zeigt eine Erfolgsmeldung"""
        messagebox.showinfo("Anmeldung erfolgreich", message)
        
    def get_credentials(self) -> tuple[str, str, bool]:
        """Gibt die eingegebenen Zugangsdaten zurück"""
        email = self.email_var.get().strip()
        if email == "ihre.email@mammotion.com":
            email = ""
        return (email, self.password_var.get(), self.remember_var.get())
        
    def set_credentials(self, email: str, password: str = "", remember: bool = False):
        """Setzt die Zugangsdaten"""
        self.email_var.set(email)
        self.password_var.set(password)
        self.remember_var.set(remember)
        
        if email:
            self.email_entry.configure(fg='#495057')
        if password:
            self.password_entry.focus()
        else:
            self.email_entry.focus()
            
    def show(self):
        """Zeigt das Fenster an"""
        self.email_entry.focus()
        self.root.mainloop()
        
    def hide(self):
        """Versteckt das Fenster"""
        self.root.withdraw()
        
    def destroy(self):
        """Zerstört das Fenster"""
        self.root.destroy()


def test_login_window():
    """Test-Funktion für das Login-Fenster"""
    def on_login(email, password, remember):
        print(f"Login: {email}, {password}, {remember}")
        window.show_success("Anmeldung erfolgreich!")
        window.root.after(2000, window.destroy)
        
    def on_cancel():
        print("Login abgebrochen")
        
    window = TkinterLoginWindow(on_login=on_login, on_cancel=on_cancel)
    window.show()


if __name__ == "__main__":
    test_login_window()
