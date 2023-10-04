# BACK END
import glob
import os
import warnings
from decimal import Decimal

warnings.simplefilter(action='ignore', category=FutureWarning)  # Turn off warnings about future deprication
import pandas as pd
import sqlite3
from tqdm import tqdm
from multiprocessing import Pool, freeze_support
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from openpyxl import load_workbook


root_folder = os.getcwd()  # Gets the root folder the program is being run from.


def delete_database(database_name):
    """
    Parameters
    ----------
    database_name : STRING
        The name of the database to delete
    -------
    Takes a database name, and deletes it.
    """
    # Get the file path by adding the /databases/ folder to the root folder, and the database name which is being deleted
    file_path = os.path.join(f"{root_folder}/databases/", f"{database_name}")
    print(file_path)

    try:
        # Attempt to remove the file
        os.remove(file_path)
        print(f"The file at {file_path} has been removed successfully.")
    except OSError as e:
        # Print error if it does not delete successfully
        print(f"Error: {file_path} : {e.strerror}")


def make_dataframe(file_path):
    """
    Parameters
    ----------
    file_path : STRING
        A path to a file which contains the '.out' files
    Returns
    -------
    dataframe : PANDAS DATAFRAME
        A dataframe made from the input paths file with units correctly converted
    -------
    Creates a pandas dataframe from the '*.out' files of a given folder, and returns it.
    Converts the incorrect units, to usable units by multiplying certain files contents by *100.
    """
    # open the file path provided
    with open(file_path, "r") as file:
        # convert the file to a dataframe
        dataframe = pd.read_csv(file, delim_whitespace=True)  # data is seperated by whitespace

        # Multiply the client specified files by 100
        if file_path.endswith(('BranchLosses.out', 'GenerationPowerInjection.out',
                               'NativeDemandComponent.out', 'NetPowerInjection.out',
                               'transmissionLosses.out')):
            # Only the columns after the first 4 need multiplying
            dataframe.iloc[:, 4:] = dataframe.iloc[:, 4:] * 100

    return dataframe


def convert_files_to_database(folder_path, output_name, progress_callback):
    """
    Parameters
    ----------
    folder_path : STRING
        A path to a folder containing .out files
    output_name : TYPE
        The name which the database should be called
    progress_callback : FUNCTION
        function from popup.py module. Updates the loading bar during file conversion, based on how far through the file conversion the program has gotten.
    ----------
    Returns
    -------
    Can return an exception if the given folder contains no .out files

    ----------------
    Takes a folder path, and a database name. finds all '.out' files in the file path, and creates a
    SQLite database with a table for each .out file found.

    If no .out files exist, to simplify error handling, it creates a dummy database from a pre-existing file, deletes that database after conversion is complete, and then returns an exception.
    This is because the loading bar on the front end will have issues if the function fails before a database is created.
    """
    # Get all .out files from the folder

    # Assume the folder given is not empty
    empty = False

    # Get all the .out files from the folder
    file_paths = glob.glob(os.path.join(folder_path, "*.out"))

    # If there are no .out files
    if len(file_paths) == 0:
        # use the Dummy.out file instead
        file_paths = glob.glob(os.path.join(root_folder, "*.out"))
        # remember that the given folder was empty to delete and raise exception later
        empty = True

    # get only the names of the files, from the file paths
    file_names = [os.path.splitext(os.path.basename(file))[0] for file in file_paths]

    # connect to the database
    conn = sqlite3.connect(fr"{root_folder}\databases\{output_name}.db")

    # Use multiprocessing to convert files to the database quicker.
    with Pool() as pool:
        # Loop through all the data files and convert them to a database table
        for i, dataframe in tqdm(enumerate(pool.imap(make_dataframe, file_paths)),
                                 # TQDM makes an error bar. a dataframe is made by calling the make_dataframe function
                                 # for each filepath, make a dataframe for the file.
                                 desc="Converting files to dataframe",  # description for the loading bar
                                 total=len(file_paths),  # Length of the loading bar
                                 disable=True):  # know how far through the loading is done

            # Set the name of the database table to the name of the file being added
            table_name = file_names[i]
            # Add the dataframe to the database
            dataframe.to_sql(table_name, conn, if_exists='replace', index=False)
            # Call the progress callback with the progress percentage
            progress_callback((i + 1) / len(file_paths))

    # Commit and close connection to the database
    conn.commit()
    conn.close()

    # If the folder given was empty
    if empty:
        delete_database(f"{output_name}.db")  # Delete the Dummy database
        raise Exception("This folder does not contain any .out files")  # Return an exception


def generator_linking(node, day, hour, database, ax):
    """
    Parameters
    ----------
    node : str
        The node being investigated
    day : str
        The day being investigated.
    hour : str
        The hour being investigated.
    database : dict
        The database being used for this program instance.
    ax : matplotlib.axes.Axes
        The axes object of a matplotlib plot.
    ----------
    Description
    ----------
    This function summarises all the relevant data from the specific timeframe of a node, in a way which is easier to graph.

    It also creates a bar graph showing the energy inputes and outputes of a node. Using stacked bars for injections/withdrawals coming from other node lines.
    """

    # This function is run from popup.py before the main window is opened. This if statement checks whether the selected database will connect to the backend properly.
    # If it doesnt an exception is raised in popup screen, instead of crashing on the main screen.
    # If everything is okay, it simply returns 'true' and continues onto the main screen
    if ax == "test":
        return (True)

    # This gets all the injection/withdrawal information to use
    data = injection_withdrawal(database, node, day, hour)

    # This remakes the data so it is easier to graph
    summary_data = {}

    # Summarize injection data
    injection_data = data['injection']
    # If there is injection data, we don't need the total for the graphs, as we only need to show where they are coming from
    if injection_data["total"] != 0:
        del injection_data["total"]
    summary_data['injection'] = injection_data

    # Summarize energy generated data
    energy_data = data['energy generated']
    # Define the list of energy sources
    energy_sources = ['black coal', 'NGCC', 'OCGT', 'wind', 'solar', 'HYDRO', 'PHES', 'BESS']

    # Iterate over the energy sources and extract the 'total' values to be set the the power type
    for source in energy_sources:
        try:
            summary_data[source] = energy_data[source]['total']
            # If the source didn't make any power, and so is not in the energy_data dictionary, set that source to 0
        except KeyError:
            summary_data[source] = 0

    # Summarize withdrawal data
    withdrawal_data = data['withdrawal']
    # Withdrawls need to be negative values.
    for k in withdrawal_data:
        withdrawal_data[k] *= -1
    # Set the summary data to the withdrawl data
    summary_data['withdrawal'] = withdrawal_data
    # If there is injection data, we don't need the total for the graphs, as we only need to show where they are coming from
    if withdrawal_data["total"] != 0:
        del withdrawal_data["total"]

    # Copy over remaining top-level keys
    summary_data['source demand'] = -data['source demand']
    summary_data['PHES Storage'] = -data['PHES Storage']
    summary_data['BESS Storage'] = -data['BESS Storage']
    summary_data['transmission losses'] = -data['transmission losses']

    # This is for printing the new dictionary in a nicely formatted way to see what is going on:
    """
    for key, value in summary_data.items():
        if isinstance(value, dict):
            print(f"{key.capitalize()}:")
            for subkey, subvalue in value.items():
                print(f"    {subkey.capitalize()}: {subvalue}")
        else:
            print(f"{key.capitalize()}: {value}")
    """

    # THIS PART COULD BE A NEW FUNCTION IF WE HAD MORE TIME
    # Define the data for the graph
    labels = list(summary_data.keys())
    values = list(summary_data.values())

    # Define the colors which can be used in the graph
    colors = ['blue', 'green', 'red', 'purple', 'orange', 'gold', 'brown', 'pink', 'gray', 'coral', 'teal', 'magenta',
              'cyan', 'lime']
    # And the colors for the withdrawal stacked bar
    colors2 = ['coral', 'brown', 'pink', 'gray', 'gold']

    # This is to see whether the stacked bar is up to the injections, or withdrawals.
    # It starts as false, and after making the first stack bar, switches to true.
    withdrawal = False

    # Get index, and label value of the labels list
    for i, label in enumerate(labels):
        # If the value of the dictionary, is a nested dictionary (The injection/withdrawal lines) The following will create a stacked bar and legend for them
        if isinstance(values[i], dict):
            # Change the color list if it is the stakced withdrawal graph
            if withdrawal:
                color = colors2
            else:
                color = colors
            # Create lists to store the nested dictionary labels and values
            sub_labels = []
            sub_values = []

            for k, v in values[i].items():
                # If the key is 'total' (Which should only happen if the withdrawal/injection = 0). Create a bar with the 'injection'/'withdrawal' label.
                # This stops the column from disapearing completely if empty
                if k == 'total':
                    ax.bar(label, v, color=colors[i])
                # If there are values, set their Key and Value to be held in a seperate list to be graphed/legended differently
                else:
                    sub_labels.append(f"{k}: {v}")  # Add key and value for the dictionary
                    sub_values.append(v)  # Add value to subvalues for the graph

            # Set the bottom of the stacked bar initially to 0.
            sub_bottom = 0

            # Loop through all the injections or withdrawal to make the stacked bar
            for sub_value, sub_label, sub_color in zip(sub_values, sub_labels, color):
                ax.bar(label, sub_value, color=sub_color, bottom=sub_bottom, label=sub_label)  # Make a stacked bar.
                sub_bottom += sub_value  # add next stack, to the end of the prior stack so the bar will be as big as the total power generated

            # Add sub-legend labels for sub-values
            sub_legend = ax.legend(loc='lower left', title="Injections/Withdrawls")
            withdrawal = True  # Change colors for second stack

        # If there was no nested dictionary add a simple bar:
        else:
            # Plot single value
            ax.bar(label, values[i], color=colors[i])

    # Add main titles
    ax.set_title('Energy Balance')
    ax.set_xlabel('Category')
    ax.set_ylabel('MW')
    ax.minorticks_on()  # Minor grid info
    ax.yaxis.set_minor_formatter(plt.ScalarFormatter())
    ax.grid(axis="y", which='minor', linestyle='--', alpha=0.4)  # Helps track minor grid info with horizontal lines
    ax.grid(axis="x", which='major', linestyle='--', alpha=0.4)  # Helps track the data with vertical lines
    ax.yaxis.grid()

    # Set the y-axis limits so that 0 is always in the center
    # Calculate the maximum absolute value of all the data
    max_abs_value = 0
    # This code finds the largest bar in the current graph, and makes the + and - side of the graph show this number * 1.05.
    for value in values:
        if isinstance(value, dict):
            nested_dict_total = abs(sum(value.values()))
            if nested_dict_total > max_abs_value:
                max_abs_value = Decimal(nested_dict_total)
        else:
            value_abs = abs(value)
            if value_abs > max_abs_value:
                max_abs_value = Decimal(value_abs)
    print(f"MAX VALUE: {max_abs_value}")
    max_abs_value *= Decimal(1.05)

    # This is the line which makes the + and - values the same, resulting in the graph always being centered on 0.
    ax.set_ylim(-max_abs_value, max_abs_value)

    # Create the legend labels
    legend_labels = [label for label in labels]
    # Create the legend handles
    legend_handles = [mpatches.Rectangle((0, 0), 1, 1, color=colors[i]) for i in range(len(colors))]

    ax.legend(legend_handles, legend_labels, loc='upper right', bbox_to_anchor=(1.0, 1.0), ncol=2)
    ax.add_artist(sub_legend)


def injection_withdrawal(database, node, day, hour, db_map={}):
    """
    Parameters
    ----------
    database : str
        The name of the database being used in this instance of the program
    node : database
        The node being investigated
    day : str
        The day being investigated.
    hour : str
        The hour being investigated.
    ------------
    Returns
    -----------
    power_flow : dictionary
        A dictionary containing all information about power getting generated and power coming in/out of a node
    ----------
    Description
    ----------
    This function creates a dictionary template to use for all possibilities of power that could interact with a node.
    It calls upon many other functions to fill this dictionary with the neccassary information and returns it once complete.
    """
    # The template which needs to be filled.
    power_flow = {"energy generated": {
        "black coal": 0,
        "NGCC": 0,
        "OCGT": 0,
        "wind": 0,
        "solar": 0,
        "HYDRO": 0,
        "PHES": 0,
        "BESS": 0},
        "injection": {"total": 0},
        "withdrawal": {"total": 0},
        "source demand": 0,
        "PHES Storage": 0,
        "BESS Storage": 0,
        "transmission losses": 0,
    }
    db_map.update({
        "generated_energy": {},
        "branch_direction": {},
        "source_demand_calculation": {},
        "storage_load_calculation": {},
        "transmission_losses_calculation": {}
    })
    # Fills all the dictionary data with the correct information
    power_flow = generated_energy(database, node, day, hour, power_flow, db_map["generated_energy"])
    power_flow = branch_direction(database, node, day, hour, power_flow, db_map["branch_direction"])
    power_flow = source_demand_calculation(database, node, day, hour, power_flow, db_map["source_demand_calculation"])
    power_flow = storage_load_calculation(database, node, day, hour, power_flow, db_map["storage_load_calculation"])
    power_flow = transmission_losses_calculation(database, node, day, hour, power_flow,
                                                 db_map["transmission_losses_calculation"])
    # Remove this comment block to see how the dictionary is formatted and filled
    """
    print(f"for node {node}, on day {day}, and hour {hour}: ")
    for key, value in power_flow.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for subkey, subvalue in value.items():
                if isinstance(subvalue, dict):
                    print(f"\t{subkey}:")
                    for subsubkey, subsubvalue in subvalue.items():
                        print(f"\t\t{subsubkey}: {subsubvalue}")
                        continue
                else:
                    print(f"\t{subkey}: {subvalue}")
                    continue
        else:
           print(f"{key}: {value}")
           continue
    """

    # Returns the dictionary
    return power_flow


def generated_energy(database, node, day, hour, power_flow, db_map):
    """
    Description
    --------------
    The function retrieves energy generation information from a database for a specific node, day, hour, and power flow dictionary.
    It populates the power flow dictionary with the energy generated by different types of generators associated with the node.
    ---------------
    Parameters:
    ------------
    database : string
         The path to the SQLite database.
    node : int
         The identifier of the node for which to retrieve generator information.
    day : int
        The day for which to retrieve energy generation data.
    hour : int
        The hour for which to retrieve energy generation data.
    power_flow : dict
        A dictionary representing the power flow, which will be updated with the energy generated information.
    -------------
    Returns
    -------------
    power_flow : dictionary
        The updated power flow dictionary with the energy generated information.
    --------------
    """

    # This mapping file has information on the generators making energy at each node.
    mapping = pd.read_excel(os.path.join(folder_path, "mapping files/generator-node mapping.xlsx"), header=1).iloc[:,
              :4]

    # Get the generator information associated with the given node
    node_generators = mapping.loc[mapping['atNode'] == node].reset_index()

    # Make SQL query to get the energy of each generator from specified node

    # makes a list of generators written as 'gen1, gen2' etc to search in a query
    columns = [f'gen{i}' for i in node_generators['//ID']]
    # Turns the list into a string seperated by commas
    select_columns = ', '.join(columns)
    # The query will look like : "SELECT gen1, gen2 FROM energyGenerate WHERE day=19 AND hour=12;"
    query = f"SELECT {select_columns} FROM energyGenerate WHERE day={day} AND hour={hour};"

    # Access the database
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    # Perform the query and save the results
    cursor.execute(query)
    results = cursor.fetchone()

    # total_power = sum(results)
    # print(total_power)
    conn.close()  # close the connection

    # Setting up dictionary to find how much power each type contributed
    tech_type_power = {"total": 0}

    # Loop through the selected nodes generators, and get their Name, type, and output.
    for i in range(len(node_generators)):
        generator = node_generators.loc[i]
        gen_name = generator['name'].replace('_', ' ')  # name of the generator
        gen_type = generator['Technology type']  # Energy type of generator
        gen_output = round(Decimal(results[i]), 2)  # how much energy that generator made
        db_map[gen_name] = columns[i]
        # Get power contribution from each technology type
        # to remove empty items from the dictionary, change to > 0 instead of >= 0
        if gen_output >= 0:
            # if the energy type has not been added yet, create a nested dictionary
            if gen_type not in tech_type_power:
                tech_type_power[gen_type] = {"total": gen_output, gen_name: gen_output}
            # If the type has already been added, then add the new generated to the already existing nested dictionary
            else:
                tech_type_power[gen_type]["total"] += gen_output
                if gen_name not in tech_type_power[gen_type]:
                    tech_type_power[gen_type][gen_name] = gen_output
                else:
                    tech_type_power[gen_type][gen_name] += gen_output

        # Add to the total power generated at the node
        tech_type_power["total"] += gen_output

    # Assign the power contribution to the energy generated key in the power_flow dictionary
    print(power_flow)
    power_flow["energy generated"] = tech_type_power

    # Return the generator information
    return power_flow

def update_generator_node(node, name, type, edit):

    katNode = node
    kname = name.replace(' ', '_')
    ktype = type.replace(' ', '_')
    kedit = edit.replace(' ', '_')

    excel_file = "mapping files/generator-node mapping.xlsx"
    data = pd.read_excel(excel_file, header=None)

    selected_data = data.iloc[1:, 1:4]

    for index, row in selected_data.iterrows():
        if row[1] == katNode and row[2] == kname:
            selected_data.at[index, 2] = kedit
            selected_data.at[index, 3] = ktype
            break

    data.iloc[1:, 1:4] = selected_data

    data.to_excel("mapping files/generator-node mapping.xlsx", index=False, header=False)


def branch_direction(database, node, day, hour, power_flow, db_map):
    """
    Description
    --------------
    Finds which way power is travelling to and from nodes through their transmission lines
    and adds the loss or gain of power as well as the information of the 'to' and 'from' node to the power_flow dictionary
    ---------------
    Parameters:
    ------------
    database : string
         The path to the SQLite database.
    node : int
         The identifier of the node for which to retrieve generator information.
    day : int
        The day for which to retrieve energy generation data.
    hour : int
        The hour for which to retrieve energy generation data.
    power_flow : dict
        A dictionary representing the power flow, which will be updated with the energy generated information.
    -------------
    Returns
    -------------
    power_flow : dictionary
        The updated power flow dictionary with the branch flow information.
    --------------
    """
    # This mapping file gets the information on which nodes interact with each other from transmission lines
    mapping = pd.read_excel(os.path.join(folder_path, "mapping files/from and to node mapping.xlsx"), header=1,
                            usecols="B:C")

    # See all in the power transmitted from branchFlow table at the specified time
    query = f"SELECT * FROM branchFlow WHERE day={day} AND hour={hour};"

    # Access the database
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    # Perform the query and save the results
    cursor.execute(query)
    results = cursor.fetchone()
    # Remove the first 4 results (cprice, etc.)
    results = results[4:]
    field_name = cursor.description[4:]
    conn.close()  # close the connection

    # Loop through the results of the query
    for i, x in enumerate(results):
        node_map = mapping.iloc[i]

        # Only use results, where the searched for node is either sending, or recieving power
        if node_map.values[0] == node or node_map.values[1] == node:
            # print(f"{results[i]}  : {node_map.values}", end ="   \t")

            """
            There are 4 possible cases which will be explained here.
            given node = node the user searched

            case 1: The given node is getting power injected into it from a lower node (Injecting to given node)
            case 2: the given node is sending power to a higher node (Withdrawaling from given node)

            case 3: there is a negative flow, where power is going away from the given node, to a lower node (Withdrawaling from given node)
            case 4: There is a negative flow, where power is being sent to the given node, from a higher node (Injecting to given node)
            """

            # Case 1
            #
            if results[i] > 0 and node_map.values[1] == node:
                # print(f"{node_map.values[0]} --> {node_map.values[1]} (case: 1)")
                # Add to the injection total
                power_flow["injection"]["total"] += results[i]
                # add the node which it recieved the injection from and log the total power from that node
                if node_map.keys not in power_flow:
                    power_flow["injection"][f"from {node_map.values[0]}"] = results[i]
                    db_map[f"from {node_map.values[0]}"] = (field_name[i][0], lambda x: float(x) * 1)
                else:
                    power_flow[node_map.keys] += results[i]

            # Case 2
            # If the result of the query was a POSITIVE number AND the LOWER node is the given node:
            elif results[i] > 0 and node_map.values[0] == node:
                # print(f"{node_map.values[0]} --> {node_map.values[1]} (case: 2)")
                # Add to the Withdrawal total
                power_flow["withdrawal"]["total"] += (results[i])
                # Note the node which it sent the withdrawal to.
                if node_map.keys not in power_flow:
                    power_flow["withdrawal"][f"to {node_map.values[1]}"] = results[i]
                    db_map[f"to {node_map.values[1]}"] = (field_name[i][0], lambda x: float(x) * 1)
                else:
                    power_flow[node_map.keys] += results[i]

            # Case 3
            # If the result of the query was a NEGATIVE number AND the HIGHER node is the given node:
            elif results[i] < 0 and node_map.values[1] == node:
                # print(f"{node_map.values[0]} <-- {node_map.values[1]} (case: 3: backwards flow)")
                # Make the result positive, and add it to the withdrawal total
                power_flow["withdrawal"]["total"] -= (results[i])
                # Note the node which it is getting sent to
                if node_map.keys not in power_flow:
                    power_flow["withdrawal"][f"to {node_map.values[0]}"] = results[i] * -1
                    db_map[f"to {node_map.values[0]}"] = (field_name[i][0], lambda x: float(x) * -1)
                else:
                    power_flow[node_map.keys] += results[i]

            # Case 4
            # If the result of the query was a NEGATIVE number AND the LOWER node is the given node:
            elif results[i] < 0 and node_map.values[0] == node:
                # print(f"{mapping.iloc[i].values[0]} <-- {mapping.iloc[i].values[1]} (case: 4: backwards flow)")
                # Make the result positive, and add it to the injection total
                power_flow["injection"]["total"] -= (results[i])
                # Log the node it was recieved from
                if node_map.keys not in power_flow:
                    power_flow["injection"][f"from {node_map.values[1]}"] = results[i] * -1
                    db_map[f"from {node_map.values[1]}"] = (field_name[i][0], lambda x: float(x) * -1)
                else:
                    power_flow[node_map.keys] += results[i]

            else:
                # print("No energy at this node!")
                continue

    # Return the updated dictionary
    return (power_flow)


