from tkinter import filedialog
from tkinter import *
from tkinter.messagebox import *
from tkinter import ttk
from PIL import Image, ImageTk
import PIL
from matplotlib import pyplot as plt
import numpy as np
import tempfile
from os.path import basename
import io
import os
import pandas as pd
import networkx as nx




import lnetreduce

class Interface(Frame):
    global filename
    global Timescale_value
    global work_folder

    """The main window.
    All widgets are stored as attributes in this window."""
    def __init__(self, fenetre, bg='#ADB7FA', bt='#334DFF', **kwargs):
        self.color=StringVar()
        self.color=bg
        self.color_button=bt
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
        self.charge_network.grid(row=1, column=1,pady=(20,10),padx=40,sticky=W)

        
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
        self.charge_reduced_simulation.grid(row=2, column=1,pady=(10,10),padx=40,sticky=W)

        self.button_vectors=Button(self.frame2,bg=self.color_button,text="Save eigen vectors",font=("Helvetica"),command=self.cliquerVector,state=DISABLED)
        self.button_vectors.grid(row=3, column=1,pady=(10,20),padx=40,sticky=W)


        ################################################################################################################
        # Defined button functions
        ################################################################################################################    


        #Function to select file
    def cliquerFile(self): 
        global filename  
        self.charge_network.configure(state=DISABLED)
        self.charge_simulation.configure(state=DISABLED)
        self.reduce.configure(state=DISABLED)
        self.charge_reduced_simulation.configure(state=DISABLED)
        self.charge_network_reduced.configure(state=DISABLED)
        self.button_vectors.configure(state=DISABLED)   
        filename =  filedialog.askopenfilename(initialdir = "/HOME",title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
        try:
            lnetreduce.load_graph(filename)
            self.labelFile.configure(text=basename(filename))
            self.charge_network.configure(state=NORMAL)
            self.charge_simulation.configure(state=NORMAL)
            self.reduce.configure(state=NORMAL)
            self.charge_reduced_simulation.configure(state=DISABLED)
            self.charge_network_reduced.configure(state=DISABLED)
            self.button_vectors.configure(state=DISABLED)
        except:
            showwarning(message='An error occured loading the model, \n please check format', )

        ################################################################################################################
        # Simulation part
        ################################################################################################################ 

    def cliquerSimulation(self):
        global Timescale_value_init
        global imageo
        global resultsimu
        Timescale_value_init=5

        imageo = simulatepy(filename, Timescale_value_init, method=None)

        self.resultInit=Toplevel(master=fenetre,bg="white")
        self.resultInit.title("Initial model simulation")

        self.resultInit.frameOption=Frame(master=self.resultInit,bg=self.color)
        self.resultInit.frameOption.pack(fill=BOTH)

        self.resultInit.layoutOption=Label(master=self.resultInit.frameOption,text="Timescale :",bg=self.color)
        self.resultInit.layoutOption.grid(row=1, column=1,pady=(10,20),padx=40,)

        self.resultInit.Entry_number=Entry(master=self.resultInit.frameOption,textvariable="Timescale_value_init")
        self.resultInit.Entry_number.grid(row=1, column=2,pady=(10,20),padx=40,)
        

        self.resultInit.solverOption=Label(master=self.resultInit.frameOption,text="Solver :",bg=self.color)
        self.resultInit.solverOption.grid(row=2, column=1,pady=(10,20),padx=40,)

        self.resultInit.Solver=ttk.Combobox(master=self.resultInit.frameOption,textvariable="SolverValueInit",values=["LSODA","odeint"])
        self.resultInit.Solver.set('LSODA')
        self.resultInit.Solver.grid(row=2, column=2,pady=(10,20),padx=40,)


        self.resultInit.GoButton=Button(master=self.resultInit.frameOption, text="Start",command=self.cliquerChangeTimescale,bg=self.color_button)
        self.resultInit.GoButton.grid(row=3, column=2,pady=(10,20),padx=40,sticky=W)

        #visualization block
        self.resultInit.frameImage=Frame(master=self.resultInit,bg="white")
        self.resultInit.frameImage.pack()

        resultsimu= ImageTk.PhotoImage(imageo,width=1000,height=1200)
        self.resultInit.canva=Canvas(self.resultInit.frameImage,width=resultsimu.width(),height=resultsimu.height())
        self.resultInit.canva.create_image(0,0,anchor=NW,image=resultsimu)
        self.resultInit.canva.image=resultsimu
        self.resultInit.canva.pack(fill=BOTH)

        self.resultInit.frameSave=Frame(master=self.resultInit,bg=self.color)
        self.resultInit.frameSave.pack(fill=BOTH)

        self.resultInit.Format_CB=ttk.Combobox(master=self.resultInit.frameSave,textvariable="FormatValueInit",values=["pdf","png"])
        self.resultInit.Format_CB.grid(row=2, column=2,pady=(10,20),padx=40,)

        self.resultInit.SaveButton=Button(master=self.resultInit.frameSave, text="Save",command=self.saveInitSiumulation,bg=self.color_button)
        self.resultInit.SaveButton.grid(row=3, column=2,pady=(10,20),padx=40,sticky=W)


    def cliquerChangeTimescale(self):   
        global resultsimu 
        if self.resultInit.Entry_number.get()!="" and self.resultInit.Entry_number.get().isdigit() and self.resultInit.Solver.get() in ["LSODA","odeint"]:
            if self.resultInit.Solver.get()=='LSODA':
                imageo = simulatepy(filename, self.resultInit.Entry_number.get(),method=None)

                resultsimu= ImageTk.PhotoImage(imageo,width=1000,height=1200)
            
                self.resultInit.canva.create_image(0,0,anchor=NW,image=resultsimu)
                self.resultInit.canva.image=resultsimu
            elif self.resultInit.Solver.get()=='odeint':
                imageo = simulatepy(filename, self.resultInit.Entry_number.get(),method='odeint')

                resultsimu= ImageTk.PhotoImage(imageo,width=1000,height=1200)
            
                self.resultInit.canva.create_image(0,0,anchor=NW,image=resultsimu)
                self.resultInit.canva.image=resultsimu
                
            else:
                showwarning(message="please choose a solver in the list ")                

        else:
            showwarning(message="please enter a positive integer as power of ten for timescale value ")
       

    def saveInitSiumulation(self):
        format = self.resultInit.Format_CB.get()   
        self.work_folder =  filedialog.askdirectory(initialdir = "/HOME",title = "Select folder") 
        savename = self.work_folder+"/"+basename(filename) + "input_model_simulation." + self.resultInit.Format_CB.get()

        if self.resultInit.Format_CB.get() =="png":
            SimuToSave= ImageTk.getimage(resultsimu)
            
            SimuToSave.save(savename)
            #simulatepy(filename, self.resultInit.Entry_number.get(),meth)

        elif self.resultInit.Format_CB.get()=="pdf":
            SimuToSave= ImageTk.getimage(resultsimu)
            SimuToSave=SimuToSave.convert('RGB')
            SimuToSave.save(savename)

        else:
            showwarning(message='Please select a correct format', )

        
        
    # Reduce the model
    def cliquerResult(self):
        global G
        global work_folder
        try:
            G = reductionpy(filename)
        except:
            G = reductionpy(filename)
            showwarning(message='An error occured when reducing model', )

                # Enable network and simulation vizualisation
        self.charge_network_reduced.configure(state=NORMAL)
        self.charge_reduced_simulation.configure(state=NORMAL)
        self.button_vectors.configure(state=NORMAL)
        work_folder =  filedialog.askdirectory(initialdir = "/HOME",title = "Select folder") 
        #save reduced model
        lnetreduce.save_graph( G[1], '%s/%s_reduced.tsv' % (work_folder,basename(filename).split('.')[0]))   
        


    def cliquerSimulationReduced(self):

        global Timescale_value
        global resultsimureduced
        Timescale_value=5
        imageo = simulatepy('%s/%s_reduced.tsv' % (work_folder,basename(filename).split('.')[0]), Timescale_value,method=None)
        self.result=Toplevel(master=fenetre)
        self.result.title("Reduced model simulation")
        

        self.result.frameOption=Frame(master=self.result,bg=self.color)
        self.result.frameOption.pack(fill=BOTH)

        self.result.TimescaleOption=Label(master=self.result.frameOption,text="Timescale :", bg=self.color)
        self.result.TimescaleOption.grid(row=1, column=1,pady=(10,20),padx=40,)


        self.result.Entry_number=Entry(master=self.result.frameOption,textvariable=Timescale_value)
        self.result.Entry_number.grid(row=1, column=2,pady=(10,20),padx=40,)

        self.result.solverOption=Label(master=self.result.frameOption,text="Solver :",bg=self.color)
        self.result.solverOption.grid(row=2, column=1,pady=(10,20),padx=40,)

        self.result.Solver=ttk.Combobox(master=self.result.frameOption,textvariable="SolverValueInit",values=["LSODA","odeint"])
        self.result.Solver.set('LSODA')
        self.result.Solver.grid(row=2, column=2,pady=(10,20),padx=40,)

        self.result.GoButton=Button(master=self.result.frameOption, text="Start",command=self.cliquerChangeTimescaleReduced,bg=self.color_button)
        self.result.GoButton.grid(row=3, column=2,pady=(10,20),padx=40,sticky=W)

        self.result.frameImage=Frame(master=self.result)
        self.result.frameImage.pack()

        resultsimureduced= ImageTk.PhotoImage(imageo,width=1000,height=1200)
        self.result.canva=Canvas(self.result.frameImage,width=resultsimureduced.width(),height=resultsimureduced.height())
        self.result.canva.create_image(0,0,anchor=NW,image=resultsimureduced)
        self.result.canva.image=resultsimureduced
        self.result.canva.pack(fill=BOTH)

        self.result.frameSave=Frame(master=self.result,bg=self.color)
        self.result.frameSave.pack(fill=BOTH)

        self.result.Format_CB=ttk.Combobox(master=self.result.frameSave,textvariable="FormatValueReduced",values=["pdf","png"])
        self.result.Format_CB.grid(row=2, column=2,pady=(10,20),padx=40,)

        self.result.SaveButton=Button(master=self.result.frameSave, text="Save",command=self.saveReducedSiumulation,bg=self.color_button)
        self.result.SaveButton.grid(row=3, column=2,pady=(10,20),padx=40,sticky=W)


    def cliquerChangeTimescaleReduced(self):
        global resultsimureduced
        if self.result.Entry_number.get()!="" and self.result.Entry_number.get().isdigit() and self.result.Solver.get() in ["LSODA","odeint"]:
            if self.result.Solver.get()=='LSODA':
                imageo = simulatepy('%s/%s_reduced.tsv' % (work_folder,basename(filename).split('.')[0]), self.result.Entry_number.get(),method=None)
                resultsimureduced= ImageTk.PhotoImage(imageo,width=1000,height=1200)
                self.result.canva.create_image(0,0,anchor=NW,image=resultsimureduced)
                self.result.canva.image=resultsimureduced
            elif self.result.Solver.get()=='odeint':
                imageo = simulatepy(filename, self.result.Entry_number.get(),method='odeint')

                resultsimureduced= ImageTk.PhotoImage(imageo,width=1000,height=1200)
            
                self.result.canva.create_image(0,0,anchor=NW,image=resultsimu)
                self.result.canva.image=resultsimureduced
            else:
                showwarning(message="please choose a solver in the list ")                

        else:
            showwarning(message="please enter a positive integer as power of ten for timescale value ")


    def saveReducedSiumulation(self):
            format = self.result.Format_CB.get()   
            self.work_folder =  filedialog.askdirectory(initialdir = "/HOME",title = "Select folder") 
            savename = self.work_folder+"/"+basename(filename) + "input_model_simulation." + self.result.Format_CB.get()
            

            if self.result.Format_CB.get() =="png":
                SimuToSave= ImageTk.getimage(resultsimureduced)               
                SimuToSave.save(savename)           

            elif self.result.Format_CB.get()=="pdf":
                SimuToSave= ImageTk.getimage(resultsimureduced)
                SimuToSave=SimuToSave.convert('RGB')
                SimuToSave.save(savename)

            else:
                showwarning(message='Please select a correct format', )


        ################################################################################################################
        # Network Part
        ################################################################################################################ 
        


    def cliquerNetwork(self):
        global Layout
        LayoutValue='dot'
        FormatValue='png'
        input_G = lnetreduce.load_graph(filename)
        savename = filename + "input_graph" + "." + FormatValue
        imageo = draw_graph(input_G,'neato',True,None)
        self.networkInitWindow=Toplevel(master=fenetre,bg="white")
        self.networkInitWindow.title("Initial network")
        

        self.networkInitWindow.frameOption=Frame(master=self.networkInitWindow,bg=self.color)
        self.networkInitWindow.frameOption.pack(fill=BOTH)

        self.networkInitWindow.layoutOption=Label(master=self.networkInitWindow.frameOption,text="Layout :",bg=self.color)
        self.networkInitWindow.layoutOption.grid(row=1, column=1,pady=(10,20),padx=40,)


        self.networkInitWindow.Layout_CB=ttk.Combobox(master=self.networkInitWindow.frameOption,textvariable="LayoutValueInit",values=["neato","dot","twopi","circo","fdp"])
        self.networkInitWindow.Layout_CB.grid(row=1, column=2,pady=(10,20),padx=40,)

        self.networkInitWindow.GoButton=Button(master=self.networkInitWindow.frameOption, text="Vizualise",command=self.cliquerChangeLayout,bg=self.color_button)
        self.networkInitWindow.GoButton.grid(row=3, column=2,pady=(10,20),padx=40,sticky=W)

        self.networkInitWindow.frameImage=Frame(master=self.networkInitWindow)
        self.networkInitWindow.frameImage.pack()

        resultNetwork= ImageTk.PhotoImage(imageo,width=1000,height=1200)
        self.networkInitWindow.canva=Canvas(self.networkInitWindow.frameImage,width=resultNetwork.width(),height=resultNetwork.height())
        self.networkInitWindow.canva.create_image(0,0,anchor=NW,image=resultNetwork)
        self.networkInitWindow.canva.image=resultNetwork
        self.networkInitWindow.canva.pack(fill=BOTH)

        self.networkInitWindow.frameSave=Frame(master=self.networkInitWindow,bg=self.color)
        self.networkInitWindow.frameSave.pack(fill=BOTH)

        self.networkInitWindow.SaveButton=Button(master=self.networkInitWindow.frameSave, text="Save",command=self.cliquerFolder,bg=self.color_button)
        self.networkInitWindow.SaveButton.grid(row=3, column=2,pady=(10,20),padx=40,sticky=W)

        self.networkInitWindow.Format_CB=ttk.Combobox(master=self.networkInitWindow.frameSave,textvariable="FormatValueInit",values=["pdf","png","svg"])
        self.networkInitWindow.Format_CB.grid(row=2, column=2,pady=(10,20),padx=40,)

        self.networkInitWindow.formatOption=Label(master=self.networkInitWindow.frameSave,text="Format :",bg=self.color)
        self.networkInitWindow.formatOption.grid(row=2, column=1,pady=(10,20),padx=40,)


    def cliquerChangeLayout(self):
        input_G = lnetreduce.load_graph(filename)
        format='png'
        if self.networkInitWindow.Format_CB.get()!="":
            format = self.networkInitWindow.Format_CB.get()
        layout='neato'
        if self.networkInitWindow.Layout_CB.get()!="":
            layout = self.networkInitWindow.Layout_CB.get()
        savename = filename + "input_graph" + "." + format

        
        imageo=draw_graph(input_G,layout,True,None)
        resultNetwork= ImageTk.PhotoImage(imageo)
        #self.networkInitWindow.canva=Canvas(self.networkInitWindow.frameImage,width=resultNetwork.width(),height=resultNetwork.height())

        self.networkInitWindow.canva.delete("all")
        self.networkInitWindow.canva.config(width=resultNetwork.width(),height=resultNetwork.height())
        self.networkInitWindow.canva.create_image(0,0,anchor=NW,image=resultNetwork)
        self.networkInitWindow.canva.image=resultNetwork
        self.networkInitWindow.canva.pack(fill=BOTH)


    def cliquerFolder(self):   
        if self.networkInitWindow.Format_CB.get() in ["dot","pdf","png","svg"]:
            
            if self.networkInitWindow.Layout_CB.get() in ["neato","dot","twopi","circo","fdp"]:
                format = self.networkInitWindow.Format_CB.get()   
                self.work_folder =  filedialog.askdirectory(initialdir = "/HOME",title = "Select folder") 
                savename = self.work_folder+"/"+basename(filename) + "input_graph." + self.networkInitWindow.Format_CB.get()
                input_G = lnetreduce.load_graph("models/flower_2.csv")

                layout = self.networkInitWindow.Layout_CB.get()
                draw_graph(input_G,layout,True,savename)
            else:
                showwarning(message='Please select an existing layout', )
             

        else:
            showwarning(message='Please select a correct format', )


    def cliquerNetwork_reduced(self):
        LayoutValue='dot'
        u_G = lnetreduce.load_graph('%s/%s_reduced.tsv' % (work_folder,basename(filename).split('.')[0]))
        rsavename = filename + "reduced_graph" + ".png"
        imageo = draw_graph(u_G,'neato',False,None)

        self.networkReducedWindow=Toplevel(master=fenetre,bg="white")
        self.networkReducedWindow.title("Reduced network")

        self.networkReducedWindow.frameOption=Frame(master=self.networkReducedWindow,bg=self.color)
        self.networkReducedWindow.frameOption.pack(fill=BOTH)

        self.networkReducedWindow.layoutOption=Label(master=self.networkReducedWindow.frameOption,text="Layout :",bg=self.color)
        self.networkReducedWindow.layoutOption.grid(row=1, column=1,pady=(10,20),padx=40,)


        self.networkReducedWindow.Layout_CB=ttk.Combobox(master=self.networkReducedWindow.frameOption,textvariable="LayoutValue",values=["neato","dot","twopi","circo","fdp"])
        self.networkReducedWindow.Layout_CB.grid(row=1, column=2,pady=(10,20),padx=40,)

        self.networkReducedWindow.GoButton=Button(master=self.networkReducedWindow.frameOption, text="Vizualise",command=self.cliquerChangeLayout_reduced,bg=self.color_button)
        self.networkReducedWindow.GoButton.grid(row=3, column=2,pady=(10,20),padx=40,sticky=W)

        self.networkReducedWindow.frameImage=Frame(master=self.networkReducedWindow)
        self.networkReducedWindow.frameImage.pack()

        resultNetwork= ImageTk.PhotoImage(imageo,width=1000,height=1200)
        self.networkReducedWindow.canva=Canvas(self.networkReducedWindow.frameImage,width=resultNetwork.width(),height=resultNetwork.height())
        self.networkReducedWindow.canva.create_image(0,0,anchor=NW,image=resultNetwork)
        self.networkReducedWindow.canva.image=resultNetwork
        self.networkReducedWindow.canva.pack(fill=BOTH)

        self.networkReducedWindow.frameSave=Frame(master=self.networkReducedWindow,bg=self.color)
        self.networkReducedWindow.frameSave.pack(fill=BOTH)

        self.networkReducedWindow.SaveButton=Button(master=self.networkReducedWindow.frameSave, text="Save",command=self.cliquerFolderReduced,bg=self.color_button)
        self.networkReducedWindow.SaveButton.grid(row=3, column=2,pady=(10,20),padx=40,sticky=W)

        self.networkReducedWindow.Format_CB=ttk.Combobox(master=self.networkReducedWindow.frameSave,textvariable="FormatValue",values=["pdf","png","svg"])        
        self.networkReducedWindow.Format_CB.grid(row=2, column=2,pady=(10,20),padx=40,)

        self.networkReducedWindow.formatOption=Label(master=self.networkReducedWindow.frameSave,text="Format :",bg=self.color)
        self.networkReducedWindow.formatOption.grid(row=2, column=1,pady=(10,20),padx=40,)


    def cliquerChangeLayout_reduced(self):
        #os.system("python3 simulate.py "+filename+"_reduced.tsv "+self.result.Entry_number.get())
        u_G = lnetreduce.load_graph('%s/%s_reduced.tsv' % (work_folder,basename(filename).split('.')[0]))

        if self.networkReducedWindow.Layout_CB.get() in ["neato","dot","twopi","circo","fdp"]:
            layout = self.networkReducedWindow.Layout_CB.get()
        
            imageo=draw_graph(u_G,layout,False,None)

            resultNetwork= ImageTk.PhotoImage(imageo)
        #self.networkReducedWindow.canva=Canvas(self.networkReducedWindow.frameImage,width=resultNetwork.width(),height=resultNetwork.height())

            self.networkReducedWindow.canva.delete("all")
            self.networkReducedWindow.canva.config(width=resultNetwork.width(),height=resultNetwork.height())
            self.networkReducedWindow.canva.create_image(0,0,anchor=NW,image=resultNetwork)
            self.networkReducedWindow.canva.image=resultNetwork
            self.networkReducedWindow.canva.pack(fill=BOTH)
        else:
            showwarning(message='Please select an existing layout', )



    def cliquerFolderReduced(self):   
        if self.networkReducedWindow.Format_CB.get() in ["dot","pdf","png","svg"]:

            if self.networkReducedWindow.Layout_CB.get() in ["neato","dot","twopi","circo","fdp"]:
                format = self.networkReducedWindow.Format_CB.get()   
                self.work_folder =  filedialog.askdirectory(initialdir = "/HOME",title = "Select folder") 
                savename = self.work_folder+"/"+basename(filename) + "reduced_graph" + "." + format 
                u_G=lnetreduce.load_graph('%s/%s_reduced.tsv' % (work_folder,basename(filename).split('.')[0]))
                layout = self.networkReducedWindow.Layout_CB.get()
                draw_graph(u_G,layout,True,savename) 

            else:
                showwarning(message='Please select an existing layout', )
             
        else:
            showwarning(message='Please select a correct format', )

    def cliquerVector(self):        
    	self.work_folder =  filedialog.askdirectory(initialdir = "/HOME",title = "Select folder") 
    	savename = self.work_folder+"/"+basename(filename) + "reduced" 
    	generateVectors(savename)

def generateVectors(savename):
    u_G=lnetreduce.load_graph(filename)
    R = lnetreduce.reduction.right_vector(u_G)
    L = lnetreduce.reduction.left_vector(u_G)
    with open(savename+"right_vector.txt","w") as f:
        f.write(str(R))
    with open(savename+"left_vector.txt","w") as g:
        g.write(str(L))            


def reductionpy(filename):
    input_G = lnetreduce.load_graph(filename)
    try:
        u_G = lnetreduce.reduce_graph( input_G )
    except:
        try:
            u_G = lnetreduce.reduce_graph( input_G ,partial=True)
            showwarning(message='Failed to completely reduce the model, a partially reduced model have been generated')

        except:
            showwarning(message='Sorry, this instance is not reducible because its reduced form has non separated reaction speeds')
            sys.exit()

    #lnetreduce.save_graph( u_G, '%s_reduced.tsv' % filename)
    return input_G, u_G

def simulatepy(_filename, _timescale,method,path=None):
    timescale = int(_timescale)
    fig = plt.figure()
    lnetreduce.simulate_and_plot(_filename, timescale,method=method)
    return fig_to_image(fig,save=path)

def fig_to_image(fig, buffer=False,save=None):
    if buffer:
        io_buf = io.BytesIO()
        fig.savefig(io_buf, format='raw')
        io_buf.seek(0)
        img = Image.fromarray( np.reshape(np.frombuffer(io_buf.getvalue(), dtype=np.uint8),
        newshape=(int(fig.bbox.bounds[3]), int(fig.bbox.bounds[2]), -1)) )
        io_buf.close()
        return img
    # save and load from a tmp file
    tf = tempfile.TemporaryFile(suffix='.png')
    fig.savefig(tf, format='png')
    if save!=None:
        fig.savefig(save)
    return Image.open(tf)

def draw_graph( G, layout,curve,path  ):
    fig = plt.figure()
    lnetreduce.plot_graph(G, edge_labels=True, curve=curve,layout=layout) 

    return fig_to_image(fig,save=path)

def launch_gui():
    global fenetre
    fenetre = Tk()
    interface = Interface(fenetre)
    fenetre.title("LNetReduce")
    interface.mainloop()



    
