import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import hashlib
from datetime import datetime

from task import Task
from task_manager import TaskManager

# Globale Variablen für den angemeldeten Benutzer
current_user_id = None
current_username = ""

# Globale Widgets für den Zugriff aus den Funktionen
entry_title = None
entry_subject = None
entry_date = None
combo_priority = None
text_description = None
search_entry = None
filter_box = None
filter_month = None
filter_year = None
tree = None
status_label = None

# ---------------- DATENBANK VERBINDUNG ----------------
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="Jeder", 
            password="taskplaner123",        
            database="tasks"
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Datenbankfehler", f"Verbindung fehlgeschlagen: {err}")
        return None

def passwort_hashen(passwort):
    return hashlib.sha256(passwort.encode('utf-8')).hexdigest()

# ---------------- REGISTRIERUNG ----------------
def registrierung_fenster_oeffnen():
    def konto_erstellen():
        username = reg_user_entry.get().strip()
        password = reg_password_entry.get().strip()
        password_repeat = reg_password_repeat_entry.get().strip()

        if not username or not password or not password_repeat:
            messagebox.showwarning("Eingabefehler", "Bitte alle Felder ausfüllen.")
            return

        if password != password_repeat:
            messagebox.showerror("Fehler", "Die Passwörter stimmen nicht überein.")
            return

        conn = get_db_connection()
        if not conn:
            return

        cursor = conn.cursor()
        hashed_password = passwort_hashen(password)

        try:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                messagebox.showerror("Fehler", "Dieser Benutzername ist bereits vergeben.")
                return

            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            
            messagebox.showinfo("Erfolg", "Konto erfolgreich erstellt! Sie können sich jetzt einloggen.")
            reg_window.destroy()

        except mysql.connector.Error as err:
            messagebox.showerror("Fehler", f"Registrierung fehlgeschlagen: {err}")
        finally:
            cursor.close()
            conn.close()

    reg_window = tk.Toplevel(login_window)
    reg_window.title("Registrieren")
    reg_window.geometry("350x360")
    reg_window.configure(bg="white")
    reg_window.grab_set()

    tk.Label(reg_window, text="Konto erstellen", font=("Arial", 18, "bold"), bg="white", fg="#16A34A").pack(pady=15)
    tk.Label(reg_window, text="Benutzername", font=("Arial", 10, "bold"), bg="white").pack(anchor="w", padx=30)
    reg_user_entry = tk.Entry(reg_window, font=("Arial", 11), bg="#F8FAFC")
    reg_user_entry.pack(fill="x", padx=30, pady=(5, 10), ipady=4)
    tk.Label(reg_window, text="Passwort", font=("Arial", 10, "bold"), bg="white").pack(anchor="w", padx=30)
    reg_password_entry = tk.Entry(reg_window, font=("Arial", 11), show="*", bg="#F8FAFC")
    reg_password_entry.pack(fill="x", padx=30, pady=(5, 10), ipady=4)
    tk.Label(reg_window, text="Passwort wiederholen", font=("Arial", 10, "bold"), bg="white").pack(anchor="w", padx=30)
    reg_password_repeat_entry = tk.Entry(reg_window, font=("Arial", 11), show="*", bg="#F8FAFC")
    reg_password_repeat_entry.pack(fill="x", padx=30, pady=(5, 15), ipady=4)

    tk.Button(reg_window, text="Registrieren", command=konto_erstellen, font=("Arial", 11, "bold"), bg="#16A34A", fg="white", relief="flat", pady=6).pack(fill="x", padx=30, pady=10)