def source_demand_calculation(database, node, day, hour, power_flow, db_map):
    """
    Description
    --------------
    Gets the source demand information and adds it to the power_flow dictionary

    ---------------
    Parameters:
    ------------
    database : string
         The path to the SQLite database.
    node : int
         The identifier of the node for which to retrieve generator information.
    day : int
        The day for which to retrieve energy generation data.
    hour : int
        The hour for which to retrieve energy generation data.
    power_flow : dict
        A dictionary representing the power flow, which will be updated with the energy generated information.
    -------------
    Returns
    -------------
    power_flow : dictionary
        The updated power flow dictionary with the source demand information.
    --------------
    """

    # Find the source demand at the given node on the correct time
    query = f"SELECT node{node} FROM sourceDemandComponent WHERE day={day} AND hour={hour};"

    # Access the database
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    # Perform the query and save the results
    cursor.execute(query)
    results = cursor.fetchone()
    # print(results[0])
    power_flow["source demand"] += results[0]
    db_map["source demand"] = f"node{node}"

    conn.close()  # close the connection

    # Return the dictionary
    return (power_flow)


def storage_load_calculation(database, node, day, hour, power_flow, db_amp):
    """
    Description
    --------------
    Finds the storage load information (PHES and BESS) for the given node at the given time
    Returns the updated power_flow dictionary
    ---------------
    Parameters:
    ------------
    database : string
         The path to the SQLite database.
    node : int
         The identifier of the node for which to retrieve generator information.
    day : int
        The day for which to retrieve energy generation data.
    hour : int
        The hour for which to retrieve energy generation data.
    power_flow : dict
        A dictionary representing the power flow, which will be updated with the energy generated information.
    -------------
    Returns
    -------------
    power_flow : dictionary
        The updated power flow dictionary with the storage flow information.
    --------------
    """

    # Query to find the PHES information
    query = f"SELECT node{node} FROM PHESChargingLoadsByNode WHERE day={day} AND hour={hour};"

    # Access the database
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    # Perform the query and save the results
    cursor.execute(query)
    results = cursor.fetchone()
    # print(results[0])
    power_flow["PHES Storage"] += results[0]
    db_amp["PHES Storage"] = ("PHESChargingLoadsByNode", f"node{node}")

    # Query to get the BESS information
    query = f"SELECT node{node} FROM StorageChargingLoadsByNode WHERE day={day} AND hour={hour};"

    # Access the database
    # Perform the query and save the results
    cursor.execute(query)
    results = cursor.fetchone()
    # print(results[0])
    power_flow["BESS Storage"] += results[0]
    db_amp["BESS Storage"] = ("StorageChargingLoadsByNode", f"node{node}")
    conn.close()  # close the connection

    # Return the updated dictionary
    return (power_flow)


