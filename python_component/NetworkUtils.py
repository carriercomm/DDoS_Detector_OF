#  File NetworkUtils.py, 
#  brief: Methods to handle sockets.
#
#  Copyright (C) 2012  Rodrigo de Souza Braga
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

import socket

DEST_IP = '192.168.0.11'
DEST_PORT = 1337

def sendTrafficData(data):
	try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	except socket.error, msg:
	    print 'Failed to create socket. Error code: ' + str(msg[0]) + \
		' , Error message : ' + msg[1]
	    return None
	
	try:
	    s.connect((DEST_IP, DEST_PORT))
	except socket.gaierror, msg:
	    print 'Error in address IP - ' + msg[0]
	    s.close()
	    return None
	except socket.error, msg:
	    print 'Conection failed - ' + msg[0]
	    s.close()
	    return None

	s.sendall(str(data))
	#response = s.recv(1024)
	s.close()

