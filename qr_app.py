#!/usr/bin/env python
# coding: utf-8

# In[3]:


import qrcode
import pyperclip
import speech_recognition as sr
import cv2
from tkinter import *
from tkinter import filedialog, colorchooser, messagebox
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
import schedule
import time
import threading
import os
import csv
from PIL import ImageGrab
import io

# Global variables for QR generation, encryption, etc.
qr_fg_color = "black"
qr_bg_color = "white"
logo_path = None
qr_history = []
scan_history = []
key = Fernet.generate_key()
cipher = Fernet(key)


def encrypt_text(text):
    """Encrypt the data before generating the QR"""
    return cipher.encrypt(text.encode()).decode()


def decrypt_text(encrypted_text):
    """Decrypt the data after scanning the QR"""
    return cipher.decrypt(encrypted_text.encode()).decode()


def generate_qr():
    global qr_fg_color, qr_bg_color, logo_path, qr_history
    data = entry.get()
    if data.strip() == "":
        messagebox.showwarning("Input Required", "Please enter text or URL.")
        return

    # Encrypt the data before generating the QR
    encrypted_data = encrypt_text(data)

    # Get QR size from input slider
    qr_size = size_slider.get()
    border_size = border_slider.get()

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=qr_size,
        border=border_size
    )
    qr.add_data(encrypted_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=qr_fg_color, back_color=qr_bg_color).convert("RGB")

    if logo_path:
        try:
            logo = Image.open(logo_path)
            logo = logo.resize((int(qr_size * 5), int(qr_size * 5)))  # scale the logo size relative to QR size
            pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
            img.paste(logo, pos, mask=logo if logo.mode == 'RGBA' else None)
        except Exception as e:
            messagebox.showwarning("Logo Error", str(e))

    filepath = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
        title="Save QR Code"
    )
    if filepath:
        img.save(filepath)
        qr_history.append(filepath)
        update_history()
        messagebox.showinfo("Saved", f"QR Code saved:\n{filepath}")
        show_image(filepath)


def show_image(path):
    img = Image.open(path).resize((200, 200))
    photo = ImageTk.PhotoImage(img)
    qr_label.config(image=photo)
    qr_label.image = photo


def choose_fg_color():
    global qr_fg_color
    color = colorchooser.askcolor(title="Choose QR Color")
    if color[1]:
        qr_fg_color = color[1]


def choose_bg_color():
    global qr_bg_color
    color = colorchooser.askcolor(title="Choose Background Color")
    if color[1]:
        qr_bg_color = color[1]


def select_logo():
    global logo_path
    path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if path:
        logo_path = path
        messagebox.showinfo("Logo Selected", logo_path)


