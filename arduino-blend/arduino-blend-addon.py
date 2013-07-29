import bpy
from bpy.props import *
import aud
import sys 

#-----------------SETUP OF SERIAL PORT CONNECTON TO ARDUINO-------------------
import site   # I dont know why
import serial # module for talking to a serial port
import time   # module for reading system time 
import struct # module that packs data into byte sized chunks to be sent over serial

#--------------------------Globla variabls-------------------------------------------------
USB_device_path = "/dev/ttyUSB" #None
Serial_Port = None
ports_to_try = 10




sound = False
#try:
#        
#    hover_sound = aud.Factory.file("sounds/hover_sound.wav")
#    except IOError:
#        pass
#    open_sound = aud.Factory.file("sounds/open_sound.wav")
#    #print(sound.volume)
#    #sound.volume(1) #this has no effect .. how do we change the volume?
#    
#    aud.device().play(open_sound)
    


#bl_info = {
#    "name": "Arduino",
#    "author": "Mohamed Sakr", "Rylan Grayston"
#    "version": (0, 0, 1),
#    "blender": (2, 6, 6),
#    "location": "Properties editor > Object Tab",
#    "description": ("Arduino"),
#    "warning": "",  # used for warning icon and text in addons panel
#    "wiki_url": "",
#    "tracker_url": "" ,
#    "category": "Object"}




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

micro = None # 
# codes will be asinged to varables .. when we send a code its related variable will be filled with the next value we send.
start_codes_at =32600

class Code:
    ''' this holds actual lines of code to be writen to the ino file
    instaces of the Code class will be specific to the chip but not the board
    for example all Arduinos boards will probably be able to use the same Code instance
    but talking to a propeler dev board will require a compleatly differnt Code instance
    I really only know the Arduino Wireing languag right now so I dont know if this 
    is the right way to cover multiple micro contoler brands but for now ill asume that
    alot of the things you can do with them are the same but jsut with differn lines of code
    
    
    '''
    
    def __init__(
                 self,
                 micro_brand,
                 pin_type
                 ):
        # ie arduino or avr or propeler etc.             
        self.micro_brand = micro_brand
        # a dictinary of pin types : code to set pin as that type ie {'output':'
        self.pin_type = pin_type
        
                     
                  
        
    
    

class Pin:
    '''Ok the Pin class holds everything we know about a pin aka wire on the micro controler board.
    It also holds the blender object that we want to control this pin instance with '''
    
    def __init__ (
                  self, 
                  board_number = 1, 
                  chip_number=None, 
                  types=None, 
                  type=None, 
                  pwm_range=None, 
                  hi_z=None, 
                  value=None, 
                  object=None, 
                  object_index=None, 
                  factor=None,
                  code=1
                  ):
        #how the pin is labled on the pcb 
        self.board_number = board_number
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
        # a number to signal to the micro controler that we want to update this pins value 
        self.code = code + board_number

# and now a class to hold all the data we know about the micro contoler 
#including a list of its pins!

            
class MicroControler:
    ''' this holds everything we know about the micro contorler 
    and the pcb its on 
    '''
    def __init__(
                  self,
                  name = None,
                  code = None,
                  pins = None,
                  serial_port_bandwidth = 9600, #
                  start_codes_at = 32600
                 ):
        # the name of the micro controler
        self.name = name
        # returns code to be writen in the micro contoler script .ino
        self.code = code
        # a list of pins 
        self.pins = pins
        self.serial_port_bandwidth = serial_port_bandwidth
        self.start_codes_at = start_codes_at
    name = None  
    def make_code(self,name = name, code_type = None, values = None, pin = None):
        #print(self.name,'<<<<<<<<<<<<')
        if 'rduino' in self.name:
            ###### arduino make_code():    #######
            if code_type == 'pinMode':
                #return(micro.code.pin_type[pin.type][0] + pin.board_number + micro.code.pin_type[pin.type][1])
                return(self.code.pin_type[pin.type][0] + str(pin.board_number) + self.code.pin_type[pin.type][1])
            ###################################### 
    def make_all_code(self,name=name):
        if 'rduino' in self.name:
            ##### arduino make_all_code ###
            #open a file to write in 
            file = open('auto_script/auto_script.ino', 'w')
            #write some commets 
            print('//  This file was automaticaly generated by arduino blend , a blender add on created by:')
            print('//  Rylan Grayston: Project founder,  wrote the code that writes the code :P')
            print('//  Mohamed Sakr: gave the code a gui in blender')  
            
            
            file.write('//  This file was automaticaly generated by arduino blend, \n//  which is gui blender add on created by:\n')
            file.write('//  Rylan Grayston: Project founder,  wrote the code that writes this code :P\n')
            file.write('//  Mohamed Sakr: gave the code a gui in blender\n\n\n')
            file.write('/*\n\n\n\n*/\n\n\n')
            #write the first bit of code that is alwase the same
            file.write('void setup() {\n')
            #start the serial port
            file.write('  Serial.begin(9600);\n\n')
            #write the pin setMode codes for each pin 
            for pin in self.pins:
                file.write('  ')
                file.write(self.make_code(pin = pin, code_type = 'pinMode'))
                file.write('\n')
            #end the setup code
            file.write('} \n\n\n')
            
            #[
            ######beguin definining functions
            #define read_two bytes
            file.write('int ReadTwoBytes(){\n  return  (Serial.read() + (Serial.read() << 8));\n}\n\n')
            #define write two bytes
            file.write('void WriteTwoBytes(int x){\n  Serial.write((x&0xFF));\n  Serial.write((x>>8));\n}\n\n')
            #]
                
            #write the second bit of code that is alwase the same 
            file.write('void loop() {')
            #write the loop contents that is alwase the same ie serial variable reciver code 
            
            #write the if statements for pins 
            #write closing bit of code that is alwase the same 
            file.write('\n\n}')
            ###############################
