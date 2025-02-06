import os
import re
import webbrowser
import sqlite3
import tkinter as tk
from tkinter import *
from tkinter import messagebox, filedialog
from tkinter.ttk import Combobox
from tkinter import Button, Listbox, Frame
from tkinter import Menu
from tkinter import Toplevel, Label, Entry, Button
from tkinter import ttk, END
import csv
from PIL import Image, ImageTk
# from functools import partial

################################################################

# USERNAME = "hamed"
# PASSWORD = "4690"

# def verify_login(login_window, username_entry, password_entry):
#     entered_username = username_entry.get()
#     entered_password = password_entry.get()

#     if entered_username == USERNAME and entered_password == PASSWORD:
#         login_window.destroy()  
#         open_main_window() 
#     else:
#         messagebox.showerror("Login Failed", "Invalid username or password.")

# def open_main_window():
#     root.protocol("WM_DELETE_WINDOW", lambda: on_main_window_close(root))
#     root.mainloop()

# def on_login_window_close():
#     if messagebox.askyesno("Exit", "Are you sure you want to close the application?"):
#         exit()  

# def on_main_window_close(root):
#     if messagebox.askyesno("Exit", "Are you sure you want to close the application?"):
#         root.destroy()  

# def create_login_window():
#     login_window = tk.Tk()
#     login_window.title("Login")
#     login_window.geometry("300x200")
#     login_window.iconbitmap("MovieVault.ico")
#     login_window.bind("<Return>", lambda event: verify_login(login_window, username_entry, password_entry))

#     login_window.protocol("WM_DELETE_WINDOW", on_login_window_close)

#     tk.Label(login_window, text="Username:", font=("Segoe UI", 12)).pack(pady=5)
#     username_entry = tk.Entry(login_window, font=("Segoe UI", 12))
#     username_entry.pack(pady=5)

#     tk.Label(login_window, text="Password:", font=("Segoe UI", 12)).pack(pady=5)
#     password_entry = tk.Entry(login_window, show="*", font=("Segoe UI", 12))
#     password_entry.pack(pady=5)

#     login_button = tk.Button(
#         login_window, 
#         text="Login", 
#         command=partial(verify_login, login_window, username_entry, password_entry), 
#         font=("Segoe UI", 12)
#     )
#     login_button.pack(pady=10)

#     login_window.mainloop()

# create_login_window()

################################################################

undo_stack = []
redo_stack = []

current_table = 'Movies'
is_movie_database = True

def switch_database_table(event=None):
    global is_movie_database, current_table
    
    if current_table == 'Movies':
        current_table = 'Series'
        is_movie_database = False
    elif current_table == 'Series':
        current_table = 'Unwatched'
        is_movie_database = False  
    else:
        current_table = 'Movies'
        is_movie_database = True

    load_data()
    update_movie_count() 
    refresh_list(event) 
    # messagebox.showinfo("Switched", f"{current_table} Switched!")

################################################################

def load_data():
    movies_list.delete(0, END) 
    c.execute(f"SELECT name FROM {current_table}")
    data = c.fetchall()
    for item in data:
        movies_list.insert(END, item[0])

################################################################

movie_mapping = {}

def normalize_path(path):
    return path.replace("\\", "/")

################################################################

def scan_folder_from_path(path, genre):
    path = normalize_path(path)
    
    if not os.path.exists(path):
        messagebox.showerror("Error", "Path does not exist!")
        return

    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv')): 
                clean_name = os.path.basename(filename)
                directory_path = os.path.dirname(os.path.join(root, filename)) 

                add_movie(clean_name, genre, directory_path)

    all_movies = []  
    for root, dirs, files in os.walk(path):  
        for filename in files:
            if filename.endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv')): 
                clean_name = os.path.basename(filename)  
                all_movies.append(clean_name)  

    sorted_movies = sorted(all_movies)

    for movie in sorted_movies:
        add_movie(movie, genre)
    
    refresh_list(event)

################################################################

def clean_movie_name(movie_name):
    match = re.search(r"(.*?\.\d{4})", movie_name)
    if match:
        cleaned_name = match.group(1)
    else:
        cleaned_name = movie_name

    return cleaned_name

################################################################

def search_movie_in_google(movie_name):
    # refresh_list()
    if not movie_name:
        messagebox.showerror("Error", "No movie selected.")
        return

    if current_table == 'Series':
        match = re.search(r"^(.*?)\sS\d{2}E\d{2}", movie_name)
        if match:
            cleaned_name = match.group(1)
        else:
            cleaned_name = movie_name
    else:  
        cleaned_name = re.sub(r"[\.\-_]", " ", movie_name)
        match = re.search(r"(.*?\d{4})", cleaned_name)
        if match:
            cleaned_name = match.group(1)

    google_search_url = f"https://www.google.com/search?q={cleaned_name.strip()}"

    webbrowser.open(google_search_url)

################################################################

def search_movie_in_imdb(movie_name):
    # refresh_list()
    if not movie_name:
        messagebox.showerror("Error", "No item selected.")
        return

    if current_table == 'Series':
        match = re.search(r"^(.*?)\sS\d{2}E\d{2}", movie_name)
        if match:
            cleaned_name = match.group(1)
        else:
            cleaned_name = movie_name
    else:  
        cleaned_name = re.sub(r"[\.\-_]", " ", movie_name)
        match = re.search(r"(.*?\d{4})", cleaned_name)
        if match:
            cleaned_name = match.group(1)

    imdb_search_url = f"https://www.imdb.com/find?q={cleaned_name.strip()}"

    webbrowser.open(imdb_search_url)

################################################################

def IMDb_Top_250():
    search_url = f"https://www.imdb.com/chart/top/?ref_=nv_mv_250"
    webbrowser.open(search_url)

def Most_Popular_Movies():
    search_url = f"https://www.imdb.com/chart/moviemeter/?ref_=nv_mv_mpm"
    webbrowser.open(search_url)

def Top_250_TV_Shows():
    search_url = f"https://www.imdb.com/chart/toptv/?ref_=nv_tvv_250"
    webbrowser.open(search_url)

def Most_Popular_TV_Shows():
    search_url = f"https://www.imdb.com/chart/tvmeter/?ref_=nv_tvv_mptv"
    webbrowser.open(search_url)
    
################################################################

def get_selected_movie_name():
    try:
        selected_index = movies_list.curselection()[0]  
        selected_name = movies_list.get(selected_index)  
        return selected_name
    except IndexError:
        # messagebox.showerror("Error", "No movie selected.")
        return None

################################################################

def copy_to_clipboard(event):
    selected_items = movies_list.curselection()
    if not selected_items:
        messagebox.showwarning("Warning", "No movie selected to copy!")
        return

    movie_display_name = movies_list.get(selected_items[0])
    movie_original_name = movie_mapping.get(movie_display_name, movie_display_name)

    root.clipboard_clear()
    root.clipboard_append(movie_original_name)
    root.update()
    messagebox.showinfo("Copied", f"'{movie_original_name}' copied to clipboard!")
    