# ---------------- ANMELDUNG ----------------
def login_pruefen():
    global current_user_id, current_username
    username = login_user_entry.get().strip()
    password = login_password_entry.get().strip()

    if not username or not password:
        messagebox.showwarning("Eingabefehler", "Bitte Benutzername und Passwort eingeben.")
        return

    conn = get_db_connection()
    if not conn:
        return

    cursor = conn.cursor()
    hashed_password = passwort_hashen(password)
    
    try:
        cursor.execute("SELECT id, username FROM users WHERE username = %s AND password = %s", (username, hashed_password))
        user = cursor.fetchone()
        
        if user:
            current_user_id = user[0]
            current_username = user[1]
            
            for widget in login_window.winfo_children():
                widget.destroy()
                
            hauptanwendung_starten(login_window) 
        else:
            messagebox.showerror("Fehler", "Falscher Benutzername oder Passwort.")
    except mysql.connector.Error as err:
        messagebox.showerror("Fehler", f"Fehler bei Authentifizierung: {err}")
    finally:
        cursor.close()
        conn.close()

# ---------------- DATA STORAGE & ACTIONS ----------------
def daten_laden(search_term="", status_filter="Alle", sortieren_typ=None):
    if tree is None:
        return
        
    for row in tree.get_children():
        tree.delete(row)
        
    conn = get_db_connection()
    if not conn:
        return
        
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT Aufgabenummer, titel, fach, faelligkeitsdatum, prioritaet, status, beschreibung FROM aufgaben WHERE user_id = %s", (current_user_id,))

        rows = cursor.fetchall()
        
        manager = TaskManager()
        
        # Tasks erstellen
        for r in rows:
            db_id, titel, fach, datum, prio, status, beschreibung = r

            task = Task(
                title=titel,
                description=beschreibung or "",
                priority=prio,
                status=status,
                due_date=str(datum),
                subject=fach
            )
            
            task.db_id = db_id
            manager.add_task(task)

        # Sortierung
        if sortieren_typ == "datum":
            gefiltert = manager.sort_tasks_by_due_date()
        elif sortieren_typ == "prio":
            prio_reihenfolge = {"Hoch": 0, "Mittel": 1, "Niedrig": 2}
            gefiltert = sorted(manager.get_all_tasks(), key=lambda t: prio_reihenfolge.get(t.priority, 3))
        else:
            gefiltert = manager.get_all_tasks()

        # Status Filter
        if status_filter in ["Offen", "Erledigt"]:
            gefiltert = manager.filter_tasks_by_status(status_filter)
        elif status_filter == "Überfällig":
            gefiltert = manager.get_overdue_tasks()
        elif status_filter == "Heute fällig":
            gefiltert = manager.get_tasks_due_today()

        # Monat / Jahr Filter
        m_wahl = filter_month.get()
        j_wahl = filter_year.get()

        #prüfen, ob das Jahr oder der Monat im Text vorkommt
        if j_wahl != "Alle":
            gefiltert = [t for t in gefiltert if j_wahl in str(t.due_date)]
            
        if m_wahl != "Alle":
            # Fügt den Bindestrich hinzu (z.B. "-01-"), damit es genau den Monat trifft
            gefiltert = [t for t in gefiltert if f"-{m_wahl}-" in str(t.due_date)]

        # Suche
        if search_term:
            gefiltert = [t for t in gefiltert if search_term.lower() in t.title.lower() or search_term.lower() in t.description.lower()]

        # Anzeige in Tabelle
        for task in gefiltert:
            db_id = task.db_id
    
            sauberes_datum = str(task.due_date)[:10]
            tage_uebrig = task.days_left() if hasattr(task, 'days_left') else 0

            if task.status == "Erledigt":
                tage_text = "✓"
            elif tage_uebrig < 0:
                tage_text = f"Seit {-tage_uebrig} Tagen überfällig"
            elif tage_uebrig == 0:
                tage_text = "Heute fällig"
            else:
                tage_text = f"Noch {tage_uebrig} Tage"

            tree.insert("", "end", iid=db_id, values=(
                task.title,
                task.subject,
                sauberes_datum,
                task.priority,
                task.status,
                tage_text
            ))

        status_label.config(text="Daten erfolgreich geladen.")
    except Exception as err:
        status_label.config(text=f"Fehler beim Laden: {err}")
    finally:
        cursor.close()
        conn.close()

