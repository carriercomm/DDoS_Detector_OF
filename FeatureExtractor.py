#  File FeatureExtractor.py, 
#  brief: Receives collected flows and extracts features that 
#		  are important to DDoS attack detection.
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


def get_median_in_array(array):
    
    array.sort()
    array_lenght = len(array)
    mod = divmod(array_lenght, 2)
    
    if mod[1] == 0:

       m1 = array[mod[0]-1]
       m2 = array[mod[0]]
       return (m1 + m2) / 2

    else:
       return array[mod[0]]
     

def median_per_flow(flows):
    
    med_pkts = []
    med_bytes = []
    med_duration = []
    
    for f in flows:
      
      med_pkts.append(int(f['packet_count']))
      med_bytes.append(int(f['byte_count']))
      med_duration.append(int(f['duration_sec']))
     
    return get_median_in_array(med_pkts), get_median_in_array(med_bytes), get_median_in_array(med_duration)   


def avg_per_flow(flows):
  
    sum_pkts = 0
    sum_bytes = 0
    sum_duration = 0
    
    for f in flows:
      sum_pkts = sum_pkts + int(f['packet_count'])
      sum_bytes = sum_bytes + int(f['byte_count'])
      sum_duration = sum_duration + int(f['duration'])
    
    n_flows = len(flows)
    return (1.0 * (sum_pkts/n_flows), 1.0 * (sum_bytes/n_flows), 1.0 * (sum_duration/n_flows) )

def num_correlative_flows(flows):
  
    ips = []
    num_cf = 0 
    tmp = list(flows)

    while len(tmp) > 0:

      aux = tmp.pop()
      ips.append(aux['match'].get('nw_src'))
      ips.append(aux['match'].get('nw_dst'))
      
      for f2 in tmp:

	if ips[0] == f2['match'].get('nw_dst') and ips[1] == f2['match'].get('nw_src'):
	  num_cf = num_cf + 1
	  del tmp[tmp.index(f2)]
	  break
      del ips[0:2]        
      
    return num_cf

def distinct_ports(flows):
    
    ports = {}
    tmp = []

    for f in flows:      
      tmp.append(f['match'].get('tp_src'))
      tmp.append(f['match'].get('tp_dst'))
      
      for i in range(1):
	if ports.has_key(tmp[i]) != 1:
	  ports[tmp[i]] = 0
	else:
	  ports[tmp[i]] = ports.get(tmp[i]) + 1
      del tmp[0:2] 
      
    return len(ports)
    
def percentage_correlative_flows(num_correlative_flows, num_flows):
    
    return 1.0 * (2 * num_correlative_flows) / num_flows


def one_direction_gen_speed(num_correlative_flows, num_flows, interval):
    
    return 1.0 * (num_flows - num_correlative_flows) / interval

### Tracker Module.

def percentage_per_port(ports):

    total = 0   
    switch_port_percents = {}

    for port in ports.keys():
	total = total + int(ports[port])

    for port in ports.keys():
	switch_port_percents[port] = int(ports[port])*100 / total
    
    print "portas(%)" + str(switch_port_percents)
	

def flows_per_port(flows):

    switch_ports_dic = {}

    for f in flows:

       inport_atual = int(f['match'].get('in_port')) 	       

       if not switch_ports_dic.has_key(inport_atual):
	    switch_ports_dic[inport_atual] = 1
       else: 
	    switch_ports_dic[inport_atual] = switch_ports_dic[inport_atual] + 1
 
    percentage_per_port(switch_ports_dic)