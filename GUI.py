from tkinter import filedialog
from tkinter import *
from tkinter.messagebox import *
from tkinter import ttk
from PIL import Image, ImageTk
from os.path import basename
import os




class Interface(Frame):
	
	"""Notre fenêtre principale.
	Tous les widgets sont stockés comme attributs de cette fenêtre."""
	
	def __init__(self, fenetre,bg='#33FFD8', **kwargs):
		self.color=StringVar()
		self.color='#33FFD8'
		self.color_button='#334DFF'

		Frame.__init__(self, fenetre, width=768, height=576,bg=self.color, **kwargs)

		self.pack()


		self.title_label = Label(self, text="Monomolecular reduction tool, \nthis tool reduce the model based on 4 reduction rules",font=("Helvetica",15),bg=self.color)
		self.title_label.pack(pady=30,padx=30)

		################################################################################################################
		# Starting model part
		################################################################################################################


		self.frame1=LabelFrame(self,relief='groove',bg=self.color,bd=5,text="Starting model")
		self.frame1.pack(fill=BOTH, pady=30,padx=40)
		#self.frame1.grid(row=0, column=2, columnspan=3, )


		#Input file selection
		self.inputFile_label = Label(self.frame1, text="Choose model file :",font=("Helvetica"),bg=self.color)
		self.inputFile_label.grid(row=2,column=0,pady=10,padx=10)

		self.inputFile_button = Button(self.frame1, text="Browse...", command=self.cliquerFile,font=("Helvetica"),bg=self.color_button)
		self.inputFile_button.grid(row=2, column=1,pady=10,padx=20)

		self.labelFile=Label(self.frame1,text="",bg=self.color)
		self.labelFile.grid(row=2,column=2)


		self.inputFile_label = Label(self.frame1, text="Vizualise :",font=("Helvetica"),bg=self.color)
		self.inputFile_label.grid(row=3,column=0,pady=10,padx=10)		

		self.charge_network = Button(self.frame1, text="Network", command=self.cliquerNetwork,font=("Helvetica"),bg=self.color_button,state=DISABLED)
		self.charge_network.grid(row=3, column=1,pady=20,padx=20)

		
		self.charge_simulation = Button(self.frame1, text="Simulation", command=self.cliquerSimulation,font=("Helvetica"),bg=self.color_button,state=DISABLED)
		self.charge_simulation.grid(row=3, column=2,pady=20,padx=20)

		self.reduce = Button(self.frame1, text="Reduce model", command=self.cliquerResult,font=("Helvetica"),bg=self.color_button,state=DISABLED)
		self.reduce.grid(row=4, column=1,pady=20,padx=20)

		################################################################################################################
		# Reduced model part
		################################################################################################################

		self.frame2=LabelFrame(self,relief='groove',bg=self.color,bd=5,text="Reduced model")
		self.frame2.pack(side="bottom",fill=BOTH,pady=(0,50),padx=40)
		#self.frame2.grid(row=7, column=2, columnspan=3, )

		self.inputFile_label = Label(self.frame2, text="Vizualise :",font=("Helvetica"),bg=self.color)
		self.inputFile_label.grid(row=3,column=0,pady=10,padx=10)		

		self.charge_network_reduced = Button(self.frame2, text="Network", command=self.cliquerResult,font=("Helvetica"),bg=self.color_button,state=DISABLED)
		self.charge_network_reduced.grid(row=3, column=1,pady=20,padx=20)

		
		self.charge_reduced_simulation = Button(self.frame2, text="Simulation", command=self.cliquerSimulationReduced,font=("Helvetica"),bg=self.color_button,state=DISABLED)
		self.charge_reduced_simulation.grid(row=3, column=2,pady=20,padx=20)


		################################################################################################################
		# Defined button functions
		################################################################################################################	


		#Function to select file
	def cliquerFile(self):        
		self.filename =  filedialog.askopenfilename(initialdir = "/HOME",title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
		self.labelFile.configure(text=basename(self.filename))
		self.charge_network.configure(state=NORMAL)
		self.charge_simulation.configure(state=NORMAL)
		self.reduce.configure(state=NORMAL)

	def cliquerSimulation(self):
		os.system("python3 simulate.py "+self.filename+" 5")
		result=Toplevel(master=fenetre,bg='red')
		imageo=Image.open(self.filename+".png")
		resultsimu= ImageTk.PhotoImage(imageo,width=1000,height=1200)
		canva=Canvas(result,width=resultsimu.width(),height=resultsimu.height())
		canva.create_image(0,0,anchor=NW,image=resultsimu)
		canva.image=resultsimu
		canva.pack(fill=BOTH)


		
		
		# Load simulation image
	def cliquerResult(self):
		# Reduce the model
		os.system("python3 reduction.py "+self.filename)
		#able network and simulation vizualisation
		self.charge_network_reduced.configure(state=NORMAL)
		self.charge_reduced_simulation.configure(state=NORMAL)

	def cliquerSimulationReduced(self):
		os.system("python3 simulate.py "+self.filename+"_reduced.tsv 5")
		result=Toplevel(master=fenetre,bg='red')
		imageo=Image.open(self.filename+"_reduced.tsv.png")
		resultsimu= ImageTk.PhotoImage(imageo,width=1000,height=1200)
		canva=Canvas(result,width=resultsimu.width(),height=resultsimu.height())
		canva.create_image(0,0,anchor=NW,image=resultsimu)
		canva.image=resultsimu
		canva.pack(fill=BOTH)



		



if __name__ == "__main__":
	fenetre = Tk()
	interface = Interface(fenetre)
	fenetre.title("Monomolecular reduction tool")
	interface.mainloop()
	