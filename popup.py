import traceback

import customtkinter as ctk
import tkinter as tk
import backend as back
import run
import PIL
from colours import *

logo = 0

class confirmDelete(ctk.CTkFrame):
    def __init__(self, master, database, **kwargs):
        super().__init__(master, **kwargs)

        def confirm():
            database_name = f"{database}.db"
            back.delete_database(database_name)
            self.place_forget()
            master.DBlist.generateDBbuttons()

        def cancel():
            self.place_forget()

        deleteInfo = ctk.CTkLabel(self, text=("Are you sure you want to delete " + database + "?"), fg_color=gray)
        deleteInfo.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        # Cancel button
        cancelBtn = SquareButton(self, text="Cancel", command=cancel)
        cancelBtn.place(relx=0.25, rely=0.6, anchor=tk.CENTER)
        # Confirm button
        confirmBtn = SquareButton(self, text="Delete", command=confirm)
        confirmBtn.place(relx=0.75, rely=0.6, anchor=tk.CENTER)


class DBItems(ctk.CTkButton):
    def __init__(self, master, database, **kwargs):
        super().__init__(master, **kwargs)
        def confirm():
            # Shows the confirmation popup
            self.deleteGUI = confirmDelete(master.master.master.master.master.sDB, database, corner_radius=0, fg_color=gray, border_color=black, border_width=2)
            self.deleteGUI.place(relx=0.5, rely=0.5, relwidth=0.7, relheight=0.7, anchor=tk.CENTER)
        # Database Items
        self.configure(self, text=database, command=lambda: master.select_database(database), height=30, corner_radius=0)
        self.pack(fill=tk.X, padx=10, pady=(10,0))
        # Delete Button
        deleteBTN = SquareButton(self, text="X", command=confirm)
        deleteBTN.place(relx=0.95,rely=0.5, relwidth=0.1, relheight=1, anchor=tk.CENTER)


class DBLists(ctk.CTkScrollableFrame):
    # Function to load a folder as a database
    def select_folder(self):
        # Open a folder selection dialog
        self.folder_path = tk.filedialog.askdirectory()
        # Update the selected folder path label
        self.folder_label.configure(text=self.folder_path)

    # Function to make buttons that list the databases
    def generateDBbuttons(self):
        # Clears already existing buttons
        for i in self.DBs:
            i.pack_forget()
        self.DBs.clear()
        self.options_list = back.database_list() # collects the list of current existing databases

        # Generates the database buttons in a list
        for database in self.options_list:
            if self.search_result == "" or self.search_result.lower() in database.lower():
                self.DBs.append(DBItems(self, database, anchor="w", fg_color=white, text_color=black, hover_color=white))

    # Function to select the database
    def select_database(self, database_name):
        print(database_name)
        if database_name != "":
            run.database_raw = database_name
            database_name = f"databases/{database_name}.db"
            run.database_name = database_name
            self.master.master.master.master.close_popup(database_name)

    def __init__(self, master, **kwarg):
        super().__init__(master, **kwarg)
        self.search_result = "" # Template value for s
        self.DBs = []


class selectDB(ctk.CTkFrame):
    # Shows the Selection Screen
    def ShowSS(self):
        self.master.ss.pack(fill="both", expand=1)
        self.pack_forget()

    def __init__(self, master, **kwarg):
        super().__init__(master, **kwarg)
        # Generates the results after 1 tick
        # NOTE: This part is required because without it, the new character entered would not be registered in the search result
        def searchResults():
            self.after(1, result)

        def result():
            self.searchResult = self.search.get() # gets the string within the entry box
            self.DBlist.search_result = self.searchResult
            self.DBlist.generateDBbuttons()

        self.selectLabel = ctk.CTkLabel(self, text="SELECT DATABASE", corner_radius=0, fg_color=dark_gray, text_color=white)
        self.selectLabel.place(relx=0.5, rely=0.05, relwidth=1, relheight=0.1, anchor=tk.CENTER)

        # Back button
        self.backButton = SquareButton(self, text="Back", command=self.ShowSS)
        self.backButton.place(x=0, y=0, relwidth=0.1, relheight=0.1)

        # Search box
        self.search = ctk.CTkEntry(self, placeholder_text="Search:", fg_color=white, text_color=black, corner_radius=0)
        self.search.bind("<Key>", command=lambda x: searchResults())
        self.search.place(relx=0.5, rely=0.25, relwidth=0.9, relheight=0.1, anchor=tk.CENTER)

        # List of all the databases
        self.DBlist = DBLists(self, corner_radius=0, fg_color=gray)
        self.DBlist.place(relx=0.5, rely=0.625, relwidth=0.9, relheight=0.55, anchor=tk.CENTER)


