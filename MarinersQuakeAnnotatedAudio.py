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
import matplotlib.animation as animation
import subprocess
from pathlib import Path

def normalize_rgb(r, g, b):
    """Normalize RGB colors for Matplotlib."""
    return (r / 255.0, g / 255.0, b / 255.0)

# Define your station details
network = "UW"
station = "RIZZS"
location = "--"
channel = "HNZ"

# Define the y-axis limits in mm/s^2. Default is None/auto-scale.
#ylimits = 0.1

# --- Big Honking Banner ---
banner_text = "SUÁREZ GRAND SLAM!     MARINERS WIN GAME 5!"
banner_fontsize = 26  # adjust as desired
banner_height = 0.12  # fraction of figure height

# Define audio file:
audio_filename = "SuarezGrandSlamAudio.mp3"

# Define figure title
#title_line1 = "  SUAREZ GRAND SLAM!  Mariners WIN!"
title_line1 = "                                                               "
title_line2 = "                                                               "
#title_line3 = "  Vertical ground motion called by UW.RIZZS   ALCS Game 5 Oct 17, 2025"
title_line3 = "    UW.RIZZS and Rick Rizzs   ALCS Game 5 Oct 17, 2025"
make_gif = False   # also create a GIF version
show_time_marker = False  # include a red line sliding in time in the animation

# Define frames per second.  fps = 0 to just make .png and no .mp4 (faster)
fps = 20  # (20 is smooth if only showing ~20 sec)

# Define start and end times using local times 
pacific = pytz.timezone('America/Los_Angeles')
utc = pytz.utc
plot_start_time_local = pacific.localize(datetime(2025, 10, 17, 18, 0, 5))
plot_end_time_local = pacific.localize(datetime(2025, 10, 17, 18, 1, 15))
video_start_local = pacific.localize(datetime(2025, 10, 17, 18, 0, 12))
video_end_local   = pacific.localize(datetime(2025, 10, 17, 18, 1, 15))
#video_end_local   = pacific.localize(datetime(2025, 10, 17, 18, 0, 18))

# Each annotation has: label text, the input time where the red line should be,
# the x-position where text should appear, and the y-position (amplitude)

annotations = []

# 10x10 fig size:
#annotations = [
#    {"label": "Going...", "time": datetime(2025,10,17,18,0,16,int(0.8 * 1e6)), "x_text": datetime(2025,10,17,18,0,9, int(0.4 * 1e6)), "y_text": -0.04, "red_line_amp": 0.03},
#    {"label": "Going...", "time": datetime(2025,10,17,18,0,18,int(0.8 * 1e6)), "x_text": datetime(2025,10,17,18,0,17, int(0.01 * 1e6)), "y_text": -0.04, "red_line_amp": 0},
#    {"label": "GOODBYE BASEBALL!", "time": datetime(2025,10,17,18,0,21), "x_text": datetime(2025,10,17,18,0,13, int(0.1*1e6)), "y_text": 0.05, "red_line_amp": 0.05},
#]

# 13x6 fig size:
#annotations = [
#    {"label": "Suarez hit...", "time": datetime(2025,10,17,18,0,16,int(0.8 * 1e6)), "x_text": datetime(2025,10,17,18,0,13, int(0.4 * 1e6)), "y_text": -0.04, "red_line_amp": 0.03},
#    {"label": "Suarez slam!", "time": datetime(2025,10,17,18,0,21), "x_text": datetime(2025,10,17,18,0,17, int(0.5*1e6)), "y_text": 0.05, "red_line_amp": 0.05},
#]

animation_filename = "UW.RIZZS_animation.mp4"
plot_start_time = plot_start_time_local.astimezone(utc)
plot_end_time = plot_end_time_local.astimezone(utc)

# Define frequency bands for the response removal
pre_filt = (0.2, 0.3, 30.0, 35.0)

# Set filter parameters for plotted seismogram. 
#   Make sure these are in between the 2nd and 3rd in pre_filt.
filter_type = 'bandpass'
freqmin = 1.
freqmax = 30.

# Define colors and linewidth.  Just look up RGB values for team colors
trace_color = normalize_rgb(12,44,86)
text_color = normalize_rgb(0,92,92)
trace_linewidth = 0.4

