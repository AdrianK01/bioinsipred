# Name: Conway's game of life
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
import math
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
    burnt_neighbours, chaparral_neighbours, burning_neighbours, forest_neighbours, lake_neighbours, scrubland_neighbours, city_neighbours = neighbourcounts
    NW, N, NE, W, E, SW, S, SE = neighbourstates
    #constants
    c1=0.045 #
    c2=0.131
    ph=0.58
    V=8 #Wind speed
    #Angle from the cells
    N_angle=2*np.pi
    NW_angle=np.pi/4
    W_angle=np.pi/2
    SW_angle=3*np.pi/4
    S_angle=np.pi
    SE_angle=5*np.pi/4
    E_angle=3*np.pi/2
    NE_angle=7*np.pi/4
    # 0 - Burnt, 1 - Chaparral(Grass), 2 - Burning, 3 - Dense Forest, 4 - Lake, 5 - Scrubland

    #Get the wind probability from the most potent neighbour
    wind_grid = np.zeros(grid.shape)
    wind_grid[S==2] = math.exp(c1*V)*(math.exp(V*c2*(math.cos(S_angle)-1)))
    wind_grid[SE==2] = math.exp(c1*V)*(math.exp(V*c2*(math.cos(SE_angle)-1)))
    wind_grid[SW==2] = math.exp(c1*V)*(math.exp(V*c2*(math.cos(SW_angle)-1)))
    wind_grid[W==2] = math.exp(c1*V)*(math.exp(V*c2*(math.cos(W_angle)-1)))
    wind_grid[E==2] = math.exp(c1*V)*(math.exp(V*c2*(math.cos(E_angle)-1)))
    wind_grid[NW==2] = math.exp(c1*V)*(math.exp(V*c2*(math.cos(NW_angle)-1)))
    wind_grid[NE==2] = math.exp(c1*V)*(math.exp(V*c2*(math.cos(NE_angle)-1)))
    wind_grid[N==2] = math.exp(c1*V)*(math.exp(V*c2*(math.cos(N_angle)-1)))
    print("Wind Probability Grid")
    print(wind_grid)

    #generate new set of chances of field to burn
    chance_grid[:] = np.random.randint(0,101, size=chance_grid.shape)
    print("Chance Grid")
    print(chance_grid)
    #Calculate of chance of each cell catching on fire
    probability_grid=np.zeros(grid.shape)
    probability_grid =(ph*(1+flammability_grid)*wind_grid)
    print("Probability Grid")
    print(probability_grid)
    # if 2 or more burning neighbours and is not burning there is a chance of catching a fire and then if flammability score is lower than chance of catching on fire it will burn ; water doesn't burn
    chance_to_catch_on_fire = (burning_neighbours>=1) & (grid!=0) & (grid!=4)
    burning = chance_to_catch_on_fire & (fuel_grid>0) & (chance_grid/100<=probability_grid)
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
    city = (grid==6)
    # Set all cells to 0 (burnt)
    grid[:, :] = 0
    #Terrain unaffected by fire remains the same
    grid[not_burning_chaparral]=1
    grid[not_burning_forest]=3
    grid[not_burning_scrubland]=5
    grid[lake]=4
    grid[city]=6
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
    # 0 - Burnt, 1 - Chaparral(Grass), 2 - Burning, 3 - Dense Forest, 4 - Lake, 5 - Scrubland, 6 - City
    config.states = (0, 1, 2, 3, 4, 5, 6)
    # ------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----
    config.state_colors = [(0,0,0),(0.75,0.75,0), (1,0,0), (0.3, 0.4, 0.15), (0, 0.7, 0.95), (1, 1, 0.05), (0.5, 0, 0.5)]
    # config.num_generations = 150
    config.grid_dims = (10,10)

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
    #Flammability values
    chaparral_flammability_value = 0.4
    scrubland_flammability_value = 0
    city_flammability_value = -0.5
    forest_flammability_value = -0.3
    lake_flammability_value = -200
    #Fuel values (how many cycle will they burn for) for terrain types
    #One tick is considered to be around ~2h
    chaparral_fuel_value = 3*(24/2) #To burn ~3days
    scrubland_fuel_value = 3 #To burn 6h
    forest_fuel_value = 24*(24/2) #To burn 24 days
    city_fuel_value = 14*(24/2) #To burn 14 days
    lake_fuel_value = 0
    initial_fire_fuel_value=7*(24/2) #To burn 1 week
    #Access the inital grid and set up values based on the terrain type
    initial_grid=config.initial_grid
    chaparral = (initial_grid==1)
    forest = (initial_grid==3)
    lake = (initial_grid==4)
    scrubland = (initial_grid==5)
    fire = (initial_grid==2)
    city = (initial_grid==6)
    #Edit fueld grid to include values for specif terrains
    fuel_grid[chaparral] = chaparral_fuel_value
    fuel_grid[forest] = forest_fuel_value
    fuel_grid[lake] = lake_fuel_value
    fuel_grid[scrubland] = scrubland_fuel_value
    fuel_grid[fire]= initial_fire_fuel_value
    fuel_grid[city]=city_fuel_value
    #Edit flammability grid to include values for specif terrains
    flammability_grid[chaparral] = chaparral_flammability_value
    flammability_grid[forest] = forest_flammability_value
    flammability_grid[lake] = lake_flammability_value
    flammability_grid[scrubland] = scrubland_flammability_value
    flammability_grid[city] = city_flammability_value
    # Create grid object
    #print ("Fuel Grid")
    #print (fuel_grid)
    #print ("Flammability_grid")
    #print (flammability_grid)
    #print ("Chance grid")
    #print (chance_grid)
    grid = Grid2D(config, (transition_func, fuel_grid, flammability_grid, chance_grid))
    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