# ok now if a choice is made 
#we will create an instance of that micor controler
#for now to keep this quick ill just put two pins in its list 
# of pins ... pin 13 as that pin has an LED on it already 
# in the case of arduino boards!
# note which instance we create will depend on the micro controler
#selected from the list 

def instantiate_micro(chosen_micro):
    
    if chosen_micro == 'Arduino Pro Mini':
        micro = MicroControler(name='Arduino Pro Mini',
                                code = Code(
                                            micro_brand = 'Arduino',
                                            pin_type = {'none':['// lol.. a comment that dose nothing ', ' at all'], 
                                                        'analog_in':['//... lol nothing, nevermind ', ' at all'],
                                                        'pwm':['pinMode(', ', OUTPUT);'], 
                                                        'digital_out':['pinMode(', ', OUTPUT);']
                                                        }
                                            ),
                                pins = [
                                        Pin(
                                            board_number=13, 
                                            chip_number=17, 
                                            types='output', 
                                            type=None, 
                                            pwm_range=None, 
                                            hi_z=None, 
                                            value=None, 
                                            object=None, 
                                            object_index=None, 
                                            factor=None,
                                            code = start_codes_at 
                                            ),
                                        Pin(
                                            board_number=2, 
                                            chip_number=32, 
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
                                            board_number=3, 
                                            chip_number=1, 
                                            types='output PWM analog_out', 
                                            type=None, 
                                            pwm_range=[0,255], 
                                            hi_z=None, 
                                            value=None, 
                                            object=None, 
                                            object_index=None, 
                                            factor=None
                                            ),
                                        Pin(
                                            board_number=4, 
                                            chip_number=32, 
                                            types='output analog_out', 
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
        return(micro)
    elif chosen_micro == 'Arduino Lenardo':
        print('There is no data for the ', chosen_micro, 
        ' Please consider make arequest along with a donation! to ardiunoBlend.org')
        #return {'CANCELLED'} #commented out for now as this is not a modal op yet
micro = instantiate_micro(chosen_micro)   

#ok now we access the pin data of the micro controler like this 
print(micro.pins[0].value)



def link_gui():
    i = 0
    #print('---->',bpy.data.scenes['Scene'].arduino.steps[0].button_choice)
    note = None
    for pin in micro.pins:
        #print(bpy.data.scenes['Scene'].arduino.steps[i].button_choice) 
        if bpy.data.scenes['Scene'].arduino.steps[i].button_choice != micro.pins[i].type:
            #print('pin has changed')
            global micro
            micro.pins[i].type = bpy.data.scenes['Scene'].arduino.steps[i].button_choice
            note = 'Pin ' + str(pin.board_number) +' set as ' + pin.type + ' with >>> ' + str(micro.make_code(code_type='pinMode', pin = pin)) #micro.code.pin_type[pin.type][0] + pin.board_number + micro.code.pin_type[pin.type][1]
            #micro.make_code()
            #print(micro.code.pin_type['output'])
            
        i += 1        
    return(note)
            
    #for xx, in bpy.data.scenes['Scene'].arduino.steps:
        #print('hh')
#        if xx.button_choice not in micro.pins[i].type:
#            print('button changed')
#            micro.pins[i].type = xx.button_choice 
#            
    
        


# or better yet (when there are more pins) like this

for pin in micro.pins:
    print('\nboard_number: ', pin.board_number, '\nchip_number: ', pin.chip_number)
   
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
    ''' this reads thrue all the data set by the arduino blend gui panles and
     creates the a script which when loaded onto a micro controler 
    will cause the micro controler pins to be a slave to the chosen blender 
    properties. and will cause things in blender to be slaves to the chosen 
    input pins on the arduino'''  
    
    
    micro.make_all_code()
    
    
    
    print('Created C:\\auto_script.ino')
    print(micro.pins[0].type)
    pass

# I will pause here for now and let you get this much of the 
#code into the modal oporator and talking to the gui 

# Thanks ahead of time ! and give me a skype call with and 
#questions as soon as you have read this far!


time.sleep(.1)

def open_serial_port():

    for port in range(ports_to_try):
            
        try:
            #operation_that_can_throw_ioerror()
            # Create a serial object. The name will need changed accordingly  $$ The name will need to be changed accordingly
            global Serial_Port
            Serial_Port = serial.Serial(USB_device_path + str(port), timeout = 1) # instantiates an object called Serial_Port
            print('Opening Serial Port') 
            #time.sleep(2)  # gives the Serial Port time to open 
            progress(60) # gives the seril port time to open and a fancy display in terminal
            Serial_Port.flushInput() # flushes the serial buffer
            Serial_Port.flushOutput() 
            msg = ('Serial Port opened at ' + USB_device_path + str(port))
            print(msg)
            
            return(msg)
        except serial.serialutil.SerialException:   #except serial.SerialException, e:
            msg = ('Cannot open serial port at ports ' + USB_device_path + str(0) + ' thru to ' + USB_device_path + str(ports_to_try))  #handle_the_exception_somehow()
            print(msg)
            return(msg)
        
def close_serial_port():
    try:
        msg =  ' Serial Port Closed ' #   this doset work but its what i want.. >>> 'Serial Port at ' + Serial_port.port + ' has been Closed'
        
        Serial_Port.close()
        return(msg)
    except serial.serialutil.SerialException:
        msg = 'Cannot Close port, as u have yet to open one!'
        print(msg)
        return(msg)    

def progress(n):
   for i in range(n+1):
       sys.stdout.write('\r%3s%% [%s>%s]' % (i, '='*i, ' '*(n-i)))
       sys.stdout.flush()
       time.sleep(0.04)



def GetFiltersString(steps):
    if len(steps) == 0:
        return "xxx"
    
    else:
        TheFilter = ""
        for step in steps:
            if step.name == "Median":
                TheFilter += 'a'
            elif step.name == "Mean":
                TheFilter += 'b'
            elif step.name == "Gaussian":
                TheFilter += 'c'
            elif step.name == 'MeanCurvature':
                TheFilter += 'd'
            elif step.name == "Laplacian":
                TheFilter += 'e'
            else:
                TheFilter += 'f'

            TheFilter += str(step.width)            
            TheFilter += str(step.iterations)

            
        return TheFilter


Micro_choices = (
    ('a', "Arduino Pro Mini", "tool tip"),
    ('b', "Arduino Lenardo", "tool tip")
)


def make_pin_setup_button(pin):
    ''' returns a list of items containt the data for the setup pins buttons'''
    pin_setup_button = EnumProperty(items=(
        ('none', 'None', 'tool tip'),
        ('analog_in', 'Analog In', 'tool tip'),
        ('pwm', 'PWM', 'tool tip'),
        ('digital_out', 'Digital Out', 'tool tip')),
        name="B_Choice"
    )
pin_setup_button = make_pin_setup_button(micro.pins[0])

dict_of_pin_setup_buttons = {}
for identifier, label, description in Micro_choices:
    dict_of_pin_setup_buttons[identifier] = label


class pin_groop(bpy.types.PropertyGroup):
    button_choice = EnumProperty(items=(
        ('none', 'None', 'tool tip'),
        ('analog_in', 'Analog In', 'tool tip'),
        ('pwm', 'PWM', 'tool tip'),
        ('digital_out', 'Digital Out', 'tool tip')),
        name="B_Choice"
    )


class arduino(bpy.types.PropertyGroup):            
    type_add = EnumProperty(
        items=Micro_choices,
        name = "Choose Micro Controler",
        default = 'a',
        #update=type_add_cb
    )
    
    steps = CollectionProperty(type=pin_groop, name="arduino Step")
    index = IntProperty() # min/max/default?


class arduino_UL_steplist(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.label(item.name)
            
            row.prop(item, "button_choice", text=" ", expand=True)
            
            
            sub = row.row()
            sub.scale_x = .4
            
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon_value=icon)


class arduino_step_reset(bpy.types.Operator):
    bl_idname = 'object.arduino_step_reset'
    bl_label = 'Reset'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}


    @classmethod
    def poll(cls, context):
        return ((context.active_object is not None) and
                context.active_object.type == 'MESH')


    def execute(self, context):
        if True: #(context.scene.arduino.type_add == 'a'):
            micro = instantiate_micro(chosen_micro)
            steps = context.scene.arduino.steps    
            steps.clear()
            for pin in micro.pins:                          #rylan
                step = steps.add()        
                step.name =  "Pin " + str(pin.board_number)          # "Pin_" + str(i+1)
            
            context.scene.arduino.index = len(steps) - 1

#        elif (context.scene.arduino.type_add == 'b'):
#            steps = context.scene.arduino.steps    
#            steps.clear()
#            for i in range(40):                          #rylan
#                step = steps.add()        
#                step.name = "Pin_" + str(i+1)
#            
#            context.scene.arduino.index = len(steps) - 1
                    
        else:    
            steps = context.scene.arduino.steps    
            steps.clear()
        
        return {'FINISHED'}
    

class arduino_step_reset(bpy.types.Operator):
    bl_idname = 'object.arduino_create_ino'
    bl_label = 'Ino'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}


    @classmethod
    def poll(cls, context):
        return ((context.active_object is not None) and
                context.active_object.type == 'MESH')


    def execute(self, context):
        link_gui()        
        create_ino()          
        self.report({'INFO'}, "Created C:\\auto_script.ino  Load This File On To Your Micro Controler!")     
        return {'FINISHED'}
    
class arduino_step_reset(bpy.types.Operator):
    bl_idname = 'object.open_serial_port_button'
    bl_label = 'Ino'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}


    @classmethod
    def poll(cls, context):
        return ((context.active_object is not None) and
                context.active_object.type == 'MESH')


    def execute(self, context):
        #link_gui()  
        msg = open_serial_port()          
        self.report({'INFO'}, msg)     
        return {'FINISHED'}   
    
    
