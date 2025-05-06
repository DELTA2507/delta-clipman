import os
import tkinter as tk
import pyperclip
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
import threading

clipboard_history = []
pinned_items = []
last_clipboard = ""

def pin_selected():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        item = listbox.get(index)
        if item not in pinned_items:
            pinned_items.append(item)
            pinned_listbox.insert("end", item)
            label.config(text=f"Pinned: {item[:50]}")
            filter_list()

def filter_list(*args):
    query = search_var.get().lower()
    listbox.delete(0, "end")

    for item in pinned_items:
        if query in item.lower():
            listbox.insert("end", item)

    for item in reversed(clipboard_history):
        if query in item.lower() and item not in pinned_items:
            listbox.insert("end", item)

def save_history():
    with open("history.txt", "w", encoding="utf-8") as f:
        for item in clipboard_history:
            f.write(item.replace("\n", "⏎") + "\n")

def load_history():
    if not os.path.exists("history.txt"):
        return
    with open("history.txt", "r", encoding="utf-8") as f:
        for line in f:
            item = line.strip().replace("⏎", "\n")
            if item not in clipboard_history:
                clipboard_history.append(item)


def quit_app():
    save_history()
    icon.visible = False
    icon.stop()
    root.destroy()

def clear_all():
    clipboard_history.clear()
    pinned_items.clear()
    listbox.delete(0, "end")
    pinned_listbox.delete(0, "end")
    label.config(text="History cleared.")

def delete_selected():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        item = listbox.get(index)
        listbox.delete(index)
        if item in clipboard_history:
            clipboard_history.remove(item)
        if item in pinned_items:
            pinned_items.remove(item)
            pinned_listbox.delete(0, "end")
            for pinned_item in pinned_items:
                pinned_listbox.insert("end", pinned_item)
        label.config(text="Entry deleted.")

def check_clipboard():
    global last_clipboard
    current = pyperclip.paste()
    if current != last_clipboard and current.strip() != "" and current not in clipboard_history:
        last_clipboard = current
        clipboard_history.append(current)
        if len(clipboard_history) > 200:
            clipboard_history.pop(0)
        update_display(current)
    root.after(1000, check_clipboard)

def update_display(text):
    label.config(text=f"Latest:{text[:50]}")
    filter_list()

def on_select(event):
    selected = listbox.curselection()
    if selected:
        value = listbox.get(selected[0])
        pyperclip.copy(value)
        label.config(text=f"Copied back: {value[:50]}")

def create_image():
    width, height = 64, 64
    image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, height), fill="blue")
    return image

def on_quit(icon, item):
    quit_app()

def setup_tray_icon():
    icon_image = Image.open("ClipManpy.ico")

    menu = Menu(
        MenuItem("Show", show_window),
        MenuItem("Quit", on_quit)
    )

    global icon
    icon = Icon("ClipMan", icon_image, menu=menu)

    icon_thread = threading.Thread(target=icon.run)
    icon_thread.daemon = True
    icon_thread.start()

def show_window(icon=None, item=None):
    root.deiconify()
    root.lift()

def hide_window():
    root.withdraw()

root = tk.Tk()
root.title("ClipMan: Clipboard Manager")
try:
    root.iconbitmap("ClipManpy.ico")
except:
    pass
root.geometry("500x800")
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

label = tk.Label(root, text="Waiting for clipboard...", wraplength=380, justify="left", font=("Arial", 14))
label.pack(pady=20)

pinned_frame = tk.Frame(root)
pinned_frame.pack(pady=10, fill="both", expand=True)

pinned_label = tk.Label(pinned_frame, text="Pinned Items", font=("Arial", 14, "bold"))
pinned_label.pack()

pinned_listbox = tk.Listbox(pinned_frame, font=("Courier", 12), selectmode="single")
pinned_listbox.pack(side="left", fill="both", expand=True)

pinned_scrollbar = tk.Scrollbar(pinned_frame, command=pinned_listbox.yview)
pinned_scrollbar.pack(side="right", fill="y")
pinned_listbox.config(yscrollcommand=pinned_scrollbar.set)

pin_button = tk.Button(button_frame, text="Pin Selected", command=pin_selected)
pin_button.grid(row=0, column=2, padx=10)

search_var = tk.StringVar()
search_var.trace_add("write", filter_list)
search_entry = tk.Entry(root, textvariable=search_var, font=("Arial", 12), width=50)
search_entry.pack(pady=(10, 0))

list_frame = tk.Frame(root)
list_frame.pack(pady=10, fill="both", expand=True)

scrollbar = tk.Scrollbar(list_frame)
scrollbar.pack(side="right", fill="y")

listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Courier", 12))
listbox.pack(side="left", fill="both", expand=True)
scrollbar.config(command=listbox.yview)

listbox.bind("<<ListboxSelect>>", on_select)

clear_button = tk.Button(button_frame, text="Clear All", command=clear_all)
clear_button.grid(row=0, column=0, padx=10)

delete_button = tk.Button(button_frame, text="Delete Selected", command=delete_selected)
delete_button.grid(row=0, column=1, padx=10)

close_button = tk.Button(root, text="Close", command=quit_app)
close_button.pack(pady=20)

root.protocol("WM_DELETE_WINDOW", hide_window)

load_history()
check_clipboard()
setup_tray_icon()
root.mainloop()