################################################################

def show_context_menu(event):
    try:
        selected_index = movies_list.nearest(event.y)  
        selected_movie = movies_list.get(selected_index)
        movie_name = selected_movie.split(" (")[0]  
        context_menu = Menu(root, tearoff=0)
        if current_table == "Unwatched":
            context_menu.add_command(label="Mark as Watched    ", command=lambda: toggle_movie(event), accelerator="Ctrl+W")
        if current_table == "Movies":
            context_menu.add_command(label="Mark as Unwatched    ", command=lambda: mark_as_unwatched(event), accelerator="Ctrl+E")
        context_menu.add_command(label="Copy Name to Clipboard    ", command=lambda: copy_to_clipboard(event), accelerator="Ctrl+C")
        context_menu.add_command(label="Delete Item", command=lambda: delete_movie_gui(event), accelerator="Del")
        context_menu.add_command(label="Search in Google", command=lambda: search_movie_in_google(get_selected_movie_name()))
        context_menu.add_command(label="Search in IMDb", command=lambda: search_movie_in_imdb(get_selected_movie_name()))
        context_menu.add_command(label="Quit", command=lambda: on_closing()) 

        context_menu.post(event.x_root, event.y_root)  
    except IndexError:
        pass

################################################################

root = Tk()
root.title("MovieVault")
# root.geometry("900x730")  
root.geometry("920x730") 
root.iconbitmap("MovieVault.ico") 
root.resizable(False, False)

################################################################

conn = sqlite3.connect('VAULT.db')
c = conn.cursor()

################################################################

def create_tables():
    c.execute('''CREATE TABLE IF NOT EXISTS Movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                genre TEXT,
                adr TEXT)''')
    conn.commit()
    try:
        c.execute("ALTER TABLE Movies ADD COLUMN adr TEXT")
    except sqlite3.OperationalError:
        pass

    c.execute('''CREATE TABLE IF NOT EXISTS Series (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                genre TEXT,
                adr TEXT)''')
    conn.commit()
    try:
        c.execute("ALTER TABLE Series ADD COLUMN adr TEXT")
    except sqlite3.OperationalError:
        pass

    c.execute('''CREATE TABLE IF NOT EXISTS Unwatched (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                genre TEXT,
                adr TEXT)''')
    conn.commit()
    try:
        c.execute("ALTER TABLE Unwatched ADD COLUMN adr TEXT")
    except sqlite3.OperationalError:
        pass

create_tables()

################################################################

def update_movie_count():
    c.execute(f"SELECT COUNT(*) FROM {current_table}")
    count = c.fetchone()[0]
    
    table_label1.config(text=f"Current Table:")
    table_label2.config(text=f"{current_table}")
    movie_count_label.config(text=f"|| Total Items: {count}")

################################################################

def add_movie(name, genre, adr=None):
    if adr is None: 
        adr = "Manual Input"
    try:
        c.execute(f"SELECT * FROM {current_table} WHERE name = ?", (name,))
        if c.fetchone():
            messagebox.showinfo("Error", "This item is already in the collection!")
            return False  

        c.execute(f"INSERT OR IGNORE INTO {current_table} (name, genre, adr) VALUES (?, ?, ?)", (name, genre, adr))
        conn.commit()
        movie_id = c.lastrowid
        undo_stack.append(("add", [(movie_id, name, genre, adr)]))
        redo_stack.clear()

        update_movie_count()  
        return True
    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred while adding the movie: {e}")
        return False

################################################################

def scan_folder(event, path, genre):
    try:
        new_movies = []
        for root, dirs, files in os.walk(path):  
            for filename in files:
                if filename.endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv')):
                    clean_name = os.path.basename(filename)  
                    directory_path = os.path.abspath(root)
                    c.execute(f"SELECT * FROM {current_table} WHERE name = ?", (clean_name,))
                    if c.fetchone():
                        continue
                    c.execute(f"INSERT INTO {current_table} (name, genre, adr) VALUES (?, ?, ?)", (clean_name, genre, directory_path))
                    conn.commit()
                    movie_id = c.lastrowid
                    new_movies.append((movie_id, clean_name, genre, directory_path))
        if new_movies:
            undo_stack.append(("add", new_movies))
            redo_stack.clear()
        refresh_list(event)
        update_movie_count()
    except Exception as e:
        messagebox.showerror("Folder Scan Error", f"An error occurred while scanning the folder: {e}")
    
################################################################

def search_movie(name):
    try:
        c.execute(f"SELECT * FROM {current_table} WHERE name LIKE ?", ('%' + name + '%',))
        movies = c.fetchall()
        return movies
    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred while searching for the movie: {e}")
        return []

################################################################

def show_all_movies():
    try:
        c.execute(f"SELECT * FROM {current_table}")
        movies = c.fetchall()
        return movies
    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred while fetching all movies: {e}")
        return []

################################################################

def show_movies_gui():
    try:
        c.execute(f"SELECT * FROM {current_table}")
        items = c.fetchall()

        items_sorted = sorted(items, key=lambda x: x[1].strip().lower()) 

        movies_list.delete(0, END)
        movie_mapping.clear()

        for item in items_sorted:
            name = item[1].strip()
            if '.' in name:
                parts = name.rsplit('.', 1)
                cleaned_name = re.sub(r"[\.\-_]", " ", parts[0]) + '.' + parts[1]  # جایگزینی ., - و _
            else:
                cleaned_name = re.sub(r"[\.\-_]", " ", name)
    
            movies_list.insert(END, f"{cleaned_name} ({item[2].strip()})") 
            movie_mapping[f"{cleaned_name} ({item[2].strip()})"] = name
    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred while displaying the movies: {e}")

################################################################

def add_movie_gui(event=None):
    movie_name = movie_name_entry.get()
    genre = genre_combobox.get()
    if not genre:
        genre = "General"
    if movie_name and genre:
        if add_movie(movie_name, genre, adr=None):  
            messagebox.showinfo("Success", f"Item '{movie_name}' added to {current_table.lower()}!")
            show_movies_gui() 
            update_movie_count()  
        else:
            messagebox.showinfo("Error", "This item is already in the Vault!")
    else:
        messagebox.showerror("Error", "Please fill in the movie name.")

################################################################

def bind_enter_key():
    movie_name_entry.bind("<Return>", add_movie_gui)

################################################################