def scan_qr():
    cap = cv2.VideoCapture(0)
    messagebox.showinfo("QR Scanner", "Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        decoded_objs = decode(frame)
        for obj in decoded_objs:
            (x, y, w, h) = obj.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            encrypted_text = obj.data.decode("utf-8")
            decrypted_text = decrypt_text(encrypted_text)  # Decrypt the QR data
            cv2.putText(frame, decrypted_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)
            print("Decoded and Decrypted:", decrypted_text)
            pyperclip.copy(decrypted_text)
            scan_history.append(decrypted_text)  # Save scan history
        cv2.imshow("QR Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


def update_history():
    history_listbox.delete(0, END)
    for item in qr_history[-10:]:  # show last 10
        history_listbox.insert(END, os.path.basename(item))


def save_history():
    # Save QR Code history to a CSV file
    with open('qr_history.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["QR Code File Path"])
        for item in qr_history:
            writer.writerow([item])
    messagebox.showinfo("Saved", "QR history saved to qr_history.csv.")


def clear_input():
    entry.delete(0, END)


def listen_for_commands():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for commands...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"Command: {command}")
        if "generate qr" in command:
            generate_qr()
        elif "scan qr" in command:
            scan_qr()
        elif "clear input" in command:
            clear_input()
        elif "exit" in command:
            root.quit()
        else:
            print("Command not recognized")
    except sr.UnknownValueError:
        print("Sorry, I did not understand the command.")
    except sr.RequestError:
        print("Could not request results; check your internet connection.")


def scheduled_qr_generation():
    # Here, you'd have your QR generation logic
    print("Scheduled QR Code Generation triggered!")


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


def toggle_theme():
    if root["bg"] == "#ffffff":
        root.config(bg="#222222")
        for widget in root.winfo_children():
            try:
                widget.config(bg="#222222", fg="white")
            except:
                pass
    else:
        root.config(bg="#ffffff")
        for widget in root.winfo_children():
            try:
                widget.config(bg="#ffffff", fg="black")
            except:
                pass


def search_history():
    query = search_entry.get().lower()
    history_listbox.delete(0, END)
    for item in qr_history:
        if query in os.path.basename(item).lower():
            history_listbox.insert(END, os.path.basename(item))


def validate_qr():
    """Validate if the QR code can be scanned properly"""
    data = entry.get()
    if not data:
        messagebox.showwarning("Input Required", "Enter some text or URL for QR code validation.")
        return

    try:
        # Try scanning the QR code from the data
        img = qrcode.make(data)
        img.show()
        messagebox.showinfo("Validation", "QR code is valid and can be scanned.")
    except Exception as e:
        messagebox.showerror("Validation Error", f"An error occurred: {e}")


def reset_application():
    """Reset the application fields and settings"""
    entry.delete(0, END)
    size_slider.set(10)
    border_slider.set(4)
    qr_fg_color = "black"
    qr_bg_color = "white"
    logo_path = None
    messagebox.showinfo("Reset", "Application reset successfully!")


def copy_qr_to_clipboard():
    """Copy QR code image to clipboard"""
    data = entry.get()
    if not data:
        messagebox.showwarning("Input Required", "Please enter data for QR code generation.")
        return

    encrypted_data = encrypt_text(data)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=size_slider.get(),
        border=border_slider.get()
    )
    qr.add_data(encrypted_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=qr_fg_color, back_color=qr_bg_color).convert("RGB")

    # Copy the image to the clipboard
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    ImageGrab.grabclipboard(img_byte_arr)
    messagebox.showinfo("Clipboard", "QR code copied to clipboard.")


def change_bg_color():
    color = colorchooser.askcolor(title="Choose Background Color")[1]
    if color:
        root.config(bg=color)
        for widget in root.winfo_children():
            try:
                widget.config(bg=color, fg="white" if color != "#ffffff" else "black")
            except:
                pass


# GUI setup
root = Tk()
root.title("QR Code Generator")
root.geometry("600x850")
root.config(bg="#ffffff")

# Title and Input Field
Label(root, text="QR Code Generator", font=("Helvetica", 18, "bold"), bg="#ffffff").pack(pady=10)

Label(root, text="Enter text or URL:", font=("Helvetica", 12), bg="#ffffff").pack()
entry = Entry(root, font=("Helvetica", 12), width=40)
entry.pack(pady=10)

# Size Slider
Label(root, text="Select QR Size:", font=("Helvetica", 12), bg="#ffffff").pack()
size_slider = Scale(root, from_=5, to=20, orient=HORIZONTAL, bg="#ffffff", fg="black")
size_slider.set(10)  # Default size
size_slider.pack(pady=10)

# Border Size Slider
Label(root, text="Select Border Size:", font=("Helvetica", 12), bg="#ffffff").pack()
border_slider = Scale(root, from_=1, to=10, orient=HORIZONTAL, bg="#ffffff", fg="black")
border_slider.set(4)  # Default border
border_slider.pack(pady=10)

# Buttons for QR generation, scanning, etc.
frame = Frame(root, bg="#ffffff")
frame.pack(pady=5)

Button(frame, text="QR Color", bg="#ff5722", fg="white", font=("Helvetica", 12), command=choose_fg_color).grid(row=0, column=0, padx=5, pady=5)
Button(frame, text="Background", bg="#009688", fg="white", font=("Helvetica", 12), command=choose_bg_color).grid(row=0, column=1, padx=5, pady=5)
Button(frame, text="Add Logo", bg="#3f51b5", fg="white", font=("Helvetica", 12), command=select_logo).grid(row=0, column=2, padx=5, pady=5)

Button(root, text="Generate QR Code", bg="#28a745", fg="white", font=("Helvetica", 12), command=generate_qr).pack(pady=10)
Button(root, text="Scan QR Code", bg="#757575", fg="white", font=("Helvetica", 12), command=scan_qr).pack(pady=10)
Button(root, text="Clear Input", bg="#dc3545", fg="white", font=("Helvetica", 12), command=clear_input).pack(pady=5)
Button(root, text="Reset App", bg="#673ab7", fg="white", font=("Helvetica", 12), command=reset_application).pack(pady=5)
Button(root, text="Validate QR", bg="#ff9800", fg="white", font=("Helvetica", 12), command=validate_qr).pack(pady=5)
Button(root, text="Copy QR to Clipboard", bg="#9c27b0", fg="white", font=("Helvetica", 12), command=copy_qr_to_clipboard).pack(pady=10)

qr_label = Label(root, bg="#ffffff")
qr_label.pack(pady=10)

# QR History Section
Label(root, text="QR History (Last 10):", font=("Helvetica", 12), bg="#ffffff").pack()
history_listbox = Listbox(root, height=5, width=50)
history_listbox.pack(pady=5)

# Search Bar for QR History
Label(root, text="Search History:", font=("Helvetica", 12), bg="#ffffff").pack(pady=5)
search_entry = Entry(root, font=("Helvetica", 12), width=40)
search_entry.pack(pady=5)
Button(root, text="Search", bg="#ff5722", fg="white", font=("Helvetica", 12), command=search_history).pack(pady=5)

Button(root, text="Save History", bg="#00bcd4", fg="white", font=("Helvetica", 12), command=save_history).pack(pady=10)
Button(root, text="Toggle Dark Mode", bg="#4caf50", fg="white", font=("Helvetica", 12), command=toggle_theme).pack(pady=10)

# Add background color change button
Button(root, text="Change Background Color", bg="#607d8b", fg="white", font=("Helvetica", 12), command=change_bg_color).pack(pady=10)

# Footer
Label(root, text="Developed by FaiLure.BraiN", font=("Helvetica", 9), bg="#ffffff", fg="gray").pack(side="bottom", pady=10)

# Scheduler and Voice Command Threading
threading.Thread(target=run_scheduler, daemon=True).start()
threading.Thread(target=listen_for_commands, daemon=True).start()

root.mainloop()


# In[ ]:




