added wile in daisy branch

### The Idea
Blender is great at simulating the real world.
Arduino is great at doing things in the real world.
So lets get them connected.

Put shortly we intend to do the following with a GUI addon in blender.

blender data<-->blue tooth serial port<-->arduino variables and pins

The blender addon will give you buttons for each pin alowing you to 
setup how your micro contoler will work.  The arduino-blend script 
Actualy genarates the code that goes on the micro controler.

Upon uploading the genarated code the blender file and the arduino 
can communicate!





If you wish to commit you must read project-goals-READ-THIS.txt

### Insturctions 


1 download the latest blender, git the zip file not the installer !

2 make sure you have python3 installed on your system 

3 unzip your the blender program you downloaded 

4 copy the site packages folder from python3 to the moduals folder in the blender folder you jsut down loaded

5 do the same for serial

6 open blender form the unziped blender folder

7 from blender open the arduino_blend.blend file 

8 click save as and chose a new name sutid for your project

9 plug in your micro controler via usb

10 hit run script button or alt-p with your mouse in the text window

11 click the object properties tab ( look for a little cube to your left 

12 open a panle named Arduino blend or Micro setup 

13 click the buttons to your desired setings

14 use drivers to conect your blender objects

15 click the make C:\auto_script.ino button

16 open the auto_script.ino with arduino ide

17 upload it to your micro controler

18 in blender click open serial port 

19 click the real time box and the animation box and the record box

developers:

Our goal is to get the above list to look like this

1 download the arduino_blend.zip corasponding to your OS and arcitecture from www.arduino-blend.org and unzip it

2 open blender from the unziped folder

3 chose your micro and set the buttons as you wish

4 use drivers to the pin propertis you wish to affect 

5 with your micro pluged in to a usb port hit upload to micro button

6 click the real time , animation, or record box 

Have fun!

to shorten it more we shuld probably make some example blends .. like a blink LED on pin 13 when cube moves or something  



```
CODE
```