def transmission_losses_calculation(database, node, day, hour, power_flow, db_map):
    """
    Description
    --------------
    Finds the transmission losses for the given parameters and returns the updated dictionary
    ---------------
    Parameters:
    ------------
    database : string
         The path to the SQLite database.
    node : int
         The identifier of the node for which to retrieve generator information.
    day : int
        The day for which to retrieve energy generation data.
    hour : int
        The hour for which to retrieve energy generation data.
    power_flow : dict
        A dictionary representing the power flow, which will be updated with the energy generated information.
    -------------
    Returns
    -------------
    power_flow : dictionary
        The updated power flow dictionary with the transmission loss information.
    --------------
    """

    # Query to get the transmission losses for the right time and node
    query = f"SELECT node{node} FROM transmissionLosses WHERE day={day} AND hour={hour};"

    # Access the database
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    # Perform the query and save the results
    cursor.execute(query)
    results = cursor.fetchone()
    # print(results[0])
    power_flow["transmission losses"] += results[0]
    db_map["transmission losses"] = f"node{node}"
    conn.close

    # Returns the updated dictionary
    return (power_flow)


def database_list():
    """
    Description
    -----------
    Finds all database files in the databases folder and returns their names as a list

    ----
    Returns
    ----
    file_names : list
        A list of database file names
    """
    # Get the path for all files ending in '.db'
    file_paths = glob.glob(os.path.join('databases', "*.db"))
    # Split the paths into only the file names
    file_names = [os.path.splitext(os.path.basename(file))[0] for file in file_paths]
    # Return the list of file names
    return (file_names)


def create_dataframe(database, node, day, test):
    """
    Description
    ---
    Makes a pandas dataframe for a nodes 'injection_withdrawal()' information for a whole day

    ---
    Parameters
    ---
    database : string
         The path to the given database.
    node : int
         the node wanting to be made into a dataframe.
    day : int
        The day for which to make a pandas dataframe for
    test : string
        Checking whether the function got called early
    """
    # Check whether the function got called early and cancel it
    if test == True:
        return (True)

    # List to store a flattened dictionary
    results = []

    # Loop over the code 48 times (for each 30 minute interval of the day)
    for hour in range(1, 49):
        # Get the nodes information for each hour
        result = injection_withdrawal(database, node, day, hour)
        # flatten the dictionary
        flat_result = flatten_dict(result)
        # add the flattened dictionary to the list
        results.append(flat_result)

    # convert the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(results)
    # Return the dataframe of the whole days results
    return df


# Create a function to flatten nested dictionaries
def flatten_dict(d, parent_key=''):
    """
    Description
    ---
    Flattens nested dictionaries into a dictionary
    Uses the parent dictionary as a prefix of the nested keys
    ----
    Paramaters
    ---
    d : dict
        the dictionary to flatten
    parent_key : string
        The parent key of the nested dictionary. Leave blank if N/A
    ---
    Returns
    ---
    items: A dictionary with all nests removed
    """
    # A list to hold the dictionary items
    items = []
    # Get the key and value of all dictionary items
    for k, v in d.items():
        # The key should be set to the parent dictionary key + current key, if there is no parent key, then only the current key
        new_key = (f"{parent_key} {k}") if parent_key else k
        # If there is a nested dictionary call this function again with the nested dictionary, and set the parent key, to the current key
        # Then add the flattened dictionary to the items list
        if isinstance(v, dict):
            items.extend(flatten_dict(v, k).items())
        # If the value is not a dictionary, add the key value pair to the items list
        else:
            items.append((new_key, v))
    # Return the dictionary made from the items list
    return dict(items)


