# BACK END
import backend as back

# FRONT END
import os
import traceback
import tkinter as tk

import customtkinter as ctk
import PIL
import matplotlib
import math

from tkinter import IntVar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from multiprocessing import freeze_support

matplotlib.use("TkAgg")

from tkinter import messagebox
import pandas as pd

import popup
from colours import *

folder_path = ""  # Creates a path for the folder of the
database_name = ""
database_raw = ""

nodeLimit = 60  # Hard limit of the nodes (59)

# Names the Nodes
nodeList = []
for i in range(1, nodeLimit):
    nodeList.append(str(i))


# The box that contains the input data
class InputData(ctk.CTkFrame):
    def stringGenerate(self, data):

        # String generation for the raw data from the backend
        dataString = ""
        for key, value in data.items():
            if isinstance(value, dict):
                dataString += f"{key}:\n"
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, dict):
                        dataString += f"   {subkey}:\n"
                        for subsubkey, subsubvalue in subvalue.items():
                            dataString += f"    {subsubkey}: {subsubvalue}\n"
                            continue
                    else:
                        dataString += f"  {subkey}: {subvalue}\n"
                        continue
            else:
                dataString += f"{key}: {value}\n"
                continue
        print(dataString)
        return dataString

    def generateInfo(self):
        try:
            # Attempts to generate and load in the data
            self.dataGroup1 = back.injection_withdrawal(database_name, int(self.master.nodeCompare1.nodeDropdown.get()),
                                                        int(self.dayEntry.get()),
                                                        int(self.hourEntry.get()))
            self.master.nodeCompare1.textbox.configure(state="normal")
            self.master.nodeCompare1.textbox.delete("0.0", "end")
            self.master.nodeCompare1.textbox.insert("0.0", self.stringGenerate(self.dataGroup1))
            self.master.nodeCompare1.textbox.configure(state="disabled")

            self.dataGroup2 = back.injection_withdrawal(database_name, int(self.master.nodeCompare2.nodeDropdown.get()),
                                                        int(self.dayEntry.get()),
                                                        int(self.hourEntry.get()))
            self.master.nodeCompare2.textbox.configure(state="normal")
            self.master.nodeCompare2.textbox.delete("0.0", "end")
            self.master.nodeCompare2.textbox.insert("0.0", self.stringGenerate(self.dataGroup2))
            self.master.nodeCompare2.textbox.configure(state="disabled")
            self.dayErrorLabel.configure(text="")
            self.hourErrorLabel.configure(text="")
            self.master.nodeCompare1.hourErrorLabel.configure(text="Invalid Node")
            self.master.nodeCompare2.hourErrorLabel.configure(text="Invalid Node")
        except Exception as e:
            # If the generation attempts fails, then it will determine the cause of the issue
            # Tests if the day is an integer between 0 and 364 days
            try:
                if 364 >= int(self.dayEntry.get()) >= 0:
                    self.dayErrorLabel.configure(text="")
                else:
                    # If the if statement fails then the number is outside the scope
                    self.dayErrorLabel.configure(text="Out of Scope")
            except:
                # If the attempt fails, data is not an integer and is an invalid day
                self.dayErrorLabel.configure(text="Invalid Day")

            # Tests if the hour is an integer between 1 and 48 hours
            try:
                if 48 >= int(self.hourEntry.get()) >= 1:
                    self.hourErrorLabel.configure(text="")
                else:
                    # If the if statement fails then the number is outside the scope
                    self.hourErrorLabel.configure(text="Out of Scope")
            except:
                # If the attempt fails, data is not an integer and is an invalid hour
                self.hourErrorLabel.configure(text="Invalid Hour")

            # Tests if the node is an integer between 1 and the node limit
            try:
                if nodeLimit > int(self.master.nodeCompare1.nodeDropdown.get()) >= 1:
                    self.master.nodeCompare1.nodeErrorLabel.configure(text="")
                else:
                    # If the if statement fails then the number is outside the scope
                    self.master.nodeCompare1.nodeErrorLabel.configure(text="Out of Scope")
            except:
                # If the attempt fails, data is not an integer and is an invalid node
                self.master.nodeCompare1.nodeErrorLabel.configure(text="Invalid Node")

            # Tests if the node is an integer between 1 and the node limit
            try:
                if nodeLimit > int(self.master.nodeCompare2.nodeDropdown.get()) >= 1:
                    self.master.nodeCompare2.nodeErrorLabel.configure(text="")
                else:
                    # If the if statement fails then the number is outside the scope
                    self.master.nodeCompare2.nodeErrorLabel.configure(text="Out of Scope")
            except:
                # If the attempt fails, data is not an integer and is an invalid node
                self.master.nodeCompare2.nodeErrorLabel.configure(text="Invalid Node")

            if str(e).find('"FROM"') > 0:
                self.generationError.configure(
                    text="An error has been given.\nLikely mapping file data is missing\nfor one of the given nodes")
            else:
                self.generationError.configure(text="")

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(corner_radius=0, fg_color=gray)  # Sets the colour of this object to gray

        # Label for the input
        self.inputLabel = ctk.CTkLabel(self, text="Input Data", fg_color=dark_gray, text_color=white)
        self.inputLabel.place(relx=0.5, rely=0.05, relwidth=1, relheight=0.1, anchor=ctk.CENTER)

        # Day label and input
        self.dayLabel = ctk.CTkLabel(self, text="Day (0-364)")
        self.dayLabel.place(relx=0.5, rely=0.15, relwidth=0.9, anchor=ctk.CENTER)
        self.dayEntry = ctk.CTkEntry(self, corner_radius=0)
        self.dayEntry.place(relx=0.5, rely=0.23, relwidth=0.9, anchor=ctk.CENTER)
        self.dayErrorLabel = ctk.CTkLabel(self, text="", text_color="red")
        self.dayErrorLabel.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

        # Hour label and input
        self.hourLabel = ctk.CTkLabel(self, text="Hour (1-48)")
        self.hourLabel.place(relx=0.5, rely=0.45, relwidth=0.9, anchor=ctk.CENTER)
        self.hourEntry = ctk.CTkEntry(self, corner_radius=0)
        self.hourEntry.place(relx=0.5, rely=0.53, relwidth=0.9, anchor=ctk.CENTER)
        self.hourErrorLabel = ctk.CTkLabel(self, text="", text_color="red")
        self.hourErrorLabel.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

        self.generationError = ctk.CTkLabel(self, text="", text_color="red")
        self.generationError.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

        if(something):
            valuesArray=[
                "one",
                "two"
            ]
            combobox = ctk.CTkComboBox(master, values=valuesArray)
            combobox.pack(padx=20, pady=10)
            combobox.set(valuesArray[0])
            combobox.place(relx=.5, rely=.6, anchor=ctk.CENTER)

        # Hour label and input
        self.generate = RoundButton(self, text="Generate", command=self.generateInfo)
        self.generate.place(relx=0.5, rely=0.95, relwidth=0.9, anchor=ctk.CENTER)

