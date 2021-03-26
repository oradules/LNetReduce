from tkinter import filedialog
from tkinter import *
from tkinter.messagebox import *
from tkinter import ttk
from PIL import Image, ImageTk




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

				#Input file selection
		self.inputFile_label = Label(self, text="Choose model file :",font=("Helvetica"),)
		self.inputFile_label.grid(row=2,column=0,pady=10)

		self.inputFile_button = Button(self, text="Browse...", command=self.cliquerFile,font=("Helvetica"))
		self.inputFile_button.grid(row=2, column=2,pady=10)


		self.change_page = Button(self, text="Simulation of the reduced model", command=self.cliquerResult,font=("Helvetica"))
		self.change_page.grid(row=3, column=0,pady=10)

		#Function to select file
	def cliquerFile(self):        
		self.filename =  filedialog.askopenfilename(initialdir = "/HOME",title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
		self.labelFile.configure(text=self.filename)

	def cliquerResult(self):
		result=Toplevel(master=fenetre,bg='red')
		imageo=Image.open("input_file.png")
		resultsimu= ImageTk.PhotoImage(imageo)
		canva=Canvas(result,width=resultsimu.width(),height=resultsimu.height())
		canva.create_image(0,0,anchor=NW,image=resultsimu)
		canva.image=resultsimu
		canva.pack()

		





if __name__ == "__main__":
	fenetre = Tk()
	interface = Interface(fenetre)
	fenetre.title("Monomolecular reduction tool")
	interface.mainloop()
	