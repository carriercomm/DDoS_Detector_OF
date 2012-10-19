#  File Som.py, 
#  brief: implementation of Self-Organized Maps
#
#  Copyright (C) 2010  Rodrigo de Souza Braga
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

#!/usr/bin/env python

from random import *
from math import *

from GetMapGroup import *

def read_file_log(filename, array_input):
    
    log_file = open(str(filename),'r')
    for line in log_file:
	x = eval(line)
	array_input.append(x)

class Node:
    
    def __init__(self, array_size, y, x, input_sample):
        
        self.array_size = array_size
        self.array = [0.0]*array_size
        self.y = y
        self.x = x
	
	if (len(input_sample)==0): 
	    for i in range(array_size):
		self.array[i] = uniform(0,100)
	else:
	    for i in range(array_size):
		self.array[i] = input_sample[i]

    def print_array(self):
        print self.array

class Som:
    
    def __init__(self, height, width, array_size, som_map_file, trainning):
        
        self.height = height
        self.width = width
        self.array_size = array_size
        self.total = height*width
        self.nodes = [0]*(self.total)
        self.som_map = []
        
	if (trainning==1):		## Se for para fazer o treinamento deve ser setado em 1
	    self.read_nodes()
	else:
	    read_file_log(som_map_file, self.som_map)
	    self.read_file_nodes(self.som_map)

    def read_nodes(self):

	for i in range(self.height):
            for j in range(self.width):
                self.nodes[(i)*(self.width)+j]=Node(self.array_size,i,j, [])

    def read_file_nodes(self, samples):

	for i in range(self.height):
            for j in range(self.width):
		self.nodes[(i)*(self.width)+j]=Node(self.array_size,i,j, samples[(i)*(self.width)+j])

    def euclidean_dist(self, input_vector, weights, input_len):
        
        summation = 0
        
        for i in range(0, input_len):
            temp = (input_vector[i] - weights[i]) * (input_vector[i] - weights[i]) 
            summation = summation + temp
            
        return summation           

    
    def get_bmu(self, input_vector, input_len):
        
        bmu = self.nodes[0]
	x=0
	y=0
        best_dist = self.euclidean_dist(input_vector, bmu.array, input_len)
        
        for i in range(self.height):
            for j in range(self.width):
                
                new_dist = self.euclidean_dist(input_vector, self.nodes[(i)*(self.width)+j].array, input_len)
                
                if (new_dist < best_dist):
                    x = i
		    y = j
                    bmu = self.nodes[(i)*(self.width)+j]
                    best_dist = new_dist

	return (x,y)
    
    def neighborhood_radius(self, init_radius, iteration, time_constant):
        
        return init_radius * exp(-1.0*iteration/time_constant)
    
    def distance_to(self, node1, node2):
        
        return sqrt((node1.x-node2.x)**2+(node1.y-node2.y)**2)

    def get_influence(self, distance, radius, iteration):

        return exp(-1.0*(distance**2)/(2*radius*(iteration+1)))

    def adjust_weights(self, node_target, input_vector, input_len, learning_rate, influence):
        
        for i in range(0, input_len):
            
            node_weight = node_target.array[i]
            input_weight = input_vector[i]
            
            node_weight = node_weight + (influence * learning_rate * (input_weight-node_weight))
 
            if (node_weight < 0):
                node_weight=0
                       
            node_target.array[i] = node_weight
                            
    def train(self, num_iterations, inputs, num_inputs):
        
        lw = self.width
        lh = self.height
        
        grid_radius = self.max(lw, lh)/2
        
        time_constant = num_iterations / log(grid_radius)
        
        iteration = 0
        start_learning_rate = 0.5
        learning_rate = 0.1
	#print "time_constant: ", str(time_constant), "grid_radius: ", str(grid_radius)

        while (iteration < num_iterations):
        
            nbh_radius = self.neighborhood_radius(grid_radius, iteration, time_constant)
    
            for x in range(0, num_inputs):            
            
                bmu = self.get_bmu(inputs[x], self.array_size)
                
                for i in range(self.width):
                    for j in range(self.height):
                        
                        temp = self.nodes[(j)*(self.width)+i]
                        dist = self.distance_to(bmu, temp)
                         
                        if (dist <= (nbh_radius)):
                                
                            influence = self.get_influence(dist, nbh_radius, iteration)
                            self.adjust_weights(self.nodes[(j)*(self.width)+i], inputs[x], self.array_size, learning_rate, influence)
             
            iteration=iteration+1
            learning_rate = start_learning_rate * exp(-1.0 *iteration / time_constant)
    
    def classify_sample(self, sample, sample_size):
	
	coord_bmu = self.get_bmu(sample, sample_size)
	if sample_size == 4:
	    return verify_class_size4(coord_bmu[0], coord_bmu[1])
	else:
	    return verify_class_size6(coord_bmu[0], coord_bmu[1])

    def print_matrix(self):

	x=""
	for i in range(self.height):
	    for j in range(self.width):
		x= x+str(int(self.nodes[(i)*(self.width)+j].array[0]))+"  "
	    print x+"\n"
	    x=""
   
    def max(self, a, b):
        
        if (a > b):
            return a
        return b