# Choose and load the PNSN logo
PNSNlogo = "PNSNLogo_RGB_Main.png"
img2 = mpimg.imread(PNSNlogo)
img1 = mpimg.imread("Seattle_Mariners_Logo.png")

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
    data = tr.data * 100 / 9.8 # go from m/s^2 to %g
    times = [datetime.utcfromtimestamp(plot_start_time.timestamp() + t) for t in tr.times()]

    # Calculate dynamic time offset based on date and daylight saving
    offset = pacific.utcoffset(times[0]).total_seconds() / 3600

    # Adjust times to Pacific Time dynamically considering daylight savings
    fudged_local_times = [t + timedelta(hours=offset) for t in times]
    fudged_plot_start_time = plot_start_time + timedelta(hours=offset)

    # Create a figure for plotting
    # ==========================================================
    # FIGURE AND TITLE / LOGO LAYOUT
    # ==========================================================

    plt.rcParams['font.size'] = 14
    plt.rcParams['font.weight'] = 'bold'
    fig = plt.figure(figsize=(10, 10))

    # Add an Axes that spans the full width, with no ticks or frame
    banner_ax = fig.add_axes([0, 1 - banner_height, 1, banner_height])
    banner_ax.set_facecolor(trace_color)
    banner_ax.set_xticks([])
    banner_ax.set_yticks([])
    banner_ax.set_xlim(0, 1)
    banner_ax.set_ylim(0, 1)

    # Add the text, centered both horizontally and vertically
    banner_ax.text(
        0.5, 0.5, banner_text,
        color='white',
        fontsize=banner_fontsize,
        fontweight='bold',
        fontfamily='sans-serif',
        fontname='Arial',
        ha='center', va='center',
        transform=banner_ax.transAxes
    )

    # Optional: bring the banner to the very top visually
    banner_ax.set_zorder(10)

    # Define grid for the main plot only (no more right-side images)
    gs = gridspec.GridSpec(1, 1)
    ax_plot = plt.subplot(gs[0, 0])

    # --- Build multi-line title ---
    title_lines = [title_line1]
    if 'title_line2' in locals() and title_line2.strip():
        title_lines.append(title_line2)
    if 'title_line3' in locals() and title_line3.strip():
        title_lines.append(title_line3)

    # Join and wrap lines if they’re long
    wrapped_title = "\n".join([
        "\n".join(textwrap.wrap(line, width=80)) for line in title_lines
    ])

    ax_plot.set_title(wrapped_title, color=text_color, loc='left', fontsize = 16)

    # --- Axis labels and style ---
    #ax_plot.set_xlabel('Time (local)', color=text_color, fontweight="bold")
    ax_plot.set_ylabel(f"{ground_motion_label} {ground_motion_units}",
                       color=text_color, fontsize=12, fontweight="bold")
    ax_plot.tick_params(axis='both', which='both', colors=text_color)
    for spine in ax_plot.spines.values():
        spine.set_color(text_color)

    ####ax_plot.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    ax_plot.xaxis.set_major_formatter(DateFormatter('%-I:%M:%S %p'))
    plt.xticks(rotation=45)

    # --- Insert the PNSN logo in top-left corner above title ---
    # Use fig.add_axes to position it in figure coordinates (0–1)
    logopnsn_ax = fig.add_axes([0.77, 0.75, 0.18, 0.18])  # [left, bottom, width, height]
    logopnsn_ax.imshow(img2)
    logopnsn_ax.axis("off")

    logoS_ax = fig.add_axes([0.035, 0.77, 0.1, 0.1])
    logoS_ax.imshow(img1)
    logoS_ax.axis("off")

    # --- Adjust margins ---
    plt.subplots_adjust(left=0.12, right=0.94, bottom=0.12, top=0.8)

    # --- Adjust the y-axis of seismogram if desired
    try:
        ax_plot.set_ylim([-1*ylimits,ylimits])
    except:
        pass

    fig.canvas.draw_idle()

except Exception as e:
    print("Failed to process the seismogram:", str(e))

