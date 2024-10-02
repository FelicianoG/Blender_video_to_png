import bpy
import os

# Prompt the user to enter the path to the video file
video_file = input("Please enter the path to the video file: ")

video_file = video_file.rstrip()

# Check if the provided path exists and is a file
if not os.path.isfile(video_file):
    raise Exception(f"The specified file does not exist: {video_file}")

# Set the video folder path from the file path
video_folder_path = os.path.dirname(video_file)

# Extract the name of the video file (without extension) to use for the output folder
video_name = os.path.splitext(os.path.basename(video_file))[0]

# Clear existing data to start fresh
bpy.ops.wm.read_factory_settings(use_empty=True)

# Create the Sequencer if it doesn't exist
scene = bpy.context.scene
if not scene.sequence_editor:
    scene.sequence_editor_create()

# Ensure there is a SEQUENCE_EDITOR context available
# Switch one of the existing areas to 'SEQUENCE_EDITOR'
screen = bpy.context.window.screen
sequencer_area = None

# Look for an area to change to 'SEQUENCE_EDITOR'
for area in screen.areas:
    if area.type == 'SEQUENCE_EDITOR':
        sequencer_area = area
        break

# If no SEQUENCE_EDITOR area was found, convert an area to SEQUENCE_EDITOR
if not sequencer_area:
    for area in screen.areas:
        if area.type in {'VIEW_3D', 'OUTLINER', 'PROPERTIES'}:  # Choose an area to convert
            area.type = 'SEQUENCE_EDITOR'
            sequencer_area = area
            break

# Check if we successfully found or converted an area to SEQUENCE_EDITOR
if not sequencer_area:
    raise RuntimeError("Could not find or create a SEQUENCE_EDITOR area for the operation.")

# Add the video strip to the Sequencer using the found SEQUENCE_EDITOR area
with bpy.context.temp_override(area=sequencer_area):
    bpy.ops.sequencer.movie_strip_add(filepath=video_file, frame_start=1, channel=1)

print('Successfully added video strip to the sequencer.')

# Get the video strip
video_strip = bpy.context.scene.sequence_editor.sequences_all[0]

# Print the FPS of the video
video_fps = video_strip.fps
print(f"Video FPS: {video_fps}")

# Calculate the total frame length of the video
video_length = video_strip.frame_final_duration
print(f"Video length: {video_length} frames")

# Prompt user to choose how to specify the start and end: percentage or frames
selection = input("Do you want to specify start and end by percentage 'p' or frames 'f'? ").strip().lower()

if selection == 'p':
    # Prompt user for start and end percentages
    start_percentage = float(input("Enter the start percentage of the video (0-100): "))
    end_percentage = float(input("Enter the end percentage of the video (0-100): "))

    if not (0 <= start_percentage <= 100) or not (0 <= end_percentage <= 100):
        raise Exception("Start and end percentages must be between 0 and 100.")

    if start_percentage >= end_percentage:
        raise Exception("Start percentage must be less than end percentage.")

    # Calculate the start and end frames based on the given percentages
    start_frame = int(video_length * (start_percentage / 100))
    end_frame = int(video_length * (end_percentage / 100))

elif selection == 'f':
    # Prompt user for start frame and total number of frames
    start_frame = int(input("Enter the start frame (minimum 1): "))
    total_frames = int(input(f"Enter the number of frames to include (1 to {video_length - start_frame + 1}): "))

    if not (1 <= start_frame <= video_length):
        raise Exception(f"Start frame must be between 1 and {video_length}.")

    if not (1 <= total_frames <= (video_length - start_frame + 1)):
        raise Exception(f"Total frames must be between 1 and {video_length - start_frame + 1}.")

    # Calculate end frame based on start frame and total frames
    end_frame = start_frame + total_frames - 1

else:
    raise Exception("Invalid selection. Please enter 'percentage' or 'frames'.")

# Set the start and end frame for the scene
bpy.context.scene.frame_start = start_frame
bpy.context.scene.frame_end = end_frame

# Set output .blend file path (automatically in the video folder for convenience)
output_blend_path = os.path.join(video_folder_path, "new_sequencer.blend")

# Create an output directory for PNG sequence named after the video file
img_sequence_folder = os.path.join(video_folder_path, f"{video_name}_img_seq")
if not os.path.exists(img_sequence_folder):
    os.makedirs(img_sequence_folder)
    print(f"Created directory for PNG sequence at: {img_sequence_folder}")

# Set render settings for PNG sequence
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = os.path.join(img_sequence_folder, "frame_")

# Render the image sequence for the specified frame range
bpy.ops.render.render(animation=True)

print(f"PNG sequence rendered to: {img_sequence_folder}")
