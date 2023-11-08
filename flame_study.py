# Name: Conway's game of life
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, CAConfig, randomise2d
import capyle.utils as utils
import numpy as np


def transition_func(grid, neighbourstates, neighbourcounts, fuel_grid, flammability_grid, chance_grid):
    # unpack state counts for state 0 and state 1, 2
    burnt_neighbours, chaparral_neighbours, burning_neighbours, forest_neighbours, lake_neighbours, scrubland_neighbours = neighbourcounts
    # create boolean arrays for the birth & survival rules
    # 0 - Burnt, 1 - Chaparral(Grass), 2 - Burning, 3 - Dense Forest, 4 - Lake, 5 - Scrubland

    #generate new set of chances of field to burn
    chance_grid[:] = np.random.randint(0,101, size=chance_grid.shape)
    print("Chance Grid")
    print(chance_grid)
    # if 2 or more burning neighbours and is not burning there is a chance of catching a fire and then if flammability score is lower than chance of catching on fire it will burn ; water doesn't burn 
    burning = (burning_neighbours >= 1) & (grid != 0) & (fuel_grid>0)  & (grid !=4) & (grid !=2) & (flammability_grid<=chance_grid)
    not_burning_near_fire_chaparral = (flammability_grid>chance_grid) & (grid==2) & (burning_neighbours >= 1)
    not_burning_near_fire_forest = (flammability_grid>chance_grid) & (grid==3) & (burning_neighbours >= 1)
    not_burning_near_fire_scrubland = (flammability_grid>chance_grid) & (grid==5) & (burning_neighbours >= 1)
    #if burning then burn out after fuel runs outs
    already_burning = (grid==2)
    fuel_grid[already_burning] -=1
    ran_out_of_fuel = (fuel_grid==0) & (grid==2)
    still_burning = (fuel_grid>0) & (grid==2)
    #if burnt remain burnt out
    burnt = (grid==0)
    #terrain remains the same if not put on fire
    #not_burning_chaparral = (burning_neighbours<1) & (grid==1)
    not_burning_chaparral = (grid==1)
    not_burning_forest = (grid==3)
    not_burning_scrubland = (grid==5)
    lake = (grid==4)
    # Set all cells to 0 (burnt)
    grid[:, :] = 0
    #Terrain unaffected by fire remains the same
    grid[not_burning_chaparral]=1
    grid[not_burning_forest]=3
    grid[not_burning_scrubland]=5
    grid[lake]=4
    grid[not_burning_near_fire_chaparral]=1
    grid[not_burning_near_fire_forest]=3
    grid[not_burning_near_fire_scrubland]=5
    # Set new cells on fire, then burn out already existing cells
    grid[burning] = 2
    grid[still_burning]=2
    #Burn out terrain that is on fire and run out of fuel
    grid[ran_out_of_fuel] = 0
    grid[burnt]=0
    return grid


def setup(args):
    config_path = args[0]
    config = utils.load(config_path)
    # ---THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED---
    config.title = "Flame study project"
    config.dimensions = 2
    # 0 - Burnt, 1 - Chaparral(Grass), 2 - Burning, 3 - Dense Forest, 4 - Lake, 5 - Scrubland
    config.states = (0, 1, 2, 3, 4, 5)
    # ------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----
    config.state_colors = [(0,0,0),(0.75,0.75,0), (1,0,0), (0.3, 0.4, 0.15), (0, 0.7, 0.95), (1, 1, 0.05)]
    # config.num_generations = 150
    # config.grid_dims = (200,200)

    # ----------------------------------------------------------------------

    if len(args) == 2:
        config.save()
        sys.exit()

    return config


def main():
    # Open the config object
    config = setup(sys.argv[1:])
    fuel_grid = np.zeros(config.grid_dims)
    flammability_grid = np.zeros(config.grid_dims)
    chance_grid = np.zeros(config.grid_dims)
    chance_grid[:] = np.random.randint(0,101, size=chance_grid.shape)
    #Flammability values (the higher it is the less likely the terrain is to catch on fire, from 0-100) for terrain types
    chaparral_flammability_value = 20
    scrubland_flammability_value = 0
    forest_flammability_value = 50
    lake_flammability_value = 200 #You don't want to set lake on fire do you?
    #Fuel values (how many cycle will they burn for) for terrain types
    chaparral_fuel_value = 2
    scrubland_fuel_value = 1
    forest_fuel_value = 5
    lake_fuel_value = 0
    initial_fire_fuel_value=10
    #Access the inital grid and set up values based on the terrain type
    initial_grid=config.initial_grid
    chaparral = (initial_grid==1)
    forest = (initial_grid==3)
    lake = (initial_grid==4)
    scrubland = (initial_grid==5)
    fire = (initial_grid==2)
    #Edit fueld grid to include values for specif terrains
    fuel_grid[chaparral] = chaparral_fuel_value
    fuel_grid[forest] = forest_fuel_value
    fuel_grid[lake] = lake_fuel_value
    fuel_grid[scrubland] = scrubland_fuel_value
    fuel_grid[fire]= initial_fire_fuel_value
    #Edit flammability grid to include values for specif terrains
    flammability_grid[chaparral] = chaparral_flammability_value
    flammability_grid[forest] = forest_flammability_value
    flammability_grid[lake] = lake_flammability_value
    flammability_grid[scrubland] = scrubland_flammability_value
    # Create grid object
    print ("Fuel Grid")
    print (fuel_grid)
    print ("Flammability_grid")
    print (flammability_grid)
    print ("Chance grid")
    print (chance_grid)
    grid = Grid2D(config, (transition_func, fuel_grid, flammability_grid, chance_grid))
    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
