# LAZOR-Project-G11

## Table of Contents
* Introduction
* Configuration/Installation
* Operating Instructions
* File Manifest
* Troubleshooting
* Credits and Acknowledgments

## Introduction
### General
These programs will automatically find the solutions to any layout of  the game "Lazors" (available as an app on iOS and Android). This game utilizes several manipulatable blocks that can be placed decisively by the user around a grid to change the light path of a lazer. The goal is to guide the lazer to specific target point(s) using a specific combinaiton of blocks.

### Inputs and Ouputs
The goal of this project is to create a program that will read in a text file of a given Lazors level and output the solution as a txt file. The input will be a special text file known as a .bff, which will store the layout as a grid of "x"s (places where blocks are allowed), "o"s (places where blocks are not allowed), "A"s (reflect blocks, which reflect the path of light), "B"s (opaque blocks, which absorb light), and "C"s (refract blocks, which split the path of light into a reflected direction and a direction through the block). The .bff file will also store the given lasers and their difrections, as well as the coordinates of the desired goal points.

The solution txt file will be stored in a created folder named "Solutions", and named aproproately for the level it solves. It will read out the coordinates of where specific blocks should be placed, with each coordinate cooresponding to a placement on the level's layout represented by a nxn matrix starting with rows and columns numbered (1,2,3,4,...n).

## Others

## Configuration/Installation


## Operating Instructions


## File Manifest
The given files in this repository are:
* README
** the d
* LAZOR
** s

## Troubleshooting
This program may run longer than desierd based on the make and model of the computer, possible permutations of the level, and other factors. If problems persist for more than 1.5 minutes, stop and restart the code.

## Credits and Acknowledgments

Team Members:      
* Rohit Chaudhari (Rohit-07-Chaudhari)  
* Phoebe Chen     (PhoebeChenn) 
* Margaret Wang   (MargFW)
     
This project is inspired by EN.540.635 (Software Carpentry) with help of course intstructors Anastasia Georgiou and Colin Yancey.