def update_graph(df, show, ax):
    """
    Description
    -----
    Creates a graph from a dataframe, with the ability to filter what is shownin the graph

    -----
    Parameters
    -----
    df : pandas dataframe
        A dataframe to create the graph from
    show : list
        A list of which items in the dataframe should be shown
    ax : the axes of a matplotlib plot
    """
    # print(show)

    # Access the figure of the axes
    fig = ax.figure

    # Loop for every column of the dataframe
    for column in df.columns:
        # If and word, in the dataframes column, is also a word from the 'show' list: graph that column
        # Or if show is 'all' then graph all columns
        if any(word in column for word in show) or show == 'all':
            ax.plot(df[column], label=column)

    # Settings for the graph
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))  # Move legend to the left
    ax.minorticks_on()  # Turn minor ticks on
    # ax.yaxis.set_minor_formatter(plt.ScalarFormatter())
    # Set the x-axis grid to be dashed and have a low opacity to create "soft" gridlines
    ax.grid(axis="y", which='minor', linestyle='--', alpha=0.4)  # Add minor lines horizontally
    ax.grid(axis="x", which='major', linestyle='--', alpha=0.4)  # Add major lines vertically
    ax.yaxis.grid()  # Add a grid


def upodate_db(database, sql):
    try:
        # Access the database
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        # Perform the query and save the results
        cursor.execute(sql)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(e)
        return False


def write_db_generated_energy(database, node, day, hour, key, data):
    query = f"UPDATE energyGenerate SET {key}={data} WHERE day={day} AND hour={hour};"
    return upodate_db(database, query)


def write_db_branch_direction(database, node, day, hour, key, data):
    _key, _func = key
    da = _func(data)
    _data = str(da) if "." in data else int(da)
    query = f"UPDATE branchFlow SET {_key}={_data} WHERE day={day} AND hour={hour};"
    return upodate_db(database, query)


def write_db_source_demand_calculation(database, node, day, hour, key, data):
    query = f"UPDATE sourceDemandComponent SET {key}={data} WHERE day={day} AND hour={hour};"
    return upodate_db(database, query)


def write_db_storage_load_calculation(database, node, day, hour, key, data):
    table_name, _key = key
    query = f"UPDATE {table_name} SET {_key}={data} WHERE day={day} AND hour={hour};"
    return upodate_db(database, query)


def write_db_transmission_losses_calculation(database, node, day, hour, key, data):
    query = f"UPDATE transmissionLosses SET {key}={data} WHERE day={day} AND hour={hour};"
    return upodate_db(database, query)


def write_db(database, node, day, hour, db_map, key, data):
    db_key = ""
    func = ""
    for _, value in db_map.items():
        if key in value:
            func = _
            db_key = value[key]
            break
    if not db_key:
        return False
    if func == "generated_energy":
        return write_db_generated_energy(database, node, day, hour, db_key, data)
    elif func == "branch_direction":
        return write_db_branch_direction(database, node, day, hour, db_key, data)
    elif func == "source_demand_calculation":
        return write_db_source_demand_calculation(database, node, day, hour, db_key, data)
    elif func == "storage_load_calculation":
        return write_db_storage_load_calculation(database, node, day, hour, db_key, data)
    elif func == "transmission_losses_calculation":
        return write_db_transmission_losses_calculation(database, node, day, hour, db_key, data)
    return False


# Variables access database in backend testing
database = r"E:\外包\桐木\3821WIL_Spencer-main\databases\777.db"
database_folder = "databases"
folder_path = ""

# This holds the main program, used to prevent subprocesses from going where they arn't supposed to
# You can test functions without the fron end by calling them here and printing the results
if __name__ == '__main__':
    # Call the functions
    # freeze_support()  # Required for Windows OS
    # fig = plt.figure()
    # generator_linking(node=8, day=2, hour=25, database=database, ax=fig.add_subplot(111))
    # injection_withdrawal("databases/New database.db", node = 4, day=0, hour=13)
    # create_csv(database, node = 4, day = 1, csv = True)
    pass
