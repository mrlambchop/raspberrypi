import wiringpi2
from time import *
import os
import threading

pin_to_switch = [ [17, 22], [4, 27], [24, 25] ]

on = 0
off = 1
unknown = 2
state_name = [ "on", "off", "unknown" ]

default = off

outlet_state = [ unknown, unknown, unknown ]

def make_32bit_time( hr, min):
        return (hr << 16) | min

def set_led( state ):
        if( state == on ):
                wiringpi2.digitalWrite(18,1)
        else:
                wiringpi2.digitalWrite(18,0)


def set_outlet( outlet_num, state ):
        if( outlet_state[ outlet_num ] != state):
                button = pin_to_switch[outlet_num]
                print "Turn outlet", outlet_num, state_name[state], "using pin ", button[state]
                wiringpi2.digitalWrite(button[state],1)
                set_led( on )
                sleep(1.3)
                wiringpi2.digitalWrite(button[state],0)
                set_led( off )
                sleep(0.2)
                outlet_state[ outlet_num ] = state

def setup_pins():
        for switch in pin_to_switch:
                for button in switch:
                        print "Setting up pin to output", button
                        wiringpi2.pinMode(button,1)
                        wiringpi2.digitalWrite(button,0) #turn off by default


class LightTimer(threading.Thread):
    def __init__(self, time_list, outlet ):
        super(LightTimer, self).__init__()
        self.time_list = time_list
        self.outlet = outlet
        self.keep_running = True
        #first check to see if the lights should be on already
        now = localtime()
        #print now
        #check that 'now' is after the on time AND that 'now' is less than the off time
        #if self.time_between( now, time_list[0], time_list[1] ):
        #    print "First time, setting outlet", outlet, "on"
        #    set_outlet( outlet, on )
        #else:
        #    print "First time, setting outlet", outlet, "off"
        #    set_outlet( outlet, off )

    def run(self):
        try:
            while self.keep_running:
                now = localtime()
                if self.time_equal( now, self.time_list[0]):
                   print "Turning outlet", self.outlet, "on"
                   set_outlet( self.outlet, on )
                if self.time_equal( now, self.time_list[1]):
                   print "Turning outlet", self.outlet, "off"
                   set_outlet( self.outlet, off )
                sleep(30)
        except:
            raise
            return

    def time_greater( self, now, time ):
        print now.tm_hour, now.tm_min, time[0], time[1]
        if ( make_32bit_time(now.tm_hour, now.tm_min) >= make_32bit_time(time[0], time[1]) ):
            return True
        else:
            return False

    def time_less( self, now, time ):
        print now.tm_hour, now.tm_min, time[0], time[1]
        if ( make_32bit_time(now.tm_hour, now.tm_min) <= make_32bit_time(time[0], time[1]) ):
            return True
        else:
            return False

    def time_has_wrapped( self, now, time ):
        if (now.tm_hour < 24) and (time[0] < now.tm_hour):
            return True
        else:
            return False

    def time_between( self, now, start, stop ):
        print "between", now.tm_hour, now.tm_min, start, stop
        #easy case
        if self.time_greater( now, start) and self.time_less( now, stop):
            print "fail 1"
            return True
        elif self.time_has_wrapped( now, start) and self.time_less( now, stop):
            print "fail 2"
            return True
        else:
            print "fail 3"
            return False

    def time_equal( self, now, time ):
        print now.tm_hour, now.tm_min, time[0], time[1]
        if (now.tm_hour == time[0] and now.tm_min == time[1]):
            return True
        else:
            return False

    def just_die(self):
        self.keep_running = False

#test cases
#assert( time_between( [ 23, 00], [ 16, 00], [11, 59] ) == True )
#assert( time_between( [ 23, 00], [ 16, 00], [01, 00] ) == True )
#assert( time_between( [ 12, 00], [ 11, 00], [11, 59] ) == False )

wiringpi2.wiringPiSetupGpio()
setup_pins()

set_led( on )

set_outlet( 0, default )
set_outlet( 1, default )
set_outlet( 2, default )

stair_lights = LightTimer( [ [16, 46], [00, 28] ], 2 )
stair_lights.start()

window_lights = LightTimer( [ [16, 32], [23, 48] ], 0 )
window_lights.start()

tree_lights = LightTimer( [ [16, 00], [2, 00] ], 1 )
tree_lights.start()

try:
    while True:
         text = str(raw_input())
         if text == "stop":
            stair_lights.just_die()
            window_lights.just_die()
            tree_lights.just_die()
            break
except:
    print("Yikes lets get out of here")
    stair_lights.just_die()
    window_lights.just_die()
    tree_lights.just_die()


