#  File GetMapGroup.py, 
#  brief: find sample group in Som's Map
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


 """If return 0, then is a sample of attack traffic, otherwise is a 
    sample of normal traffic."""

def verify_class_size4(x, y):
    
    if (x >= 32 and x <= 33 and y <= 4):
        return 1

    if (x == 34 and y <= 5):
        return 1

    if (x >= 35 and x <= 37 and y <= 7):
        return 1

    if (x >= 38 and x <= 39 and y <= 8):
        return 1

    return 0


def verify_class_size6(x, y):

    if (x >= 31 and y <= 1):
        return 1

    if (x == 32 and y <= 3):
        return 1

    if (x == 33 and y <= 4):
        return 1

    if (x == 34 and y <= 5):
        return 1

    if (x == 35 and y <= 6):
        return 1

    if (x >= 36 and x <= 37 and y <= 7):
        return 1

    if (x >= 38 and x <= 39 and y <= 8):
        return 1

    return 0

