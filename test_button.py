import tkinter as tk

class DemoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Button Relief Demo")

        self.create_widgets()

    def create_widgets(self):
        self.button = tk.Button(self, text="Click me!", width=10, height=2)
        self.button.grid(row=0, column=0, padx=10, pady=10)

        # Bind the Button-1 event to the on_button_click function
        self.button.bind('<Button-1>', self.on_button_click)

    def on_button_click(self, event):
        # Change the button's relief to FLAT when clicked
        self.button.config(relief=tk.FLAT)

if __name__ == "__main__":
    app = DemoApp()
    app.mainloop()