# ==========================================================
# ANIMATION SECTION (progressively reveal seismogram)
# ==========================================================
try:
    if fps > 0:
        print("Creating animation...")

        # --- Normalize time objects (make all tz-naive) ---
        xdata = np.array([t.replace(tzinfo=None) for t in fudged_local_times])
        ydata = np.array(data)
        video_start_naive = video_start_local.replace(tzinfo=None)
        video_end_naive   = video_end_local.replace(tzinfo=None)
        plot_start_naive  = plot_start_time_local.replace(tzinfo=None)
        plot_end_naive    = plot_end_time_local.replace(tzinfo=None)

        # Prepare annotations (tz-naive for Matplotlib)
        for ann in annotations:
            ann["time_naive"]   = ann["time"].replace(tzinfo=None)
            ann["x_text_naive"] = ann["x_text"].replace(tzinfo=None)

        # Pre-create artists (hidden initially)
        annotation_artists = []
        for ann in annotations:
            line = ax_plot.plot(
                [ann["time_naive"], ann["time_naive"]],
                [-ann["red_line_amp"], ann["red_line_amp"]],
                color='red', lw=0.5, alpha=0.8, visible=False
            )[0]
            txt = ax_plot.text(
                ann["x_text_naive"], ann["y_text"], ann["label"],
                color='black',
                fontsize=14,
                fontweight='bold',
                ha='center', va='bottom',
                fontfamily='sans-serif',  # ensures sans-serif family
                fontname='Arial',         # explicitly use Arial
                bbox=dict(facecolor=text_color, alpha=0.4, edgecolor='none'),
                visible=False
            )
            annotation_artists.append((ann, line, txt))

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
        line_anim, = ax_plot.plot(x_pre, y_pre, '-', color=trace_color, linewidth=trace_linewidth)
        time_marker = None
        if show_time_marker:
            time_marker = ax_plot.axvline(video_start_naive, color='r', lw=1.5)

        # Pre-create artists (hidden initially)
        annotation_artists = []
        for ann in annotations:
            line = ax_plot.plot(
                [ann["time_naive"], ann["time_naive"]],
                [-ann["red_line_amp"], ann["red_line_amp"]],
                color='red', lw=1.5, alpha=0.8, visible=False
            )[0]
            txt = ax_plot.text(
                ann["x_text_naive"], ann["y_text"], ann["label"],
                color='black',
                fontsize=26,
                fontweight='bold',
                ha='center', va='bottom',
                fontfamily='sans-serif',  # ensures sans-serif family
                fontname='Arial',         # explicitly use Arial
                bbox=dict(facecolor=text_color, alpha=0.4, edgecolor='none'),
                visible=False
            )
            annotation_artists.append((ann, line, txt))
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

            # --- Reveal annotations when their time has arrived ---
            current_time = x_anim[min(idx - 1, len(x_anim) - 1)]
            for ann, line, txt in annotation_artists:
                if ann["time_naive"] <= current_time:
                    line.set_visible(True)
                    txt.set_visible(True)

            artists = [line_anim]
            if show_time_marker and time_marker is not None:
                artists.append(time_marker)
            for _, line, txt in annotation_artists:
                artists.extend([line, txt])
            return tuple(artists)

            #return (line_anim,) if not show_time_marker else (line_anim, time_marker)

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
        plt.savefig(f"seismogram_{network}.{station}.{channel}_{ground_motion_label}.png",
                    dpi=150, bbox_inches='tight')
        print(f"Static seismogram saved as seismogram_{network}.{station}.{channel}_{ground_motion_label}.png")

    else:
        ax_plot.plot(fudged_local_times, data, '-', color=trace_color, linewidth=trace_linewidth)
        for ann in annotations:
            tna = ann["time"].replace(tzinfo=None)
            xtna = ann["x_text"].replace(tzinfo=None)
            ax_plot.plot([tna, tna],
                         [-ann["red_line_amp"], ann["red_line_amp"]],
                         color='red', lw=1.5, alpha=0.8)
            ax_plot.text(
                xtna, ann["y_text"], ann["label"],
                color='black',
                fontsize=26,
                fontweight='bold',
                ha='center', va='bottom',
                fontfamily='sans-serif',
                fontname='Arial',
                bbox=dict(facecolor=text_color, alpha=0.4, edgecolor='none')
            )
        try:
            ax_plot.set_ylim([-1 * ylimits, ylimits])
        except:
            pass
        fig.canvas.draw_idle()
        plt.savefig(f"seismogram_{network}.{station}.{channel}_{ground_motion_label}.png",
                    dpi=150, bbox_inches='tight')
        print(f"Static seismogram saved as seismogram_{network}.{station}.{channel}_{ground_motion_label}.png")
 
except Exception as e:
    print("Animation failed:", str(e))


# ==========================================================
# ADD AUDIO
# ==========================================================
video_filename = animation_filename
output_filename = Path(video_filename).with_name("seismogram_animation_with_audio.mp4")

cmd = [
    "ffmpeg", "-y",
    "-i", video_filename,       # input video
    "-i", audio_filename,       # input audio
    "-c:v", "copy",             # copy video stream (no re-encode)
    "-c:a", "aac",              # re-encode audio to AAC for MP4 compatibility
    "-shortest",                # stop when the shorter stream ends
    str(output_filename)
]

subprocess.run(cmd, check=True)
print(f"Combined video+audio saved as {output_filename}")


