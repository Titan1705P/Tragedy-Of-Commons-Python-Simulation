# -*- coding: utf-8 -*-
"""Commonsipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JTjE5RYXmaWlZ0i-04TCTwZhw9ENhEDf

# Import Dependencies
"""

# Commented out IPython magic to ensure Python compatibility.

#!pip install mesa --quiet
'''
try: 
  import mesa
except: 
  !pip3 install mesa --quiet'''
import mesa
import numpy as np
import math
import matplotlib.pyplot as plt
import random

# %matplotlib inline

"""# Helper Functions"""

def get_distance(pos_1, pos_2):
  '''
  Calculate the Euclidean distance between two positions

  used in trade.move()
  '''

  x1, y1 = pos_1
  x2, y2 = pos_2
  dx = x1 - x2
  dy = y1 - y2
  return math.sqrt(dx**2 + dy**2)

def flatten(list_of_lists):
  '''
  helper function for model datacollector for trade price
  collapses agent price list into one list
  '''
  return [item for sublist in list_of_lists for item in sublist]

def geometric_mean(list_of_prices):
  '''
  find the geometric mean of a list of prices
  '''
  return np.exp(np.log(list_of_prices).mean())


"""# Resource Classes"""

class Grass(mesa.Agent):
  

  def __init__(self, unique_id, model, pos, max_sugar): 
    super().__init__(unique_id, model)
    self.pos = pos
    self.amount = max_sugar
    self.max_sugar = 1
    
    self.r = 0.2 #growth rate
    #self.mingrass = 

  def step(self):
    
    
    self.amount = min([self.max_sugar,self.amount + self.r*self.amount*(1-self.amount) ])#growth determined by logistic eq

"""# Cow Agent"""

class Cow(mesa.Agent): 
  

  def __init__(self, unique_id, model, pos, moore=False,
               vision=0,owner_id=0):
    super().__init__(unique_id, model)
    self.pos = pos
    self.moore = moore
    self.vision = vision
    self.owner_id = owner_id
    #self.sugar = sugar
    #self.spice = spice
    
    

  
  def get_grass(self, pos):
    '''
    used in self.get_grass_amount()
    '''

    this_cell = self.model.grid.get_cell_list_contents(pos)
    for agent in this_cell:
      if type(agent) is Grass:
        return agent
    return None
  
  
  def get_grass_amount(self,pos):
    '''
    used in self.move() as part of self.calculate_welfare()
    '''

    grass_patch = self.get_grass(pos)
    if grass_patch:
      return grass_patch.amount
    return 0
  
  
  
  def get_trader(self, pos):
      '''
      helper function used in self.trade_with_neighbors()
      '''

      this_cell = self.model.grid.get_cell_list_contents(pos)

      for agent in this_cell: 
        if isinstance(agent, Cow):
          return agent
  
  
  def is_occupied_by_other(self,pos):
    '''
    helper function part 1 of self.move()
    '''

    if pos == self.pos: 
      # agent's position is considered unoccupied as agent can stay there
      return False
    # get contents of each cell in neighborhood
    this_cell = self.model.grid.get_cell_list_contents(pos)
    for a in this_cell: 
      # see if occupied by another agent
      if isinstance(a, Cow): 
        return True
    return False
  
  def calculate_welfare(self, grass):
    
    if(grass>=0.7):
      return grass
    else:
      return 0 
    

  
  def move(self):
    '''
    Function for trader agent to identify optimal move for each step in 4 parts
    1 - identify all possible moves
    2 - determine which move maximizes welfare
    3 - find closest best option
    4 - move
    '''

    # 1. identify all possible moves

    neighbors = [i
                 for i in self.model.grid.get_neighborhood(
                   self.pos, self.moore, True, self.vision  #the current cell not included
                 ) if not self.is_occupied_by_other(i)]

    # 2. determine which move maximizes welfare

    welfares = [
        self.calculate_welfare(
             self.get_grass_amount(pos)) 
        for pos in neighbors
    ]

    # 3. Find closest best option

    # find the highest welfare in welfares 
    max_welfare = max(welfares)
    #print([welfares])
    
    
      
    if(True): 
      # get the index of max welfare cells
      candidate_indices = [i for i in range(len(welfares))
                            if math.isclose(welfares[i], max_welfare)]

        # convert index to positions of those cells
      candidates = [neighbors[i] for i in candidate_indices]

      min_dist = min(get_distance(self.pos, pos) for pos in candidates)

      final_candidates = [ pos for pos in candidates
                          if math.isclose(get_distance(self.pos, pos), min_dist, rel_tol=1e-02
                                          )]
      self.random.shuffle(final_candidates)
        
        # 4. Move Agent
      self.model.grid.move_agent(self, final_candidates[0])

  def eat(self):
    # get sugar
    grass_patch = self.get_grass(self.pos)

    if grass_patch.amount>0.7:#if grass is 
        #self.grass = self.grass - self.metabolism_grass + grass_patch.amount
        grass_patch.amount=grass_patch.amount-0.55
    else:
        grass_patch.amount=0.1 #eat till grass is 0.2
        self.die()
        #print("H")


  def die(self):
   
    self.model.deadcows=self.model.deadcows+1
    #print("D")
    
    #print(self.model.deadcows) 
    self.model.grid.remove_agent(self)
    self.model.schedule.remove(self)
    self.model.commoners[self.owner_id].cowslist.remove(self)