class arduino_step_reset(bpy.types.Operator):
    bl_idname = 'object.close_serial_port_button'
    bl_label = 'Ino'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}


    @classmethod
    def poll(cls, context):
        return ((context.active_object is not None) and
                context.active_object.type == 'MESH')


    def execute(self, context):
        #link_gui()        
        msg = close_serial_port()          
        self.report({'INFO'}, msg)     
        return {'FINISHED'}    
       
     
       

class arduino_steplist(bpy.types.Panel):
    """Tooltip"""
    bl_label = "Micro Controler Setup"                              #rylan
    bl_idname = "Arduino_steplist"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}


    def draw(self, context):
        layout = self.layout

        layout.prop(context.scene.arduino, "type_add", expand=False)  #rylan
        
        
        layout.operator("object.arduino_step_reset", text="Update Micro Controler Selection ", ) #icon="TRIA_DOWN"
        layout.label("Set the mode of each pin:")
        
        
        
        row = layout.row()
        
        row.template_list("arduino_UL_steplist", "", context.scene.arduino, "steps", context.scene.arduino, "index", rows=4, maxrows=10,)
        #row.prop(pin_setup_button, text=" ", expand=True)
      
        
        row = layout.row()
        row.operator("object.arduino_create_ino", text=" Create C:\\auto_script.ino ", )  # icon="ZOOMIN"
        
        row = layout.row()
        row.operator("object.open_serial_port_button", text=" Open Serial Port ", )
        
        row = layout.row()
        row.operator("object.close_serial_port_button", text="Close Serial Port ", ) 
        #print('panle draw function was called') 
        if sound: 
            aud.device().play(hover_sound)

        
        msg = link_gui()
        if msg != None:
            print(msg)
            #self.report({'INFO'}, msg)

def register(): 
    bpy.utils.register_module(__name__) # registers all the oporator and panle classes with bender
    bpy.types.Scene.arduino = PointerProperty(type=arduino) 

        
def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.arduino
    
    
if __name__ == "__main__":
    register()
   