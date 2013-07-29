# Athor : Rylan Grayston 

import time


#Ok so here is the plan... 
#
#this addon registes its self and 
#creates a its own aria in the porperties window 
#Mohamed to be clear it shuld create its own aria or space 
#in the same way that you can click the litle wrench for the 
#modifiers we need to add a button with a litle micro chip icon.
#our hole gui add on will go in here.
#
#the script ads a panle to the micro controler aria 
#called "micro controler setup"
#the panle contains the follown in this order
#
#drop down menu called 'Choose a micro controler' with the following optons 
#'Arduino Pro Mini'
#'Arduino Lenardo' 
#the choice made can be held in a variable

# the micro contoler the user has chosen out of the drop down menu:
chosen_micro = 'Arduino Pro Mini'

#as soon as the user has chosen a micro contoler 
#we must emdiately run a function called instatiate_micro()

#so that we can  display a list of the  selected micro contolers pins
#with the opton to set the pins as input or output.
# Mohamed I asume we can know that a choice has been made
#however if we canot then
#can call this scrip 30 times a second right of the bat
#and do a loop like this:

####while chosen_micro == None:
####    return {'CANCELLED'}

#
#first lets make a class to hold the data of a pin on the micro contoler

class Pin:
    '''Ok the Pin class holds everything we know about a pin aka wire on the micro controler board.
    It also holds the blender object that we want to control this pin instance with '''
    
    def __init__ (
                  self, 
                  board_lable = None, 
                  chip_number=None, 
                  types=None, 
                  type=None, 
                  pwm_range=None, 
                  hi_z=None, 
                  value=None, 
                  object=None, 
                  object_index=None, 
                  factor=None
                  ):
        #how the pin is labled on the pcb 
        self.board_lable = board_lable
        #what number dose pin corspond to on the chip
        self.chip_number = chip_number
        # string of posible types this pin can be set to ie 'input output pwm in out analog_in digital_out analog_out analog_output digital_in digital_input' 
        self.types = types 
        # what type to set this pin to in the setup .ino
        self.type = type
        #range of values for pwm pin ie [0,255]
        self.pwm_range = pwm_range
        #can we set this pin to hi z True or False
        self.hi_z = hi_z
        # the value to set the pin at ie HIGH, LOW, HIGH_Z, 125 
        self.value = value
        # blender data to follow ie bpy.data.objects['Cube'].location[]
        self.object = object
        # 0, 1, 2  denoting xyz or rgb etc in the object 
        self.object_index = object_index
        # a number to multiply the orginal blender unit with 
        self.factor = factor

# and now a class to hold all the data we know about the micro contoler 
#including a list of its pins!

            
class MicroControler:
    ''' this holds everything we know about the micro contorler 
    and the pcb its on 
    '''
    def __init__(
                  self,
                  name = None,
                  pins = None
                 ):
        # the name of the micro controler
        self.name = name
        # a list of pins 
        self.pins = pins
        

# ok now if a choice is made 
#we will create an instance of that micor controler
#for now to keep this quick ill just put two pins in its list 
# of pins ... pin 13 as that pin has an LED on it already 
# in the case of arduino boards!
# note which instance we create will depend on the micro controler
#selected from the list 


if chosen_micro == 'Arduino Pro Mini':
    micro = MicroControler(name='arduino',
                            pins = [
                                    Pin(
                                        board_lable='13', 
                                        chip_number=17, 
                                        types='output', 
                                        type=None, 
                                        pwm_range=None, 
                                        hi_z=None, 
                                        value=None, 
                                        object=None, 
                                        object_index=None, 
                                        factor=None
                                        ),
                                    Pin(
                                        board_lable='2', 
                                        chip_number=32, 
                                        types='output', 
                                        type=None, 
                                        pwm_range=None, 
                                        hi_z=None, 
                                        value=None, 
                                        object=None, 
                                        object_index=None, 
                                        factor=None
                                        )
                                 ]
                           )
elif chosen_micro == 'Arduino Lenardo':
    print('There is no data for the ', chosen_micro, 
    ' Please consider make arequest along with a donation! to ardiunoBlend.org')
    #return {'CANCELLED'} #commented out for now as this is not a modal op yet


#ok now we access the pin data of the micro controler like this 
print(micro.pins[0].value)

# or better yet (when there are more pins) like this

for pin in micro.pins:
    print('\nboard_lable: ', pin.board_lable, '\nchip_number: ', pin.chip_number)
   
# ok as i was saying on we need to display a list of pins
#in the "setup-micro-contorler" panel

# so Mohamad this is where you come in ... 
#itarate thur the list of pins 
#creating a 4 button wide button choice
#like the one in the material propertis 
# where you can chose between "Surface" "wire" "volume" and "Halo"
#only in this case the buton choices shuld read
#'Digital Out' , 'PWM', 'Analog In' 'None'
#and the users choice shuld afect the variable
#pin.type

#the code might look somthing like this

def create_4_button_choice():
    pass

for pin in micro.pins:
    create_4_button_choice()
    
# ok last thing for now..
#Mohamed can you creat a button labled 'create ino'
#that runs this function

def create_ino():
    pass

# I will pause here for now and let you get this much of the 
#code into the modal oporator and talking to the gui 

# Thanks ahead of time ! and give me a skype call with and 
#questions as soon as you have read this far!


time.sleep(.1)
