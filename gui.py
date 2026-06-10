import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import sys
import os

class AppInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("YouTube Automation Dashboard")
        self.geometry("900x600")
        self.configure(padx=20, pady=20)
        
        # Configure grid style
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Segoe UI', 10), padding=5)
        style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'))

        self.create_widgets()
        
    def create_widgets(self):
        # Left Panel (Controls)
        control_frame = ttk.LabelFrame(self, text="Actions", padding=15)
        control_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ttk.Label(control_frame, text="Shorts Automation", style='Header.TLabel').pack(pady=(0, 10))
        self.btn_short = ttk.Button(control_frame, text="▶ Generate Single Short", command=lambda: self.run_script("main.py"))
        self.btn_short.pack(fill="x", pady=5)
        
        self.btn_loop_short = ttk.Button(control_frame, text="🔁 Run Shorts Loop", command=lambda: self.run_script("run_loop.bat"))
        self.btn_loop_short.pack(fill="x", pady=5)

        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=15)

        ttk.Label(control_frame, text="Long Video Automation", style='Header.TLabel').pack(pady=(0, 10))
        self.btn_long = ttk.Button(control_frame, text="▶ Generate Long Video", command=lambda: self.run_script("main_long.py"))
        self.btn_long.pack(fill="x", pady=5)
        
        self.btn_loop_long = ttk.Button(control_frame, text="🔁 Run Long Loop", command=lambda: self.run_script("run_long_loop.bat"))
        self.btn_loop_long.pack(fill="x", pady=5)

        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=15)
        
        self.btn_clear = ttk.Button(control_frame, text="🗑️ Clear Console", command=self.clear_console)
        self.btn_clear.pack(fill="x", side="bottom", pady=5)

        # Right Panel (Console Output)
        console_frame = ttk.LabelFrame(self, text="Console Output", padding=10)
        console_frame.grid(row=0, column=1, sticky="nsew")
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)

        self.console = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, font=('Consolas', 10), bg="black", fg="#00FF00")
        self.console.grid(row=0, column=0, sticky="nsew")
        self.console.config(state=tk.DISABLED)

    def write_to_console(self, text):
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, text)
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)

    def clear_console(self):
        self.console.config(state=tk.NORMAL)
        self.console.delete(1.0, tk.END)
        self.console.config(state=tk.DISABLED)

    def run_script(self, target):
        self.write_to_console(f"\n[{target}] Starting task...\n")
        self.set_buttons_state(tk.DISABLED)
        
        # Run in a separate thread so it doesn't freeze the GUI
        thread = threading.Thread(target=self._execute_command, args=(target,))
        thread.daemon = True
        thread.start()

    def _execute_command(self, target):
        try:
            if target.endswith(".py"):
                # Always use the virtual environment's python.exe
                python_path = os.path.join(".venv", "Scripts", "python.exe")
                if not os.path.exists(python_path):
                    python_path = "python" # fallback to system python
                cmd = [python_path, target]
            else:
                cmd = [target]
                
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            for line in iter(process.stdout.readline, ''):
                self.write_to_console(line)

            process.stdout.close()
            process.wait()
            
            self.write_to_console(f"\nTask finished with exit code {process.returncode}\n")
        except Exception as e:
            self.write_to_console(f"\nError running task: {e}\n")
        finally:
            self.set_buttons_state(tk.NORMAL)

    def set_buttons_state(self, state):
        self.btn_short.config(state=state)
        self.btn_loop_short.config(state=state)
        self.btn_long.config(state=state)
        self.btn_loop_long.config(state=state)

"""
To run this application, type the following command in your terminal:
python gui.py
"""

if __name__ == "__main__":
    app = AppInterface()
    app.mainloop()