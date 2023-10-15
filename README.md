# CAEEPR Data Modeler

## Description
This program is designed to make it easier for the clients from CAEEPR to view and visualise data which they provide in the form of multiple .out files. 

The .out files each provide one snippit of information about a specific node or branch between nodes. This output format makes it difficult to see all the data on a specific node, as it is split between many large files. and to view five bits of information on the node at once, all five files would need to be opened.

This program allows all the .out files to be collected into one central database, where each file is its own table. The program then uses this database, along with a user provided 'mapping file' containing context for the different .out files to gather information from the different tables about a specific node and output it in a convinient format to the user.

## Usage
NOTE: At this moment, the program is only accurate for scenarios which use the initial mapping files provided by the client. There are instructions for future development to include multiple mapping files lower in this document.

### Installation
To install the program, download the 'CAEEPR Model setup.exe' and follow the prompts to install and create a desktop shortcut to the program.

Windows defender may alert you that the program may not be safe on initial startup and try to prevent it from running. This is because our team does not have a windows license to attach to our program for windows to consider it reputable as this is a lengthy process.

It is safe to click 'more info' and Allow the program to 'run anyway'.

### The initialisation window
Upon opening the program via the shortcut, two options are presented.

#### Adding a new scenario
If you wish to analyse a scenario which has not been previously added to the program, click on the right side selection; 'CREATE DATABASE'.

In this menu, there is a textbox which the user can enter the name which they want their new scenario to be named.

Next, click 'Select Folder' button which will open a file explorer. Navigate to the folder which contains the '.out' files (the folder will show as though it is empty. This is normal), and click the 'Select folder' button. 

Click the 'Create database' button and allow the program some time to convert the files into a database for you. From here you can choose to open this scenario with the freshly made database, add a new scenario, or navigate back to the first screen to select another scenario.

#### Open existing scenario
If the scenario to be analysed has already beed added to the program, click the left side button 'SELECT DATABASE'. You can then search for the scenario name in the text box provided, or scroll to find it in the list below. Once you have found the correct scenario, click on it to open the program.

#### Delete existing scenario
In the 'SELECT DATABASE' menu, there is a button with a red 'X' beside the database names. To delete a database, click on this button and confirm your selection.

### Main window
#### Navigation
To navigate around the main window, there is a navigation bar which can be opened/closed by clicking the button with three bars on the top left of the program.

Here you can navigate to the three different features the program provides, or exit back to the initialisation window to select a new scenario.

#### The 'Compare' window
##### Description
This window can compare two nodes at a moment in time. It gives a text output of the total energy the nodes generated, how the energy was generated, and injections or withdrawls to other nodes from the selected node, as well as their source demand, storage loads, and transmission losses. (We will call this data an 'energy balance').

##### Usage
To use this window, on the left and right side under the 'Node' columns, select the nodes you wish to compare. You can do this by typing the node, or selecting it from a dropdown box.

Then in the middle column, specify the day, and hour you want to compare the nodes on. 

Finally click the 'Generate' button at the bottom of the middle column to view the information from the two nodes at the point in time selected.

The output is formatted with indentations, singiling the indented data is directly related to the parent heading. 

#### The 'Animation' window
##### Description
This window generates a visual bar graph of the energy balance for a specified node, at a specified half hour interval.

The graph can be animated to automatically increase the time being shown in 30 minute increments, to allow a movie style visualisation of what happens at a node as the time goes on.

For injection/withdrawal power flows to/from other nodes, a stacked bar graph is created, showing how much energy was sent or recieved from what node at that point in time. The legend in the bottom left corner of the graph refers to these stacked graphs.

It also allows the user to pause this animation, or search for a custom time in the day, and save the graph as a image file onto their computer for future reference.

The legend in the upper right refers to the bars in the power flow being analysed.

##### Usage
Select a node by typing it's number, or seelcting from the dropdown box. Then specify a day to analyse (the animation will automatically continue to the next day when the end of the specified day is reached).

There is a sliding bar which can be interacted with at the bottom of the window, this allows the time to be incremented fowards or backwards. A display in the bottom center of the screen shows the time which is being presented.
(This display can be clicked to change from 24 hour time, 12 hour time, or 1-48 half hour increments).

To begin the animation, click the 'PLAY' button on the bottom left of the screen. Click the same button to pause the animation.

To save the graph at any point in time, click the 'SAVE' button on the bottom right. In the file explorer, specify where to save the image, and enter a name for it, then select 'save'.

#### The 'Overview' window
##### Description
This window generates a filterable line graph, and CSV file which shows the power balance of a specified node, for the entire specified day.

##### Usage
Begin by selecting a node by typing into the textbox, or using the dropdown menu on the left hand side. Then enter a day to be analysed in the right side text box.

Finally click 'Generate'. Allow time for the graph to generate, it is normal for it to take a while.

To generate teh CSV file generate the graph then click the 'Save CSV' button. A file explorer menu will open, where you can navigate to the path which it should be saved, and name the file what you wish.

The graph initially shows the total energy generated, storage, transmission losses, injection/withdrawals and the source demand.

Checkboxes at the bottom of the window allow the user to filter what is shown in the graph. The boxes can be selected to show more information about the power flow, or deselected to show less information.

