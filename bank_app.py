import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from bank_db import Database

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class BankApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = Database("bank.db")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 600
        window_height = 440
        posx = int((screen_width / 2) - (window_width / 2))
        posy = int((screen_height / 2) - (window_height / 2))
        self.title("AI Bank")
        self.geometry(f"{window_width}x{window_height}+{posx}+{posy}")
        self.minsize(window_width, window_height)
        self.switch_frame(LoginScreen)

    def switch_frame(self, new_frame):
        if hasattr(self, 'current_frame'):
            self.current_frame.destroy()
        self.current_frame = new_frame(self)
        self.current_frame.place(relx=0.5, rely=0.5, anchor="center")

class LoginScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.grid_columnconfigure(0, weight=1)
        self.create_widgets()

    def create_widgets(self):
        self.lbl_title = ctk.CTkLabel(self, text="Log Into Your Account", font=("Century Gothic", 20))
        self.lbl_message = ctk.CTkLabel(self, text="", font=("Arial", 12), justify="left", wraplength=220)
        self.ent_username = ctk.CTkEntry(self, placeholder_text="Username", width=220)
        self.ent_password = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=220)
        self.btn_login = ctk.CTkButton(self, text="Login", width=220, command=self.login)
        self.btn_create_account = ctk.CTkButton(self, text="Create Account", width=220, command=self.create_account)

        self.lbl_title.grid(row=0, column=0, padx=(50), pady=(50, 10))
        self.lbl_message.grid(row=1, column=0, padx=(50), pady=(10, 0), sticky="w")
        self.ent_username.grid(row=2, column=0, padx=(50), pady=(0, 10))
        self.ent_password.grid(row=3, column=0, padx=(50), pady=(10, 10))
        self.btn_login.grid(row=4, column=0, padx=(50), pady=(20, 10))
        self.btn_create_account.grid(row=5, column=0, padx=(50), pady=(0, 50))

    def create_account(self):
        username = self.ent_username.get()
        password = self.ent_password.get()
        try:
            self.parent.db.register(username, password)
            self.lbl_message.configure(text="Account Created Successfully", text_color="green")
        except ValueError as e:
            self.lbl_message.configure(text=str(e), text_color="red")
    
    def login(self):
        username = self.ent_username.get()
        password = self.ent_password.get()
        user_id = self.parent.db.login(username, password)
        if user_id:
            self.parent.current_user_id = user_id
            self.parent.switch_frame(MainScreen)
        else:
            self.lbl_message.configure(text="*Invalid Username or Password", text_color="red")

class MainScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.grid_columnconfigure(0, weight=1)
        self.create_widgets()

    def create_widgets(self):
        self.btn_check_balance = ctk.CTkButton(self, text="Check Balance", width=220, command=self.show_balance)
        self.btn_deposit = ctk.CTkButton(self, text="Deposit", width=220, command=self.show_deposit)
        self.btn_withdraw = ctk.CTkButton(self, text="Withdraw", width=220, command=self.show_withdraw)
        self.btn_transfer = ctk.CTkButton(self, text="Transfer", width=220, command=self.show_transfer)
        self.btn_logout = ctk.CTkButton(self, text="Logout", width=220, command=self.logout)

        self.btn_check_balance.grid(row=0, column=0, padx=(50), pady=(50, 10))
        self.btn_deposit.grid(row=1, column=0, padx=(50), pady=(10, 10))
        self.btn_withdraw.grid(row=2, column=0, padx=(50), pady=(10, 10))
        self.btn_transfer.grid(row=3, column=0, padx=(50), pady=(10, 10))
        self.btn_logout.grid(row=4, column=0, padx=(50), pady=(10, 50))

    def show_balance(self):
        self.parent.switch_frame(BalanceFrame)

    def show_deposit(self):
        self.parent.switch_frame(DepositFrame)

    def show_withdraw(self):
        self.parent.switch_frame(WithdrawFrame)

    def show_transfer(self):
        self.parent.switch_frame(TransferFrame)

    def logout(self):
        self.parent.current_user_id = None
        self.parent.switch_frame(LoginScreen)