def aufgabe_hinzufuegen():
    titel = entry_title.get()
    fach = entry_subject.get()
    faelligkeitsdatum = entry_date.get()
    prioritaet = combo_priority.get()
    beschreibung = text_description.get("1.0", tk.END).strip()
    status = "Offen"

    if not titel or not fach or not faelligkeitsdatum:
        messagebox.showwarning("Eingabefehler", "Bitte Titel, Fach und Fälligkeitsdatum ausfüllen.")
        return

    try:
        Task.validate_due_date(faelligkeitsdatum)
    except ValueError as e:
        messagebox.showerror("Eingabefehler", str(e))
        return

    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO aufgaben (user_id, titel, fach, faelligkeitsdatum, prioritaet, status, beschreibung) VALUES (%s, %s, %s, %s, %s, %s, %s)", (current_user_id, titel, fach, faelligkeitsdatum, prioritaet, status, beschreibung))
        conn.commit()
        status_label.config(text="Aufgabe erfolgreich hinzugefügt.")
        felder_leeren()
        daten_laden(search_entry.get(), filter_box.get())
    except mysql.connector.Error as err:
        status_label.config(text=f"Fehler beim Hinzufügen: {err}")
    finally:
        cursor.close()
        conn.close()

def aufgabe_bearbeiten():
    ausgewaehlt = tree.selection()
    if not ausgewaehlt:
        messagebox.showwarning("Auswahl fehlt", "Bitte wählen Sie eine Aufgabe aus der Liste.")
        return
        
    aufgabe_id = ausgewaehlt[0]
    titel = entry_title.get()
    fach = entry_subject.get()
    faelligkeitsdatum = entry_date.get()
    prioritaet = combo_priority.get()
    beschreibung = text_description.get("1.0", tk.END).strip()

    if not titel or not fach or not faelligkeitsdatum:
        messagebox.showwarning("Eingabefehler", "Bitte Titel, Fach und Fälligkeitsdatum ausfüllen.")
        return

    try:
        Task.validate_due_date(faelligkeitsdatum)
    except ValueError as e:
        messagebox.showerror("Eingabefehler", str(e))
        return

    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE aufgaben SET titel = %s, fach = %s, faelligkeitsdatum = %s, prioritaet = %s, beschreibung = %s WHERE Aufgabenummer = %s AND user_id = %s", (titel, fach, faelligkeitsdatum, prioritaet, beschreibung, aufgabe_id, current_user_id))
        conn.commit()
        status_label.config(text="Aufgabe erfolgreich bearbeitet.")
        daten_laden(search_entry.get(), filter_box.get())
    except mysql.connector.Error as err:
        status_label.config(text=f"Fehler beim Bearbeiten: {err}")
    finally:
        cursor.close()
        conn.close()

def aufgabe_loeschen():
    ausgewaehlt = tree.selection()
    if not ausgewaehlt:
        messagebox.showwarning("Auswahl fehlt", "Bitte wählen Sie eine Aufgabe aus der Liste.")
        return
        
    aufgabe_id = ausgewaehlt[0]
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM aufgaben WHERE Aufgabenummer = %s AND user_id = %s", (aufgabe_id, current_user_id))
        conn.commit()
        status_label.config(text="Aufgabe erfolgreich gelöscht.")
        felder_leeren()
        daten_laden(search_entry.get(), filter_box.get())
    except mysql.connector.Error as err:
        status_label.config(text=f"Fehler beim Löschen: {err}")
    finally:
        cursor.close()
        conn.close()

def als_erledigt_markieren():
    ausgewaehlt = tree.selection()
    if not ausgewaehlt:
        messagebox.showwarning("Auswahl fehlt", "Bitte wählen Sie eine Aufgabe aus der Liste.")
        return
        
    aufgabe_id = ausgewaehlt[0] # Holt die reine ID aus dem Tuple
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE aufgaben SET status = 'Erledigt' WHERE Aufgabenummer = %s AND user_id = %s", (aufgabe_id, current_user_id))
        conn.commit()
        status_label.config(text="Aufgabe als erledigt markiert.")
        daten_laden(search_entry.get(), filter_box.get())
    except mysql.connector.Error as err:
        status_label.config(text=f"Fehler beim Aktualisieren: {err}")
    finally:
        cursor.close()
        conn.close()

