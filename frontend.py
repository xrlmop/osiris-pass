import string
import secrets
import tkinter as tk
import customtkinter as ctk
import platform
import threading
import backend

IS_MAC = platform.system() == "Darwin"

if IS_MAC:
    try:
        from AppKit import NSApp, NSWindowStyleMaskFullSizeContentView
    except ImportError:
        pass

ctk.set_appearance_mode("dark")

NEON_COLOR = "#00FFA3"
ALERT_COLOR = "#FF3333"

FONT_NAME = "Courier" if IS_MAC else "Consolas"
FONT_PIXEL = (FONT_NAME, 12, "bold")
FONT_PIXEL_BIG = (FONT_NAME, 18, "bold")
FONT_PIXEL_SMALL = (FONT_NAME, 10, "bold")

class NeonNotification(ctk.CTkToplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title(title)
        self.geometry("420x200")
        self.resizable(False, False)
        self.configure(fg_color="#0A0A0C")
        self.transient(parent)
        self.grab_set()
        self.overrideredirect(True)
        
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 210
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 100
        self.geometry(f"+{x}+{y}")

        main_frame = ctk.CTkFrame(self, width=416, height=196, fg_color="#0A0A0C", border_width=2, border_color=NEON_COLOR, corner_radius=0)
        main_frame.pack(padx=2, pady=2, fill="both", expand=True)

        ctk.CTkLabel(main_frame, text=f">> {title.upper()} <<", font=FONT_PIXEL, text_color=NEON_COLOR).pack(pady=(15, 10))
        msg_lbl = ctk.CTkLabel(main_frame, text=message, font=FONT_PIXEL_SMALL, text_color="#FFFFFF", justify="center", wraplength=360)
        msg_lbl.pack(pady=10, fill="both", expand=True)

        btn_ok = ctk.CTkButton(main_frame, text="[ OK ]", width=120, height=30, fg_color="#0A0A0C", hover_color=NEON_COLOR, text_color=NEON_COLOR, border_width=1, border_color=NEON_COLOR, font=FONT_PIXEL, corner_radius=0, command=self.destroy)
        btn_ok.pack(pady=(5, 15))
        
        self.lift()
        self.focus_set()

class NeonConfirmDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message, callback):
        super().__init__(parent)
        self.title(title)
        self.configure(fg_color="#0A0A0C")
        self.overrideredirect(True)
        self.geometry("420x200")
        self.transient(parent)
        self.grab_set()
        self.callback = callback

        x = parent.winfo_x() + (parent.winfo_width() // 2) - 210
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 100
        self.geometry(f"+{x}+{y}")

        main_frame = ctk.CTkFrame(self, fg_color="#0A0A0C", border_width=2, border_color=NEON_COLOR, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)

        ctk.CTkLabel(main_frame, text=f">> {title.upper()} <<", font=FONT_PIXEL, text_color=NEON_COLOR).pack(pady=(15, 10))
        ctk.CTkLabel(main_frame, text=message, font=FONT_PIXEL_SMALL, text_color="#FFFFFF", justify="center", wraplength=360).pack(pady=10, fill="both", expand=True)

        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=(5, 15))

        ctk.CTkButton(btn_frame, text="[ YES ]", width=110, height=30, fg_color="#0A0A0C", hover_color=NEON_COLOR, text_color=NEON_COLOR, border_width=1, border_color=NEON_COLOR, font=FONT_PIXEL, corner_radius=0, command=self.action_yes).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="[ NO ]", width=110, height=30, fg_color="#0A0A0C", hover_color=ALERT_COLOR, text_color="#FFFFFF", border_width=1, border_color=ALERT_COLOR, font=FONT_PIXEL, corner_radius=0, command=self.destroy).pack(side="left", padx=10)
        
        self.lift()
        self.focus_set()

    def action_yes(self):
        self.destroy()
        self.callback()
class PasswordManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("OSIRIS PASS")
        self.geometry("850x620")
        self.minsize(650, 550)
        self.configure(fg_color="#0A0A0C")
        
        if IS_MAC:
            self.update_idletasks()
            try:
                ns_window = NSApp().windowWithWindowNumber_(self.winfo_id())
                if ns_window:
                    ns_window.setStyleMask_(ns_window.styleMask() | NSWindowStyleMaskFullSizeContentView)
                    ns_window.setTitlebarAppearsTransparent_(True)
                    ns_window.setTitleVisibility_(True)
            except Exception:
                pass
        
        self.vault = None
        self.salt = None
        self.current_account_id = ""
        self.master_pwd = ""
        self.password_visibility = {} 
        self.input_pass_visible = False
        self.login_master_visible = False
        self.dropdown_window = None
        self.animation_running = True

        self.eye_lines = [
            "⠐⢤⣀⣀⡀⠀⠀⠀⢀⣀⣀⣀⣀⣠⣤⣤⣤⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⠀⠀",
            "⡄⠀⠈⠛⠿⢿⡿⠟⠛⠛⠛⠛⠛⠛⠛⠉⠉⠉⠉⠉⠁⠀⠀⠈⠉⠉⠛⠻⡇⠀",
            "⢹⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⣴⣶⣶⣶⣶⣦⣄⠀⠀⠀⠁⠀",
            "⠀⢻⣿⣿⣶⣶⣦⣤⣤⣤⣤⣤⣶⣾⣿⣿⠿⠛⢋⣿⣿⣿⣿⡛⢿⣷⣄⠀⠀⠀",
            "⠀⠀⣿⣿⣿⡿⢿⣿⣿⣿⣿⣿⣿⣭⣁⡀⠀⠀⠸⣿⣿⣿⣿⠇⠀⣘⣿⣿⣦⡄",
            "⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠉⠉⠛⠿⢿⣿⣿⣶⣶⣿⣿⣿⣿⣶⣿⣿⡿⠿⠿⣇",
            "⠀⠀⠀⠀⠀⠀⠐⣶⣤⡀⠀⠀⠀⠀⠀⠀⠉⠙⠛⣻⣿⣿⣿⡟⠉⠀⠀⠀⠀⠀",
            "⠀⠀⠀⠀⢀⣶⡿⠿⢿⣿⡆⠀⠀⠀⠀⠀⠀⣀⣴⣿⣿⢿⣿⡅⢸⠀⠀⠀⠀⠀",
            "⠀⠀⠀⠀⣿⡏⠀⠀⠀⢹⠇⠀⠀⠀⢀⣠⣾⣿⡿⠋⠁⢸⣿⣿⡟⠀⠀⠀⠀⠀",
            "⠀⠀⠀⠀⢿⣷⡀⠀⠔⠋⢀⣀⣤⣶⣿⡿⠛⠁⠀⠀⠀⢸⣿⡟⠀⠀⠀⠀⠀⠀",
            "⠀⠀⠀⠀⠀⠙⠿⠿⣿⣿⡿⠿⠟⠋⠁⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀",
            "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⠀⠀⠀⠀⠀⠀⠀",
            "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡿⠿⠆⠀⠀⠀⠀⠀⠀"
        ]
        self.base_ascii_eye = "\n".join(self.eye_lines)

        self.show_splash_screen()

    def show_splash_screen(self):
        self.clear_window()
        self.splash_frame = ctk.CTkFrame(self, fg_color="#0A0A0C", corner_radius=0)
        self.splash_frame.pack(fill="both", expand=True)
        
        self.splash_eye = ctk.CTkLabel(self.splash_frame, text="", font=(FONT_NAME, 9, "bold"), text_color=NEON_COLOR, justify="center")
        self.splash_eye.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        
        self.splash_text = ctk.CTkLabel(self.splash_frame, text="", font=FONT_PIXEL_BIG, text_color="#0A0A0C")
        self.splash_text.place(relx=0.5, rely=0.75, anchor=tk.CENTER)
        
        self.splash_author = ctk.CTkLabel(self.splash_frame, text="", font=FONT_PIXEL_SMALL, text_color="#0A0A0C")
        self.splash_author.place(relx=0.5, rely=0.82, anchor=tk.CENTER)
        
        self.after(300, lambda: self.build_eye_matrix_slowly(0))

    def build_eye_matrix_slowly(self, current_line):
        if current_line <= len(self.eye_lines):
            visible_text = "\n".join(self.eye_lines[:current_line])
            self.splash_eye.configure(text=visible_text)
            self.after(180, lambda: self.build_eye_matrix_slowly(current_line + 1))
        else:
            self.after(400, lambda: self.trigger_splash_sequence(1))

    def trigger_splash_sequence(self, stage):
        if stage == 1:
            self.splash_text.configure(text=">> OSIRIS PASS <<", text_color=NEON_COLOR)
            self.splash_author.configure(text="powered by @xrlmop", text_color="#FFFFFF")
            self.after(1500, lambda: self.trigger_splash_sequence(2))
        elif stage == 2:
            self.show_login_screen()

    def animate_ascii_eye(self, step=0):
        if not self.animation_running or not hasattr(self, 'lbl_eye') or not self.lbl_eye.winfo_exists():
            return
        color_frames = [NEON_COLOR, "#00E695", "#00CC8A", "#00B37B", "#00CC8A", "#00E695"]
        current_color = color_frames[step % len(color_frames)]
        self.lbl_eye.configure(text_color=current_color)
        
        if step % 7 == 0:
            blinking_eye = self.base_ascii_eye.replace("⣿⣿⣿⣿⠇", "⣿⠶⠶⣿⠇")
            self.lbl_eye.configure(text=blinking_eye)
        else:
            self.lbl_eye.configure(text=self.base_ascii_eye)
            
        self.after(200, lambda: self.animate_ascii_eye(step + 1))

    def generate_26_digit_id(self):
        return ''.join(secrets.choice(string.digits) for _ in range(26))

    def generate_secure_master(self):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        secure_pwd = ''.join(secrets.choice(alphabet) for _ in range(24))
        
        self.entry_master.configure(state="normal")
        self.entry_master.delete(0, tk.END)
        self.entry_master.insert(0, secure_pwd)
        self.entry_master.configure(show="")
        self.login_master_visible = True
        self.btn_toggle_login_eye.configure(text="[-] ")
        
        self.clipboard_clear()
        self.clipboard_append(secure_pwd)
        self.show_notify("GENERATOR", "MASTER KEY GENERATED!\nCOPIED TO CLIPBOARD.")
        self.entry_master.focus_force()

    def create_new_account_inputs(self):
        new_id = self.generate_26_digit_id()
        current_accounts = backend.get_saved_accounts()
        if new_id not in current_accounts:
            current_accounts.append(new_id)
        
        backend.add_account_to_index(new_id)
        
        self.entry_account_display.configure(state="normal")
        self.entry_account_display.delete(0, tk.END)
        self.entry_account_display.insert(0, new_id)
        self.entry_account_display.configure(state="readonly")
        
        self.clipboard_clear()
        self.clipboard_append(new_id)
        self.show_notify("NEW ID", f"26-DIGIT DIGITAL ID CREATED!\n{new_id}\nCOPIED TO CLIPBOARD.")
        self.entry_master.focus_force()

    def copy_login_from_screen(self):
        text = self.entry_account_display.get().strip()
        if text and text not in ["SELECT OR CREATE ID", "CREATE NEW ID ->", ""]:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.show_notify("CLIPBOARD", "ACCOUNT ID COPIED!")

    def copy_master_from_screen(self):
        text = self.entry_master.get().strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.show_notify("CLIPBOARD", "MASTER KEY COPIED!")

    def toggle_login_password_visibility(self):
        self.login_master_visible = not self.login_master_visible
        if self.login_master_visible:
            self.entry_master.configure(show="")
            self.btn_toggle_login_eye.configure(text="[-] ")
        else:
            self.entry_master.configure(show="*")
            self.btn_toggle_login_eye.configure(text="[+] ")

    def show_custom_dropdown(self):
        if self.dropdown_window is not None:
            self.dropdown_window.destroy()
            self.dropdown_window = None
            return

        saved_accs = backend.get_saved_accounts()
        if not saved_accs:
            self.show_notify("MENU", "NO SAVED ACCOUNTS FOUND.\nUSE [GEN] TO CREATE ONE.")
            return

        self.dropdown_window = ctk.CTkToplevel(self)
        self.dropdown_window.overrideredirect(True)
        self.dropdown_window.configure(fg_color="#0A0A0C")
        
        x = self.entry_account_display.winfo_rootx()
        y = self.entry_account_display.winfo_rooty() + self.entry_account_display.winfo_height() + 2
        width = self.entry_account_display.winfo_width()
        height = min(len(saved_accs) * 32 + 6, 150)
        
        self.dropdown_window.geometry(f"{width}x{height}+{x}+{y}")
        self.dropdown_window.transient(self)
        self.dropdown_window.grab_set()

        menu_frame = ctk.CTkScrollableFrame(self.dropdown_window, width=width-4, height=height-4, fg_color="#0A0A0C", border_width=1, border_color=NEON_COLOR, corner_radius=0, label_text="")
        menu_frame.pack(fill="both", expand=True)

        for acc in saved_accs:
            btn_item = ctk.CTkButton(
                menu_frame, 
                text=acc, 
                font=FONT_PIXEL_SMALL, 
                anchor="w", 
                fg_color="#0A0A0C", 
                text_color=NEON_COLOR, 
                hover_color=NEON_COLOR,
                height=28,
                corner_radius=0,
                command=lambda a=acc: self.select_account_from_dropdown(a)
            )
            btn_item.bind("<Enter>", lambda e, b=btn_item: b.configure(fg_color=NEON_COLOR, text_color="#0A0A0C"))
            btn_item.bind("<Leave>", lambda e, b=btn_item: b.configure("#0A0A0C", text_color=NEON_COLOR))
            btn_item.pack(fill="x", pady=1)

    def select_account_from_dropdown(self, account_id):
        self.entry_account_display.configure(state="normal")
        self.entry_account_display.delete(0, tk.END)
        self.entry_account_display.insert(0, account_id)
        self.entry_account_display.configure(state="readonly")
        
        if self.dropdown_window:
            self.dropdown_window.destroy()
            self.dropdown_window = None
            
        self.entry_master.focus_force()
    def show_login_screen(self):
        self.clear_window()
        self.login_frame = ctk.CTkFrame(self, width=520, height=550, corner_radius=0, fg_color="#141419", border_width=2, border_color=NEON_COLOR)
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.lbl_eye = ctk.CTkLabel(self.login_frame, text=self.base_ascii_eye, font=("Courier", 8, "bold") if IS_MAC else ("Consolas", 8, "bold"), text_color=NEON_COLOR, justify="center")
        self.lbl_eye.pack(pady=(15, 0))
        self.animation_running = True
        self.animate_ascii_eye()
        label = ctk.CTkLabel(self.login_frame, text=">> OSIRIS PASS <<", font=FONT_PIXEL_BIG, text_color=NEON_COLOR)
        label.pack(pady=(5, 2))
        sub_label = ctk.CTkLabel(self.login_frame, text="DECENTRALIZED MULTI-VAULT KEEPER", font=FONT_PIXEL_SMALL, text_color="#8A8A93")
        sub_label.pack(pady=(0, 15))
        ctk.CTkLabel(self.login_frame, text="DIGITAL ACCOUNT ID:", font=FONT_PIXEL_SMALL, anchor="w", text_color=NEON_COLOR).pack(fill="x", padx=45)
        id_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        id_frame.pack(pady=5)
        saved_accs = backend.get_saved_accounts()
        default_val = saved_accs if saved_accs else "SELECT OR CREATE ID"
        self.entry_account_display = ctk.CTkEntry(id_frame, width=170, height=35, fg_color="#0A0A0C", border_color=NEON_COLOR, text_color=NEON_COLOR, font=FONT_PIXEL_SMALL, corner_radius=0)
        self.entry_account_display.insert(0, default_val)
        self.entry_account_display.configure(state="readonly")
        self.entry_account_display.pack(side="left", padx=(0, 2))
        btn_open_menu = ctk.CTkButton(id_frame, text="[V]", width=45, height=35, fg_color="#141419", hover_color=NEON_COLOR, text_color=NEON_COLOR, border_width=1, border_color=NEON_COLOR, font=FONT_PIXEL, corner_radius=0, command=self.show_custom_dropdown)
        btn_open_menu.bind("<Enter>", lambda e: btn_open_menu.configure(fg_color=NEON_COLOR, text_color="#0A0A0C"))
        btn_open_menu.bind("<Leave>", lambda e: btn_open_menu.configure(fg_color="#141419", text_color=NEON_COLOR))
        btn_open_menu.pack(side="left", padx=2)
        btn_gen_id = ctk.CTkButton(id_frame, text="[GEN]", width=55, height=35, fg_color="#141419", hover_color=NEON_COLOR, text_color=NEON_COLOR, border_width=1, border_color=NEON_COLOR, font=FONT_PIXEL, corner_radius=0, command=self.create_new_account_inputs)
        btn_gen_id.bind("<Enter>", lambda e: btn_gen_id.configure(fg_color=NEON_COLOR, text_color="#0A0A0C"))
        btn_gen_id.bind("<Leave>", lambda e: btn_gen_id.configure(fg_color="#141419", text_color=NEON_COLOR))
        btn_gen_id.pack(side="left", padx=2)
        btn_copy_id = ctk.CTkButton(id_frame, text="[CP]", width=45, height=35, fg_color="#141419", hover_color=NEON_COLOR, text_color=NEON_COLOR, border_width=1, border_color=NEON_COLOR, font=FONT_PIXEL, corner_radius=0, command=self.copy_login_from_screen)
        btn_copy_id.bind("<Enter>", lambda e: btn_copy_id.configure(fg_color=NEON_COLOR, text_color="#0A0A0C"))
        btn_copy_id.bind("<Leave>", lambda e: btn_copy_id.configure(fg_color="#141419", text_color=NEON_COLOR))
        btn_copy_id.pack(side="left")
        ctk.CTkLabel(self.login_frame, text="MASTER-PASSWORD:", font=FONT_PIXEL_SMALL, anchor="w", text_color=NEON_COLOR).pack(fill="x", padx=45, pady=(12, 0))
        master_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        master_frame.pack(pady=5)
        self.entry_master = ctk.CTkEntry(master_frame, placeholder_text="ENTER MASTER KEY", show="*", width=220, height=35, fg_color="#0A0A0C", border_color=NEON_COLOR, text_color=NEON_COLOR, font=FONT_PIXEL, corner_radius=0, placeholder_text_color="#454554")
        self.entry_master.pack(side="left", padx=(0, 5))
        self.entry_master.bind("<Button-1>", lambda event: self.entry_master.focus_force())
        self.btn_toggle_login_eye = ctk.CTkButton(master_frame, text="[+] ", width=55, height=35, fg_color="#141419", hover_color=NEON_COLOR, text_color=NEON_COLOR, border_width=1, border_color=NEON_COLOR, font=FONT_PIXEL, corner_radius=0, command=self.toggle_login_password_visibility)
        self.btn_toggle_login_eye.bind("<Enter>", lambda e: self.btn_toggle_login_eye.configure(fg_color=NEON_COLOR, text_color="#0A0A0C"))
        self.btn_toggle_login_eye.bind("<Leave>", lambda e: self.btn_toggle_login_eye.configure(fg_color="#141419", text_color=NEON_COLOR))
        self.btn_toggle_login_eye.pack(side="left", padx=2)
        btn_copy_master = ctk.CTkButton(master_frame, text="[CP]", width=45, height=35, fg_color="#141419", hover_color=NEON_COLOR, text_color=NEON_COLOR, border_width=1, border_color=NEON_COLOR, font=FONT_PIXEL, corner_radius=0, command=self.copy_master_from_screen)
        btn_copy_master.bind("<Enter>", lambda e: btn_copy_master.configure(fg_color=NEON_COLOR, text_color="#0A0A0C"))
        btn_copy_master.bind("<Leave>", lambda e: btn_copy_master.configure(fg_color="#141419", text_color=NEON_COLOR))
        btn_copy_master.pack(side="left")
        btn_gen_master = ctk.CTkButton(self.login_frame, text="[ GENERATE MASTER PASSWORD ]", width=340, height=30, fg_color="#141419", hover_color=NEON_COLOR, text_color=NEON_COLOR, border_width=1, border_color=NEON_COLOR, font=FONT_PIXEL, corner_radius=0, command=self.generate_secure_master)
        btn_gen_master.bind("<Enter>", lambda e: btn_gen_master.configure(fg_color=NEON_COLOR, text_color="#0A0A0C"))
        btn_gen_master.bind("<Leave>", lambda e: btn_gen_master.configure(fg_color="#141419", text_color=NEON_COLOR))
        btn_gen_master.pack(pady=12)
        btn_login = ctk.CTkButton(self.login_frame, text="[ PASS ]", width=340, height=45, font=FONT_PIXEL, fg_color="#0A0A0C", hover_color=NEON_COLOR, text_color=NEON_COLOR, border_width=1, border_color=NEON_COLOR, corner_radius=0, command=self.attempt_login)
        btn_login.bind("<Enter>", lambda e: btn_login.configure(fg_color=NEON_COLOR, text_color="#0A0A0C"))
        btn_login.bind("<Leave>", lambda e: btn_login.configure(fg_color="#0A0A0C", text_color=NEON_COLOR))
        btn_login.pack(pady=5)
        btn_delete_acc = ctk.CTkButton(self.login_frame, text="[ WIPE / DELETE ACCOUNT ]", width=340, height=30, font=FONT_PIXEL_SMALL, fg_color="#141419", hover_color=ALERT_COLOR, text_color=ALERT_COLOR, border_width=1, border_color=ALERT_COLOR, corner_radius=0, command=self.delete_account_trigger)
        btn_delete_acc.bind("<Enter>", lambda e: btn_delete_acc.configure(fg_color=ALERT_COLOR, text_color="#FFFFFF"))
        btn_delete_acc.bind("<Leave>", lambda e: btn_delete_acc.configure(fg_color="#141419", text_color=ALERT_COLOR))
        btn_delete_acc.pack(pady=(5, 5))
        lbl_watermark = ctk.CTkLabel(self.login_frame, text="powered by @xrlmop", font=FONT_PIXEL_SMALL, text_color="#454554")
        lbl_watermark.pack(side="bottom", pady=5)
        self.update()
    def delete_account_trigger(self):
        target_id = self.entry_account_display.get().strip()
        if target_id in ["SELECT OR CREATE ID", "CREATE NEW ID ->", ""]:
            self.show_notify("WIPE ERROR", "SELECT A VALID ID TO WIPE.")
            return
        def confirm_wipe():
            backend.delete_account_from_system(target_id)
            self.show_notify("WIPE SUCCESS", "ACCOUNT WIPED COMPLETELY.")
            self.show_login_screen()
        self.show_confirm("CRITICAL WARNING", f"WIPE ALL DATA FOR ID:\n{target_id}\n\nTHIS CANNOT BE UNDONE!", confirm_wipe)

    def attempt_login(self):
        acc_id = self.entry_account_display.get().strip()
        pwd = self.entry_master.get().strip()
        app_context = self
        if acc_id in ["SELECT OR CREATE ID", "CREATE NEW ID ->", ""]:
            app_context.show_notify("ACCESS DENIED", "CHOOSE OR GENERATE A VALID ACCOUNT ID!")
            return
        if not pwd:
            app_context.show_notify("ACCESS DENIED", "MASTER KEY CANNOT BE EMPTY!")
            return
        def run_crypto_in_background():
            vault, salt = backend.load_vault(acc_id, pwd)
            app_context.after(0, lambda: handle_crypto_result(vault, salt))
        def handle_crypto_result(vault, salt):
            if vault is None:
                app_context.show_notify("ERROR", "DECRYPTION FAILED! WRONG MASTER KEY.")
            else:
                app_context.animation_running = False  
                app_context.vault = vault
                app_context.salt = salt
                app_context.current_account_id = acc_id
                app_context.master_pwd = pwd
                app_context.show_main_screen()
        threading.Thread(target=run_crypto_in_background, daemon=True).start()

    def show_main_screen(self):
        self.clear_window()
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        left_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#141419", border_width=1, border_color="#1f1f29")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        ctk.CTkLabel(left_frame, text="ACTIVE TERMINAL ID:", font=FONT_PIXEL_SMALL, text_color="#8A8A93").pack(pady=(15, 0))
        lbl_id = ctk.CTkLabel(left_frame, text=f"ID: {self.current_account_id[:10]}...", font=FONT_PIXEL, text_color=NEON_COLOR)
        lbl_id.pack(pady=(0, 15))
        ctk.CTkLabel(left_frame, text="ADD RECORD", font=FONT_PIXEL, text_color=NEON_COLOR).pack(pady=10)
        self.entry_site = ctk.CTkEntry(left_frame, placeholder_text="SITE / APP NAME", width=220, height=35, fg_color="#0A0A0C", border_color=NEON_COLOR, font=FONT_PIXEL, corner_radius=0, text_color=NEON_COLOR, placeholder_text_color="#454554")
        self.entry_site.pack(pady=6)
        self.entry_login = ctk.CTkEntry(left_frame, placeholder_text="LOGIN / EMAIL", width=220, height=35, fg_color="#0A0A0C", border_color=NEON_COLOR, font=FONT_PIXEL, corner_radius=0, text_color=NEON_COLOR, placeholder_text_color="#454554")
        self.entry_login.pack(pady=6)
        pass_input_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        pass_input_frame.pack(pady=6)
        self.entry_pass = ctk.CTkEntry(pass_input_frame, placeholder_text="PASSWORD", show="*", width=175, height=35, fg_color="#0A0A0C", border_color=NEON_COLOR, font=FONT_PIXEL, corner_radius=0, text_color=NEON_COLOR, placeholder_text_color="#454554")
        self.entry_pass.pack(side="left", padx=(0, 5))
        self.entry_pass.bind("<Button-1>", lambda event: self.entry_pass.focus_force())
        self.btn_toggle_input_eye = ctk.CTkButton(pass_input_frame, text="[+]", width=40, height=35, fg_color="#0A0A0C", border_width=1, border_color=NEON_COLOR, hover_color=NEON_COLOR, text_color=NEON_COLOR, font=FONT_PIXEL, corner_radius=0, command=self.toggle_input_password_visibility)
        self.btn_toggle_input_eye.bind("<Enter>", lambda e: self.btn_toggle_input_eye.configure(fg_color=NEON_COLOR, text_color="#0A0A0C"))
        self.btn_toggle_input_eye.bind("<Leave>", lambda e: self.btn_toggle_input_eye.configure(fg_color="#0A0A0C", text_color=NEON_COLOR))
        self.btn_toggle_input_eye.pack(side="left")
        btn_gen = ctk.CTkButton(left_frame, text="[GEN PASSWORD]", width=220, height=30, fg_color="#0A0A0C", text_color=NEON_COLOR, border_width=1, border_color=NEON_COLOR, hover_color="#141419", font=FONT_PIXEL_SMALL, corner_radius=0, command=self.generate_random_password)
        btn_gen.bind("<Enter>", lambda e: btn_gen.configure(fg_color=NEON_COLOR, text_color="#0A0A0C"))
        btn_gen.bind("<Leave>", lambda e: btn_gen.configure(fg_color="#0A0A0C", text_color=NEON_COLOR))
        btn_gen.pack(pady=4)
        btn_add = ctk.CTkButton(left_frame, text="[ ENCRYPT & SAVE ]", width=220, height=40, font=FONT_PIXEL, fg_color="#0A0A0C", hover_color=NEON_COLOR, text_color=NEON_COLOR, border_width=1, border_color=NEON_COLOR, corner_radius=0, command=self.add_password)
        btn_add.bind("<Enter>", lambda e: btn_add.configure(fg_color=NEON_COLOR, text_color="#0A0A0C"))
        btn_add.bind("<Leave>", lambda e: btn_add.configure(fg_color="#0A0A0C", text_color=NEON_COLOR))
        btn_add.pack(pady=20)
        btn_lock = ctk.CTkButton(left_frame, text="[ LOCK VAULT ]", width=220, height=35, fg_color="#141419", hover_color=ALERT_COLOR, text_color=ALERT_COLOR, font=FONT_PIXEL, border_width=1, border_color=ALERT_COLOR, corner_radius=0, command=self.show_login_screen)
        btn_lock.bind("<Enter>", lambda e: btn_lock.configure(fg_color=ALERT_COLOR, text_color="#FFFFFF"))
        btn_lock.bind("<Leave>", lambda e: btn_lock.configure(fg_color="#141419", text_color=ALERT_COLOR))
        btn_lock.pack(side="bottom", pady=20)
        self.right_frame = ctk.CTkScrollableFrame(self, label_text="SECURED RECORDS INDEX", label_font=FONT_PIXEL, label_text_color=NEON_COLOR, fg_color="#0A0A0C", corner_radius=0)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self.refresh_password_list()
        self.update()
        self.focus_force()
    def toggle_input_password_visibility(self):
        self.input_pass_visible = not self.input_pass_visible
        if self.input_pass_visible:
            self.entry_pass.configure(show="")
            self.btn_toggle_input_eye.configure(text="[-]")
        else:
            self.entry_pass.configure(show="*")
            self.btn_toggle_input_eye.configure(text="[+]")

    def generate_random_password(self):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        generated_password = ''.join(secrets.choice(alphabet) for _ in range(16))
        self.entry_pass.delete(0, tk.END)
        self.entry_pass.insert(0, generated_password)
        if not self.input_pass_visible:
            self.toggle_visibility_forced(True)

    def toggle_visibility_forced(self, make_visible):
        self.input_pass_visible = make_visible
        self.entry_pass.configure(show="" if make_visible else "*")
        self.btn_toggle_input_eye.configure(text="[-]" if make_visible else "[+]")

    def refresh_password_list(self):
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        if not self.vault:
            empty_lbl = ctk.CTkLabel(self.right_frame, text="INDEX EMPTY. ADD RECORD VIA TERMINAL.", font=FONT_PIXEL_SMALL, text_color="gray")
            empty_lbl.pack(pady=40)
            return
        for site, creds in self.vault.items():
            if site not in self.password_visibility:
                self.password_visibility[site] = False
            item_frame = ctk.CTkFrame(self.right_frame, fg_color="#141419", corner_radius=0, border_width=1, border_color=NEON_COLOR)
            item_frame.pack(fill="x", pady=6, padx=5)
            info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            info_frame.pack(side="left", padx=15, pady=10, fill="both", expand=True)
            display_pass = creds['password'] if self.password_visibility[site] else "••••••••••••••••"
            ctk.CTkLabel(info_frame, text=f"TARGET: {site.upper()}", font=FONT_PIXEL, anchor="w", text_color=NEON_COLOR).pack(fill="x", pady=2)
            ctk.CTkLabel(info_frame, text=f"LOGIN:  {creds['login']}", font=FONT_PIXEL_SMALL, anchor="w", text_color="#FFFFFF").pack(fill="x")
            ctk.CTkLabel(info_frame, text=f"KEY:    {display_pass}", font=FONT_PIXEL_SMALL, anchor="w", text_color="#FFFFFF").pack(fill="x")
            actions_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            actions_frame.pack(side="right", padx=10)
            eye_char = "[SHOW]" if not self.password_visibility[site] else "[HIDE]"
            btn_eye = ctk.CTkButton(actions_frame, text=eye_char, width=55, height=32, fg_color="#0A0A0C", border_width=1, border_color="#33333f", hover_color=NEON_COLOR, text_color=NEON_COLOR, font=FONT_PIXEL_SMALL, corner_radius=0, command=lambda s=site: self.toggle_visibility(s))
            btn_eye.bind("<Enter>", lambda e, b=btn_eye: b.configure(fg_color=NEON_COLOR, text_color="#0A0A0C"))
            btn_eye.bind("<Leave>", lambda e, b=btn_eye: b.configure("#0A0A0C", text_color=NEON_COLOR))
            btn_eye.pack(side="left", padx=2)
            btn_cp_log = ctk.CTkButton(actions_frame, text="[CP LOG]", width=70, height=32, fg_color="#0A0A0C", border_width=1, border_color=NEON_COLOR, hover_color=NEON_COLOR, text_color=NEON_COLOR, font=FONT_PIXEL_SMALL, corner_radius=0, command=lambda l=creds['login'], app=self: app.copy_to_clipboard(l, "LOGIN"))
            btn_cp_log.bind("<Enter>", lambda e, b=btn_cp_log: b.configure(fg_color=NEON_COLOR, text_color="#0A0A0C"))
            btn_cp_log.bind("<Leave>", lambda e, b=btn_cp_log: b.configure("#0A0A0C", text_color=NEON_COLOR))
            btn_cp_log.pack(side="left", padx=2)
            btn_cp_key = ctk.CTkButton(actions_frame, text="[CP KEY]", width=70, height=32, fg_color="#0A0A0C", border_width=1, border_color=NEON_COLOR, hover_color=NEON_COLOR, text_color=NEON_COLOR, font=FONT_PIXEL_SMALL, corner_radius=0, command=lambda p=creds['password'], app=self: app.copy_to_clipboard(p, "KEY"))
            btn_cp_key.bind("<Enter>", lambda e, b=btn_cp_key: b.configure(fg_color=NEON_COLOR, text_color="#0A0A0C"))
            btn_cp_key.bind("<Leave>", lambda e, b=btn_cp_key: b.configure("#0A0A0C", text_color=NEON_COLOR))
            btn_cp_key.pack(side="left", padx=2)
            btn_del = ctk.CTkButton(actions_frame, text="[X]", width=35, height=32, fg_color="#141419", border_width=1, border_color=ALERT_COLOR, hover_color=ALERT_COLOR, text_color=ALERT_COLOR, font=FONT_PIXEL, corner_radius=0, command=lambda s=site, app=self: app.delete_password_trigger(s))
            btn_del.bind("<Enter>", lambda e, b=btn_del: b.configure(fg_color=ALERT_COLOR, text_color="#FFFFFF"))
            btn_del.bind("<Leave>", lambda e, b=btn_del: b.configure("#141419", text_color=ALERT_COLOR))
            btn_del.pack(side="left", padx=2)

    def toggle_visibility(self, site):
        self.password_visibility[site] = not self.password_visibility[site]
        self.refresh_password_list()

    def copy_to_clipboard(self, text, type_name):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.show_notify("SUCCESS", f"{type_name} COPIED!")

    def add_password(self):
        site = self.entry_site.get().strip()
        login = self.entry_login.get().strip()
        pwd = self.entry_pass.get().strip()
        if not site or not login or not pwd:
            self.show_notify("VALIDATION ERROR", "ALL TERMINAL FIELDS MUST BE FILLED.")
            return
        self.vault[site] = {"login": login, "password": pwd}
        backend.save_vault(self.current_account_id, self.master_pwd, self.salt, self.vault)
        self.entry_site.delete(0, tk.END)
        self.entry_login.delete(0, tk.END)
        self.entry_pass.delete(0, tk.END)
        self.toggle_visibility_forced(False)
        self.refresh_password_list()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_notify(self, title, message):
        NeonNotification(self, title, message)

    def show_confirm(self, title, message, callback):
        NeonConfirmDialog(self, title, message, callback)

if __name__ == "__main__":
    app = PasswordManagerApp()
    app.mainloop()
