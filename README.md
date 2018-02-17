# README #

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for? ###

* Prototyping Dreadbot OpenCV vision stuff here.

### How do I get set up? ###

These instructions are for preparing a Raspberry PI 3 B to run Dreadbot Python code.

Stop! If you are a Dreadbot team member you can ask Mr. Seward for a working Raspberry PI image. That will save you time and be easier. However following the instructions here will be a good exercise in following sketchy instructions detailing a typical Linux Software Install.

If you choose to execution these instructions, I salute you and bon chance!

#### Step 0 ####

Install every programmer's friend GIT on your workstation and your PI.

Clone this repo to execute most of these steps.


```
#!bash

git clone https://bitbucket.org/rtd/dreadbots.git

```

In addition to GIT, you will need to install and learn to use SSH, if you want to work with your raspberry PI over the network. You can of course execute these instructions using a keyboard, mouse & monitor connected to the PI running the PIXEL UI.

Google for using GIT and SSH to familiarize your self with these important tools.


#### Step 1 ####

An older version of opencv can be installed like this: (GRIP code generated doesn't work with this opencv version alone. However I installed this on my road to building a working environment.)

Before you can do this, you must connect your PI to the Internet. So connect it to your WIFI or plug in an ethernet cable. Please note the WashFIRST wifi is really slow, so expect this to take sometime at Maker Work.

```
#!bash

sudo apt-get update -y
sudo apt-get install libopencv-dev python-opencv -y
```

This step was found at this URL: https://milq.github.io/install-opencv-ubuntu-debian/

#### Step 2 ####

Verify opencv is installed.


```
#!python
python
>>> import cv2
>>> print cv2.__version__
```

If this executes without error opencv 2.xx is installed and integrated with Python.

Move to the next step.

#### Step 3 ####

GRIP generates opencv 3.0 code. So in order to use the GRIP python code without modifications we need to install opencv 3.0 and integrate that with python. Unfortunately that requires a fair amount of steps. So bear with us. 

The steps are originally found here.

 * https://milq.github.io/install-opencv-ubuntu-debian/

Download the Dreadbot script from here [install-opencv-3_2](https://bitbucket.org/rtd/dreadbots/raw/a7cb9c329278c940d11fc749533ac909e2f35e37/opencv/install-opencv-3_2.sh) .

```
#!bash

wget https://bitbucket.org/rtd/dreadbots/raw/a7cb9c329278c940d11fc749533ac909e2f35e37/opencv/install-opencv-3_2.sh
```
Once you have downloaded the file you may run it like so.

```
#!bash

bash install-opencvs-3.2.sh
```

When you run this it will take a lot of time. It will be slow on WashFIRST. So if you can run it from home that might be faster. Expect your PI to be busy for at least an hour or two.

You will know the install succeeds if you see the text at the bottom of the build.

  "Go Dreadbots! Your install was successful."

If you don't see that then there was a problem. Ask a mentor for help.

#### Step 4 ####

Test your opencv install with your PI. 

The following tests should let you know if everything is working on your PI with opencv and Python.

 * dreadbots/opencv/image_capture.py  :: *Should capture an image from the camera*
 * dreadbots/opencv/image_capture_2.py :: *Should capture images from the camera and identify any cats (or pictures of cats) present in the image.*
 * dreadbots/opencv/testgrip/grip.py :: *Should capture images and analyze them for yellow blobs present in the images.*

#### Step 5 ####

Although I thought full support for WPILib would be required for vision. I now believe only the pynetworktables python module is required. This module enables communications to the roboRIO vi Network Tables using a pure python implementation of the FRC protocol.

##### Pythonic Way #####

It is common practice for python programmers to list their dependencies for their project in a requirements.txt file. You can then install all your project module dependencies in one command. It is an elegant install method, much beloved by python developers. 

The most pythonic way to install these modules needed is:

```
#!bash

cd sensorproto/
sudo pip install -r requirements.txt 
```
##### Manual Way #####

A more direct and less elegant way to accomplish the same thing is:


```
#!bash

sudo pip install enum34
sudo pip install pynetworktables
```

After this step you should have everything you need to run the sensorproto project.

#### Step 6 ####

Run the sensorproto project. This is a prototype project that integrates:
* Ian's GRIP project (automatically generated python code)
* Images from Raspberry PI Camera
* pynetworktables to report the visions observations / suggestions to the roboRIO.

To run this prototype, do the following:


```
#!bash

cd sensorproto/
python ./sensor.py
```

The prototype will observe blobs in its camera view. Display on the PI the detected image features. Report the observations to the roboRIO. Pause for keyboard input. To unpause , press the spacebar will the "Analyze" window has focus. 

#### Step 7 ####

This is all I have at the moment. Stay tuned for more.

### Code Deployment Notes ###

Here are notes on deploying code changes to a PI attached to robot.

How I apply the code. I use a PI (which provides a handy linux environment). 

1) I pull the latest code from this bitbucket repo.
2) I connect to the robot network I want to update: Prototype, Gamakichi or where ever.
3) I run ~/dreadbots/push_to_bot.sh [from the ~/dreadbots/ ] directory. ~/dreadbots/ is a dir where the GIT repo is checked out locally for me.
4) I restart the sensor.py program. The Web interface running at port 9000 should be sufficient for this purpose.

http://10.36.56.101:9000/


### Contribution guidelines ###

This is a prototype repo. At the moment I intend for this to be a personal sandbox. In a week or two we should move the good bits into the Dreadbot team repo under a python project or similar.

Thanks for tuning in. More to come.

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* sewardrobert@gmail.com
* Dreadbots 3656 FIRST Robotics.