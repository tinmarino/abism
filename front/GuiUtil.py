
def About():
    """Pop about window"""
    tk = Tk()
    tk.title("About Abism")
    txt = ("Adaptive Background Interactive Strehl Meter\n"
           "ABISM version " + G.version + " (2013 -- 2020) \n"
           "Authors: Girard Julien, Tourneboeuf Martin\n"
           "Emails: juliengirard@gmail.com tinmarino@gmail.com\n")
    l1 = Label(tk, text=txt)
    l1.pack()
    tk.mainloop()


