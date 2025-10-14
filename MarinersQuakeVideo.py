#!/home/ahutko/miniconda3/bin/python

import pytz
from datetime import datetime, timedelta
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from obspy import read, read_inventory
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import requests
import matplotlib.image as mpimg
from matplotlib import gridspec
import textwrap
import matplotlib.animation as animation
import numpy as np
import time

def normalize_rgb(r, g, b):
    """Normalize RGB colors for Matplotlib."""
    return (r / 255.0, g / 255.0, b / 255.0)

# Define your station details
network = "UW"
station = "RIZZS"
location = "--"
channel = "HNZ"

# Define the y-axis limits in mm/s^2. Default is None/auto-scale.
#ylimits = 1.5

# Define figure title
# Vertical ground motion called by {network}.{station}   ALDS Game 5 {fudged_plot_start_time.strftime("%b %d, %Y")} Polanco Game Winning Single, Crawford Scores, MARINERS WIN!!
title_line1 = "ALDS Game 5  —  Polanco Game-Winning Single"
title_line2 = "Crawford Scores, MARINERS WIN!!"
make_gif = False   # also create a GIF version
show_time_marker = False

# Define start and end times using local times 
pacific = pytz.timezone('America/Los_Angeles')
utc = pytz.utc
plot_start_time_local = pacific.localize(datetime(2025, 10, 10, 22, 4, 0))
plot_end_time_local = pacific.localize(datetime(2025, 10, 10, 22, 11, 0))
fps = 5  # frames per second (2–10 typical)
#video_start_local = datetime(2025, 10, 10, 22, 7, 0)  # local datetime
#video_end_local   = datetime(2025, 10, 10, 22, 8, 0)  # local datetime
video_start_local = pacific.localize(datetime(2025, 10, 10, 22, 7, 0))
video_end_local   = pacific.localize(datetime(2025, 10, 10, 22, 8, 0))

animation_filename = "seismogram_animation.mp4"
plot_start_time = plot_start_time_local.astimezone(utc)
plot_end_time = plot_end_time_local.astimezone(utc)

# Define frequency bands for the response removal
pre_filt = (0.2, 0.3, 30.0, 35.0)

# Set filter parameters for plotted seismogram. 
#   Make sure these are in between the 2nd and 3rd in pre_filt.
filter_type = 'bandpass'
freqmin = 10.
freqmax = 15.

# Define colors and linewidth.  Just look up RGB values for team colors
trace_color = normalize_rgb(12,44,86)
text_color = normalize_rgb(0,92,92)
trace_linewidth = 0.2

# Choose and load the PNSN logo
PNSNlogo = "PNSNLogo_RGB_Main.png"
img2 = mpimg.imread(PNSNlogo)
img1 = mpimg.imread("SeisTheMoment.png")

# Define padding (for processing, not for display) 
padding = 5  # Calculate padding based on the lowest corner of the response removal filter

# Define the ground motion type, options are: DISP, VEL, ACC, DEF
ground_motion_type = "ACC"
ground_motion_label = {}
if ground_motion_type == "ACC":
    ground_motion_label = "Acceleration"
    #ground_motion_units = "(m/s^2)"
    #ground_motion_units = "(mm/s^2)"
    ground_motion_units = "% g"
elif ground_motion_type == "VEL":
    ground_motion_label = "Velocity"
    ground_motion_units = "(m/s)"
elif ground_motion_type == "DISP":
    ground_motion_label = "Displacement"
    ground_motion_units = "(m)"

# Download data
julian_day = UTCDateTime(plot_start_time).julday
mseed_url = "https://seismo.ess.washington.edu/~ahutko/UW.RIZZS/UW.RIZZS.." + channel + ".2025." + str(julian_day)
xml_url = "https://seismo.ess.washington.edu/~ahutko/UW.RIZZS/Station_UW_RIZZS.xml"

with open("waveform.mseed", "wb") as f:
    f.write(requests.get(mseed_url).content)
with open("station.xml", "wb") as f:
    f.write(requests.get(xml_url).content)

# Read waveform and station metadata
st = read("waveform.mseed")
inv = read_inventory("station.xml")