"""Owner Agent"""
class Commoner():
  def __init__(self,up,down,n,model):
    self.upfactor = up #fractional change
    self.downfactor = down
    self.num_cows = [n]#list with first entry
    self.model = model
    self.cowslist = []
  def decrease_cows(self,policy=1):
    
    remcows = int(self.num_cows[-1]*self.downfactor)#to be removed from scheduler
    if(policy==2):
      remcows = int(self.num_cows[-1]*self.downfactor/5)#to be removed from scheduler


    for i in range(remcows):
      self.model.grid.remove_agent(self.cowslist[i])#remove the required number of cow objects from the scheduler
      self.model.schedule.remove(self.cowslist[i])

    self.cowslist = self.cowslist[remcows:] #randomize if necessary
    #self.num_cows.append(self.num_cows[-1]-remcows)  
    
    #print("decrease "+str(self.num_cows))


  def increase_cows(self,o_id,agent_id,width=101,height=99,limitc=10000):
    addcows = int(self.num_cows[-1]*self.upfactor*4)
    if((self.num_cows[-1]+addcows)>limitc):
      addcows=0
    
    agent_id=agent_id+1
    
    for i in range(addcows):
      #get agent position
      x = self.model.random.randrange(width)
      y = self.model.random.randrange(height)

      cow = Cow(agent_id, 
                      self.model,
                      (x,y),
                      moore = False, #nbd
                      vision = 2,owner_id =o_id )#vision=2 hardcoded
      #place agent
      self.model.grid.place_agent(cow, (x,y))
      self.model.schedule.add(cow)
      self.cowslist.append(cow)
      agent_id= agent_id+1
    
    self.model.lastid = agent_id


"""# Model Class"""