def scan_folder_gui(event=None):
    folder_path = filedialog.askdirectory()  
    if folder_path:  
        genre = genre_combobox.get()  
        if not genre:  
            genre = "General"
        scan_folder(event, folder_path, genre) 
        show_movies_gui()

        if current_table == 'Unwatched':
            messagebox.showinfo("Success", f"{current_table} movies scanned and added!")  
        else:
            messagebox.showinfo("Success", f"{current_table} scanned and added!")  

    # else:
    #     messagebox.showerror("Error", "Please select a folder.")

################################################################

def scan_folder_from_entry(event=None):
    folder_path = path_entry.get() 
    if folder_path:  
        genre = genre_combobox.get()  
        if not genre: 
            genre = "General"
        scan_folder(event, folder_path, genre) 
        show_movies_gui()
        messagebox.showinfo("Success", "Movies scanned and added!")  
    else:
        messagebox.showerror("Error", "Please enter a valid path.")

################################################################

def delete_movie_gui(event=None):
    selected_items = movies_list.curselection() 
    if not selected_items:
        return

    deleted_movies = []
    for index in selected_items[::-1]:  
        movie_display_name = movies_list.get(index)  
        movie_original_name = movie_mapping.get(movie_display_name)
        if movie_original_name:
            c.execute(f"SELECT * FROM {current_table} WHERE name = ?", (movie_original_name,))
            movie_data = c.fetchone()
            if movie_data:
                deleted_movies.append(movie_data)  # movie_data = (id, name, genre, adr)
                c.execute(f"DELETE FROM {current_table} WHERE id = ?", (movie_data[0],))
    conn.commit()
    if deleted_movies:
        undo_stack.append(("remove", deleted_movies))
        redo_stack.clear()
    update_movie_count()
    show_movies_gui()

################################################################

def clear_list(event=None):
    result = messagebox.askquestion("Are you sure?", "Do you really want to reset the database?")
    if result == 'yes':
        c.execute(f"DELETE FROM {current_table}")  
        conn.commit()
        
        c.execute(f"DELETE FROM sqlite_sequence WHERE name='{current_table}'")
        conn.commit()

        c.execute("VACUUM") 
        conn.commit()
        
        movies_list.delete(0, END)

        if current_table == 'Unwatched':
            messagebox.showinfo("Success", f"All {current_table.lower()} movies have been deleted from the database and space has been optimized.")
        else:
            messagebox.showinfo("Success", f"All {current_table.lower()} have been deleted from the database and space has been optimized.")

    # else:
    #     messagebox.showinfo("Cancelled", "The operation has been cancelled.")
    
    update_movie_count()

################################################################

def dynamic_search(event):
    search_text = search_entry.get().strip()
    
    if not search_text:
        search_results_label.config(text="") 
        refresh_list(event)
        return

    search_text_cleaned = search_text.replace(" ", ".")  
    
    c.execute(f"SELECT * FROM {current_table} WHERE name LIKE ?", ('%' + search_text_cleaned + '%',))
    movies_cleaned = c.fetchall()
    
    c.execute(f"SELECT * FROM {current_table} WHERE name LIKE ?", ('%' + search_text + '%',))
    movies_original = c.fetchall()

    all_movies = {movie[1]: movie for movie in movies_cleaned + movies_original}

    movies_list.delete(0, END)
    for movie in all_movies.values():
        cleaned_name = re.sub(r"[\.\-_]", " ", movie[1])  
        movies_list.insert(END, f"{cleaned_name} ({movie[2]})")

    result_count = len(all_movies)
    if result_count > 0:
        search_results_label.config(text=f"Search Results: {result_count}")
    else:
        search_results_label.config(text="No results found.")

################################################################

group_search_popup_open = False

def group_search_popup(event=None):
    global group_search_popup_open

    if group_search_popup_open: 
        return  
    group_search_popup_open = True

    popup = Toplevel(root)
    popup.title("Group Search")
    popup.geometry("520x150")
    popup.iconbitmap("MovieVault.ico")
    popup.resizable(False, False)

    def on_close():
        global group_search_popup_open
        group_search_popup_open = False
        popup.destroy()

    popup.protocol("WM_DELETE_WINDOW", on_close)
    popup.bind("<Destroy>", lambda event: on_close())

    Label(popup, text="Please enter the names in order using the format: Name1, Name2, ...", font=("Segoe UI", 12)).pack(pady=5)

    group_search_entry = Entry(popup, width=60, font=("Segoe UI", 10))
    group_search_entry.pack(pady=5)

    def perform_group_search(event=None):
        search_text = group_search_entry.get().strip()
        if not search_text:
            search_results_label.config(text="")
            refresh_list(event)
            return

        movie_names = [name.strip() for name in search_text.split(",")]

        movies_list.delete(0, END)
        total_results = 0
        unique_results = set()

        for name in movie_names:
            file_format = ""
            if '.' in name and name.split(".")[-1].isalpha():
                parts = name.rsplit('.', 1) 
                name_cleaned = parts[0].replace(".", " ") 
                file_format = f".{parts[1]}" 
            else:
                name_cleaned = name.replace(".", " ") 

            match = re.search(r"(.*?\d{4})", name_cleaned)
            if match:
                name_cleaned = match.group(1)

            name_cleaned = name_cleaned.strip() + file_format
            name_parts = name_cleaned.split()

            search_query = " AND ".join([f"name LIKE ?"] * len(name_parts))
            params = [f"%{part}%" for part in name_parts]

            c.execute(f"SELECT * FROM {current_table} WHERE {search_query}", tuple(params))
            results = c.fetchall()

            for movie in results:
                cleaned_movie_name = f"{movie[1].replace('.', ' ')} ({movie[2]})"
                unique_results.add(cleaned_movie_name) 

        for result in sorted(unique_results):
            movies_list.insert(END, result)

        total_results = len(unique_results)
        if total_results > 0:
            search_results_label.config(text=f"Search Results: {total_results}")
        else:
            search_results_label.config(text="No results found.")

        popup.destroy()

    search_img = PhotoImage(file="search.png")  
    search_button = Button(popup, image=search_img, command=perform_group_search)
    search_button.pack(pady=10)  
    search_button.image = search_img  
    search_button.bind("<Enter>", on_enter_search_button)
    search_button.bind("<Leave>", on_leave_search_button)

    group_search_entry.bind("<Return>", lambda event: perform_group_search(event))  
    
################################################################

group_scan_popup_open = False

