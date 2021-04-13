from tkinter import filedialog
from tkinter import *
from tkinter.messagebox import *
from tkinter import ttk
from PIL import Image, ImageTk
from os.path import basename
import os
from simulate import *
from reduction import *




class Interface(Frame):
	global filename
	global Timescale_value

	
	"""Notre fenêtre principale.
	Tous les widgets sont stockés comme attributs de cette fenêtre."""
	
	def __init__(self, fenetre,bg='#ADB7FA', **kwargs):
		self.color=StringVar()
		self.color='#ADB7FA'
		self.color_button='#334DFF'
		filename=StringVar()
		Timescale_value=IntVar()
		 

		Frame.__init__(self, fenetre, width=768, height=576,bg=self.color, **kwargs)

		self.pack()


		self.title_label = Label(self, text="LNetReduce: \n tool for reducing linear reaction networks \n with separated time scales",font=("Helvetica",14),bg=self.color)
		self.title_label.pack(pady=30,padx=30)

		################################################################################################################
		# Starting model part
		################################################################################################################
		self.frame3=Label(self,bg=self.color,bd=5)
		self.frame3.pack(fill=BOTH, pady=(30,0),padx=40)

		#Input file selection
		self.inputFile_label = Label(self.frame3, text="Choose model file :",font=("Helvetica"),bg=self.color)
		self.inputFile_label.grid(row=1,column=0,pady=10,padx=10)

		self.inputFile_button = Button(self.frame3, text="Browse...", command=self.cliquerFile,font=("Helvetica"),bg=self.color_button)
		self.inputFile_button.grid(row=1, column=1,pady=10,padx=20)

		self.labelFile=Label(self.frame3,text="",bg=self.color)
		self.labelFile.grid(row=1,column=2)


		#starting model block
		self.frame1=LabelFrame(self,relief='groove',bg=self.color,bd=5,text="Starting model",font=("Helvetica",14))
		self.frame1.pack(fill=BOTH, pady=(10,30),padx=40)


		self.charge_network = Button(self.frame1, text="Vizualise network", command=self.cliquerNetwork,font=("Helvetica"),bg=self.color_button,state=DISABLED)
		self.charge_network.grid(row=1, column=1,pady=(20,10),padx=40)

		
		self.charge_simulation = Button(self.frame1, text="Simulation", command=self.cliquerSimulation,font=("Helvetica"),bg=self.color_button,state=DISABLED)
		self.charge_simulation.grid(row=2, column=1,pady=(10,20),padx=40,sticky=W)



		self.frame4=Label(self,bg=self.color,bd=5)
		self.frame4.pack(fill=BOTH, pady=(10,30),padx=40)


		self.reduce = Button(self.frame4, text="Reduce model", command=self.cliquerResult,font=("Helvetica", 12,"bold"),bg=self.color_button,state=DISABLED)
		self.reduce.pack(pady=20,padx=20)

		################################################################################################################
		# Reduced model part
		################################################################################################################

		self.frame2=LabelFrame(self,relief='groove',bg=self.color,bd=5,text="Reduced model",font=("Helvetica",14))
		self.frame2.pack(side="bottom",fill=BOTH,pady=(0,50),padx=40)
		#self.frame2.grid(row=7, column=2, columnspan=3, )



		self.charge_network_reduced = Button(self.frame2, text="Vizualise network", command=self.cliquerNetwork_reduced,font=("Helvetica"),bg=self.color_button,state=DISABLED)
		self.charge_network_reduced.grid(row=1, column=1,pady=(20,10),padx=40)
		
		
		self.charge_reduced_simulation = Button(self.frame2, text="Simulation", command=self.cliquerSimulationReduced,font=("Helvetica"),bg=self.color_button,state=DISABLED)
		self.charge_reduced_simulation.grid(row=2, column=1,pady=(10,20),padx=40,sticky=W)


		################################################################################################################
		# Defined button functions
		################################################################################################################	


		#Function to select file
	def cliquerFile(self): 
		global filename       
		filename =  filedialog.askopenfilename(initialdir = "/HOME",title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
		self.labelFile.configure(text=basename(filename))
		self.charge_network.configure(state=NORMAL)
		self.charge_simulation.configure(state=NORMAL)
		self.reduce.configure(state=NORMAL)

	def cliquerSimulation(self):
		global Timescale_value_init
		Timescale_value_init='5'
		#os.system("python3 simulate.py "+filename+" 5")
		simulatepy(filename, Timescale_value_init)

		#change timescale block
		self.resultInit=Toplevel(master=fenetre)
		self.resultInit.title("Initial model simulation")

		self.resultInit.frameOption=Frame(master=self.resultInit)
		self.resultInit.frameOption.pack(fill=BOTH)

		self.resultInit.layoutOption=Label(master=self.resultInit.frameOption,text="Timescale :")
		self.resultInit.layoutOption.grid(row=1, column=1,pady=(10,20),padx=40,)

		self.resultInit.Entry_number=Entry(master=self.resultInit.frameOption,textvariable="Timescale_value")
		self.resultInit.Entry_number.grid(row=1, column=2,pady=(10,20),padx=40,)

		self.resultInit.GoButton=Button(master=self.resultInit.frameOption, text="Start",command=self.cliquerChangeTimescale)
		self.resultInit.GoButton.grid(row=2, column=2,pady=(10,20),padx=40,sticky=W)

		#visualization block
		self.resultInit.frameImage=Frame(master=self.resultInit)
		self.resultInit.frameImage.pack()

		imageo=Image.open(filename+".png")
		resultsimu= ImageTk.PhotoImage(imageo,width=1000,height=1200)
		self.resultInit.canva=Canvas(self.resultInit.frameImage,width=resultsimu.width(),height=resultsimu.height())
		self.resultInit.canva.create_image(0,0,anchor=NW,image=resultsimu)
		self.resultInit.canva.image=resultsimu
		self.resultInit.canva.pack(fill=BOTH)


	def cliquerChangeTimescale(self):
		
		#os.system("python3 simulate.py "+filename+" "+self.resultInit.Entry_number.get())
		print( self.resultInit.Entry_number.get())
		if self.resultInit.Entry_number.get()!="":
			simulatepy(filename, self.resultInit.Entry_number.get())
		
			imageo=Image.open(filename+".png")

			resultsimu= ImageTk.PhotoImage(imageo,width=1000,height=1200)
		
			self.resultInit.canva.create_image(0,0,anchor=NW,image=resultsimu)
			self.resultInit.canva.image=resultsimu
		


		
		
	# Reduce the model
	def cliquerResult(self):
		global G
		G = reductionpy(filename)
		#os.system("python3 reduction.py "+filename)
		#able network and simulation vizualisation
		self.charge_network_reduced.configure(state=NORMAL)
		self.charge_reduced_simulation.configure(state=NORMAL)

	def cliquerSimulationReduced(self):

		global Timescale_value
		Timescale_value='5'
		simulatepy(filename+"_reduced.tsv", Timescale_value)
		#os.system("python3 simulate.py "+filename+"_reduced.tsv 5")
		self.result=Toplevel(master=fenetre)
		self.result.title("Reduced model simulation")
		

		self.result.frameOption=Frame(master=self.result)
		self.result.frameOption.pack(fill=BOTH)

		self.result.TimescaleOption=Label(master=self.result.frameOption,text="Timescale :")
		self.result.TimescaleOption.grid(row=1, column=1,pady=(10,20),padx=40,)


		self.result.Entry_number=Entry(master=self.result.frameOption,textvariable="Timescale_value")
		self.result.Entry_number.grid(row=1, column=2,pady=(10,20),padx=40,)

		self.result.GoButton=Button(master=self.result.frameOption, text="Start",command=self.cliquerChangeTimescaleReduced)
		self.result.GoButton.grid(row=2, column=2,pady=(10,20),padx=40,sticky=W)

		self.result.frameImage=Frame(master=self.result)
		self.result.frameImage.pack()

		imageo=Image.open(filename+"_reduced.tsv.png")
		resultsimu= ImageTk.PhotoImage(imageo,width=1000,height=1200)
		self.result.canva=Canvas(self.result.frameImage,width=resultsimu.width(),height=resultsimu.height())
		self.result.canva.create_image(0,0,anchor=NW,image=resultsimu)
		self.result.canva.image=resultsimu
		self.result.canva.pack(fill=BOTH)


	def cliquerChangeTimescaleReduced(self):
		#os.system("python3 simulate.py "+filename+"_reduced.tsv "+self.result.Entry_number.get())
		if self.result.Entry_number.get()!="":
			simulatepy(filename+"_reduced.tsv", self.result.Entry_number.get())
			imageo=Image.open(filename+"_reduced.tsv.png")
			resultsimu= ImageTk.PhotoImage(imageo,width=1000,height=1200)
			self.result.canva.create_image(0,0,anchor=NW,image=resultsimu)
			self.result.canva.image=resultsimu

	def cliquerNetwork(self):
		global Layout
		LayoutValue='dot'
		FormatValue='png'
		input_G = load(filename)
		savename = filename + "input_graph" + "." + FormatValue
		draw_graph(input_G,savename,'png','dot')
		#os.system("python3 simulate.py "+filename+"_reduced.tsv 5")
		self.networkInitWindow=Toplevel(master=fenetre,bg="white")
		self.networkInitWindow.title("Initial network")
		

		self.networkInitWindow.frameOption=Frame(master=self.networkInitWindow,bg=self.color)
		self.networkInitWindow.frameOption.pack(fill=BOTH)

		self.networkInitWindow.layoutOption=Label(master=self.networkInitWindow.frameOption,text="Layout :",bg=self.color)
		self.networkInitWindow.layoutOption.grid(row=1, column=1,pady=(10,20),padx=40,)


		self.networkInitWindow.Layout_CB=ttk.Combobox(master=self.networkInitWindow.frameOption,textvariable="LayoutValue",values=["neato","dot","twopi","circo","fdp"])
		self.networkInitWindow.Layout_CB.grid(row=1, column=2,pady=(10,20),padx=40,)

		self.networkInitWindow.formatOption=Label(master=self.networkInitWindow.frameOption,text="Format :",bg=self.color)
		self.networkInitWindow.formatOption.grid(row=2, column=1,pady=(10,20),padx=40,)


		self.networkInitWindow.Format_CB=ttk.Combobox(master=self.networkInitWindow.frameOption,textvariable="FormatValue",values=["dot","gif","jpeg","jpg","pdf","png","ps","svg"])
		self.networkInitWindow.Format_CB.grid(row=2, column=2,pady=(10,20),padx=40,)

		self.networkInitWindow.GoButton=Button(master=self.networkInitWindow.frameOption, text="Start",command=self.cliquerChangeLayout,bg=self.color_button)
		self.networkInitWindow.GoButton.grid(row=3, column=2,pady=(10,20),padx=40,sticky=W)

		self.networkInitWindow.frameImage=Frame(master=self.networkInitWindow)
		self.networkInitWindow.frameImage.pack()

		imageo=Image.open(savename)
		resultNetwork= ImageTk.PhotoImage(imageo,width=1000,height=1200)
		#resultNetwork.resize(500,800)
		#resultNetwork.zoom(500,500)
		#resultNetwork=resultNetwork._PhotoImage__photo.zoom(4)
		self.networkInitWindow.canva=Canvas(self.networkInitWindow.frameImage,width=resultNetwork.width(),height=resultNetwork.height())
		self.networkInitWindow.canva.create_image(0,0,anchor=NW,image=resultNetwork)
		self.networkInitWindow.canva.image=resultNetwork
		self.networkInitWindow.canva.pack(fill=BOTH)


	def cliquerChangeLayout(self):
		#os.system("python3 simulate.py "+filename+"_reduced.tsv "+self.result.Entry_number.get())
		input_G = load(filename)
		format='png'
		if self.networkInitWindow.Format_CB.get()!="":
			format = self.networkInitWindow.Format_CB.get()
		layout='dot'
		if self.networkInitWindow.Layout_CB.get()!="":
			layout = self.networkInitWindow.Layout_CB.get()
		savename = filename + "input_graph" + "." + format
		draw_graph(input_G,savename,format,layout)
		if format=='png' or format=='jpeg' or format=='gif' or format=='jpg':
			imageo=Image.open(savename)
			resultNetwork= ImageTk.PhotoImage(imageo)
			#self.networkInitWindow.canva=Canvas(self.networkInitWindow.frameImage,width=resultNetwork.width(),height=resultNetwork.height())
			self.networkInitWindow.canva.delete("all")
			self.networkInitWindow.canva.config(width=resultNetwork.width(),height=resultNetwork.height())
			self.networkInitWindow.canva.create_image(0,0,anchor=NW,image=resultNetwork)
			self.networkInitWindow.canva.image=resultNetwork
			self.networkInitWindow.canva.pack(fill=BOTH)
		else:
			self.networkInitWindow.canva.delete("all")
			self.networkInitWindow.canva.config(width=len(savename)*6+6*14,height=20)
			self.networkInitWindow.canva.create_text(2,2,anchor=NW,text="File saved in "+savename)
			self.networkInitWindow.canva.text="File saved in "+savename
			self.networkInitWindow.canva.pack(fill=BOTH)

	def cliquerNetwork_reduced(self):
		LayoutValue='dot'
		#G = reductionpy(filename)
		u_G=load('%s_reduced.tsv' % filename)
		rsavename = filename + "reduced_graph" + ".png"
		draw_graph(u_G,rsavename,'png','dot')
		#os.system("python3 simulate.py "+filename+"_reduced.tsv 5")
		self.networkReducedWindow=Toplevel(master=fenetre,bg="white")
		self.networkReducedWindow.title("Reduced network")
		

		self.networkReducedWindow.frameOption=Frame(master=self.networkReducedWindow)
		self.networkReducedWindow.frameOption.pack(fill=BOTH)

		self.networkReducedWindow.layoutOption=Label(master=self.networkReducedWindow.frameOption,text="Layout :",bg=self.color)
		self.networkReducedWindow.layoutOption.grid(row=1, column=1,pady=(10,20),padx=40,)


		self.networkReducedWindow.Layout_CB=ttk.Combobox(master=self.networkReducedWindow.frameOption,textvariable="LayoutValue",values=["neato","dot","twopi","circo","fdp"])
		self.networkReducedWindow.Layout_CB.grid(row=1, column=2,pady=(10,20),padx=40,)
		
		self.networkReducedWindow.formatOption=Label(master=self.networkReducedWindow.frameOption,text="Format :",bg=self.color)
		self.networkReducedWindow.formatOption.grid(row=2, column=1,pady=(10,20),padx=40,)

		self.networkReducedWindow.Format_CB=ttk.Combobox(master=self.networkReducedWindow.frameOption,textvariable="FormatValue",values=["dot","gif","jpeg","jpg","pdf","png","ps","svg"])
		self.networkReducedWindow.Format_CB.grid(row=2, column=2,pady=(10,20),padx=40,)

		self.networkReducedWindow.GoButton=Button(master=self.networkReducedWindow.frameOption, text="Start",command=self.cliquerChangeLayout_reduced,bg=self.color_button)
		self.networkReducedWindow.GoButton.grid(row=3, column=2,pady=(10,20),padx=40,sticky=W)

		self.networkReducedWindow.frameImage=Frame(master=self.networkReducedWindow)
		self.networkReducedWindow.frameImage.pack()

		imageo=Image.open(rsavename)
		resultNetwork= ImageTk.PhotoImage(imageo,width=1000,height=1200)
		self.networkReducedWindow.canva=Canvas(self.networkReducedWindow.frameImage,width=resultNetwork.width(),height=resultNetwork.height())
		self.networkReducedWindow.canva.create_image(0,0,anchor=NW,image=resultNetwork)
		self.networkReducedWindow.canva.image=resultNetwork
		self.networkReducedWindow.canva.pack(fill=BOTH)


	def cliquerChangeLayout_reduced(self):
		#os.system("python3 simulate.py "+filename+"_reduced.tsv "+self.result.Entry_number.get())
		u_G=load('%s_reduced.tsv' % filename)
		format='png'
		if self.networkReducedWindow.Format_CB.get()!="":
			format = self.networkReducedWindow.Format_CB.get()
		layout='dot'
		if self.networkReducedWindow.Layout_CB.get()!="":
			layout = self.networkReducedWindow.Layout_CB.get()
		rsavename = filename + "reduced_graph" + "." + format
		draw_graph(u_G,rsavename,format,layout)
		if format=='png' or format=='jpeg' or format=='gif' or format=='jpg':
			imageo=Image.open(rsavename)
			resultNetwork= ImageTk.PhotoImage(imageo)
			#self.networkReducedWindow.canva=Canvas(self.networkReducedWindow.frameImage,width=resultNetwork.width(),height=resultNetwork.height())
			self.networkReducedWindow.canva.delete("all")
			self.networkReducedWindow.canva.config(width=resultNetwork.width(),height=resultNetwork.height())
			self.networkReducedWindow.canva.create_image(0,0,anchor=NW,image=resultNetwork)
			self.networkReducedWindow.canva.image=resultNetwork
			self.networkReducedWindow.canva.pack(fill=BOTH)
		else:
			self.networkReducedWindow.canva.delete("all")
			self.networkReducedWindow.canva.config(width=len(rsavename)*6+6*14,height=20)
			self.networkReducedWindow.canva.create_text(2,2,anchor=NW,text="File saved in "+rsavename)
			self.networkReducedWindow.canva.text="File saved in "+rsavename
			self.networkReducedWindow.canva.pack(fill=BOTH)


		


	# Checker le format du model
	def CheckModel(self):
		print ("check model")


	


if __name__ == "__main__":
	fenetre = Tk()
	interface = Interface(fenetre)
	fenetre.title("LNetReduce")
	interface.mainloop()
	