class Commons(mesa.Model):
  
  def __init__(self, width=101,height=99,n_commoners = 10, popl=1000, limit = 1000, policy=1,
               cvision=1):

  

    
    self.width = width
    self.height = height 
    #Initiate population attributes
    self.initial_population = popl
    self.n_comm = n_commoners
    self.limit = limit
    self.running = True
    self.deadcows = 0
    self.lastid = 0
    self.grasslimit = 8000
    self.policy = policy
    # initiate activation schedule
    self.schedule = mesa.time.RandomActivationByType(self)    
    # initiate mesa grid class
    self.grid = mesa.space.MultiGrid(self.width, self.height, torus=False)
    
    self.datacollector = mesa.DataCollector(
       model_reporters={"Cows": self.numcows,"Grass":self.grasspatches,"Total Profit":self.totalprofit,"Profit per cow":self.profitpercow })
  
    
    agent_id = 0
    for _,x,y in self.grid.coord_iter():
      max_grass = 1#grass_distribution[x,y]
      if max_grass > 0: 
        grass = Grass(agent_id, self, (x,y), max_grass)
        self.schedule.add(grass)
        self.grid.place_agent(grass, (x,y))
        agent_id += 1
        #print("grass "+str(agent_id))
    
    self.commoners = []
    self.cow_per_comm = self.initial_population//self.n_comm
    for i in range(self.n_comm):
      upwardf = np.random.normal(0.1,0.1)
      downwardf = np.random.normal(0.5,0.1)
      obj = Commoner(upwardf,downwardf,self.cow_per_comm,self)
      self.commoners.append(obj)



    for i in range(self.initial_population):
      #get agent position
      x = self.random.randrange(self.width)
      y = self.random.randrange(self.height)
     
      self.cvision = cvision
      o_id = i//self.cow_per_comm
      cow = Cow(agent_id, 
                      self,
                      (x,y),
                      moore = False, #nbd
                      vision = self.cvision,owner_id =o_id )
      #place agent
      self.grid.place_agent(cow, (x,y))
      self.schedule.add(cow)
      self.commoners[o_id].cowslist.append(cow)
      agent_id += 1

      #print("cow "+str(agent_id))
    self.lastid = agent_id
  def totalprofit(self):
      h = self.numcows()
      p = -0.1*h**2 + 20*h
      return p

  def numcows(self):
     return self.schedule.get_type_count(Cow)

  def profitpercow(self):
     h = self.numcows()
     p = self.totalprofit()  
     return p/h
 
  def grasspatches(self):
     grassagent = self.schedule.get_type_count(Grass)
     l = self.schedule.agents_by_type[Grass].values()
     ret =[]
     for i in l:
       if i.amount>0.7:
         ret.append(i)
     return len(ret)    

  def randomize_cows(self): 
    

    cow_shuffle = list(self.schedule.agents_by_type[Cow].values())
    self.random.shuffle(cow_shuffle)

    return cow_shuffle
  
  
  def yearstep(self):
    yearweeks = 25
    
    for i in range(yearweeks):#run for each year
      self.step()  

      

    for i in range(self.n_comm):#add the cow agents to respective owners
        self.commoners[i].num_cows.append(len([cow for cow in self.schedule.agents_by_type[Cow].values() if (cow.owner_id ==i)]))
        #self.commoners[i].num_cows.append(len(self.commoners[i].cowslist))  
        #print("Id " + str(i)+str(self.commoners[i].num_cows))
    
    
    for i in range(self.n_comm):
      
      if(self.policy==2):
        print(self.grasspatches())
        if(self.grasspatches()>self.grasslimit):
          self.commoners[i].increase_cows(o_id=i,agent_id=self.lastid,limitc = self.limit) 
        else:
          self.commoners[i].decrease_cows(policy=2)


          
      else:
      
        if(len(self.commoners[i].num_cows)>1):#more than one year, num_cows indictaes the no. of years
            change = self.commoners[i].num_cows[-1] - self.commoners[i].num_cows[-2]
            if(change<0):
              print("D")
              self.commoners[i].decrease_cows()
            if(change==0):
              print("I")
              self.commoners[i].increase_cows(o_id=i,agent_id=self.lastid,limitc = self.limit) 

    self.schedule.steps += 1 #important for data collector to track number of steps

    # collect model level data
    self.datacollector.collect(self)        

  def step(self):

    for grass in self.schedule.agents_by_type[Grass].values(): 
      grass.step()
      

    #take in all the cows at once into scheduler

    cow_shuffle = self.randomize_cows()
    #print(len(cow_shuffle))
    for agent in cow_shuffle: #should eat first
      #print(agent.owner_id)
      agent.move()
      agent.eat()
    
    

  def run_model(self, step_count=50):#run for 25 weeks

    for i in range(step_count):
      self.yearstep()
      #print("step"+str(i))
      #print(self.deadcows)



model = Commons(popl=400,limit = 60,policy=2,cvision=3)
model.run_model()

"""# Analyze Data"""

results = model.datacollector.get_model_vars_dataframe()

results

iy = [model.commoners[i].num_cows[-1] for i in range(model.n_comm)]
ix = range(model.n_comm)
plt.bar(ix,iy)

# plot number of agents per time step 
results.plot(y = "Cows", use_index=True)
#plt.show()


# plot number of agents per time step 
#results.plot(y = "Profit per cow", use_index=True)

# plot number of agents per time step 
results.plot(y = "Grass", use_index=True)
#plt.figure(figsize=(600,25))
#plt.ylim([0,700])
plt.show()

# plot trade price per step 
