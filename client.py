import socket
import threading
import tkinter as tk
from tkinter import messagebox
from playsound import playsound

# Sound file paths
SOUND_CLICK = "click.mp3"
SOUND_WIN = "win.mp3"
SOUND_LOSE = "lose.mp3"

def play_sound(file):
    try:
        threading.Thread(target=lambda: playsound(file), daemon=True).start()
    except:
        pass

class RPSClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Rock Paper Scissors")
        self.root.geometry("500x600")
        self.root.configure(bg="#1f1f1f")
        self.root.resizable(False, False)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect(("localhost", 9999))
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            root.destroy()
            return

        self.name = ""
        self.is_starter = False
        self.create_name_screen()

    def create_name_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Enter your name", font=("Helvetica", 20, "bold"),
                 bg="#1f1f1f", fg="#ffffff").pack(pady=40)
        self.name_entry = tk.Entry(self.root, font=("Helvetica", 16), width=25)
        self.name_entry.pack(pady=10)
        tk.Button(self.root, text="Start Game 🎮", font=("Helvetica", 14, "bold"),
                  command=self.send_name, bg="#00b894", fg="white", activebackground="#55efc4").pack(pady=20)

    def send_name(self):
        self.name = self.name_entry.get().strip()
        if not self.name:
            messagebox.showwarning("Name Required", "Please enter your name.")
            return
        self.client.send(self.name.encode())

        try:
            starter_flag = self.client.recv(1024).decode()
            self.is_starter = starter_flag == "STARTER"
        except:
            messagebox.showerror("Error", "Failed to receive starter info from server.")
            self.root.destroy()
            return

        self.create_game_screen()
        threading.Thread(target=self.receive_result, daemon=True).start()

    def create_game_screen(self):
        self.clear_screen()
        tk.Label(self.root, text=f"👋 Welcome, {self.name}!", font=("Helvetica", 18, "bold"),
                 bg="#1f1f1f", fg="#81ecec").pack(pady=15)

        tk.Label(self.root, text="Choose your move:", font=("Helvetica", 16),
                 bg="#1f1f1f", fg="#ffffff").pack(pady=10)

        btn_frame = tk.Frame(self.root, bg="#1f1f1f")
        btn_frame.pack(pady=10)

        moves = [("🪨 Rock", "rock"), ("📄 Paper", "paper"), ("✂️ Scissors", "scissors")]
        for label, move in moves:
            btn = tk.Button(btn_frame, text=label, font=("Helvetica", 20), width=12,
                            bg="#0984e3", fg="white", activebackground="#74b9ff",
                            command=lambda m=move: self.send_choice(m))
            btn.pack(pady=10)

        self.result_label = tk.Label(self.root, text="", font=("Helvetica", 16, "bold"),
                                     wraplength=460, bg="#1f1f1f", fg="white")
        self.result_label.pack(pady=30)

        tk.Button(self.root, text="Exit ❌", font=("Helvetica", 12, "bold"),
                  command=self.root.destroy, bg="#d63031", fg="white", activebackground="#ff7675").pack(pady=15)

    def send_choice(self, move):
        play_sound(SOUND_CLICK)
        self.result_label.config(text="⏳ Waiting for opponent...")
        self.client.send(move.encode())

    def receive_result(self):
        while True:
            try:
                result = self.client.recv(1024).decode()
                self.show_result(result)
            except:
                break

    def show_result(self, result_text):
        self.result_label.config(text=result_text)

        if self.is_starter:
            if "YOU win" in result_text:
                play_sound(SOUND_WIN)
            elif "YOU lose" in result_text:
                play_sound(SOUND_LOSE)
            elif "Draw" in result_text:
                play_sound(SOUND_CLICK)

        if "YOU win" in result_text:
            self.result_label.config(fg="#00ff00")
        elif "YOU lose" in result_text:
            self.result_label.config(fg="#ff4d4d")
        elif "Draw" in result_text:
            self.result_label.config(fg="#ffeaa7")
        else:
            self.result_label.config(fg="white")

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RPSClientGUI(root)
    root.mainloop()
