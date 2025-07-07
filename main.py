import tkinter as tk
from gui import *

def main():
    root = tk.Tk()
    app = GUI(root)
    app.run()


if __name__ == "__main__":
    main()