from tkinter import filedialog
from tkinter import *
from tkinter.messagebox import *
from tkinter import ttk




class Interface(Frame):
	
	"""Notre fenêtre principale.
	Tous les widgets sont stockés comme attributs de cette fenêtre."""
	
	def __init__(self, fenetre, **kwargs):

		Frame.__init__(self, fenetre, width=768, height=576, **kwargs)

		self.pack(fill=BOTH)
		#todo nicer windows
		#self.config(background='#41B77F')

		self.frame1=Frame(self,relief=GROOVE)
		self.frame1.grid(row=0, column=2, columnspan=3, rowspan=19)


		self.title_label = Label(self, text="Monomolecular reduction tool",font=("Helvetica",20),)
		self.title_label.grid(row=1,column=0,pady=10)


if __name__ == "__main__":
	fenetre = Tk()
	interface = Interface(fenetre)
	interface.mainloop()
	interface.destroy()