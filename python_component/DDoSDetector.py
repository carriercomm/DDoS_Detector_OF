#  File ddosdetector.py, 
#  brief: Nox component to get OF flows and seek 
#         for ddos traffic patterns.
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


import os.path
from nox.lib.core import *
from nox.lib.netinet.netinet import datapathid
from nox.netapps.flow_fetcher.pyflow_fetcher import flow_fetcher_app
from nox.lib.packet.packet_utils import longlong_to_octstr
from Som import *
from FeatureExtractor import *

request = {'dpid':0}

SOM_MAP_FILE = "map_size4.txt"
FLOW_COLLECTION_PERIOD  = 3


def write_pattern_log(flow_stat):
    
    file_log = open('flow_stat.log', 'a')
    file_log.write(str(flow_stat)+'\n')
   
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
	

class DDoSDetector(Component):

    def __init__(self, ctxt):
        Component.__init__(self, ctxt)
	dir_path = os.path.dirname(os.path.abspath(__file__))
        self.classifier_som = Som(40,40, 4, dir_path + "/" + SOM_MAP_FILE, 0)

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

	return str(DDoSDetector)


def getFactory():
    class Factory:
        def instance(self, ctxt):
            return DDoSDetector(ctxt)

    return Factory()