def group_scan_popup(event=None):
    global group_scan_popup_open

    if group_scan_popup_open:
        return  

    group_scan_popup_open = True

    popup = Toplevel(root)
    popup.title("Group Scan")
    popup.geometry("600x200") 
    popup.iconbitmap("MovieVault.ico")
    popup.resizable(False, False)

    def on_close():
        global group_scan_popup_open
        group_scan_popup_open = False
        popup.destroy()

    popup.protocol("WM_DELETE_WINDOW", on_close)

    Label(popup, text="Enter directory paths to scan (one per field, max 5):", font=("Segoe UI", 12)).pack(pady=10)

    entries_frame = Frame(popup)
    entries_frame.pack(fill="both", expand=True, padx=10, pady=5)

    entry_widgets = []

    def update_popup_size():
        current_height = 120 + len(entry_widgets) * 50
        popup.geometry(f"525x{current_height}")

    def add_entry_field(removable=True):
        if len(entry_widgets) >= 5:
            messagebox.showerror("Limit Reached", "Reached the maximum of 5 directories.")
            return

        frame = Frame(entries_frame)
        frame.pack(fill="x", pady=5)

        entry = Entry(frame, width=60, font=("Segoe UI", 10))
        entry.pack(side="left", padx=5)
        entry_widgets.append((entry, frame))

        add_img = PhotoImage(file="groupscanadd.png")  
        add_button = Button(frame, image=add_img, command=add_entry_field)
        add_button.image = add_img
        add_button.pack(side="left", padx=5)

        if removable:
            remove_img = PhotoImage(file="groupscanremove.png")  
            remove_button = Button(frame, image=remove_img, command=lambda: remove_entry(frame, entry))
            remove_button.image = remove_img
            remove_button.pack(side="left", padx=5)

        update_popup_size()

        entry.bind("<Return>", lambda event: perform_group_scan())

    def remove_entry(entry_frame, entry_widget):
        try:
            entry_widgets.remove((entry_widget, entry_frame))  
            entry_frame.destroy()  
            update_popup_size()  
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    for _ in range(1):
        add_entry_field(removable=False)

    def perform_group_scan():
        directories = [entry.get().strip() for entry, _ in entry_widgets if entry.get().strip()]
        genre = "General"

        if not directories:
            messagebox.showwarning("No Directories", "Please enter at least one directory to scan.")
            return

        successful_scans = 0  

        for directory in directories:
            if os.path.isdir(directory):  
                try:
                    scan_folder(event, directory, genre) 
                    successful_scans += 1
                except Exception as e:
                    messagebox.showerror("Scan Error", f"An error occurred while scanning '{directory}': {e}")
            else:
                messagebox.showerror("Invalid Directory", f"The path '{directory}' is not a valid directory.")
        
        if successful_scans > 0:
            on_close()
            refresh_list(event)
            messagebox.showinfo("Scan Complete", f"Group scan completed successfully for {successful_scans} directories!")
        else:
            messagebox.showwarning("No Scans Performed", "No valid directories were scanned.")

    scan_img = PhotoImage(file="groupscan.png")  
    scan_button = Button(popup, image=scan_img, command=perform_group_scan)
    scan_button.pack(pady=10)  
    scan_button.image = scan_img
    scan_button.bind("<Enter>", on_enter_search_button)
    scan_button.bind("<Leave>", on_leave_search_button)  

################################################################

