#!/usr/bin/python

# Copyright (C) 2005-2013 Alexander Schier
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, time

field=[""] #our program
DEBUG=0

class executor:
    waterchars="*$" #what is recognized as water (NOP)
    ignorechars="abcedefghijkmnopqrstuwxyABCDEFGHIJKLMNOPQRSTUVWXYZ"
    cmdchars="+-{}<>^v|l_=.," #used commands
    allchars=cmdchars+waterchars+ignorechars
    #+-{} = brainfuck/path like
    #^v<> Valves: flow is only possible in one direction
    #|_ Watergates: flow is only possible, if value == 0
    #l= Watergates: flow is only possible, if value != 0
    ip=[] #instruction pointers
    ip2=[] #temp ip, for the next queue
    data=[0]
    #constants for direction
    LEFT=0
    RIGHT=1
    UP=2
    DOWN=3
    NO_DIRECTTION=4
    def __init__(self, field):
        self.field=field

    def findstart(self):
        field=self.field
        for i in range(len(field)):
            for u in range(len(field[i])):
                if field[i][u]=="$":
                    return [u,i]
        return None
    def start(self):
        startp=self.findstart()
        if not startp:
            print "Startpoint not found"
            return None
        #self.do(start)
        #startp.append(self.RIGHT)# initial direction
        startp.append(self.NO_DIRECTTION) #go in every availible direction
        startp.append(0) #data position
        self.ip.append(startp)
        while len(self.ip)>0: 
        #Main Thread
            for i in range(len(self.ip)): #exec each instruction pointer
                self.ip[i]=self.do(self.ip[i])
            #try to go in the direction.
            #each ip goes first left, then right, then to top and bottom
            #IMPORTANT: Every Direction has iths own loop. So all ips go left first, then they go up, ...
            #instead of one IP going in all directions and then the next (this is psydothreaded ;-))
            for i in self.ip:
                left=self.goLeft(i)
                if left and i[2]!=self.RIGHT:
                    if DEBUG:
                        print "left", left
                    self.ip2.append(left)
            for i in self.ip:
                up=self.goUp(i)
                if up and i[2]!=self.DOWN:
                    if DEBUG:
                        print "up", up
                    self.ip2.append(up)
            for i in self.ip:
                right=self.goRight(i)
                if right and i[2]!=self.LEFT:
                    if DEBUG:
                        print "right", right
                    self.ip2.append(right)
            for i in self.ip:
                down=self.goDown(i)
                if down and i[2]!=self.UP:
                    if DEBUG:
                        print "down", down
                    self.ip2.append(down)
            
            self.ip=self.ip2
            self.ip2=[]
            if DEBUG:
                time.sleep(0.2)

    def getPoint(self, x, y):
        if self.hasPoint(x, y):
            return field[y][x]
        return None

    def hasPoint(self, x, y):
        #print "hasPoint:", x, y
        field=self.field
        if len(field)>=(y+1) and y>=0:
            if len(field[y])>=(x+1) and x>=0:
                #if self.getPoint(x, y) in self.allchars:
                if field[y][x] in self.allchars: #no recursion with getPoint
                    return 1
        return 0

    def do(self, ip):
        x=ip[0]
        y=ip[1]
        pos=ip[3]
        char=self.getPoint(x, y)
        #self.execute(char)
        if char=="+": #increment current data
            self.data[pos]+=1
            if DEBUG:
                print "+ pos:", pos, "new value", self.data[pos]
            return ip
        elif char=="-": #decrement current data
            self.data[pos]-=1 #Allows negative Values
            if DEBUG:
                print "- pos:", pos, "new value", self.data[pos]
            return ip
        elif char=="}": #increment data pointer
            if len(self.data)<=(pos+1): #new data
                self.data.append(0)
            if DEBUG:
                print "} new pos: ", (pos+1)
            return [x,y,ip[2], ip[3]+1]
        elif char=="{": #decrement data pointer
            if pos>0:
                if DEBUG:
                    print "{ new pos: ", (pos-1)
                return [x,y,ip[2], pos-1]
            else:
                print "Warning: Access on negative Memory Position."
                return [x,y,ip[2], pos]
        elif char==".":
            if DEBUG:
                print ". printing the char"
            sys.stdout.write(chr(self.data[pos]))
            return ip
        elif char==",":
            if DEBUG:
                print ". reading a char"
            self.data[pos]=ord(sys.stdin.read(1))
            return ip
        elif char=="|":
            if DEBUG:
                print "Passed a vertical check for == 0"
            return ip
        elif char=="_":
            if DEBUG:
                print "Passed a horizontal check for == 0"
            return ip
        elif char=="l":
            if DEBUG:
                print "Passed a vertical check for != 0"
            return ip
        elif char=="=":
            if DEBUG:
                print "Passed a horizontal check for != 0"
            return ip
        elif char != None and char in "<>v^l|_=":
            #this is handled in go*, while choosing the next field.
            #here we can ignore the char, and simply go on.
            return ip
        elif char != None and char in self.waterchars:
            #print char
            return ip
        else:
            print char
            return ip
        
    def goLeft(self, ip):
        x=ip[0]
        y=ip[1]
        #direction=ip[2]
        direction=self.LEFT
        pos=ip[3]
        point=self.getPoint(x-1, y)
        if point and point!=">" and not ( (point=="|" and self.data[pos]!=0) or (point=="l" and self.data[pos]==0) ):
            return((x-1, y, direction, pos))
        return None
        
    def goUp(self, ip):
        x=ip[0]
        y=ip[1]
        #direction=ip[2]
        direction=self.UP
        pos=ip[3]
        point=self.getPoint(x,y-1)
        if point and point!="v" and not ( (point=="_" and self.data[pos]!=0) or (point=="=" and self.data[pos]==0) ):
            return((x, y-1, direction, pos))
        return None

    def goRight(self, ip):
        x=ip[0]
        y=ip[1]
        #direction=ip[2]
        direction=self.RIGHT
        pos=ip[3]
        point=self.getPoint(x+1, y)
        if point and point!="<" and not ( (point=="|" and self.data[pos]!=0) or (point=="l" and self.data[pos]==0) ):
            return((x+1, y, direction, pos))
        return None
        
    def goDown(self, ip):
        x=ip[0]
        y=ip[1]
        #direction=ip[2]
        direction=self.DOWN
        pos=ip[3]
        point=self.getPoint(x, y+1)
        if point and point!="^" and not ( (point=="_" and self.data[pos]!=0) or (point=="=" and self.data[pos]==0) ):
            return((x, y+1, direction, pos))
        return None

file=open(sys.argv[1], "r")
field=file.read().split("\n")
file.close()

program = executor(field)
program.start()
print ""
