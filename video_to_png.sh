#!/bin/bash

if [ -z "$BLENDER_PATH" ]; then
  echo "BLENDER_PATH is not set in env variables"
  echo "enter the path to blender"
  read BLENDER_PATH
  echo -e "\n\nYou can add the path to blender to your env variables to stop the script asking everytime. :D \n\n"
fi

# Usually this is the path to blender in MacOS
# BLENDER_PATH="/Applications/Blender.app/Contents/MacOS/Blender" 

# Run the Python script to add the video to the sequencer
$BLENDER_PATH --background --python video_to_png.py

# Read the video folder path from the file created by Python script
VIDEO_FOLDER_PATH=$(cat /tmp/video_path.txt)