#region MainScreen Subframes
class BankingOperationFrame(ctk.CTkFrame):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.parent = parent
        self.lbl_title = ctk.CTkLabel(self, text=title, font=("Century Gothic", 20))
        self.btn_back = ctk.CTkButton(self, text="Back to Main Menu", command=self.back_to_main)

        self.lbl_title.pack(padx=50, pady=(50, 20))
        self.btn_back.pack(padx=50, pady=(10, 50), side="bottom")

    def back_to_main(self):
        self.parent.switch_frame(MainScreen)

    def only_digits(self, text):
        return text.isdigit() or text == ""
    
    def apply_digit_validation(self, entry_widget):
        entry_widget.configure(validate="key", validatecommand=(self.register(self.only_digits), "%P"))


class BalanceFrame(BankingOperationFrame):
    def __init__(self, parent, title="INFO"):
        super().__init__(parent, title)
        balance = self.parent.db.get_balance(self.parent.current_user_id)
        self.lbl_info = ctk.CTkLabel(self, text=f"{self.parent.current_user_id} ${balance:,.2f}", font= ("Century Gothic", 18))

        self.lbl_info.pack(pady=10)
        
class DepositFrame(BankingOperationFrame):
    def __init__(self, parent):
        super().__init__(parent, "DEPOSIT")
        self.ent_amount = ctk.CTkEntry(self, placeholder_text="Enter amount ($)")
        self.btn_confirm = ctk.CTkButton(self, text="Confirm", command=self.deposit)

        self.ent_amount.pack(pady=10)
        self.btn_confirm.pack(pady=10)

        self.apply_digit_validation(self.ent_amount)

    def deposit(self):
        amount = float(self.ent_amount.get())
        self.parent.db.deposit(self.parent.current_user_id, amount)
        CTkMessagebox(title="Success", message=f"Successfully deposited ${amount:,.2f}")
        self.back_to_main()

class WithdrawFrame(BankingOperationFrame):
    def __init__(self, parent):
        super().__init__(parent, "WITHDRAW")
        self.ent_amount = ctk.CTkEntry(self, placeholder_text="Enter amount ($)")
        self.btn_confirm = ctk.CTkButton(self, text="Confirm", command=self.withdraw)
        
        self.ent_amount.pack(pady=10)
        self.btn_confirm.pack(pady=10)

        self.apply_digit_validation(self.ent_amount)

    def withdraw(self):
        try:
            amount = float(self.ent_amount.get())
            updated_amount = self.parent.db.withdraw(self.parent.current_user_id, amount)
            CTkMessagebox(title="Success", message=f"Successfully withdrew ${amount:,.2f}\nRemaining balance: ${updated_amount:,.2f}")
            self.back_to_main()
        except ValueError as e:
            CTkMessagebox(title="Error", message=str(e), icon="cancel")

class TransferFrame(BankingOperationFrame):
    def __init__(self, parent):
        super().__init__(parent, "TRANSFER")
        self.ent_amount = ctk.CTkEntry(self,width=220, placeholder_text="Enter amount ($)")
        self.ent_recipient = ctk.CTkEntry(self, width=220, placeholder_text="Enter recipient acc number")
        self.btn_transfer = ctk.CTkButton(self, text="Confirm", command=self.transfer)

        self.ent_amount.pack(padx = 50, pady = 10)
        self.ent_recipient.pack(padx = 50, pady = 10)
        self.btn_transfer.pack(padx = 50, pady = 10)

        self.apply_digit_validation(self.ent_amount)
        self.apply_digit_validation(self.ent_recipient)

    def transfer(self):
        try:
            amount = float(self.ent_amount.get())
            recipient_id = self.ent_recipient.get()
            recipient_username = self.parent.db.transfer(self.parent.current_user_id, recipient_id, amount)
            CTkMessagebox(title="Success", message=f"Successfully transferred ${amount:,.2f} to {recipient_username}")
            self.back_to_main()
        except ValueError as e:
            CTkMessagebox(title="Error", message=str(e), icon="cancel")
#endregion

if __name__ == "__main__":
    app = BankApp()
    app.mainloop()