#### The 'Edit' window
##### Description
The Edit window allows you to modify the mapping files to change a generators name/location and its type. There is also an Add section in this window that allows you to add new generators, to do so, you must supply the desired name/location and generator type. Upon adding a new generator, it will be assigned to the node and day that you have selected. 

##### Usage
To modify the mapping file data, you must go to the edit section in the menu, enter the node, day and time that you wish to modify, then click the "Get Data" button, which will collect the relevant data and display it on the left side of the program. Doing so will bring up the edit and add sections of the program. 

To edit existing data you must choose which generator you would like to edit, then you will be able to change it's name/location or the generator type.

The functionailty to add new data to the program has not been included.

The output part of the window will show a preview of what the data will look like.

#### Change DB window
This window closes the main window, and re-opens the initialisation window.

### Uninstall instructions
To uninstall the program from your computer, press the windows key and search 'add or remove programs'. From the window this opens, you can search and uninstall the application as normal.
## Information about the program for future development

### General information
The program is written using Python. Packages used are listed at the top of each py files.

To run the program from the source code. Run 'run.py'.

### Architecture
### Major files
#### Backend.py
The backend is responsible for most of the logic and calculation in the program. It relys on knowing which database the user is using, which it does by receiving it as the arguement 'database' in most of it's functions.

#### popup.py
Created with TKinter
This is the initialisation window of the program. It opens from 'run.py' and will not let 'run.py' continue until it closes.

This window is responsible for creating and deleting databases from the program. 

Its main reason for existing is to ensure a database is selected to give to the main window so when the backend functions are called, there is always a database parameter to go with it.

#### run.py
This is the main window of the program. It is created with the TKinter package to create the GUI. It is split into 3 Mode classes, Mode 1 is the compare tab, Mode 2 is the 'Animation' tab, and mode 3 is the overview tab.

### Minor Files
#### /Databases/
This folder holds the databases created by the program. This is where they get saved, loaded, and deleted from.

#### /mapping files/
This folder holds the two user given mapping files. The backend interacts directly with these files to get context to add to the power flow calculations. eg it shows which generators belong to which nodes, and which branch lines interact with which nodes.

#### app_icon.ico
The icon used for the executable.

#### Dummy.out
When the user tries to make a database from a folder which holds no .out files, the program wil instead create a database from this one .out file and then delete it. (It is done this way because the loading bar was difficult to manage and many errors needed to be fixed if a database could not be made. Easier to make a fake database and delete it afterwards) (More information on this is commented in the backend.py convert_files_to_database() function).

#### Install.bat
Developers must run this file to quickly install the dependednt packages to run the source files.

#### Uninstall imports.bat
This uninstalls the packages required by the source files when you no longer need them.

#### run.spec
This file is made by the 'pyinstaller' program to create an executable. More info on this later.

#### /dist/
This folder contains the executable and all files it needs to run. It is generated when the executable is generated.

#### gitignore
files which should not be added to github.

#### colors.py
Colors used to create the front end of the program.

#### assets
Contains assets the program uses.

#### readme.md
This file you are reading.

#### Other files
The other files are not relevant to the developers or users. They are byproducts of running the program/creating the .exe and can be deleted if you wish.

## Instruction for dynamic mapping files
This is the next feature requested by the clients.

Other mapping files have already been tested, and we have confirmed they will work on this program, to allow other scenarios to be analysed. However time constraints meant this feature could not be added.

The way which the current team feels it should be implemented is given below: (Feel free to do it another way if you have an idea on how).

The program is currently designed to work with the clients' original mapping file format. However, the new mapping files they provided us contains multiple sets of mapping information within a single Excel document. To simplify the process and ensure compatibility (the way we tested it), it would be best if each set of mapping information is provided in a separate document. The format of these documents should match the structure of the original mapping file, with the only difference being that the columns can be longer.


In popup.py, after the user selects their database, another screen would be given. Similair to the first screen except instead of 'select or create **database**', it would read 'select or create **generator mapping file**'. Where the same logic would be used as the database creation/selection. The differences being the save location would be in the mapping files folder (perhaps subfolder for each mapping type) instead of database folder. And it would be a simple file save instead of a whole database creation from the file.

Then this would be repeated again for the 'from and to node mapping' files.

This can work in the same way where they can enter a custom name for each mapping file. eg 'scenario 4 generators.xlsx'.

Then for the backend functions which need the mapping files, add an arguement with the name of the mapping files the user selected (same as how the database selection gets passed in). And replace the hardcoded mapping file names, with the arguement passed into it.

## Making the executable
The execultable is made using pyinstaller - https://pyinstaller.org/en/stable/installation.html.

The run.spec is the file which pyinstaller uses to create the executable. In the top of this file there is a list named 'added_files'. This list has paths to folders which 
pyinstaller needs to create the .exe. You will have to edit these paths to make it right for your system. You can also change the 'console = FALSE' to TRUE for debugging purposes.

The 'icon=' parameter allows you to set the icon to be used for the .exe. This will also need to be updated to match your systems path.

Once all this is done. In the command line run: "  pyinstaller --noconfirm "run.spec"  " to create the executable.

## Making the setup.exe
'Inno' was used to create the setup.exe for the client. - https://jrsoftware.org/isinfo.php.
This tutorial tells you all you need to know to make one:  https://www.youtube.com/watch?v=l1p2GQxcP54.

It was discovered the program needs administrator mode to run on a global setup. So to simplify, we forced a local install only through inno