def zeile_ausgewaehlt(event):
    ausgewaehlt = tree.selection()
    if not ausgewaehlt: 
        return
    aufgabe_id = ausgewaehlt[0] # Holt die exakte ID der ausgewählten Zeile
    
    conn = get_db_connection()
    if not conn: 
        return
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT titel, fach, faelligkeitsdatum, prioritaet, beschreibung FROM aufgaben WHERE Aufgabenummer = %s AND user_id = %s", (aufgabe_id, current_user_id))
        ergebnis = cursor.fetchone()
        
        if ergebnis:
            entry_title.delete(0, tk.END)
            entry_title.insert(0, ergebnis[0])
            entry_subject.delete(0, tk.END)
            entry_subject.insert(0, ergebnis[1])
            entry_date.delete(0, tk.END)
            entry_date.insert(0, str(ergebnis[2]))
            combo_priority.set(ergebnis[3])
            
            # BESCHREIBUNG DIREKT BEFÜLLEN (Ohne lästiges Aufteilen!)
            text_description.delete("1.0", tk.END)
            text_description.insert("1.0", ergebnis[4] if ergebnis[4] else "")
            
    except mysql.connector.Error as err:
        status_label.config(text=f"Fehler beim Laden der Details: {err}")
    finally:
        cursor.close()
        conn.close()

def felder_leeren():
    entry_title.delete(0, tk.END)
    entry_subject.delete(0, tk.END)
    entry_date.delete(0, tk.END)
    text_description.delete("1.0", tk.END)
    combo_priority.current(0)
    tree.selection_remove(tree.selection())

def manuell_sortieren_datum():
    # Übergibt das Signal für Datumssortierung an daten_laden
    daten_laden(search_entry.get(), filter_box.get(), sortieren_typ="datum")

def manuell_sortieren_prio():
    # Übergibt das Signal für Prioritätssortierung an daten_laden
    daten_laden(search_entry.get(), filter_box.get(), sortieren_typ="prio")

def filtern(event=None):
    daten_laden(search_entry.get(), filter_box.get())

