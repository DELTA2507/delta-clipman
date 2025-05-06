import os
import pyperclip
import threading
import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw

clipboard_history = []
last_clipboard = ""

root = ttk.Window(themename="darkly")
root.title("ClipMan: Clipboard Manager")
root.iconbitmap("ClipManpy.ico")
root.geometry("500x700")

# Layout containers
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

label = ttk.Label(root, text="Welcome to ClipMan!", font=("Arial", 20, "bold"))
label.pack(pady=20)

status_label = ttk.Label(root, text="Waiting for clipboard...", wraplength=380, justify="left", font=("Arial", 14))
status_label.pack(pady=20)

# Frame for pinned items
pinned_frame = ttk.Labelframe(root, text="Pinned Items")
pinned_frame.pack(pady=10, padx=50, fill="both", expand=True)

# Replace ttk.Listbox with tk.Listbox
pinned_listbox = tk.Listbox(pinned_frame, selectmode="single", font=("Segoe UI", 11))
pinned_listbox.pack(side="left", fill="both", expand=True)

pinned_scrollbar = tk.Scrollbar(pinned_frame, command=pinned_listbox.yview)
pinned_scrollbar.pack(side="right", fill="y")
pinned_listbox.config(yscrollcommand=pinned_scrollbar.set)

search_var = ttk.StringVar()

def filter_list(*args):
    query = search_var.get().lower()
    listbox.delete(0, "end")
    for item in pinned_listbox.get(0, "end"):
        listbox.insert("end", item)
    for item in reversed(clipboard_history):
        if query in item.lower() and item not in pinned_listbox.get(0, "end"):
            listbox.insert("end", item)

search_var.trace_add("write", filter_list)

search_entry = ttk.Entry(root, textvariable=search_var, font=("Arial", 12), width=50)
search_entry.pack(pady=(10, 0))

list_frame = ttk.Labelframe(root, text="Clipboard History")
list_frame.pack(pady=10, padx=50, fill="both", expand=True)

# Replace ttk.Listbox with tk.Listbox
scrollbar = tk.Scrollbar(list_frame)
scrollbar.pack(side="right", fill="y")

listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Segoe UI", 11))
listbox.pack(side="left", fill="both", expand=True)
scrollbar.config(command=listbox.yview)

def save_history():
    with open("history.txt", "w", encoding="utf-8") as f:
        for item in clipboard_history:
            f.write(item.replace("\n", "⏎") + "\n")

def load_history():
    if not os.path.exists("history.txt"): return
    with open("history.txt", "r", encoding="utf-8") as f:
        for line in f:
            item = line.strip().replace("⏎", "\n")
            clipboard_history.append(item)
            listbox.insert("end", item)

def update_display(text):
    status_label.config(text=f"Latest: {text[:50]}")
    listbox.insert(0, text)

def check_clipboard():
    global last_clipboard
    current = pyperclip.paste()
    if current != last_clipboard and current.strip() != "":
        last_clipboard = current
        clipboard_history.append(current)
        update_display(current)
    root.after(1000, check_clipboard)

def on_select(event):
    selected = listbox.curselection()
    if selected:
        value = listbox.get(selected[0])
        pyperclip.copy(value)
        status_label.config(text=f"Copied back: {value[:50]}")

def pin_selected():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        item = listbox.get(index)
        if item not in pinned_listbox.get(0, "end"):
            pinned_listbox.insert("end", item)
            status_label.config(text=f"Pinned: {item[:50]}")

def delete_selected():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        item = listbox.get(index)
        listbox.delete(index)
        if item in clipboard_history:
            clipboard_history.remove(item)
        if item in pinned_listbox.get(0, "end"):
            pinned_listbox.delete(pinned_listbox.get(0, "end").index(item))
        status_label.config(text="Entry deleted.")

def clear_all():
    clipboard_history.clear()
    listbox.delete(0, "end")
    pinned_listbox.delete(0, "end")
    status_label.config(text="History cleared.")

def create_image():
    image = Image.new("RGBA", (64, 64), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 64, 64), fill="blue")
    return image

def show_window(icon, item):
    root.deiconify()
    root.lift()

def on_quit(icon, item):
    save_history()
    icon.stop()
    root.quit()

def hide_window():
    root.withdraw()

def setup_tray_icon():
    icon_image = create_image()
    menu = Menu(MenuItem("Show", show_window), MenuItem("Quit", on_quit))
    global icon
    icon = Icon("ClipManpy", icon_image, menu=menu)
    icon_thread = threading.Thread(target=icon.run)
    icon_thread.daemon = True
    icon_thread.start()

# Context menu setup
def show_context_menu(event):
    index = listbox.nearest(event.y)
    listbox.selection_clear(0, "end")
    listbox.selection_set(index)
    context_menu.tk_popup(event.x_root, event.y_root)

context_menu = ttk.Menu(root, tearoff=0)
context_menu.add_command(label="Pin", command=pin_selected)
context_menu.add_command(label="Delete", command=delete_selected)
listbox.bind("<Button-3>", show_context_menu)
listbox.bind("<<ListboxSelect>>", on_select)

# Buttons
ttk.Button(button_frame, text="Clear All", command=clear_all, bootstyle="danger").grid(row=0, column=0, padx=10)
ttk.Button(root, text="Close", command=lambda:[save_history(), root.quit()], bootstyle="secondary").pack(pady=20)

root.protocol("WM_DELETE_WINDOW", hide_window)
load_history()
check_clipboard()
setup_tray_icon()
root.mainloop()