class createFrame(ctk.CTkFrame):
    # Selects the folder the user is going to generate the database with
    def selectFolder(self):
        intLimit = 50
        # Open a folder selection dialog
        self.folderPath = tk.filedialog.askdirectory()
        # Update the selected folder path label
        if len(self.folderPath) > intLimit:
            self.folderLabel.configure(text=self.folderPath[:intLimit]+"...")
        else:
            self.folderLabel.configure(text=self.folderPath)
    # Database creation checks
    def generateDB(self):
        self.options_list = back.database_list()
        new_database_name = self.databaseName.get()
        if new_database_name.lower() in [option.lower() for option in self.options_list]:
            self.ErrorMSG.configure(text='Database name already in use')
            self.master.createDBBtn.configure(state=tk.NORMAL)
        elif new_database_name == "":
            self.ErrorMSG.configure(text='Database name is not entered')
            self.master.createDBBtn.configure(state=tk.NORMAL)
        elif self.folderPath == "":
            self.ErrorMSG.configure(text='Database folder is not selected')
            self.master.createDBBtn.configure(state=tk.NORMAL)
        else:
            self.ErrorMSG.configure(text='')
            try:
                # callback function to update the progress bar
                self.progressBarLabel.place(relx=0.5, rely=0.7, anchor=tk.CENTER)
                def update_progress_bar(progress):
                    progress_bar.set(progress)
                    self.loadDBbtn.place_forget()
                    self.progressBarLabel.configure(
                        text=("Converting files to dataframe: " + str(int(progress * 100)) + "%"))
                    if progress == 1:
                        self.progressBarLabel.configure(text=("Conversion Completed!"))
                        self.loadDBbtn.place(relx=0.5, rely=0.8, anchor=tk.CENTER)
                        self.loadDBbtn.configure(command=lambda: self.master.master.sDB.DBlist.select_database(new_database_name))
                        self.master.createDBBtn.configure(state=tk.NORMAL)
                    self.master.update()

                progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", progress_color=red)
                progress_bar.place(relx=0.5, rely=0.8, relwidth=0.8, anchor=tk.CENTER)

                update_progress_bar(0)

                # Call the backend function with the progress callback
                back.convert_files_to_database(self.folderPath, new_database_name, update_progress_bar)
                # Add the new database to the listbox selection_menu
                # self.selection_menu.insert(tk.END, new_database_name)
                # Hide the progress bar
                progress_bar.destroy()
                # progress_window.after(100, progress_bar.destroy)

            except Exception as e:
                #progress_bar.destroy
                #progress_window.destroy()
                self.progressBarLabel.configure(text=("Conversion Failed"))
                progress_bar.destroy()
                self.loadDBbtn.place_forget()
                self.master.createDBBtn.configure(state=tk.NORMAL)
                tk.messagebox.showerror('Error', f'Error in the script: {e} \n\n\n {traceback.format_exc()}')

    def __init__(self, master, **kwarg):
        super().__init__(master, **kwarg)
        self.folderPath = ""
        # Database Name & label
        self.databaseNameLabel = ctk.CTkLabel(self, text="Database Name:")
        self.databaseNameLabel.place(relx=0.1, rely=0.1)

        # Text entry for the name of the database
        self.databaseName = ctk.CTkEntry(self, corner_radius=0)
        self.databaseName.place(relx=0.1, rely=0.2, relwidth=0.8)

        # Button to select the folder
        self.selectFolder = RoundButton(self, text="Select Folder", command=self.selectFolder)
        self.selectFolder.place(relx=0.1, rely=0.35)

        # File path for the folder in text form
        self.folderLabel = ctk.CTkLabel(self, text="")
        self.folderLabel.place(relx=0.35, rely=0.35)

        # progress bar and load button (which are hidden until it is shown)
        self.progressBarLabel = ctk.CTkLabel(self, text="Converting files to dataframe: 0%")
        self.loadDBbtn = RoundButton(self, text="Load Database")

        # Error message
        self.ErrorMSG = ctk.CTkLabel(self, text="", text_color="red")
        self.ErrorMSG.place(relx=0.1, rely=0.9)


class createDB(ctk.CTkFrame):
    # Shows the select screen
    def ShowSS(self):
        self.master.ss.pack(fill="both", expand=1)
        self.pack_forget()

    # Disable the create button if the button is pressed
    def disableCreateBtn(self):
        self.createDBBtn.configure(state=tk.DISABLED)
        self.createFrame.generateDB()

    def __init__(self, master, **kwarg):
        super().__init__(master, **kwarg)
        self.createLabel = ctk.CTkLabel(self, text="CREATE DATABASE", corner_radius=0, fg_color=dark_gray, text_color=white)
        self.createLabel.place(relx=0.5, rely=0.05, relwidth=1, relheight=0.1, anchor=tk.CENTER)

        # Back Button
        self.backButton = SquareButton(self, text="Back", command=self.ShowSS)
        self.backButton.place(x=0, y=0, relwidth=0.1, relheight=0.1)

        # The Frame for the information within the create screen
        self.createFrame = createFrame(self, corner_radius=0, fg_color=gray)
        self.createFrame.place(relx=0.5, rely=0.5, relwidth=0.9, relheight=0.6, anchor=tk.CENTER)

        # The Button for the create Database button
        self.createDBBtn = RoundButton(self, text="Create Database", command=self.disableCreateBtn)
        self.createDBBtn.place(relx=0.5, rely=0.875, anchor=tk.CENTER)