# ---------------- OBERFLÄCHE HAUPTFENSTER ----------------
def hauptanwendung_starten(window):
    global entry_title, entry_subject, entry_date, combo_priority, text_description
    global search_entry, filter_box, filter_month, filter_year, tree, status_label

    window.title(f"Hausaufgaben-Manager - Eingeloggt als: {current_username}")
    window.geometry("1200x700")
    window.configure(bg="#EAF4FF")

    header = tk.Frame(window, bg="#1D4ED8", height=40)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(header, text="Hausaufgaben-Manager", font=("Arial", 11, "bold"), bg="#1D4ED8", fg="white").pack(side="left", padx=10, pady=5)

    main_frame = tk.Frame(window, bg="#EAF4FF")
    main_frame.pack(fill="both", expand=True, padx=15, pady=15)

    left_frame = tk.Frame(main_frame, bg="white", bd=2, relief="groove", width=350)
    left_frame.pack(side="left", fill="y", padx=(0, 15))
    left_frame.pack_propagate(False)

    tk.Label(left_frame, text="Neue Hausaufgabe", font=("Arial", 18, "bold"), bg="white", fg="#0F172A").pack(anchor="w", padx=15, pady=(15, 10))
    
    tk.Label(left_frame, text="Titel", font=("Arial", 11, "bold"), bg="white").pack(anchor="w", padx=15)
    entry_title = tk.Entry(left_frame, font=("Arial", 11), bg="#F8FAFC")
    entry_title.pack(fill="x", padx=15, pady=(5, 10), ipady=6)

    tk.Label(left_frame, text="Fach", font=("Arial", 11, "bold"), bg="white").pack(anchor="w", padx=15)
    entry_subject = tk.Entry(left_frame, font=("Arial", 11), bg="#F8FAFC")
    entry_subject.pack(fill="x", padx=15, pady=(5, 10), ipady=6)

    tk.Label(left_frame, text="Fälligkeitsdatum (YYYY-MM-DD)", font=("Arial", 11, "bold"), bg="white").pack(anchor="w", padx=15)
    entry_date = tk.Entry(left_frame, font=("Arial", 11), bg="#F8FAFC")
    entry_date.pack(fill="x", padx=15, pady=(5, 10), ipady=6)

    tk.Label(left_frame, text="Priorität", font=("Arial", 11, "bold"), bg="white").pack(anchor="w", padx=15)
    combo_priority = ttk.Combobox(left_frame, values=["Niedrig", "Mittel", "Hoch"], state="readonly", font=("Arial", 11))
    combo_priority.pack(fill="x", padx=15, pady=(5, 10), ipady=4)
    combo_priority.current(0)

    tk.Label(left_frame, text="Beschreibung", font=("Arial", 11, "bold"), bg="white").pack(anchor="w", padx=15)
    text_description = tk.Text(left_frame, height=4, font=("Arial", 11), bg="#F8FAFC")
    text_description.pack(fill="x", padx=15, pady=(5, 15))

    button_frame = tk.Frame(left_frame, bg="white")
    button_frame.pack(fill="x", padx=15, pady=(0, 15))

    tk.Button(button_frame, text="Hinzufügen", command=aufgabe_hinzufuegen, font=("Arial", 10, "bold"), bg="#16A34A", fg="white", relief="flat", pady=6).pack(fill="x", pady=3)
    tk.Button(button_frame, text="Bearbeiten", command=aufgabe_bearbeiten, font=("Arial", 10, "bold"), bg="#D97706", fg="white", relief="flat", pady=6).pack(fill="x", pady=3)
    tk.Button(button_frame, text="Löschen", command=aufgabe_loeschen, font=("Arial", 10, "bold"), bg="#DC2626", fg="white", relief="flat", pady=6).pack(fill="x", pady=3)
    tk.Button(button_frame, text="Als erledigt markieren", command=als_erledigt_markieren, font=("Arial", 10, "bold"), bg="#2563EB", fg="white", relief="flat", pady=6).pack(fill="x", pady=3)
    tk.Button(button_frame, text="Felder leeren", command=felder_leeren, font=("Arial", 10, "bold"), bg="#64748B", fg="white", relief="flat", pady=6).pack(fill="x", pady=3)

    right_frame = tk.Frame(main_frame, bg="white", bd=2, relief="groove")
    right_frame.pack(side="right", fill="both", expand=True)

    tk.Label(right_frame, text="Meine Aufgabenübersicht", font=("Arial", 18, "bold"), bg="white", fg="#0F172A").pack(anchor="w", padx=15, pady=(15, 10))

    control_frame = tk.Frame(right_frame, bg="white")
    control_frame.pack(fill="x", padx=15, pady=(0, 15))

    tk.Label(control_frame, text="Suche", font=("Arial", 11, "bold"), bg="white").grid(row=0, column=0, sticky="w")
    search_entry = tk.Entry(control_frame, font=("Arial", 11), bg="#F8FAFC")
    search_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10), ipady=6)
    search_entry.bind("<KeyRelease>", filtern)

    tk.Label(control_frame, text="Status-Filter", font=("Arial", 11, "bold"), bg="white").grid(row=0, column=1, sticky="w")
    filter_box = ttk.Combobox(control_frame, values=["Alle", "Offen", "Erledigt", "Überfällig", "Heute fällig"], state="readonly", font=("Arial", 11), width=12)
    filter_box.grid(row=1, column=1, sticky="w", padx=(0, 10), ipady=4)
    filter_box.current(0)
    filter_box.bind("<<ComboboxSelected>>", filtern)

    tk.Label(control_frame, text="Monat", font=("Arial", 11, "bold"), bg="white").grid(row=0, column=2, sticky="w")
    filter_month = ttk.Combobox(control_frame, values=["Alle", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"], state="readonly", font=("Arial", 11), width=6)
    filter_month.grid(row=1, column=2, sticky="w", padx=(0, 10), ipady=4)
    filter_month.current(0)
    filter_month.bind("<<ComboboxSelected>>", filtern)

    aktuelles_jahr = datetime.now().year
    jahres_liste = ["Alle"] + [str(jahr) for jahr in range(aktuelles_jahr, aktuelles_jahr + 6)]

    tk.Label(control_frame, text="Jahr", font=("Arial", 11, "bold"), bg="white").grid(row=0, column=3, sticky="w")
    filter_year = ttk.Combobox(control_frame, values=jahres_liste, state="readonly", font=("Arial", 11), width=8)
    filter_year.grid(row=1, column=3, sticky="w", ipady=4)
    filter_year.current(0)
    filter_year.bind("<<ComboboxSelected>>", filtern)

    control_frame.columnconfigure(0, weight=1)

    table_frame = tk.Frame(right_frame, bg="white")
    table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    columns = ("Titel", "Fach", "Fälligkeitsdatum", "Priorität", "Status", "Verbleibende Tage")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")

    for col in columns:
        if col == "Fälligkeitsdatum":
            # Startet die Datumssortierung bei Klick
            tree.heading(col, text=col, command=manuell_sortieren_datum)
        elif col == "Priorität":
            # Startet die Prioritätssortierung bei Klick
            tree.heading(col, text=col, command=manuell_sortieren_prio)
        else:
            tree.heading(col, text=col)
 
    tree.column("Titel", width=220)
    tree.column("Fach", width=120)
    tree.column("Fälligkeitsdatum", width=120)
    tree.column("Priorität", width=100)
    tree.column("Status", width=100)
    tree.column("Verbleibende Tage", width=140)

    tree.pack(side="left", fill="both", expand=True)
    tree.bind("<<TreeviewSelect>>", zeile_ausgewaehlt)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    status_frame = tk.Frame(window, bg="#DBEAFE", height=35)
    status_frame.pack(fill="x", side="bottom")
    status_frame.pack_propagate(False)

    status_label = tk.Label(status_frame, text="Bereit", font=("Arial", 10), bg="#DBEAFE", fg="#1E3A8A", anchor="w")
    status_label.pack(fill="x", padx=10, pady=7)

    daten_laden()

# ---------------- INITIALES LOGIN FENSTER ----------------
login_window = tk.Tk()
login_window.title("Login - Hausaufgaben-Manager")
login_window.geometry("350x340")
login_window.configure(bg="white")

tk.Label(login_window, text="Anmelden", font=("Arial", 18, "bold"), bg="white", fg="#1D4ED8").pack(pady=15)

tk.Label(login_window, text="Benutzername", font=("Arial", 10, "bold"), bg="white").pack(anchor="w", padx=30)
login_user_entry = tk.Entry(login_window, font=("Arial", 11), bg="#F8FAFC")
login_user_entry.pack(fill="x", padx=30, pady=(5, 10), ipady=4)

tk.Label(login_window, text="Passwort", font=("Arial", 10, "bold"), bg="white").pack(anchor="w", padx=30)
login_password_entry = tk.Entry(login_window, font=("Arial", 11), show="*", bg="#F8FAFC")
login_password_entry.pack(fill="x", padx=30, pady=(5, 15), ipady=4)

login_btn = tk.Button(login_window, text="Einloggen", command=login_pruefen, font=("Arial", 11, "bold"), bg="#1D4ED8", fg="white", relief="flat", pady=6)
login_btn.pack(fill="x", padx=30, pady=(10, 5))

register_btn = tk.Button(login_window, text="Neues Konto erstellen", command=registrierung_fenster_oeffnen, font=("Arial", 10, "bold"), bg="#16A34A", fg="white", relief="flat", pady=4)
register_btn.pack(fill="x", padx=30, pady=5)
login_window.mainloop()
