// there has been alot of discution as to where or not you can use the L6470 driver 
// for milling machines and many other purposes where 2 or more motors
// need to be sincronized as well as have dinamicly sined speeds.
// the problem is there is no clear way to change the speed register wile the motor 
//is runing, some have sugested to just use the L6470 in step at a time mode
// but I feel this is a waste of alot of great features ie stall detection 
// so without further adue you cna go see the solution Look lines around
// 110 to 120  ... if you run this you will see that the stepper s accearation 
//is nice and smoothe while still being controlled dynamicaly ( wile the motor is 
// running ) It is a very simple work around ...

// now the comes the part thats not done yet ... daisy chining 
// using the method dynamic speed method combinded with daisy chaining 
// one more thing ... load all the bits but one on the daisy chain while the 
// motor is finishg the privius command then using an interupt as soon as 
// the L6470 buisy pins are all low load the last bit in the daisy .. 
// this shuld reduce any delays that could cause motor noise! 
 





//dSPIN_main.ino - Contains the setup() and loop() functions.

float testSpeed = 10;
int max_speed_rise = 0;
int acceleration_rate = 1;
void setup() 
{
  // Standard serial port initialization for debugging.
  Serial.begin(9600);
  
  // dSPIN_init() is implemented in the dSPIN_support.ino file. It includes
  //  all the necessary port setup and SPI setup to allow the Arduino to
  //  control the dSPIN chip and relies entirely upon the pin redefinitions
  //  in dSPIN_example.ino
  dSPIN_init();
  
  // The following function calls are for this demo application- you will
  //  need to adjust them for your particular application, and you may need
  //  to configure additional registers.
  
  // First, let's set the step mode register:
  //   - dSPIN_SYNC_EN controls whether the BUSY/SYNC pin reflects the step
  //     frequency or the BUSY status of the chip. We want it to be the BUSY
  //     status.
  //   - dSPIN_STEP_SEL_x is the microstepping rate- we'll go full step.
  //   - dSPIN_SYNC_SEL_x is the ratio of (micro)steps to toggles on the
  //     BUSY/SYNC pin (when that pin is used for SYNC). Make it 1:1, despite
  //     not using that pin.
  dSPIN_SetParam(dSPIN_STEP_MODE, !dSPIN_SYNC_EN | dSPIN_STEP_SEL_1_128 // rylan changed to 128 micro stepping mode
  | dSPIN_SYNC_SEL_1);
  // Configure the MAX_SPEED register- this is the maximum number of (micro)steps per
  //  second allowed. You'll want to mess around with your desired application to see
  //  how far you can push it before the motor starts to slip. The ACTUAL parameter
  //  passed to this function is in steps/tick; MaxSpdCalc() will convert a number of
  //  steps/s into an appropriate value for this function. Note that for any move or
  //  goto type function where no speed is specified, this value will be used.
  dSPIN_SetParam(dSPIN_MAX_SPEED, MaxSpdCalc(100));
  // Configure the FS_SPD register- this is the speed at which the driver ceases
  //  microstepping and goes to full stepping. FSCalc() converts a value in steps/s
  //  to a value suitable for this register; to disable full-step switching, you
  //  can pass 0x3FF to this register.
  dSPIN_SetParam(dSPIN_FS_SPD, FSCalc(10000));
  // Configure the acceleration rate, in steps/tick/tick. There is also a DEC register;
  //  both of them have a function (AccCalc() and DecCalc() respectively) that convert
  //  from steps/s/s into the appropriate value for the register. Writing ACC to 0xfff
  //  sets the acceleration and deceleration to 'infinite' (or as near as the driver can
  //  manage). If ACC is set to 0xfff, DEC is ignored. To get infinite deceleration
  //  without infinite acceleration, only hard stop will work.
  dSPIN_SetParam(dSPIN_ACC, 0xFFF);
  dSPIN_SetParam(dSPIN_DEC, 0x001);
  // Configure the overcurrent detection threshold. The constants for this are defined
  //  in the dSPIN_example.ino file.
  dSPIN_SetParam(dSPIN_OCD_TH, dSPIN_OCD_TH_5625mA);
  // Set up the CONFIG register as follows:
  //  PWM frequency divisor = 1
  //  PWM frequency multiplier = 2 (62.5kHz PWM frequency)
  //  Slew rate is 290V/us
  //  Do NOT shut down bridges on overcurrent
  //  Disable motor voltage compensation
  //  Hard stop on switch low
  //  16MHz internal oscillator, nothing on output
  dSPIN_SetParam(dSPIN_CONFIG, 
                   dSPIN_CONFIG_PWM_DIV_1 | dSPIN_CONFIG_PWM_MUL_2 | dSPIN_CONFIG_SR_290V_us
                 | dSPIN_CONFIG_OC_SD_ENABLE   // rylan changed dSPIN_CONFIG_OC_SD_DISABLE to dSPIN_CONFIG_OC_SD_ENABLE to enable over current limiting 
                 | dSPIN_CONFIG_VS_COMP_DISABLE 
                 | dSPIN_CONFIG_SW_HARD_STOP | dSPIN_CONFIG_INT_16MHZ);
  // Configure the RUN KVAL. This defines the duty cycle of the PWM of the bridges
  //  during running. 0xFF means that they are essentially NOT PWMed during run; this
  //  MAY result in more power being dissipated than you actually need for the task.
  //  Setting this value too low may result in failure to turn.
  //  There are ACC, DEC, and HOLD KVAL registers as well; you may need to play with
  //  those values to get acceptable performance for a given application.
  dSPIN_SetParam(dSPIN_KVAL_RUN, 0xFF);
  dSPIN_SetParam(dSPIN_KVAL_ACC, 0xFF); // rylan added max current on acceleration 
  dSPIN_SetParam(dSPIN_KVAL_DEC, 0xFF); // rylan added max current on Decceleration
  // Calling GetStatus() clears the UVLO bit in the status register, which is set by
  //  default on power-up. The driver may not run without that bit cleared by this
  //  read operation.
  dSPIN_GetStatus();
}

// Continually turn one revolution forward, then back again, stopping in between each turn.
void loop()
{
  // 200 steps is one revolution on a 1.8 deg/step motor.
  dSPIN_Move(FWD, 40);
  while (digitalRead(dSPIN_BUSYN) == LOW);  // wait Until the movement completes, the
  dSPIN_SetParam(dSPIN_MAX_SPEED, MaxSpdCalc(max_speed_rise)); 
  max_speed_rise += acceleration_rate; 
  if (max_speed_rise > 100){
    acceleration_rate = -1;
    
  }
  if (max_speed_rise < 1){
    acceleration_rate = 1;
    delay (1000);
  }

}