# The box that contains the Node Selection
class OutputData(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(corner_radius=0, fg_color=gray)

        # Node label and dropdown menu
        self.nodeLabel = ctk.CTkLabel(self, text=f"Node (1-{nodeLimit - 1})", fg_color=dark_gray, text_color=white)
        self.nodeLabel.place(relx=0.5, rely=0.05, relwidth=1, relheight=0.1, anchor=ctk.CENTER)
        self.nodeErrorLabel = ctk.CTkLabel(self, text="", text_color="red")
        self.nodeErrorLabel.place(relx=0, rely=0.16, relwidth=1)
        self.nodeDropdown = ctk.CTkComboBox(self, values=nodeList, height=30, corner_radius=0, button_color=light_red)
        self.nodeDropdown.place(relx=0, rely=0.1, relwidth=1)

        # Data output
        self.textbox = ctk.CTkTextbox(self, state="disabled", corner_radius=0)
        self.textbox.place(relx=0.5, rely=0.6, relwidth=0.9, relheight=0.77, anchor=ctk.CENTER)


# Main frame for Mode 1 (Tab 1)
class Mode1(ctk.CTkFrame):
    # Main frame output for Mode1
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # Compare Node 1
        self.nodeCompare1 = OutputData(self)
        self.nodeCompare1.place(relx=0.18, rely=0.5, relwidth=0.3, relheight=0.9, anchor=tk.CENTER)

        # Inputs for queries
        self.dataInput = InputData(self)
        self.dataInput.place(relx=0.5, rely=0.5, relwidth=0.3, relheight=0.9, anchor=tk.CENTER)

        # Compare Node 2
        self.nodeCompare2 = OutputData(self)
        self.nodeCompare2.place(relx=0.82, rely=0.5, relwidth=0.3, relheight=0.9, anchor=tk.CENTER)


class ControlFrame(ctk.CTkFrame):
    # Shows the next hour of mode 2
    def nextHour(self):
        hourNumber = self.slider.get()  # Sets the value of the slider to hourNumber
        # print("played", hourNumber)
        hourNumber += 1  # The next iteration of the slider number
        self.slider.set(hourNumber)  # Sets the slider to the next iteration
        # Checks if the animation is turned on, day is more than 365, and more than 48 hours
        if self.animation and int(self.master.dayInput.get()) >= 364 and int(self.slider.get()) >= 48:
            self.activeAnimation()  # Turns off animation
            # print("off")
        # Checks if the hour is 49
        if hourNumber == 49:
            dayValue = int(self.master.dayInput.get()) + 1  # Adds 1 to the day
            self.master.dayInput.delete(0, "end")  # Clears the day input
            self.master.dayInput.insert(0, str(dayValue))  # Sets the new day to the day input
            self.slider.set(0)  # Resets the slider

        # Checks if the animation is on to set the next hour
        def nextFrame():
            if self.animation:
                self.sliderValue(int(self.slider.get()))
                self.nextHour()

        self.after(1000, nextFrame)  # plays the next frame function after 1000ms
        # NOTE: doing "self.after(1000, self.nextHour)" would not work because the next hour would play after the
        # button is pressed

    # Animation switch
    def activeAnimation(self):
        # Checks if the animation is
        # on : Turns off the animation and sets the button to say "PLAY"
        if self.animation:
            self.animation = False
            self.animationButton.configure(text="PLAY")
        # off and day less than 365, slider less than 48: Turns the animation on and sets the button to say "STOP"
        # then shows the next hour
        elif not self.animation and self.master.dayInput.get() != "" and self.master.nodeDropdown.get() != "":
            try:
                if int(self.master.dayInput.get()) < 364 or int(self.slider.get()) < 48:
                    self.animation = True
                    self.animationButton.configure(text="STOP")
                    self.nextHour()
            except:
                pass

    # Slider callback
    def sliderValue(self, value):
        self.master.hourValue = value
        self.master.ax.clear()
        if self.master.dayInput.get() != "" and self.master.nodeDropdown.get() != "" and int(
                self.master.nodeDropdown.get()) <= nodeLimit:
            self.master.n, self.master.d, self.master.h = int(self.master.nodeDropdown.get()), int(
                self.master.dayInput.get()), int(self.master.hourValue)
            # print(self.n, self.d, self.h)
            back.generator_linking(self.master.n, self.master.d, self.master.h, database_name, self.master.ax)
        self.master.canvas.draw()

    # Save the graph
    def saveImg(self):
        dbFileName = str(database_raw) + "_n" + str(self.master.n) + "d" + str(self.master.d) + "h" + str(
            self.hourConversion + self.minuteConversion)
        imageLocation = tk.filedialog.asksaveasfile(mode="w",
                                                    title='Save As',
                                                    filetypes=[
                                                        ("PNG Image", "*.png"),
                                                        ("JPEG Image", "*.jpeg *jpeg"),
                                                        ("GIF Image", "*.gif"),
                                                        ("All files", "*.*")
                                                    ],
                                                    initialfile=dbFileName,
                                                    defaultextension=".png"
                                                    )
        if imageLocation:
            # print(imageLocation)
            self.master.fig.savefig(imageLocation.name)

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # These three values relates to the clock, not the data
        self.timeString = "00:30 AM"  # Default time string
        self.hourConversion = 0  # Defines the number of hours
        self.minuteConversion = 30  # Defines the number of minutes

        # Function to check if the slider has been released and then generates the graph
        def releaseSlider(_):
            self.sliderValue(self.slider.get())

        # Function to stop the animation - specifically made for the user clicks the slider
        def stopAnimation(_):
            if self.animation:
                self.activeAnimation()

        # Function to translate the raw hour to a readable time
        def timeConfigure(value):
            totalMinutes = int(value) * 30
            self.hourConversion = f'{math.floor(totalMinutes / 60)}'.zfill(2)
            self.minuteConversion = f'{totalMinutes % 60}'.zfill(2)
            if self.switchFormat == 1:
                if 12 < int(self.hourConversion) < 24:
                    self.timeString = f"{int(self.hourConversion) % 12}:{self.minuteConversion} PM"
                elif int(self.hourConversion) == 12:
                    self.timeString = f"{self.hourConversion}:{self.minuteConversion} PM"
                else:
                    self.timeString = f"{int(self.hourConversion) % 24}:{self.minuteConversion} AM"
            elif self.switchFormat == 2:
                self.timeString = f"{self.hourConversion}:{self.minuteConversion}"
            elif self.switchFormat == 3:
                self.timeString = f"{value}"

            self.sliderLabel.configure(text=self.timeString)

        # Half-hour Slider
        self.slider = tk.Scale(self, from_=1, to=48, orient="horizontal", command=timeConfigure, bg=white,
                               showvalue=0, borderwidth=0)
        self.slider.place(relx=0.5, rely=0.7, relwidth=0.9, anchor=tk.CENTER)
        self.slider.bind("<1>", stopAnimation)  # Checks for an action of clicking the slider to stop the animation
        self.slider.bind("<ButtonRelease>",
                         releaseSlider)  # Checks for an action of releasing the slider to update the graph

        # Label for the slider
        self.sliderLabel = ctk.CTkLabel(self, text=self.timeString, text_color=white, corner_radius=50,
                                        fg_color=dark_gray, height=30)
        self.sliderLabel.place(relx=0.5, rely=0.3, relwidth=0.2, anchor=tk.CENTER)

        # Format switcher for the time:
        # 1 - 12 Hour (09:00 PM)
        # 2 - 24 Hour (21:00)
        # 3 - Raw int (42)
        self.switchFormat = 1

        def switchFormat(_):
            if self.switchFormat == 1:
                self.switchFormat = 2
            elif self.switchFormat == 2:
                self.switchFormat = 3
            elif self.switchFormat == 3:
                self.switchFormat = 1
            else:
                print(f"Unknown Format: {self.switchFormat}")
            timeConfigure(self.slider.get())

        self.sliderLabel.bind("<1>", switchFormat)  # click action to switch the formats

        self.sliderValue(1)  # Default hour value (00:30)

        # Save image button
        saveImage = RoundButton(self, text="SAVE", command=self.saveImg)
        saveImage.place(relx=0.75, rely=0.3, relwidth=0.15, anchor=tk.CENTER)

        # Animation button
        self.animation = False  # Default is turned off
        self.animationButton = RoundButton(self, text="PLAY", command=self.activeAnimation)
        self.animationButton.place(relx=0.25, rely=0.3, relwidth=0.15, anchor=tk.CENTER)


class AnimationFrame(ctk.CTkFrame):
    # Main frame output for Mode2
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.hourValue = 1  # Default hour value
        # Graph
        self.fig = Figure(dpi=80)
        self.ax = self.fig.add_subplot(1, 1, 1)

        # Response from a node or day change
        def node_callback(value):
            try:
                # If the day input is not empty, node dropdown is not empty, and node is less than the limit
                if self.dayInput.get() != "" and self.nodeDropdown.get() != "" and int(
                        self.nodeDropdown.get()) >= nodeLimit:
                    # Change the error message to say it is an invalid node or day
                    self.errorLabel.configure(text="Invalid input for node or day")
                    # Turns off the animation
                    if self.controls.animation:
                        self.controls.activeAnimation()
                else:
                    # Or else, clear the error and generate a new graph
                    self.ax.clear()
                    node, day, hour = int(value), int(self.dayInput.get()), int(self.hourValue)
                    # print(node, day, hour)
                    back.generator_linking(node, day, hour, database_name, self.ax)
                    self.canvas.draw()
                    self.errorLabel.configure(text="")
            # If this fails, then change the error message to say it is an invalid node or day
            except Exception as e:
                # print(e)
                self.errorLabel.configure(text="Error has occured. This node may not contain mapping information")

        # Key bind callbacks
        def newInput(value):
            self.after(1, lambda: node_callback(self.nodeDropdown.get()))

        # Error message
        self.errorLabel = ctk.CTkLabel(self, text="", text_color="red")
        self.errorLabel.place(relx=0.5, rely=0.15, anchor=tk.CENTER)

        # The Node Selection Box
        self.nodeLabel = ctk.CTkLabel(self, text=f"Node (1-{nodeLimit - 1})")
        self.nodeLabel.place(relx=0.25, rely=0.04, relwidth=0.4, anchor=tk.CENTER)
        self.nodeDropdown = ctk.CTkComboBox(self, values=nodeList, height=30, command=node_callback, corner_radius=0,
                                            button_color=light_red)
        self.nodeDropdown.place(relx=0.25, rely=0.1, relwidth=0.4, anchor=ctk.CENTER)
        self.nodeDropdown.bind("<Key>", command=newInput)

        # Button for the day input
        self.dayLabel = ctk.CTkLabel(self, text="Day (0-364)")
        self.dayLabel.place(relx=0.75, rely=0.04, relwidth=0.4, anchor=tk.CENTER)
        self.dayInput = ctk.CTkEntry(self, height=30, corner_radius=0)
        self.dayInput.insert(0, "0")
        self.dayInput.place(relx=0.75, rely=0.1, relwidth=0.4, anchor=tk.CENTER)
        self.dayInput.bind("<Key>", command=newInput)

        # Canvas for the graph
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        # self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas.get_tk_widget().place(relx=0.5, rely=0.5, relwidth=0.9, relheight=0.65, anchor=tk.CENTER)

        self.controls = ControlFrame(self, fg_color=white, corner_radius=0)
        self.controls.place(relx=0.5, rely=0.9, relheight=0.15, relwidth=0.9, anchor=tk.CENTER)


# Main frame for Mode 2 (Tab 2)
class Mode2(ctk.CTkFrame):
    # Main frame output for Sidebar
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.animationFrame = AnimationFrame(self, fg_color=gray, corner_radius=0)
        self.animationFrame.place(relx=0.5, rely=0.5, relwidth=0.94, relheight=0.9, anchor=tk.CENTER)


class GraphFrame(ctk.CTkFrame):
    def graph_generate(self):
        self.generate.configure(state="disabled")
        try:
            # If the day input is not empty, node dropdown is not empty, and node is less than the limit
            if self.dayInput.get() != "" and self.nodeDropdown.get() != "" and int(
                    self.nodeDropdown.get()) >= nodeLimit:
                # Change the error message to say it is an invalid node or day
                self.errorLabel.configure(text="Invalid input for node or day")
            else:
                # Or else, clear the error and generate a new graph
                self.ax.clear()
                node, day = int(self.nodeDropdown.get()), int(self.dayInput.get())
                # print(node, day, hour)
                self.df = back.create_dataframe(database_name, node, day, test=False)
                self.canvas.draw()
                self.update_show()
                self.errorLabel.configure(text="")
                self.master.update()

            self.after(100, self.generate.configure(state="normal"))
        # If this fails, then change the error message to say it is an invalid node or day
        except Exception as e:
            print(e)
            self.errorLabel.configure(text="Error has occured. This node may not contain mapping information")
            self.after(100, self.generate.configure(state="normal"))

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # The Node Selection Box
        self.nodeLabel = ctk.CTkLabel(self, text=f"Node (1-{nodeLimit - 1})")
        self.nodeLabel.place(relx=0.25, rely=0.04, relwidth=0.4, anchor=tk.CENTER)
        self.nodeDropdown = ctk.CTkComboBox(self, values=nodeList, height=30, corner_radius=0,
                                            button_color=light_red)
        self.nodeDropdown.place(relx=0.25, rely=0.1, relwidth=0.4, anchor=ctk.CENTER)

        # Button for the day input
        self.dayLabel = ctk.CTkLabel(self, text="Day (0-364)")
        self.dayLabel.place(relx=0.75, rely=0.04, relwidth=0.4, anchor=tk.CENTER)
        self.dayInput = ctk.CTkEntry(self, height=30, corner_radius=0)
        self.dayInput.insert(0, "0")
        self.dayInput.place(relx=0.75, rely=0.1, relwidth=0.4, anchor=tk.CENTER)

        self.fig = Figure(figsize=(13, 8), dpi=75)
        self.ax = self.fig.add_subplot()
        self.df = back.create_dataframe(database_name, 8, 1, test=True)  # Get an empty dataframe
        # ctk.CTkFrame(self, fg_color=dark_gray, corner_radius=0).place(relx=0.5, rely=0.365, relwidth=0.91, relheight=0.67, anchor=tk.CENTER)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().place(relx=0.5, rely=0.45, relwidth=0.9, relheight=0.6, anchor=tk.CENTER)
        self.canvas.draw()

        # Error message
        self.errorLabel = ctk.CTkLabel(self, text="", text_color="red")
        self.errorLabel.place(relx=0.5, rely=0.17, anchor=tk.CENTER)
        # if set to 1, means the box is ticked by default
        self.check_total = IntVar()
        self.check_total.set(1)
        self.check_coal = IntVar()
        self.check_NGCC = IntVar()
        self.check_OCGT = IntVar()
        self.check_wind = IntVar()
        self.check_solar = IntVar()
        self.check_HYDRO = IntVar()
        self.check_PHES = IntVar()
        self.check_BESS = IntVar()
        self.check_injection = IntVar()
        self.check_injection.set(1)
        self.check_withdrawal = IntVar()
        self.check_withdrawal.set(1)
        self.check_source_demand = IntVar()
        self.check_source_demand.set(1)
        self.check_storage = IntVar()
        self.check_storage.set(1)
        self.check_transmission_losses = IntVar()
        self.check_transmission_losses.set(1)

        self.generate = RoundButton(self, text="Generate", command=self.graph_generate)
        self.generate.place(relx=0.3, rely=0.8, relwidth=0.2, anchor=ctk.CENTER)

        self.csvButton = RoundButton(self, text="Save CSV", command=self.saveCSV)
        self.csvButton.place(relx=0.7, rely=0.8, relwidth=0.2, anchor=ctk.CENTER)

        # Create the checkboxes and place them in two rows
        # Row 1

        self.total_check = SquareCheckbox(self, text='total', variable=self.check_total, onvalue=1, offvalue=0,
                                          command=self.update_show)
        self.total_check.place(relx=0.11, rely=0.88, anchor=tk.CENTER)

        self.black_coal_check = SquareCheckbox(self, text='black coal', variable=self.check_coal, onvalue=1, offvalue=0,
                                               command=self.update_show)
        self.black_coal_check.place(relx=0.24, rely=0.88, anchor=tk.CENTER)

        self.NGCC_check = SquareCheckbox(self, text='NGCC', variable=self.check_NGCC, onvalue=1, offvalue=0,
                                         command=self.update_show)
        self.NGCC_check.place(relx=0.37, rely=0.88, anchor=tk.CENTER)

        self.OCGT_check = SquareCheckbox(self, text='OCGT', variable=self.check_OCGT, onvalue=1, offvalue=0,
                                         command=self.update_show)
        self.OCGT_check.place(relx=0.50, rely=0.88, anchor=tk.CENTER)

        self.wind_check = SquareCheckbox(self, text='wind', variable=self.check_wind, onvalue=1, offvalue=0,
                                         command=self.update_show)
        self.wind_check.place(relx=0.63, rely=0.88, anchor=tk.CENTER)

        self.solar_check = SquareCheckbox(self, text='solar', variable=self.check_solar, onvalue=1, offvalue=0,
                                          command=self.update_show)
        self.solar_check.place(relx=0.76, rely=0.88, anchor=tk.CENTER)

        self.storage_check = SquareCheckbox(self, text='storage', variable=self.check_storage, onvalue=1, offvalue=0,
                                            command=self.update_show)
        self.storage_check.place(relx=0.89, rely=0.88, anchor=tk.CENTER)

        # Row 2

        self.transmission_loss_check = SquareCheckbox(self, text='transmission',
                                                      variable=self.check_transmission_losses, onvalue=1, offvalue=0,
                                                      command=self.update_show)
        self.transmission_loss_check.place(relx=0.11, rely=0.95, anchor=tk.CENTER)

        self.HYDRO_check = SquareCheckbox(self, text='HYDRO', variable=self.check_HYDRO, onvalue=1, offvalue=0,
                                          command=self.update_show)
        self.HYDRO_check.place(relx=0.24, rely=0.95, anchor=tk.CENTER)

        self.PHES_check = SquareCheckbox(self, text='PHES', variable=self.check_PHES, onvalue=1, offvalue=0,
                                         command=self.update_show)
        self.PHES_check.place(relx=0.37, rely=0.95, anchor=tk.CENTER)

        self.BESS_check = SquareCheckbox(self, text='BESS', variable=self.check_BESS, onvalue=1, offvalue=0,
                                         command=self.update_show)
        self.BESS_check.place(relx=0.50, rely=0.95, anchor=tk.CENTER)

        self.injection_check = SquareCheckbox(self, text='injection', variable=self.check_injection, onvalue=1,
                                              offvalue=0, command=self.update_show)
        self.injection_check.place(relx=0.63, rely=0.95, anchor=tk.CENTER)

        self.withdrawal_check = SquareCheckbox(self, text='withdrawal', variable=self.check_withdrawal, onvalue=1,
                                               offvalue=0, command=self.update_show)
        self.withdrawal_check.place(relx=0.76, rely=0.95, anchor=tk.CENTER)

        self.source_demand_check = SquareCheckbox(self, text='demand', variable=self.check_source_demand, onvalue=1,
                                                  offvalue=0, command=self.update_show)
        self.source_demand_check.place(relx=0.89, rely=0.95, anchor=tk.CENTER)

        # When the graph is generated

    def update_show(self):
        # Holds the catagories to show
        self.show = []
        checkboxes = {
            self.total_check: self.check_total,
            self.black_coal_check: self.check_coal,
            self.NGCC_check: self.check_NGCC,
            self.OCGT_check: self.check_OCGT,
            self.wind_check: self.check_wind,
            self.solar_check: self.check_solar,
            self.HYDRO_check: self.check_HYDRO,
            self.PHES_check: self.check_PHES,
            self.BESS_check: self.check_BESS,
            self.injection_check: self.check_injection,
            self.withdrawal_check: self.check_withdrawal,
            self.source_demand_check: self.check_source_demand,
            self.storage_check: self.check_storage,
            self.transmission_loss_check: self.check_transmission_losses
        }
        # Add catagories which are ticked to filter list
        for checkbox, variable in checkboxes.items():
            if variable.get() == 1:
                self.show.append(checkbox.cget("text"))

        # If a dataframe exists
        if isinstance(self.df, pd.DataFrame):
            self.ax.clear()
            back.update_graph(self.df, self.show, self.ax)
            self.canvas.draw()
        return (self.show)
        # print(self.show)  # print the list of checked items

    def saveCSV(self):
        if isinstance(self.df, pd.DataFrame):
            try:
                csvFileName = str(database_raw)
                csvLocation = tk.filedialog.asksaveasfile(mode="w",
                                                          title='Save As',
                                                          filetypes=[
                                                              ("CSV UTF-8", "*.csv"),
                                                              ("All files", "*.*")
                                                          ],
                                                          initialfile=csvFileName,
                                                          defaultextension=".csv"
                                                          )
                if csvLocation:
                    self.df.to_csv(csvLocation.name, index=False)
                messagebox.showinfo('Save successful', 'Successfully saved')
            except Exception as e:
                messagebox.showerror('Error',
                                     f'Save failed: \n\nError: {e} \n\nCheck the file is not open, and that you have permission to save in this directory')


class Mode3(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.graphFrame = GraphFrame(self, fg_color=gray, corner_radius=0)
        self.graphFrame.place(relx=0.5, rely=0.5, relwidth=0.94, relheight=0.9, anchor=tk.CENTER)


# Main frame for Mode 4 (Tab 4)
class Mode4(ctk.CTkFrame):
    # Main frame output for Mode4
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # Compare Node 1
        self.nodeCompare1 = OutputData(self)
        self.nodeCompare1.place(relx=0.18, rely=0.5, relwidth=0.3, relheight=0.9, anchor=tk.CENTER)

        # Inputs for queries
        self.dataInput = InputData(self)
        self.dataInput.place(relx=0.5, rely=0.5, relwidth=0.3, relheight=0.9, anchor=tk.CENTER)

        # Compare Node 2
        self.nodeCompare2 = OutputData(self)
        self.nodeCompare2.place(relx=0.82, rely=0.5, relwidth=0.3, relheight=0.9, anchor=tk.CENTER)


class LogoFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # Logo of the client
        logoImg = tk.Canvas(self)
        logoImg.pack(padx=5, pady=5)

        def resize_logo(e):
            # print(e)
            logo = PIL.Image.open(os.getcwd() + "/assets/logo.png")
            if e.width < e.height:
                main = e.width
            else:
                main = e.height
            new_logo = logo.resize((main, main))
            self.logoRef = PIL.ImageTk.PhotoImage(new_logo)
            logoImg.create_image(e.width / 2, e.height / 2, image=self.logoRef, anchor="center")

        logoImg.bind("<Configure>", resize_logo)


# Main frame for the Sidebar
class Sidebar(ctk.CTkFrame):
    # Hides the Sidebar
    def hideMenu(self):
        # Animates the sidebar
        if self.master.sidebarPosition >= -0.2:
            self.master.sidebarPosition -= 0.02
            self.place(relx=self.master.sidebarPosition, rely=0, relheight=1, relwidth=0.2)
            self.after(10, self.hideMenu)
        # else:
        #     print("Closed")

    # Main frame output for Sidebar
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        sidebarImg = ctk.CTkImage(light_image=PIL.Image.open(os.getcwd() + "/assets/back.png"))
        image = ctk.CTkLabel(self, text="", image=sidebarImg, fg_color=gray, corner_radius=0)
        image.place(relx=0.5, rely=0.125, relwidth=1, relheight=0.25, anchor=tk.CENTER)

        def resize_sidebarImg(e):
            sidebarImg.configure(size=(e.width, e.height))

        image.bind("<Configure>", resize_sidebarImg)

        # Button to hide the sidebar
        icon = ctk.CTkImage(light_image=PIL.Image.open(os.getcwd() + "/assets/Sidebar Icon.png"), size=(35, 35))
        hideMenu = SquareButton(self, text="", width=40, height=40, image=icon, command=self.hideMenu)
        hideMenu.place(x=0, y=0)

        # Shows Mode1 and hides Mode2
        def mode1():
            master.mode1.pack(fill="both", expand=1)
            master.mode2.pack_forget()
            master.mode3.pack_forget()
            master.mode4.pack_forget()
            button1.configure(fg_color=light_red)
            button2.configure(fg_color=red)
            button3.configure(fg_color=red)
            button4.configure(fg_color=red)
            if master.mode2.animationFrame.controls.animation:
                global something
                something = False
                master.mode2.animationFrame.controls.activeAnimation()

        # Shows Mode2 and hides Mode1
        def mode2():
            master.mode1.pack_forget()
            master.mode2.pack(fill="both", expand=1)
            master.mode3.pack_forget()
            master.mode4.pack_forget()
            button1.configure(fg_color=red)
            button2.configure(fg_color=light_red)
            button3.configure(fg_color=red)
            button4.configure(fg_color=red)

        def mode3():
            master.mode1.pack_forget()
            master.mode2.pack_forget()
            master.mode3.pack(fill="both", expand=1)
            master.mode4.pack_forget()
            button1.configure(fg_color=red)
            button2.configure(fg_color=red)
            button3.configure(fg_color=light_red)
            button4.configure(fg_color=red)
            if master.mode2.animationFrame.controls.animation:
                master.mode2.animationFrame.controls.activeAnimation()

        def mode4():
            master.mode1.pack_forget()
            master.mode2.pack_forget()
            master.mode3.pack_forget()
            master.mode4.pack(fill="both", expand=1)
            button1.configure(fg_color=red)
            button2.configure(fg_color=red)
            button3.configure(fg_color=red)
            button4.configure(fg_color=light_red)
            if master.mode2.animationFrame.controls.animation:
                global something
                something = TRUE
                master.mode2.animationFrame.controls.activeAnimation()

        # Opens the popup
        def popupLoad():
            master.withdraw()
            popup.App().reload()

        # Button to show Mode1
        button1 = SquareButton(self, text="Compare", command=mode1)
        button1.configure(fg_color=light_red)
        button1.place(relx=0.5, rely=0.2, relwidth=1, relheight=0.1, anchor=tk.CENTER)

        # Button to show Mode2
        button2 = SquareButton(self, text="Animation", command=mode2)
        button2.place(relx=0.5, rely=0.3, relwidth=1, relheight=0.1, anchor=tk.CENTER)

        # Button to show Mode2
        button3 = SquareButton(self, text="Overview", command=mode3)
        button3.place(relx=0.5, rely=0.4, relwidth=1, relheight=0.1, anchor=tk.CENTER)

        # Button to show Mode2
        button4 = SquareButton(self, text="Edit", command=mode4)
        button4.place(relx=0.5, rely=0.5, relwidth=1, relheight=0.1, anchor=tk.CENTER)

        # Button to return to the popup
        button5 = SquareButton(self, text="Change DB", command=popupLoad)
        button5.place(relx=0.5, rely=0.65, relwidth=1, relheight=0.1, anchor=tk.CENTER)

        logo = LogoFrame(self, fg_color=dark_gray)
        logo.place(relx=0.5, rely=0.85, relwidth=0.8, relheight=0.24, anchor=tk.CENTER)

        self.mouseIn = False

        def enter(_):
            self.mouseIn = True

        def leave(_):
            self.mouseIn = False

        def exitSidebar(_):
            if not self.mouseIn:
                self.hideMenu()

        # Checks if the mouse is within the sidebar
        self.bind("<Enter>", enter)
        self.bind("<Leave>", leave)

        # Checks if the mouse is within the open menu button
        self.master.openMenuBTN.bind("<Enter>", enter)
        self.master.openMenuBTN.bind("<Leave>", leave)
        image.bind("<Enter>", enter)
        image.bind("<Leave>", leave)

        # Checks if the mouse is clicked
        self.master.bind("<1>", exitSidebar)


# Full application
class App(ctk.CTkToplevel):
    # Shows the Sidebar
    def openMenu(self):
        # Animates the sidebar
        if self.sidebarPosition <= 0:
            self.sidebarPosition += 0.02
            self.sidebar.place(relx=self.sidebarPosition, rely=0, relheight=1, relwidth=0.2)
            self.after(10, self.openMenu)
        # else:
        #     print("Opened")

    # Main app output for the App
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")  # Light Mode
        self.geometry("720x480")  # Size of the Window
        self.title("Queensland Energy Market - " + database_raw)  # Title of the Window
        self.protocol("WM_DELETE_WINDOW", lambda: self.quit())

        # Initiates Mode1
        self.mode1 = Mode1(self, fg_color=white, corner_radius=0)
        self.mode1.pack(fill="both", expand=1)

        # Initiates Mode2
        self.mode2 = Mode2(self, fg_color=white, corner_radius=0)

        # Initiates Mode3
        self.mode3 = Mode3(self, fg_color=white, corner_radius=0)

        # Initiates Mode4
        self.mode4 = Mode4(self, fg_color=white, corner_radius=0)

        self.sidebarPosition = 0  # Position of the sidebar
        # Button to show the sidebar
        icon = ctk.CTkImage(light_image=PIL.Image.open(os.getcwd() + "/assets/Sidebar Icon.png"), size=(35, 35))
        self.openMenuBTN = SquareButton(self, text="", width=40, height=40, image=icon, command=self.openMenu)
        self.openMenuBTN.place(x=0, y=0)

        # Initiates the Sidebar
        self.sidebar = Sidebar(self, fg_color=dark_red, corner_radius=0)
        self.sidebar.place(relx=0, rely=0, relheight=1, relwidth=0.2)


if __name__ == '__main__':
    freeze_support()  # This is needed for conversion to .exe
    try:
        # loads up the popup
        app = popup.App()
        app.mainloop()
    except Exception as e:
        # cannot load the app
        messagebox.showerror('Error', f'Error in the script: {e} \n\n\n {traceback.format_exc()}')
