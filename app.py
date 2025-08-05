import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import hashlib
import json

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("File Integrity Checker V2")
app.geometry("850x600")
app.resizable(False, False)

selected_folder = ""


def get_all_files(folder_path):
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            file_list.append(full_path)
    return file_list

def calculate_file_hash(file_path):
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        return None

def save_hashes_to_file():
    if not selected_folder:
        messagebox.showwarning("Warning", "Please select a folder first.")
        return

    files = get_all_files(selected_folder)
    hash_data = {}

    for file in files:
        hash_val = calculate_file_hash(file)
        if hash_val:
            relative_path = os.path.relpath(file, selected_folder)
            hash_data[relative_path] = hash_val

    with open("hashes.json", "w") as f:
        json.dump(hash_data, f, indent=4)

    output_box.insert("end", f"Hashes saved for {len(hash_data)} file(s).\n")

def load_saved_hashes():
    if not os.path.exists("hashes.json"):
        return {}
    with open("hashes.json", "r") as f:
        return json.load(f)

def compare_current_with_saved():
    if not selected_folder:
        messagebox.showwarning("Warning", "Please select a folder first.")
        return

    saved_hashes = load_saved_hashes()
    current_files = get_all_files(selected_folder)

    current_hashes = {}
    for file in current_files:
        hash_val = calculate_file_hash(file)
        if hash_val:
            relative_path = os.path.relpath(file, selected_folder)
            current_hashes[relative_path] = hash_val

    output_box.delete("1.0", "end")

    for file in current_hashes:
        if file in saved_hashes:
            if current_hashes[file] == saved_hashes[file]:
                output_box.insert("end", f"[OK] {file}\n", "ok")
            else:
                output_box.insert("end", f"[MODIFIED] {file}\n", "changed")
        else:
            output_box.insert("end", f"[NEW] {file}\n", "new")

    for file in saved_hashes:
        if file not in current_hashes:
            output_box.insert("end", f"[DELETED] {file}\n", "deleted")

def clear_output():
    output_box.delete("1.0", "end")

def select_folder():
    global selected_folder
    folder = filedialog.askdirectory()
    if folder:
        selected_folder = folder
        folder_path_label.configure(text=folder)


title_label = ctk.CTkLabel(app, text="File Integrity Checker V2", font=("Segoe UI", 24, "bold"))
title_label.pack(pady=20)

folder_frame = ctk.CTkFrame(app, fg_color="transparent")
folder_frame.pack(pady=10, fill="x", padx=20)

select_btn = ctk.CTkButton(folder_frame, text="Select Folder", command=select_folder, fg_color="#9b59b6", hover_color="#8e44ad")
select_btn.pack(side="left", padx=5)

folder_path_label = ctk.CTkLabel(folder_frame, text="No folder selected", text_color="#AAAAAA")
folder_path_label.pack(side="left", padx=10)

btn_frame = ctk.CTkFrame(app, fg_color="transparent")
btn_frame.pack(pady=10)

save_btn = ctk.CTkButton(btn_frame, text="Save Hashes", command=save_hashes_to_file, fg_color="#9b59b6", hover_color="#8e44ad")
save_btn.grid(row=0, column=0, padx=10)

compare_btn = ctk.CTkButton(btn_frame, text="Compare", command=compare_current_with_saved, fg_color="#2980b9", hover_color="#2471a3")
compare_btn.grid(row=0, column=1, padx=10)

clear_btn = ctk.CTkButton(btn_frame, text="Clear Output", command=clear_output, fg_color="#c0392b", hover_color="#a93226")
clear_btn.grid(row=0, column=2, padx=10)

output_label = ctk.CTkLabel(app, text="Output:", font=("Segoe UI", 16))
output_label.pack(pady=(15, 0))

output_box = ctk.CTkTextbox(app, height=300, corner_radius=10, font=("Consolas", 13))
output_box.pack(padx=20, pady=10, fill="both", expand=True)


output_box.tag_config("ok", foreground="lightgreen")
output_box.tag_config("changed", foreground="red")
output_box.tag_config("new", foreground="cyan")
output_box.tag_config("deleted", foreground="orange")

app.mainloop()
