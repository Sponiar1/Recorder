from gui import *
import ttkbootstrap as ttk

def main():
    root = ttk.Window(themename="darkly")
    app = GUI(root)
    app.run()


if __name__ == "__main__":
    main()