def generate_report(event=None):
    c.execute(f"SELECT adr, name FROM {current_table}")
    movie_data = c.fetchall()

    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", f"Database_report_{current_table}.csv")

    c.execute(f"SELECT COUNT(*) FROM {current_table}")
    remaining_rows = c.fetchone()[0]
    if remaining_rows == 0:  
        messagebox.showerror("Error", "Database is Empty!")

    else:
        with open(desktop_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Address", "Name"])
            for movie in movie_data:
                writer.writerow(movie)
        messagebox.showinfo("Success", "Database report has been generated on your desktop!")

################################################################

def refresh_list(event=None):
    search_results_label.config(text=f"")
    show_movies_gui()
    update_movie_count()

################################################################

def on_closing():
    root.destroy()

################################################################

def on_enter_current_table1(event):
    table_label1.config(font=("Segoe UI", 11), bg="#f0f0f0", fg="#000000")
    event.widget.config(cursor="hand2")
def on_enter_current_table2(event):
    table_label2.config(font=("Segoe UI", 11, "bold"), bg="#000000", fg="#FFFFFF" )
    event.widget.config(cursor="hand2")
def on_enter_movie(event):
    title_label1.config(font=("Segoe UI", 12, "bold"), bg="#e0e0e0", fg="#3F48CC")
    event.widget.config(cursor="hand2")
def on_enter_genre(event):
    genre_label.config(font=("Segoe UI", 12, "bold"), bg="#e0e0e0", fg="#ED0000")
    event.widget.config(cursor="hand2")
def on_enter_search(event):
    search_label.config(font=("Segoe UI", 12, "bold"), bg="#e0e0e0", fg="#22B14C")
    event.widget.config(cursor="hand2")
def on_enter_path(event):
    path_label.config(font=("Segoe UI", 12, "bold"), bg="#e0e0e0", fg="#A349A4")
    event.widget.config(cursor="hand2")

################################################################

def on_enter_add(event):
    event.widget.config(cursor="hand2")
def on_leave_add(event):
    event.widget.config(cursor="arrow")

def on_enter_scan(event):
    event.widget.config(cursor="hand2")
def on_leave_scan(event):
    event.widget.config(cursor="arrow")

def on_enter_delete(event):
    event.widget.config(cursor="hand2")
def on_leave_delete(event):
    event.widget.config(cursor="arrow")

def on_enter_search_button(event):
    event.widget.config(cursor="hand2")
def on_leave_search_button(event):
    event.widget.config(cursor="arrow")

def on_enter_switch(event):
    event.widget.config(cursor="hand2")
def on_leave_switch(event):
    event.widget.config(cursor="arrow")

def on_enter_refresh(event):
    event.widget.config(cursor="hand2")
def on_leave_refresh(event):
    event.widget.config(cursor="arrow")

def on_enter_report(event):
    event.widget.config(cursor="hand2")
def on_leave_report(event):
    event.widget.config(cursor="arrow")

def on_enter_reset(event):
    event.widget.config(cursor="hand2")
def on_leave_reset(event):
    event.widget.config(cursor="arrow")

def on_enter_close(event):
    event.widget.config(cursor="hand2")
def on_leave_close(event):
    event.widget.config(cursor="arrow")

################################################################

def on_leave_current_table1(event):
    table_label1.config(font=("Segoe UI", 11), bg="#f0f0f0", fg="#333333")
    event.widget.config(cursor="arrow")
def on_leave_current_table2(event):
    table_label2.config(font=("Segoe UI", 11, "bold"), bg="#f0f0f0", fg="#333333")
    event.widget.config(cursor="arrow")
def on_leave_movie(event):
    title_label1.config(font=("Segoe UI", 12), bg="#f0f0f0", fg="#333333")
    event.widget.config(cursor="arrow")
def on_leave_genre(event):
    genre_label.config(font=("Segoe UI", 12), bg="#f0f0f0", fg="#333333")
    event.widget.config(cursor="arrow")
def on_leave_search(event):
    search_label.config(font=("Segoe UI", 12), bg="#f0f0f0", fg="#333333")
    event.widget.config(cursor="arrow")
def on_leave_path(event):
    path_label.config(font=("Segoe UI", 12), bg="#f0f0f0", fg="#333333")
    event.widget.config(cursor="arrow")
    
##############################################

popup_open = False

def show_popup(label_text, popup_text):
    global popup_open

    if popup_open:
        return

    popup_open = True

    popup = Toplevel(root)
    popup.title("Info")
    popup.geometry("400x270")
    popup.iconbitmap("MovieVault.ico")
    popup.resizable(False, False)
    popup.transient(root)

    def close_popup():
        global popup_open  
        popup_open = False
        popup.destroy()

    popup.protocol("WM_DELETE_WINDOW", close_popup)
    popup.bind("<Destroy>", lambda event: close_popup())

    info_label = tk.Label(popup, text=f"How to use?", font=("Segoe UI", 12, "bold"))
    info_label.pack(pady=10)

    detail_text = tk.Text(popup, wrap="word", font=("Segoe UI", 12), height=6, width=40)
    detail_text.insert("1.0", popup_text)
    detail_text.tag_configure("center", justify="center")
    detail_text.tag_configure("spacing", spacing1=4, spacing2=4, spacing3=4)
    detail_text.tag_add("center", "1.0", "end")
    detail_text.tag_add("spacing", "1.0", "end") 
    detail_text.config(state="disabled")
    detail_text.pack(pady=5)

    close_img = PhotoImage(file="close.png")
    close_button = Button(popup, image=close_img, command=lambda: close_popup())
    close_button.image = close_img
    close_button.bind("<Enter>", on_enter_close)
    close_button.bind("<Leave>", on_leave_close)      
    close_button.pack(pady=10)

##############################################

show_help_open = False

def show_help(event=None):
    global show_help_open
    if show_help_open:  
        return  
    show_help_open = True

    help_window = tk.Toplevel()
    help_window.title("Help")
    help_window.geometry("500x600")
    help_window.iconbitmap("MovieVault.ico")
    help_window.resizable(False, False)

    body_font = ("Segoe UI", 12)

    logo = tk.Label(help_window, text="Help Center", font=("Segoe UI", 18, "bold"), fg="#4CAF50")
    logo.pack(pady=5)

    def on_close():
        global show_help_open
        show_help_open = False
        help_window.destroy()

    help_window.protocol("WM_DELETE_WINDOW", on_close)  
    help_window.bind("<Destroy>", lambda event: on_close())

    notebook = ttk.Notebook(help_window)
    notebook.pack(fill="both", expand=True, padx=10, pady=5)

    overview_frame = ttk.Frame(notebook)
    notebook.add(overview_frame, text="Overview")
    overview_text = tk.Text(overview_frame, wrap="word", font=body_font, height=10)
    overview_text.insert("1.0", "Welcome to the Help Center!\n\nThis section is designed to guide you through the features and functionalities of this software, ensuring you can make the most out of its capabilities. Whether you're a first-time user or an experienced one, you'll find comprehensive information and step-by-step instructions tailored to your needs. Explore the tabs above to access detailed explanations and practical tips for each feature, including managing your movie database, scanning folders, customizing genres, and generating reports. If you're unsure where to begin, start here for an overview of the software's core functionalities. Should you need additional assistance, feel free to explore the FAQ section or contact support for further guidance. I am eagerly welcoming your ideas and opinions with open arms.\n\nBest regards\nHamed.Semsarian@gmail.com\nH.MathLogix@gmail.com\nhttps://github.com/MathLogix")
    
    overview_text.config(state="disabled")
    overview_text.pack(fill="both", expand=True, padx=10, pady=5)

    features_frame = ttk.Frame(notebook)
    notebook.add(features_frame, text="Tools & Features")
    features_text = tk.Text(features_frame, wrap="word", font=body_font, height=10)
    features_text.insert("1.0", "Key features:\n\n✅ Movie Collection Management: Easily add, remove, and categorize your movies\n\n✅ Search & Filter: Quickly find movies by name\n\n✅ Automatic Folder Scanning\n\n✅ Watched & Unwatched Lists: Organize your movies based on whether you've seen them.\n\n✅ Undo & Redo actions\n\n🚨 Note: The Undo & Redo feature does not support moving movies between the Watched and Unwatched lists. This action must be done manually to avoid inconsistencies in movie tracking.")
    features_text.config(state="disabled")
    features_text.pack(fill="both", expand=True, padx=10, pady=5)

    buttons_frame = ttk.Frame(notebook)
    notebook.add(buttons_frame, text="Buttons")
    buttons_text = tk.Text(buttons_frame, wrap="word", font=body_font, height=10)
    buttons_text.insert("1.0", 
        "1. Add Movie: Adds a new movie to the database.\n\n"
        "2. Scan Folder: Scans a folder for movie files and adds them to the database.\n\n"
        "3. Group Scan: Scans multiple directories and adds them to the database at the same time.\n\n"
        "4. Delete Movie: Deletes selected movie(s) from the database.\n\n"
        "5. Group Search: Allows searching many names at the same time.\n\n"
        "6. Switch Database: Switch between different database tables.\n\n"
        "7. Refresh List: Reloads the movie list from the database.\n\n"
        "8. Generate Report: Creates a detailed report of all movies in the database.\n\n"
        "9. Reset Database: Clears all data in the database.\n\n"
        "10. Search on IMDb: Instantly searches the selected movie or series name on IMDb, providing quick access to detailed information, ratings, and reviews."
    )
    
    buttons_text.config(state="disabled")
    buttons_text.pack(fill="both", expand=True, padx=10, pady=5)

    faq_frame = ttk.Frame(notebook)
    notebook.add(faq_frame, text="FAQ")

    faq_data = [
        ("1: What happens if I reset the database?", "1: All data will be deleted permanently."),
        ("2: Can I use a custom folder for scanning?", "2: Yes, you can choose any folder to scan for movie files."),
        ("3: Are subfolders included in the scan?", "3: Yes, all subfolders within the selected directory are fully included."),
        ("4: What file formats are recognized as movies?", "4: The software supports .mp4, .avi, .mkv, .mov, .wmv, and .flv."),
        ("5: Could a software bug delete or damage personal files?", "5: No, the software does not modify or delete personal files. It is solely designed to manage and organize movie file names."),
        ("6: Could a software bug corrupt the database?", "6: No, this is not possible. The software does not have the capability to delete or corrupt the database on its own. Even if you wish to delete the database, you must do so manually from your system outside the software."),
        ("7: How do I switch databases?", "7: Use the 'Switch Database' button in the menu or toolbar."),
        ("8: Can I scan multiple folders at once?", "8: Yes, the software allows you to scan multiple folders at once using the Group Scan feature. Simply click on the Group Scan button, enter the directories you wish to scan, and the software will process all of them in one go."),
        ("9: How are duplicate movie names handled?", "9: The software automatically detects duplicate movie names and prevents them from being added to the database."),
        ("10: What happens if I accidentally add a non-movie file?", "10: The software checks file extensions before adding them to the database. Non-movie files with unrecognized extensions will not be added."),
        ("11: Is there a size limit for the database?", "11: The software does not impose any specific size limit for the database. However, the capacity may depend on your system’s storage and performance."),
        ("12: Can I export my movie list to a file?", "12: Currently, the software allows exporting the movie list as a report (e.g., CSV), which can be saved and shared for further use."),
        ("13: How do I back up my database?", "13: You can manually back up the database by copying the database file (VAULT.db) to another secure location on your system or external storage."),
        ("14: What happens if I move or rename the database file?", "14: If the database file is moved or renamed, the software will not be able to locate it. To resolve this, ensure the database file is in the expected directory."),
        ("15: Is there a way to restore a deleted database?", "15: No, once the database file is manually deleted, it cannot be recovered by the software. It is recommended to back up your database regularly to avoid data loss.")
    ]

    def search_faq(event):
        search_text = faq_search_entry.get().lower()
        faq_textbox.config(state="normal")
        faq_textbox.delete("1.0", tk.END)
        for question, answer in faq_data:
            if search_text in question.lower() or search_text in answer.lower():
                faq_textbox.insert(tk.END, f"-Q{question}\n-A{answer}\n\n")
        faq_textbox.config(state="disabled")

    faq_search_label = tk.Label(faq_frame, text="Search FAQ:", font=("Segoe UI", 12))
    faq_search_label.pack(pady=0)
    faq_search_entry = tk.Entry(faq_frame, font=("Segoe UI", 10))
    faq_search_entry.pack(fill="x", padx=10, pady=5)
    faq_search_entry.bind("<KeyRelease>", search_faq)

    faq_textbox = tk.Text(faq_frame, font=("Segoe UI", 12), wrap="word", height=15)
    faq_textbox.pack(fill="both", expand=True, padx=10, pady=5)
    faq_textbox.config(state="normal")

    for question, answer in faq_data:
        faq_textbox.insert(tk.END, f"-Q{question}\n-A{answer}\n\n")

    faq_textbox.config(state="disabled")

    close_img = tk.PhotoImage(file="close.png")
    close_button = tk.Button(help_window, image=close_img, command=help_window.destroy)
    close_button.image = close_img
    close_button.pack(pady=10)
    close_button.bind("<Enter>", on_enter_search_button)
    close_button.bind("<Leave>", on_leave_search_button)

##############################################

def undo_action(event=None):
    global undo_stack, redo_stack

    if not undo_stack:
        messagebox.showinfo("Undo", "No more actions to undo.")
        return

    op, movies = undo_stack.pop()

    if op == "add":
        for movie in movies:
            movie_id, name, genre, adr = movie
            c.execute(f"DELETE FROM {current_table} WHERE id = ?", (movie_id,))
        redo_stack.append(("add", movies)) 

    elif op == "remove": 
        restored_movies = []
        for movie in movies:
            movie_id, name, genre, adr = movie
            c.execute(f"INSERT INTO {current_table} (id, name, genre, adr) VALUES (?, ?, ?, ?)", (movie_id, name, genre, adr))
            restored_movies.append((movie_id, name, genre, adr))
        redo_stack.append(("remove", restored_movies)) 
    conn.commit()
    refresh_list(event)
    update_movie_count()
    show_movies_gui()

##############################################

def redo_action(event=None):
    global undo_stack, redo_stack

    if not redo_stack:
        messagebox.showinfo("Redo", "No more actions to redo.")
        return

    op, movies = redo_stack.pop()

    if op == "add": 
        for movie in movies:
            movie_id, name, genre, adr = movie
            c.execute(f"DELETE FROM {current_table} WHERE id = ?", (movie_id,))
        undo_stack.append(("add", movies))

    elif op == "remove": 
        for movie in movies:
            movie_id, name, genre, adr = movie
            c.execute(f"DELETE FROM {current_table} WHERE id = ?", (movie_id,))
        undo_stack.append(("remove", movies))
    conn.commit()
    refresh_list(event)
    update_movie_count()
    show_movies_gui()

##############################################

def toggle_movie(event=None):
    if current_table != "Unwatched":
        messagebox.showwarning("Warning", "The 'Mark as Watched' feature is only available in the 'Unwatched' list.")
        return

    selected_items = movies_list.curselection()
    if not selected_items:
        messagebox.showwarning("Warning", "No movie selected to toggle!")
        return

    for index in selected_items[::-1]:
        movie_display_name = movies_list.get(index)
        movie_original_name = movie_mapping.get(movie_display_name, movie_display_name)

        c.execute(f"SELECT * FROM Unwatched WHERE name = ?", (movie_original_name,))
        movie_data = c.fetchone()

        if movie_data:
            c.execute("INSERT INTO Movies (name, genre, adr) VALUES (?, ?, ?)", (movie_data[1], movie_data[2], movie_data[3]))
            c.execute("DELETE FROM Unwatched WHERE id = ?", (movie_data[0],))

    conn.commit()
    # messagebox.showinfo("Success", "Selected movies have been marked as watched and moved to the main list.")

    update_movie_count()
    refresh_list()

##############################################

def mark_as_unwatched(event=None):
    if current_table != "Movies":
        messagebox.showwarning("Warning", "The 'Mark as Unwatched' feature is only available in the 'Movies' list.")
        return

    selected_items = movies_list.curselection()
    if not selected_items:
        messagebox.showwarning("Warning", "No movie selected to toggle!")
        return

    for index in selected_items[::-1]:  
        movie_display_name = movies_list.get(index)
        movie_original_name = movie_mapping.get(movie_display_name, movie_display_name)

        c.execute(f"SELECT * FROM Movies WHERE name = ?", (movie_original_name,))
        movie_data = c.fetchone()

        if movie_data:
            c.execute("INSERT INTO Unwatched (name, genre, adr) VALUES (?, ?, ?)", (movie_data[1], movie_data[2], movie_data[3]))
            c.execute("DELETE FROM Movies WHERE id = ?", (movie_data[0],))

    conn.commit()
    # messagebox.showinfo("Success", "Selected movies have been marked as unwatched and moved back to the 'Unwatched' list.")

    update_movie_count()
    refresh_list()

##############################################

def restore_backup(event=None):
    backup_file = filedialog.askopenfilename(title="Select Backup File", filetypes=[("SQLite files", "*.db"), ("All files", "*.*")])
    
    if not backup_file:
        return

    conn_current = sqlite3.connect('VAULT.db')
    c_current = conn_current.cursor()

    try:
        conn_backup = sqlite3.connect(backup_file) 
        c_backup = conn_backup.cursor()

        c_current.execute("SELECT name FROM sqlite_master WHERE type='table';")
        current_tables = set(row[0] for row in c_current.fetchall()) 

        c_backup.execute("SELECT name FROM sqlite_master WHERE type='table';")
        backup_tables = set(row[0] for row in c_backup.fetchall())  

        if current_tables != backup_tables:
            messagebox.showerror("Error", "Backup database structure does not match current database structure.")
            return
        
        c_current.execute("SELECT MAX(id) FROM Movies")
        max_id_current = c_current.fetchone()[0] or 0

        for table in backup_tables:
            c_backup.execute(f"SELECT * FROM {table}")
            rows = c_backup.fetchall()

            for row in rows:
                new_id = max_id_current + 1
                new_row = (new_id,) + row[1:]  

                placeholders = ', '.join(['?'] * len(new_row)) 
                c_current.execute(f"INSERT OR IGNORE INTO {table} VALUES ({placeholders})", new_row)

                max_id_current += 1

        conn_current.commit()  
        
        show_movies_gui()
        refresh_list(event)
        update_movie_count()
        messagebox.showinfo("Success", "Backup restored successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while restoring backup: {e}")
    
    finally:
        conn_backup.close()
        conn_current.close()

##############################################

menubar = tk.Menu(root)

file_menu = tk.Menu(menubar, tearoff=0)           
file_menu.add_command(label="Directory Scan", command=scan_folder_gui, accelerator="Ctrl+S")
file_menu.add_command(label="Group Scan", command=group_scan_popup, accelerator="Ctrl+G")
file_menu.add_command(label="Group Search", command=group_search_popup, accelerator="Ctrl+F")
file_menu.add_command(label="Generate Report", command=generate_report, accelerator="Ctrl+R")
file_menu.add_command(label="Restore Backup", command=restore_backup, accelerator="Ctrl+B")
file_menu.add_command(label="Switch Database", command=switch_database_table, accelerator="Ctrl+Shft")
file_menu.add_command(label="Refresh List", command=refresh_list, accelerator="F5")
file_menu.add_command(label="Reset Database", command=clear_list, accelerator="F12")
file_menu.add_command(label="IMDb: Top 250 Movies", command=IMDb_Top_250)
file_menu.add_command(label="IMDb: Most Popular Movies", command=Most_Popular_Movies)
file_menu.add_command(label="IMDb: Top 250 TV Shows", command=Top_250_TV_Shows)
file_menu.add_command(label="IMDb: Most Popular TV Shows", command=Most_Popular_TV_Shows)
file_menu.add_command(label="Exit", command=root.destroy, accelerator="Alt+F4")
menubar.add_cascade(label="Menu", menu=file_menu)

menu2 = tk.Menu(menubar, tearoff=0)
menu2.add_command(label="Mark as Watched    ", command=toggle_movie, accelerator="Ctrl+W")
menu2.add_command(label="Mark as Unwatched    ", command=mark_as_unwatched, accelerator="Ctrl+E")
menu2.add_command(label="Undo    ", command=undo_action, accelerator="Ctrl+Z")
menu2.add_command(label="Redo    ", command=redo_action, accelerator="Ctrl+Y")
menu2.add_command(label="Delete    ", command=delete_movie_gui, accelerator="Del")
menubar.add_cascade(label="Tools", menu=menu2)

help_menu = tk.Menu(menubar, tearoff=0)
help_menu.add_command(label="Help    ", command=show_help, accelerator="F8")
menubar.add_cascade(label="Help", menu=help_menu)

root.config(menu=menubar)

################################################################

main_frame = Frame(root)
main_frame.pack(expand=True, fill=tk.BOTH)

left_frame = Frame(main_frame)
left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

right_frame = Frame(main_frame)
right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

movie_icon = Image.open("add2.png").resize((40, 40))  
movie_icon = ImageTk.PhotoImage(movie_icon)
title_label1 = tk.Label(left_frame, text="Add a New Movie/ Serie                              ", font=("Segoe UI", 12), height=40, compound="right", image=movie_icon, bg="#f0f0f0", fg="#333333")
title_label1.pack(pady=10)
title_label1.bind("<Enter>", on_enter_movie)
title_label1.bind("<Leave>", on_leave_movie)
title_label1.bind("<Button-1>", lambda event: show_popup("Add a New Movie/Serie", f" Add a new movie or series to your collection:\n1. Enter the name\n2. Choose the Genre from below dropdown box\n3. Press Enter or the Plus button"))

movie_name_entry = Entry(left_frame, width=50, font=("Segoe UI", 10))
movie_name_entry.pack(pady=5)

genre_icon = Image.open("genre.png").resize((40, 40))  
genre_icon = ImageTk.PhotoImage(genre_icon)
genre_label = tk.Label(left_frame, text="Genre                                                                 ", font=("Segoe UI", 12), height=40, compound="right", image=genre_icon, bg="#f0f0f0", fg="#333333")
genre_label.pack(pady=10)
genre_label.bind("<Enter>", on_enter_genre)
genre_label.bind("<Leave>", on_leave_genre)
genre_label.bind("<Button-1>", lambda event: show_popup("Genre", "Choose the Genre for your movie or series from\n the dropdown box. You can freely add any text in the Genre box."))

genre_combobox = Combobox(left_frame, width=47, font=("Segoe UI", 10))
genre_combobox['values'] = ["General", "Action", "Crime", "Drama", "Comedy", "Horror", "Adventure", "Romantic", "Science Fiction", "Fantasy", "Documentary"]
genre_combobox.set("General")
genre_combobox.pack(pady=5)

search_icon = Image.open("search2.png").resize((40, 40))  
search_icon = ImageTk.PhotoImage(search_icon)
search_label = tk.Label(right_frame, text="Search Items                                                    ", font=("Segoe UI", 12), height=40, compound="right", image=search_icon, bg="#f0f0f0", fg="#333333")
search_label.pack(pady=10)
search_label.bind("<Enter>", on_enter_search)
search_label.bind("<Leave>", on_leave_search)
search_label.bind("<Button-1>", lambda event: show_popup("Search Items", "Search for movies or series in your collection\nusing keywords."))
search_entry = Entry(right_frame, width=50, font=("Segoe UI", 10))
search_entry.pack(pady=5)
search_entry.bind("<KeyRelease>", dynamic_search)

path_icon = Image.open("path.png").resize((40, 40))  
path_icon = ImageTk.PhotoImage(path_icon)
path_label = Label(right_frame, text="Enter Folder Path to Scan                             ", font=("Segoe UI", 12), height=40, compound="right", image=path_icon, bg="#f0f0f0", fg="#333333")
path_label.pack(pady=10)
path_label.bind("<Enter>", on_enter_path)
path_label.bind("<Leave>", on_leave_path)
path_label.bind("<Button-1>", lambda event: show_popup("Enter Folder Path", " Provide the folder path where your movies or series are stored. Right click on the desired file or directory and use the {Copy as path} option. Please remember not to attempt typing the address."))
path_entry = Entry(right_frame, width=50, font=("Segoe UI", 10))
path_entry.pack(pady=5)
path_entry.bind("<KeyRelease>", lambda event: scan_folder_from_entry(event))

search_results_label = Label(root, text="", font=("Segoe UI", 12, "bold"), fg="#1E9C43")
search_results_label.pack(pady=5)

list_frame = Frame(root)
list_frame.pack(pady=5)

movies_list = Listbox(list_frame, selectmode="extended", width=149, height=25)
movies_list.grid(row=0, column=0, sticky="ns")
scrollbar = Scrollbar(list_frame, orient=VERTICAL, command=movies_list.yview)
movies_list.configure(yscrollcommand=scrollbar.set)
movies_list.bind("<Button-3>", show_context_menu)
movies_list.bind("<Double-Button-1>", lambda event: toggle_movie(event))
scrollbar.grid(row=0, column=1, sticky="ns")

add_movie_img = PhotoImage(file="add.png")
add_movie_button = Button(root, image=add_movie_img, command=add_movie_gui)
add_movie_button.image = add_movie_img 
add_movie_button.pack(side=LEFT, padx=0)
add_movie_button.bind("<Enter>", on_enter_add)
add_movie_button.bind("<Leave>", on_leave_add)

scan_button_img = PhotoImage(file="scan.png")
scan_folder_button = Button(root, image=scan_button_img, command=scan_folder_gui)
scan_folder_button.image = scan_button_img
scan_folder_button.pack(side=LEFT, padx=0)
scan_folder_button.bind("<Enter>", on_enter_scan)
scan_folder_button.bind("<Leave>", on_leave_scan)

group_scan_img = PhotoImage(file="groupscan.png")
group_scan_button = Button(root, image=group_scan_img, command=group_scan_popup)
group_scan_button.image = group_scan_img
group_scan_button.pack(side=LEFT, padx=0)
group_scan_button.bind("<Enter>", on_enter_search_button)
group_scan_button.bind("<Leave>", on_leave_search_button)

delete_button_img = PhotoImage(file="delete.png")
delete_button = Button(root, image=delete_button_img, command=delete_movie_gui)
delete_button.image = delete_button_img
delete_button.pack(side=LEFT, padx=0)
delete_button.bind("<Enter>", on_enter_delete)
delete_button.bind("<Leave>", on_leave_delete)

search_img = PhotoImage(file="search.png")
search_button = Button(root, image=search_img, command=group_search_popup)
search_button.image = search_img
search_button.pack(side=LEFT, padx=0)
search_button.bind("<Enter>", on_enter_search_button)
search_button.bind("<Leave>", on_leave_search_button)

switch_img = PhotoImage(file="switch.png")
switch_button = Button(root, image=switch_img, command=switch_database_table)
switch_button.image = switch_img
switch_button.pack(side=LEFT, padx=0)
switch_button.bind("<Enter>", on_enter_switch)
switch_button.bind("<Leave>", on_leave_switch)

refresh_img = PhotoImage(file="refresh.png")  
refresh_button = Button(root, image=refresh_img, command=refresh_list)
refresh_button.image = refresh_img  
refresh_button.pack(side=LEFT, padx=0) 
refresh_button.bind("<Enter>", on_enter_refresh)
refresh_button.bind("<Leave>", on_leave_refresh)

report_button_img = PhotoImage(file="report.png")
report_button = Button(root, image=report_button_img, command=generate_report)
report_button.image = report_button_img
report_button.pack(side=LEFT, padx=0)
report_button.bind("<Enter>", on_enter_report)
report_button.bind("<Leave>", on_leave_report)

reset_img = PhotoImage(file="reset.png")
reset_button = Button(root, image=reset_img, command=clear_list)
reset_button.image = reset_img
reset_button.pack(side=LEFT, padx=0)
reset_button.bind("<Enter>", on_enter_reset)
reset_button.bind("<Leave>", on_leave_reset)

imdb_img = PhotoImage(file="imdb.png")
imdb_button = Button(root, image=imdb_img, command=lambda: search_movie_in_imdb(get_selected_movie_name()))
imdb_button.image = imdb_img 
imdb_button.pack(side=LEFT, padx=0)
imdb_button.bind("<Enter>", on_enter_add)
imdb_button.bind("<Leave>", on_leave_add)

# movie_count_label = tk.Label(root, text=f"Total Items: ", font=("Segoe UI", 12))
# movie_count_label.pack(side=tk.LEFT, padx=5)

table_label0 = tk.Label(root, text="", font=("Segoe UI", 11))
table_label0.pack(side=tk.LEFT, padx=5)

table_label1 = tk.Label(root, text="", font=("Segoe UI", 11))
table_label1.pack(side=tk.LEFT, padx=0)
table_label1.bind("<Enter>", on_enter_current_table1)
table_label1.bind("<Leave>", on_leave_current_table1)
table_label1.bind("<Button-1>", lambda event: switch_database_table(event))

table_label2 = tk.Label(root, text="", font=("Segoe UI", 11, "bold"))
table_label2.pack(side=tk.LEFT, padx=0)
table_label2.bind("<Enter>", on_enter_current_table2)
table_label2.bind("<Leave>", on_leave_current_table2)
table_label2.bind("<Button-1>", lambda event: switch_database_table(event))

movie_count_label = tk.Label(root, text="", font=("Segoe UI", 11))
movie_count_label.pack(side=tk.LEFT, padx=0)

root.bind("<Delete>", lambda event: delete_movie_gui(event))
root.bind("<Control-w>", lambda event: toggle_movie(event))
root.bind("<Control-e>", lambda event: mark_as_unwatched(event))
root.bind("<Control-c>", lambda event: copy_to_clipboard(event))
root.bind("<Control-z>", lambda event: undo_action(event))
root.bind("<Control-y>", lambda event: redo_action(event))
root.bind("<Control-Shift_L>", lambda event: switch_database_table(event))
root.bind("<Control-r>", lambda event: generate_report(event))
root.bind("<Control-b>", lambda event: restore_backup(event))
root.bind("<F5>", lambda event: refresh_list(event))
root.bind("<F12>", lambda event: clear_list(event))
root.bind("<Control-s>", lambda event: scan_folder_gui(event))
root.bind("<Control-g>", lambda event: group_scan_popup(event))
root.bind("<Control-f>", lambda event: group_search_popup(event))
root.bind("<F8>", lambda event: show_help(event))

update_movie_count()

bind_enter_key()
show_movies_gui()
update_movie_count() 

root.focus_set()
root.mainloop()
conn.close()