try:
    # Trim the stream to the desired trimming window
    st.trim(UTCDateTime(plot_start_time) - padding, UTCDateTime(plot_end_time) + padding)

    # Remove the instrument response and apply filter
    st.remove_response(inventory=inv, output=ground_motion_type, pre_filt=pre_filt, water_level=60, plot=False)
    st.filter(filter_type, freqmin=freqmin, freqmax=freqmax)

    # Trim the stream to the desired plotting window
    st.trim(UTCDateTime(plot_start_time), UTCDateTime(plot_end_time))

    # Extract data for plotting
    tr = st[0]
    data = tr.data * 10.
    times = [datetime.utcfromtimestamp(plot_start_time.timestamp() + t) for t in tr.times()]

    # Calculate dynamic time offset based on date and daylight saving
    offset = pacific.utcoffset(times[0]).total_seconds() / 3600

    # Adjust times to Pacific Time dynamically considering daylight savings
    fudged_local_times = [t + timedelta(hours=offset) for t in times]
    fudged_plot_start_time = plot_start_time + timedelta(hours=offset)

    # Create a figure for plotting
    plt.rcParams['font.size'] = 14          # default font size
    plt.rcParams['font.weight'] = 'bold'    # default bold 
    fig = plt.figure(figsize=(13,6))
    gs = gridspec.GridSpec(2, 2, width_ratios=[10,4], height_ratios=[4,1])
    gs.update(wspace=0.03, hspace=0.03)

    # Plot main seismogram
    ax_plot = plt.subplot(gs[:,0])
    #ax_plot.plot(fudged_local_times, data, '-', color=trace_color, linewidth=trace_linewidth)

    # Set title and labels
    wrapped_title1 = "\n".join(textwrap.wrap(title_line1, width=70))
    wrapped_title2 = "\n".join(textwrap.wrap(title_line2, width=70))
    ax_plot.set_title(f"{wrapped_title1}\n{wrapped_title2}", color=text_color)
    #if channel.endswith('Z'):
    #     title = (f'Vertical ground motion called by {network}.{station}   ALDS Game 5 {fudged_plot_start_time.strftime("%b %d, %Y")} Polanco Game Winning Single, Crawford Scores, MARINERS WIN!!')
    #     wrapped_title = "\n".join(textwrap.wrap(title, width=70))
    #     ax_plot.set_title(wrapped_title, color=text_color)
    #elif channel.endswith('N'):
    #    ax_plot.set_title(f'North-South ground motion called by {network}.{station}   ALDS Game 5 {fudged_plot_start_time.strftime("%b %d, %Y")}', color=text_color) #, fontsize=12)
    #else:
    #    ax_plot.set_title(f'East-West ground motion called by {network}.{station}   ALDS Game 5 {fudged_plot_start_time.strftime("%b %d, %Y")}', color=text_color) #, fontsize=12)

    ax_plot.set_xlabel('Time (local)', color=text_color, fontweight="bold")
    ax_plot.set_ylabel(ground_motion_label + " " + ground_motion_units, color=text_color, fontsize = 12, fontweight="bold")

    # Change axis and tick colors
    ax_plot.tick_params(axis='both', which='both', colors=text_color)
    
    # Set the spine color to the same as text_color
    for spine in ax_plot.spines.values():
        spine.set_color(text_color)

    # Set the date format on the x-axis
    ax_plot.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    plt.xticks(rotation=45)

    # --- Images on right side ---
    ax_img1 = plt.subplot(gs[0, 1])
    ax_img1.imshow(img1)
    ax_img1.axis("off")

    ax_img2 = plt.subplot(gs[1, 1])
    ax_img2.imshow(img2)
    ax_img2.axis("off")

    # --- Adjust margins ---
    plt.subplots_adjust(left=0.14, right=0.99, bottom=0.21, wspace=0.03, hspace=0.03)

    # Settle geometry, then freeze image axes
    fig.canvas.draw()
    pos1 = ax_img1.get_position()
    pos2 = ax_img2.get_position()
    ax_img1.set_position(pos1)
    ax_img2.set_position(pos2)

    # --- Adjust they-axis of seismogram if desired
    try:
        ax_plot.set_ylim([-1*ylimits,ylimits])
    except:
        pass

    fig.canvas.draw_idle()

    # Save and display the plot
    plt.savefig("seismogram_" + network + "." + station + "." + channel + "_" + ground_motion_label + ".png")
    print("Acceleration seismogram saved as 'seismogram_" + network + "." + station + "." + channel + "_" + ground_motion_label + ".png'.")

except Exception as e:
    print("Failed to process the seismogram:", str(e))

ax_plot.set_xlim(plot_start_time_local, plot_end_time_local)

