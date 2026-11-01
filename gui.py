import os
import sys
import json
import threading
import subprocess
from typing import Optional

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    import customtkinter as ctk
    from tkinter import filedialog, messagebox
except ImportError:
    # Graceful fallback instructions if dependencies are not loaded
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Missing Dependency",
        "customtkinter is required to run the dashboard.\nPlease run: pip install -r requirements.txt"
    )
    sys.exit(1)

# Import helper generators for quick assist buttons
try:
    import topic_finder
    import script_generator
    import script_generator_long
    import youtube_uploader
    import youtube_uploader_long
except ImportError as e:
    print(f"Warning: Could not import automation helper: {e}")


class YouTubeAutomatorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Appearance configuration
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.title("YouTube Automator")
        self.geometry("1160x780")
        self.minsize(980, 680)

        # Internal state
        self.current_process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.thumbnail_path = ""
        self.loop_requested = False

        self._build_ui()

    def _build_ui(self):
        # Configure root grid layout
        self.grid_columnconfigure(0, weight=5)  # Left panel: Inputs
        self.grid_columnconfigure(1, weight=6)  # Right panel: Console
        self.grid_rowconfigure(0, weight=1)

        self._build_left_panel()
        self._build_right_panel()

    def _build_left_panel(self):
        # Scrollable container for all controls and inputs
        self.left_frame = ctk.CTkScrollableFrame(
            self,
            corner_radius=12,
            fg_color="#18181b",
            border_width=1,
            border_color="#27272a"
        )
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)
        self.left_frame.grid_columnconfigure(0, weight=1)

        # 1. Header
        header_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(4, 14))

        title_label = ctk.CTkLabel(
            header_frame,
            text="YouTube Automator",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#f4f4f5"
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Configure your custom video parameters or leave fields blank to auto-generate.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#a1a1aa"
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))

        # 2. Video Format Segmented Control
        format_label = ctk.CTkLabel(
            self.left_frame,
            text="Video Format",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#e4e4e7"
        )
        format_label.grid(row=1, column=0, sticky="w", pady=(10, 4))

        self.format_var = ctk.StringVar(value="Shorts (9:16)")
        self.format_segmented = ctk.CTkSegmentedButton(
            self.left_frame,
            values=["Shorts (9:16)", "Long Video (16:9)"],
            variable=self.format_var,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=34,
            selected_color="#2563eb",
            selected_hover_color="#1d4ed8",
            unselected_color="#27272a",
            unselected_hover_color="#3f3f46"
        )
        self.format_segmented.grid(row=2, column=0, sticky="ew", pady=(0, 12))

        # 3. Topic Input
        topic_header = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        topic_header.grid(row=3, column=0, sticky="ew", pady=(6, 2))
        topic_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            topic_header,
            text="Topic / Idea",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#e4e4e7"
        ).grid(row=0, column=0, sticky="w")

        self.btn_fetch_topic = ctk.CTkButton(
            topic_header,
            text="Fetch Trending",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            width=100,
            height=26,
            fg_color="#27272a",
            hover_color="#3f3f46",
            command=self._async_fetch_trending_topic
        )
        self.btn_fetch_topic.grid(row=0, column=1, sticky="e")

        self.entry_topic = ctk.CTkEntry(
            self.left_frame,
            placeholder_text="e.g., The Mystery of Dark Matter (blank for trending)",
            height=38,
            corner_radius=8,
            fg_color="#1f1f23",
            border_color="#3f3f46"
        )
        self.entry_topic.grid(row=4, column=0, sticky="ew", pady=(2, 12))

        # 4. Custom Title Input
        title_header = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        title_header.grid(row=5, column=0, sticky="ew", pady=(6, 2))
        title_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            title_header,
            text="Video Title",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#e4e4e7"
        ).grid(row=0, column=0, sticky="w")

        self.btn_gen_title = ctk.CTkButton(
            title_header,
            text="Generate Title",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            width=100,
            height=26,
            fg_color="#27272a",
            hover_color="#3f3f46",
            command=self._async_generate_title
        )
        self.btn_gen_title.grid(row=0, column=1, sticky="e")

        self.entry_title = ctk.CTkEntry(
            self.left_frame,
            placeholder_text="Custom video title (blank to auto-generate)",
            height=38,
            corner_radius=8,
            fg_color="#1f1f23",
            border_color="#3f3f46"
        )
        self.entry_title.grid(row=6, column=0, sticky="ew", pady=(2, 12))

        # 5. Custom Description Input
        desc_header = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        desc_header.grid(row=7, column=0, sticky="ew", pady=(6, 2))
        desc_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            desc_header,
            text="Video Description",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#e4e4e7"
        ).grid(row=0, column=0, sticky="w")

        self.btn_gen_desc = ctk.CTkButton(
            desc_header,
            text="Generate Description",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            width=135,
            height=26,
            fg_color="#27272a",
            hover_color="#3f3f46",
            command=self._async_generate_description
        )
        self.btn_gen_desc.grid(row=0, column=1, sticky="e")

        self.textbox_desc = ctk.CTkTextbox(
            self.left_frame,
            height=90,
            corner_radius=8,
            fg_color="#1f1f23",
            border_color="#3f3f46",
            border_width=1,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.textbox_desc.grid(row=8, column=0, sticky="ew", pady=(2, 12))

        # 6. Custom Narration Script Input
        script_header = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        script_header.grid(row=9, column=0, sticky="ew", pady=(6, 2))
        script_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            script_header,
            text="Narration Script",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#e4e4e7"
        ).grid(row=0, column=0, sticky="w")

        self.btn_gen_script = ctk.CTkButton(
            script_header,
            text="Generate Script",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            width=115,
            height=26,
            fg_color="#27272a",
            hover_color="#3f3f46",
            command=self._async_generate_script
        )
        self.btn_gen_script.grid(row=0, column=1, sticky="e")

        self.textbox_script = ctk.CTkTextbox(
            self.left_frame,
            height=110,
            corner_radius=8,
            fg_color="#1f1f23",
            border_color="#3f3f46",
            border_width=1,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.textbox_script.grid(row=10, column=0, sticky="ew", pady=(2, 6))

        script_hint = ctk.CTkLabel(
            self.left_frame,
            text="Leave blank to let AI generate. Scene cues and speaker tags are automatically cleaned.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#71717a"
        )
        script_hint.grid(row=11, column=0, sticky="w", pady=(0, 12))

        # 7. Custom Thumbnail Picker
        thumb_label = ctk.CTkLabel(
            self.left_frame,
            text="Custom Thumbnail (Optional)",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#e4e4e7"
        )
        thumb_label.grid(row=12, column=0, sticky="w", pady=(6, 2))

        thumb_row = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        thumb_row.grid(row=13, column=0, sticky="ew", pady=(2, 12))
        thumb_row.grid_columnconfigure(0, weight=1)

        self.entry_thumb = ctk.CTkEntry(
            thumb_row,
            placeholder_text="Path to image (.png, .jpg, .webp)",
            height=36,
            corner_radius=8,
            fg_color="#1f1f23",
            border_color="#3f3f46"
        )
        self.entry_thumb.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.btn_browse_thumb = ctk.CTkButton(
            thumb_row,
            text="Browse...",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            width=80,
            height=36,
            fg_color="#27272a",
            hover_color="#3f3f46",
            command=self._browse_thumbnail
        )
        self.btn_browse_thumb.grid(row=0, column=1, padx=(0, 4))

        self.btn_clear_thumb = ctk.CTkButton(
            thumb_row,
            text="Clear",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            width=60,
            height=36,
            fg_color="#27272a",
            hover_color="#3f3f46",
            command=self._clear_thumbnail
        )
        self.btn_clear_thumb.grid(row=0, column=2)

        # 8. Options Checkboxes
        options_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        options_frame.grid(row=14, column=0, sticky="ew", pady=(6, 14))

        self.skip_upload_var = ctk.BooleanVar(value=False)
        self.chk_skip_upload = ctk.CTkCheckBox(
            options_frame,
            text="Skip YouTube upload (Generate video locally in assets/)",
            variable=self.skip_upload_var,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            checkbox_height=20,
            checkbox_width=20,
            fg_color="#2563eb",
            hover_color="#1d4ed8"
        )
        self.chk_skip_upload.pack(anchor="w", pady=(0, 6))

        self.loop_mode_var = ctk.BooleanVar(value=False)
        self.chk_loop = ctk.CTkCheckBox(
            options_frame,
            text="Continuous loop mode (Start new video automatically after completion)",
            variable=self.loop_mode_var,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            checkbox_height=20,
            checkbox_width=20,
            fg_color="#2563eb",
            hover_color="#1d4ed8"
        )
        self.chk_loop.pack(anchor="w")

        # 9. Action Buttons
        action_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        action_frame.grid(row=15, column=0, sticky="ew", pady=(6, 8))
        action_frame.grid_columnconfigure(0, weight=3)
        action_frame.grid_columnconfigure(1, weight=1)

        self.btn_start = ctk.CTkButton(
            action_frame,
            text="Start Video Generation",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            height=44,
            corner_radius=8,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=self.start_generation
        )
        self.btn_start.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.btn_stop = ctk.CTkButton(
            action_frame,
            text="Stop Task",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            height=44,
            corner_radius=8,
            fg_color="#3f3f46",
            hover_color="#dc2626",
            state="disabled",
            command=self.stop_generation
        )
        self.btn_stop.grid(row=0, column=1, sticky="ew")

        # 10. Status Indicator
        self.lbl_status = ctk.CTkLabel(
            self.left_frame,
            text="Status: Ready",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#a1a1aa"
        )
        self.lbl_status.grid(row=16, column=0, sticky="w", pady=(4, 8))

    def _build_right_panel(self):
        # Console Frame
        self.right_frame = ctk.CTkFrame(
            self,
            corner_radius=12,
            fg_color="#18181b",
            border_width=1,
            border_color="#27272a"
        )
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=16)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=1)

        # Header bar for Console
        console_bar = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        console_bar.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))
        console_bar.grid_columnconfigure(0, weight=1)

        console_title = ctk.CTkLabel(
            console_bar,
            text="Console Output",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#f4f4f5"
        )
        console_title.grid(row=0, column=0, sticky="w")

        btn_copy = ctk.CTkButton(
            console_bar,
            text="Copy Logs",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            width=80,
            height=28,
            fg_color="#27272a",
            hover_color="#3f3f46",
            command=self._copy_console
        )
        btn_copy.grid(row=0, column=1, padx=(0, 6))

        btn_clear = ctk.CTkButton(
            console_bar,
            text="Clear",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            width=65,
            height=28,
            fg_color="#27272a",
            hover_color="#3f3f46",
            command=self.clear_console
        )
        btn_clear.grid(row=0, column=2)

        # Scrolled Textbox for Console Logs
        self.console = ctk.CTkTextbox(
            self.right_frame,
            corner_radius=8,
            fg_color="#0d0d0f",
            text_color="#22c55e",
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word",
            border_width=1,
            border_color="#27272a"
        )
        self.console.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.console.configure(state="disabled")

    # --- Helper Dialogs and Inputs ---
    def _browse_thumbnail(self):
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.webp"),
            ("All files", "*.*")
        ]
        chosen = filedialog.askopenfilename(title="Select Thumbnail Image", filetypes=filetypes)
        if chosen:
            self.entry_thumb.delete(0, "end")
            self.entry_thumb.insert(0, chosen)

    def _clear_thumbnail(self):
        self.entry_thumb.delete(0, "end")

    def _copy_console(self):
        content = self.console.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(content)
        self.set_status("Logs copied to clipboard.")

    def write_to_console(self, text: str):
        self.console.configure(state="normal")
        self.console.insert("end", text)
        self.console.see("end")
        self.console.configure(state="disabled")

    def clear_console(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")

    def set_status(self, text: str):
        self.lbl_status.configure(text=f"Status: {text}")

    # --- Async Assistance Buttons ---
    def _async_fetch_trending_topic(self):
        def worker():
            self.btn_fetch_topic.configure(state="disabled", text="Fetching...")
            try:
                topic = topic_finder.get_trending_topic()
                self.after(0, lambda: self._apply_topic(topic))
            except Exception as e:
                self.after(0, lambda: self.write_to_console(f"Could not fetch trending topic: {e}\n"))
            finally:
                self.after(0, lambda: self.btn_fetch_topic.configure(state="normal", text="Fetch Trending"))
        threading.Thread(target=worker, daemon=True).start()

    def _apply_topic(self, topic: str):
        self.entry_topic.delete(0, "end")
        self.entry_topic.insert(0, topic)
        self.write_to_console(f"[Assistant] Trending topic retrieved: {topic}\n")

    def _async_generate_title(self):
        topic = self.entry_topic.get().strip()
        if not topic:
            messagebox.showinfo("Topic Required", "Please enter or fetch a topic first to generate a title.")
            return

        is_long = "Long" in self.format_var.get()

        def worker():
            self.btn_gen_title.configure(state="disabled", text="Generating...")
            try:
                if is_long:
                    title = youtube_uploader_long.generate_engaging_title_long(topic)
                else:
                    title = youtube_uploader.generate_engaging_title(topic)
                self.after(0, lambda: self._apply_title(title))
            except Exception as e:
                self.after(0, lambda: self.write_to_console(f"Error generating title: {e}\n"))
            finally:
                self.after(0, lambda: self.btn_gen_title.configure(state="normal", text="Generate Title"))
        threading.Thread(target=worker, daemon=True).start()

    def _apply_title(self, title: str):
        self.entry_title.delete(0, "end")
        self.entry_title.insert(0, title)
        self.write_to_console(f"[Assistant] Generated title: {title}\n")

    def _async_generate_description(self):
        topic = self.entry_topic.get().strip()
        if not topic:
            messagebox.showinfo("Topic Required", "Please enter or fetch a topic first to generate a description.")
            return

        script = self.textbox_script.get("1.0", "end-1c").strip()
        is_long = "Long" in self.format_var.get()

        def worker():
            self.btn_gen_desc.configure(state="disabled", text="Generating...")
            try:
                if is_long:
                    desc = (
                        f"In this video, we explore {topic} in depth, breaking down essential concepts into simple, "
                        f"practical insights.\n\n"
                        f"Subscribe for more in-depth educational content.\n"
                        f"Like if you found this helpful!\n\n"
                        f"#education #learning #knowledge #tutorial #explained"
                    )
                else:
                    desc = youtube_uploader.generate_rich_description(topic, script[:120])
                self.after(0, lambda: self._apply_description(desc))
            except Exception as e:
                self.after(0, lambda: self.write_to_console(f"Error generating description: {e}\n"))
            finally:
                self.after(0, lambda: self.btn_gen_desc.configure(state="normal", text="Generate Description"))
        threading.Thread(target=worker, daemon=True).start()

    def _apply_description(self, desc: str):
        self.textbox_desc.delete("1.0", "end")
        self.textbox_desc.insert("1.0", desc)
        self.write_to_console("[Assistant] Generated description populated.\n")

    def _async_generate_script(self):
        topic = self.entry_topic.get().strip()
        if not topic:
            messagebox.showinfo("Topic Required", "Please enter or fetch a topic first to generate a script.")
            return

        is_long = "Long" in self.format_var.get()

        def worker():
            self.btn_gen_script.configure(state="disabled", text="Generating...")
            try:
                if is_long:
                    script = script_generator_long.generate_long_script(topic)
                else:
                    script = script_generator.generate_script(topic)
                self.after(0, lambda: self._apply_script(script))
            except Exception as e:
                self.after(0, lambda: self.write_to_console(f"Error generating script: {e}\n"))
            finally:
                self.after(0, lambda: self.btn_gen_script.configure(state="normal", text="Generate Script"))
        threading.Thread(target=worker, daemon=True).start()

    def _apply_script(self, script: str):
        self.textbox_script.delete("1.0", "end")
        self.textbox_script.insert("1.0", script)
        self.write_to_console(f"[Assistant] Generated script ready ({len(script)} characters).\n")

    # --- Job Execution ---
    def start_generation(self):
        if self.is_running:
            return

        is_long = "Long" in self.format_var.get()
        target_script = "main_long.py" if is_long else "main.py"

        # Collect form inputs
        topic = self.entry_topic.get().strip()
        title = self.entry_title.get().strip()
        description = self.textbox_desc.get("1.0", "end-1c").strip()
        script = self.textbox_script.get("1.0", "end-1c").strip()
        thumbnail = self.entry_thumb.get().strip()
        skip_upload = self.skip_upload_var.get()
        loop_mode = self.loop_mode_var.get()

        # Build job configuration dictionary
        job_config = {
            "mode": "long" if is_long else "shorts",
            "topic": topic,
            "title": title,
            "description": description,
            "script": script,
            "thumbnail": thumbnail,
            "skip_upload": skip_upload
        }

        # Save to assets/job_config.json for bulletproof multi-line argument passing
        os.makedirs("assets", exist_ok=True)
        config_path = os.path.abspath(os.path.join("assets", "job_config.json"))
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(job_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write job config file: {e}")
            return

        self.set_ui_running_state(True)
        mode_label = "Long Video (16:9)" if is_long else "YouTube Short (9:16)"
        self.write_to_console(f"\n{'='*55}\nStarting {mode_label} Task\n{'='*55}\n")
        if topic:
            self.write_to_console(f"• Topic: {topic}\n")
        if title:
            self.write_to_console(f"• Title: {title}\n")
        if thumbnail:
            self.write_to_console(f"• Custom Thumbnail: {thumbnail}\n")
        if skip_upload:
            self.write_to_console(f"• Upload: Local Generation Only (Upload Skipped)\n")

        thread = threading.Thread(
            target=self._execute_pipeline,
            args=(target_script, config_path, loop_mode),
            daemon=True
        )
        thread.start()

    def _execute_pipeline(self, target_script: str, config_path: str, loop_mode: bool):
        # Resolve python executable from virtualenv if available
        python_path = os.path.join(".venv", "Scripts", "python.exe")
        if not os.path.exists(python_path):
            python_path = sys.executable

        cmd = [python_path, target_script, "--config", config_path]

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        try:
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                env=env
            )

            for line in iter(self.current_process.stdout.readline, ''):
                self.write_to_console(line)

            self.current_process.stdout.close()
            returncode = self.current_process.wait()

            if returncode == 0:
                self.write_to_console("\n[Completed] Video generation finished successfully.\n")
                self.after(0, lambda: self.set_status("Completed successfully."))
            else:
                self.write_to_console(f"\n[Exited] Process finished with exit code {returncode}.\n")
                self.after(0, lambda: self.set_status(f"Process exited with code {returncode}."))

        except Exception as e:
            self.write_to_console(f"\n[Error] Failed to execute task: {e}\n")
            self.after(0, lambda: self.set_status("Error occurred during execution."))
        finally:
            self.current_process = None
            self.after(0, lambda: self.set_ui_running_state(False))

            # Handle loop mode if requested and process completed normally
            if loop_mode and self.loop_mode_var.get() and returncode == 0:
                self.write_to_console("\n[Loop Mode] Starting next automated cycle in 5 seconds...\n")
                self.after(5000, self.start_generation)

    def stop_generation(self):
        if self.current_process and self.current_process.poll() is None:
            self.write_to_console("\n[Action] Stopping running task...\n")
            try:
                self.current_process.terminate()
            except Exception as e:
                self.write_to_console(f"Could not terminate: {e}\n")
            self.set_status("Task stopped by user.")
        self.set_ui_running_state(False)

    def set_ui_running_state(self, is_running: bool):
        self.is_running = is_running
        state = "disabled" if is_running else "normal"

        self.btn_start.configure(state=state)
        self.btn_stop.configure(state="normal" if is_running else "disabled", fg_color="#ef4444" if is_running else "#3f3f46")
        self.btn_fetch_topic.configure(state=state)
        self.btn_gen_title.configure(state=state)
        self.btn_gen_desc.configure(state=state)
        self.btn_gen_script.configure(state=state)
        self.format_segmented.configure(state=state)

        if is_running:
            self.set_status("Running video generation pipeline...")
        else:
            self.set_status("Ready")


if __name__ == "__main__":
    app = YouTubeAutomatorGUI()
    app.mainloop()