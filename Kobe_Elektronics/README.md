# Kobe Electronics


## Mainboard functionality

- Consists of 2 separate isolated schematics: One with USB as power source, the other has battery with a transistor for reverse current control

- Communication between STM32 controller and computer is through microUSB

- Has LED connected to GPIO for indication, firmware controllable

- STM32 can be programmed with Samtec connector

- Has 3 MicroMatch connectors for motor encoders

- Two 4-channel for 3 motor direction and PWM signals, one nSLEEP signal and one thrower motor PWM signal

- Has voltage regulators to turn 5V to 3.3V and 16V to 5V

- Three drivers for controlling motors, with FAULT LEDs

- Drivers can be controlled through 2 PWM signals or one direction signal and one PWM signal, controlled by MODE pin signal. When GND, 1 PWM and direction

- Needs 20us low pulse on nSLEEP to initialize, otherwise when high FAULT LEDs are glowing

- Has SR pin for slew rate control, connected to PGND

- ITRIP pin for load current regulation, 3.3k resistor connected

- DIAG pin connected to PGND

- DRVOFF pin to put the driver on standby

![alt text](https://github.com/ut-robotics/picr21-team-kobe/blob/main/Kobe_Elektronics/Mainboard_footprint_w_desc.png)

