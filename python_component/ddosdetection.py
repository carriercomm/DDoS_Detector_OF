# Developed by Rodrigo Braga
# Copyright 2010 (C) LabCIA, UFAM.
# 
# This file is part of NOX.
# 
# NOX is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# NOX is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with NOX.  If not, see <http://www.gnu.org/licenses/>.

import os.path
from nox.lib.core import *
from nox.lib.netinet.netinet import datapathid
from nox.netapps.flow_fetcher.pyflow_fetcher import flow_fetcher_app
from nox.lib.packet.packet_utils import longlong_to_octstr
from som import *

request = {'dpid':0}

FLOW_COLLECTION_PERIOD  = 3

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

def write_pattern_log(flow_stat):
    
    file_log = open('flow_stat.log', 'a')
    file_log.write(str(flow_stat)+'\n')

### Modulo do Rastreador

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

    
def report_results(ff, dpid, classifier):
  
    status = ff.get_status()
    x = ff.get_flows()
    n_flows = len(x)
    
    print "\nRequisicao das Flows do DataPath: ", str(dpid)

    if status == 0 and n_flows > 0:
	num_cf = num_correlative_flows(x)
	pcf = percentage_correlative_flows(num_cf, n_flows)
	#anpf = avg_per_flow(x)
	
	#print "\n flows: ", x
	
	mnpf = median_per_flow(x)
	odgs = one_direction_gen_speed(num_cf, n_flows, FLOW_COLLECTION_PERIOD)
	num_ports = distinct_ports(x)
	sample_4 = list(mnpf)
	sample_4.append(num_ports)


	if classifier.classify_sample(sample_4, 4):
		print "A DDoS attack was detected"
		flows_per_port(x)
	else:
		print "Network free from DDoS attack"
	print "Features of traffic: " + str(sample_4)

#	print "\n\t Numero de flows: ", n_flows,\
#	"\n\t Numero de flows correlativas: ", num_cf,\
#	"\n\t Media de pkts por flow: ", anpf[0]," - ", mnpf[0],\
#	"\n\t Media de bytes por flow: ", anpf[1]," - ", mnpf[1],\
#	"\n\t Media de duracao por flow: ", anpf[2]," - ", mnpf[2],\
#	"\n\t Porcentagem de flows correlativas: ", pcf,\
#	"\n\t Velocidade de geracao de trafego em uma direcao: ", odgs,\
#	"\n\t Numero de portas diferentes: ", num_ports
	
	#flow_stat_array = [mnpf[0], mnpf[1], mnpf[2], pcf, odgs, num_ports, dpid]
	#write_pattern_log(flow_stat_array)
	

class ddosdetection(Component):

    def __init__(self, ctxt):
        Component.__init__(self, ctxt)
        self.classifier_som = Som(40,40, 4, "/home/openflow/nox/build/src/nox/coreapps/examples/map_size4.txt", 0)

    def get_flows(self, request, id):
        dpid = datapathid.from_host(long(request['dpid'], 16))
	ff = self.ffa.fetch(dpid, request, lambda: report_results(ff, id, self.classifier_som))

    def flow_timer(self, dpid):
	
	request['dpid'] = str("0x") + str(longlong_to_octstr(dpid)[6:].replace(':',''))
	addr_switch = str(longlong_to_octstr(dpid)[6:].replace(':',''))
	#print "\nRequisicao das Flows do DataPath: ", longlong_to_octstr(dpid)[6:].replace(':','') 
	self.get_flows(request, addr_switch)
	self.post_callback(FLOW_COLLECTION_PERIOD, lambda : self.flow_timer(dpid)) 

    def datapath_join_callback(self, dpid, stats):

        self.post_callback(FLOW_COLLECTION_PERIOD, lambda : self.flow_timer(dpid))

    def install(self):

        self.ffa = self.resolve(flow_fetcher_app)
        self.register_for_datapath_join(lambda dpid, stats : self.datapath_join_callback(dpid,stats))

    def getInterface(self):

	return str(ddosdetection)


def getFactory():
    class Factory:
        def instance(self, ctxt):
            return ddosdetection(ctxt)

    return Factory()