class selectionScreen(ctk.CTkFrame):

    def logoMove(self):
        if self.imgMag > 0:
            self.imgPos -= self.imgMag
            for a in range(len(self.image)):
                self.image[a].place(y=self.imgPos)
            self.imgMag -= .0625
            self.after(5, self.logoMove)

    def __init__(self, master, **kwarg):
        super().__init__(master, **kwarg)
        # Shows the select screen and hides the create screen and the select screen
        def selectMode():
            master.sDB.pack(fill="both", expand=1)
            master.cDB.pack_forget()
            master.ss.pack_forget()

            master.sDB.DBlist.generateDBbuttons()

        # Shows the create screen and hides the select screen and the select screen
        def createMode():
            master.sDB.pack_forget()
            master.cDB.pack(fill="both", expand=1)
            master.ss.pack_forget()

        global logo
        self.image = [ctk.CTkLabel(self, text="")]
        if(logo==0):
            logo = ctk.CTkImage(light_image=PIL.Image.open(os.getcwd() + "/assets/logo.png"), size=(160,160))
            self.image[0] = ctk.CTkLabel(self, text="", image=logo)
            self.image[0].place(relx=.5, anchor=tk.N)

        #self.icop = [0,20,40,0,10]
        #self.icon = [0,0,0,0,0]
        #self.icon[0] = CTkButton(self, text="", corner_radius=0, fg_color=red, hover_color=red, width=125, height=125)
        #self.icon[0].place(relx=.5, anchor=tk.N)
        #self.icon[1] = CTkButton(self, text="", corner_radius=50, fg_color=white, hover_color=white, bg_color=red, width=100, height=100)
        #self.icon[1].place(relx=.5, anchor=tk.N)
        #self.icon[2] = CTkButton(self, text="", corner_radius=50, fg_color=red, hover_color=red, width=60, height=60)
        #self.icon[2].place(relx=.5, anchor=tk.N)
        #self.icon[3] = CTkButton(self, text="", corner_radius=50, fg_color=red, hover_color=red, bg_color=red, width=30, height=60)
        #self.icon[3].place(relx=.5, anchor=tk.N)
        #self.icon[4] = CTkButton(self, text="", corner_radius=50, fg_color=white, hover_color=white, bg_color=red, width=15, height=45)
        #self.icon[4].place(relx=.5, anchor=tk.N)

        self.imgPos = 805
        self.imgMag = 10
        self.logoMove()

        # Button for the select screen
        self.select = RoundButton(self, text="SELECT DATABASE", command=selectMode)
        self.select.place(relx=0.26, rely=0.78, relwidth=0.45, relheight=0.35, anchor=tk.CENTER)

        # Button for the create screen
        self.create = RoundButton(self, text="CREATE DATABASE", command=createMode)
        self.create.place(relx=0.74, rely=0.78, relwidth=0.45, relheight=0.35, anchor=tk.CENTER)

        self.readme = ctk.CTkLabel(self, wraplength=240, text="This program is designed to make it easier for the clients from CAEEPR to view and visualise data which they provide in the form of multiple .out files.")
        self.readme.place(relx=0.5, rely=0.3, anchor=tk.N)

        self.readml = ctk.CTkLabel(self, wraplength=240, text="If the scenario to be analysed has already beed added to the program, click the left side button 'SELECT DATABASE'.")
        self.readml.place(relx=0.1, rely=0.5, anchor=tk.W)

        self.readmr = ctk.CTkLabel(self, wraplength=240, text="If you wish to analyse a scenario which has not been previously added to the program, click on the right side selection; 'CREATE DATABASE'.")
        self.readmr.place(relx=0.9, rely=0.5, anchor=tk.E)


class App(ctk.CTk):
    def reload(self):
        self.deiconify()
    def close_popup(self, database_name):
        # Close the window
        try:
            back.generator_linking(node=1, day=1, hour=1, database=database_name,
                                   ax="test")  # This needs to be checked, BEFORE run.App() is called!
            self.withdraw()
            run.App()
        except Exception as e:
            print(traceback.format_exc())
            if str(e).find("energyGenerate") > 0:
                tk.messagebox.showerror('Error',
                                     f'Error in the script: {e} \nThis error indicates the folder this database was '
                                     f'made from, was missing necassary files \n\n\n {traceback.format_exc()}')
            else:
                tk.messagebox.showerror('Error', f'Error in the script: {e} \n\n\n {traceback.format_exc()}')

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")  # Light Mode
        self.geometry("720x480")  # Size of the Window
        self.title("Queensland Energy Market")  # Title of the Window
        self.protocol("WM_DELETE_WINDOW", lambda: self.quit())

        self.ss = selectionScreen(self, corner_radius=0, fg_color=white)
        self.ss.pack(fill="both", expand=1)
        self.sDB = selectDB(self, corner_radius=0, fg_color=white)
        self.cDB = createDB(self, corner_radius=0, fg_color=white)


if __name__ == '__main__':
    app = App()
    app.mainloop()