# ==========================================================
# ANIMATION SECTION (progressively reveal seismogram)
# ==========================================================
try:
    print("Creating animation...")

    # --- Normalize time objects (make all tz-naive) ---
    xdata = np.array([t.replace(tzinfo=None) for t in fudged_local_times])
    ydata = np.array(data)
    video_start_naive = video_start_local.replace(tzinfo=None)
    video_end_naive   = video_end_local.replace(tzinfo=None)
    plot_start_naive  = plot_start_time_local.replace(tzinfo=None)
    plot_end_naive    = plot_end_time_local.replace(tzinfo=None)

    # --- Set axis limits for entire plot window ---
    ax_plot.set_xlim(plot_start_naive, plot_end_naive)
    ypad = 0.05 * (ydata.max() - ydata.min())
    ax_plot.set_ylim(ydata.min() - ypad, ydata.max() + ypad)

    # --- Split data by window segments ---
    mask_pre  = xdata <= video_start_naive
    mask_anim = (xdata > video_start_naive) & (xdata <= video_end_naive)
    mask_post = xdata > video_end_naive
    x_pre,  y_pre  = xdata[mask_pre],  ydata[mask_pre]
    x_anim, y_anim = xdata[mask_anim], ydata[mask_anim]
    x_post, y_post = xdata[mask_post], ydata[mask_post]
    print(f"Pre: {len(x_pre)}, Anim: {len(x_anim)}, Post: {len(x_post)}")

    # --- Safety fallbacks ---
    if len(x_pre) == 0:
        x_pre, y_pre = [xdata[0]], [ydata[0]]
    if len(x_anim) == 0:
        x_anim, y_anim = [xdata[-1]], [ydata[-1]]

    # --- Timing and frame setup ---
    duration = (video_end_naive - video_start_naive).total_seconds()
    frames = max(2, int(duration * fps))
    frame_interval = 1000 / fps
    samples_per_frame = max(1, int(len(x_anim) / frames))
    frame_indices = np.arange(1, len(x_anim) + 1, samples_per_frame)
    frame_indices = frame_indices[:frames]

    # --- Add one extra frame for the final "full" seismogram ---
    frame_indices = np.append(frame_indices, len(x_anim))
    print(f"Total frames: {len(frame_indices)}")

    # --- Base + animated lines ---
    base_line, = ax_plot.plot(x_pre, y_pre, '-', color=trace_color, linewidth=trace_linewidth)
    line_anim, = ax_plot.plot([], [], '-', color=trace_color, linewidth=trace_linewidth)
    time_marker = None
    if show_time_marker:
        time_marker = ax_plot.axvline(video_start_naive, color='r', lw=1.5)

    # --- Update function ---
    def update(frame_idx):
        idx = frame_indices[frame_idx]
        x_show = np.concatenate((x_pre, x_anim[:idx]))
        y_show = np.concatenate((y_pre, y_anim[:idx]))
        line_anim.set_data(x_show, y_show)

        # On final frame, include post data (fill to plot_end_time_local)
        if frame_idx == len(frame_indices) - 1 and len(x_post) > 0:
            line_anim.set_data(np.concatenate((x_show, x_post)),
                               np.concatenate((y_show, y_post)))

        # Update the red marker if enabled
        if show_time_marker and time_marker is not None:
            if frame_idx < len(frame_indices) - 1:
                time_marker.set_xdata(x_anim[min(idx - 1, len(x_anim) - 1)])
            else:
                # hide it on the final frame
                time_marker.set_visible(False)

        return (line_anim,) if not show_time_marker else (line_anim, time_marker)

    # --- Animate ---
    anim = animation.FuncAnimation(
        fig, update, frames=len(frame_indices),
        interval=frame_interval, blit=True, repeat=False
    )

    # --- Save animation files ---
    anim.save(animation_filename, writer='ffmpeg', fps=fps)
    print(f"Animation saved as {animation_filename}")

    if make_gif:
        gif_name = animation_filename.replace(".mp4", ".gif")
        anim.save(gif_name, writer='pillow', fps=fps)
        print(f"GIF saved as {gif_name}")

    # --- Ensure last frame drawn fully for static PNG ---
    plt.draw()
    plt.savefig("seismogram_static_final.png", dpi=150, bbox_inches='tight')
    print("Static 10-minute seismogram saved as seismogram_static_final.png.")

except Exception as e:
    print("Animation failed:", str(e))


