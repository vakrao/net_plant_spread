
## Modeling plant disease spread via high-resolution human mobility networks ## 

### Overview ###
----------
This research project uses data from OnSide, an agritech company with biosecurity technology covering more than 20,000 properties from multiple industries across several countries, including New Zealand and Australia. We use the data provided by Onside for the  horticulture industry in New Zealand to create high-resolution yearly, seasonal, and monthly mobility networks for 2022. We link different properties if at least one movement exists between them in a defined time period. We then leverage a Susceptible-Infected metapopulation
model to describe plant disease dynamics and calibrate the model to replicate the timing and severity of a past outbreak of Pseudomonas syringae pv. actinidiae (Psa-V). 

### Installation ### 
-------------

Clone the repository using the following command: 
```bash
  git clone https://github.com/vakrao/net_plant_spread.git
```

 uv is used as our package manager instead of pip. To install the required packages, run the following command
 ```bash
 uv build
 ```
 After running the build, the nz_env folder containing the virtual environment should be present. To run the code, we must activate the virtual environment.

 To activate the virtual environment:
 ```bash
  source nz_env/bin/activate
 ```

### Usage ###
--------------

Our model operates using .yaml files. To run our model, first define a .yaml config file specifying all parameter values.
Run ``E_runner.py`` using the defined config file. ``E_runner.py`` will output a .csv file into the folder of choice, consisting
of the monthly cumulative infection values.

To recreate the results generated in the paper, utilize the following workflow: 

#### Workflow ####
1. Define a directory where output files will be saved (used saved_fils)
2. Create a configuration file in the configs folder. 
3. Run model using following command ``E_runner.py ../configs/NAME.yaml``
4. Use the join_df.py script to aggregate outputs
5. Visualize results in the notebooks directory

The different variables present in the .yaml files in the configs directory are defined below 

**.yaml File parameters** 
- b_w: list of floats
- b_b: list of floats
- alpha: list of loats
- deltaT: either 1,3, or 12 (monthly, seasonal, or yearly)
- L: list of floats. Number of months the model is allowed to run without reporting infections. Set to 3 to replicate paper results. 
- T: integer
- P: list of integers
- prop_fn: filepath to property data
- net_file: filepath to aggregated yearly data
- inc_file: filepath to incidence data
- save_folder: filepath to folder saving seed output data
- D: list of floats
- pool_amount: integer specifying number of threads to use
- max_infected: integer specifying the maximum number of infected before the simulation ends
- run_type: string, can either be set to "calib" or "run".

After specifying the .yaml file, run the following command in the project directory. 

```python
python3 src/E_runner.py configs/example.yaml
```

E_runner calls the function run_si_model in mod_si.py and saves individual output files for every seed in the directory of choice from the run .yaml file. 

To join together the output for all seeds into one file, specify the first folder A and the folder B nested within A, containing all the output files

```python
python3 scripts/join_df.py A B
```

#### Explanation #### 
The model runs using the created .yaml files. These .yaml files specify parameter values, filepaths for the data, and the directory that the model output will be saved.  

To specify the number of seeds, there are two options using the "run" option:
  1. "calib" to use the same seeds that were used when calibrating the model in the paper
  2. "real" to use all possible seeds. 

If you would like to try changing the start_month and generating model output, run vary_sm.py similar to E_runner.py using a .yaml file, except specify the integer representing the startmonth in the "sm" variable path

### Key Functions ###

#### Reading Network Data ####

The function `read_network_data` creates the directed in-network adjacency matrix and out-network adjacency matrix. These matrices represent the number of movements incoming and outgoing from a source farm to a destination farm. The number of movements present in each matrix differs depending on the aggregation used. 

Parameters:
  - `filename`: filepath to .csv file containingt 3 columns for source, destination, and movement weight between source and destination

#### Running Metapopulation Model ####

The function `run_si_model` runs the mean-field approximation of our S-I model using the in and out network of the movement data. If seasonal or monthly aggregation is used, the in and out networks change by season or month, respectively. Infection spreads through the system, and the level of infection in each node is stored. 

**Parameters**:
- `in_bond`: dictionary of dictionaries. key: node-id, value: dictionary where key is node incoming to node-id and value is the number of movements
- `out-bond`: dictionary of dictionaries. key: node-id, value: dictionary where key is node outgoing to node-id and value is the number of movements
- `net_file`: filepath to yearly aggregation data
- `prop_size`: dictionary of property sizes. key is node-id, value is hectare amount
- `b_b`: float. beta-between value
- `b_w`: float. beta-within value
- `D`: float. detection threshold
- `seeds`: list of seed-ids
- `T`: int. number of timesteps
- `max_infected`: int. maximum allowable number of infected before ending simulation.
- `deltaT`: int. 1, 3, or 12. specifies aggregation of network data
- `min_inc`: float. minimum timesteps required
- `alpha`: float. initial amount to infect the seed node
- `F`: int. minimum number of plants needed per hectare
- `init_month`: calendar month when infection starts

**Output**
- .csv written to folder defined in configuration file using variable ``save_folder``


### Data Description ###
--------------
Mobility data from the biosecurity company is used in our metapopulation model. To access that data please follow this link to the data repository. Our model assumes that data will be organized in one of three ways: monthly, seasonal, or yearly, depending on the aggregation used. To achieve the results similar to the paper, use the data in the params files and the the notebooks in the notebook/manuscript_notebooks folder. For more information on how we filtered the data, either refer to the linked paper or the README in the data repository. 





