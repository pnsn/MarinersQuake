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

# use variables for time window
year = 2025
month = 10
day_start = 10
day_end = 10
hr_start = 22
min_start = 2
sec_start = 0
hr_end = 22
min_end = 8
sec_end = 0

# Define the y-axis limits in mm/s^2. Default is None/auto-scale.
#ylimits = 1.5

# Define figure title
title_line1 = "  Starting vertical ground motion called by UW.RIZZS   ALCS Game 3 Oct 15, 2025"
title_line2 = "  This is what inbetween innings looks like (loud music thumping)"
make_gif = False   # also create a GIF version
show_time_marker = False  # include a red line sliding in time in the animation

# Define frames per second.  fps = 0 to just make .png and no .mp4 (faster)
fps = 20  # (20 is smooth if only showing ~20 sec)

# Define start and end times using local times 
pacific = pytz.timezone('America/Los_Angeles')
utc = pytz.utc
video_start_local = pacific.localize(datetime(year, month, day_start, hr_start, min_start, sec_start))
video_end_local   = pacific.localize(datetime(year, month, day_end, hr_end, min_end, sec_end))
animation_filename = "UW.RIZZS_animation.mp4"
plot_start_time_local = pacific.localize(datetime(year, month, day_start, hr_start, min_start, sec_start))
plot_end_time_local = pacific.localize(datetime(year, month, day_end, hr_end, min_end, sec_end))

plot_start_time = plot_start_time_local.astimezone(utc)
plot_end_time = plot_end_time_local.astimezone(utc)
video_start = video_start_local.astimezone(utc)
video_end   = video_end_local.astimezone(utc)

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
#    ground_motion_units = "(m/s^2)"
#    ground_motion_units = "(mm/s^2)"
    ground_motion_units = "%g"
elif ground_motion_type == "VEL":
    ground_motion_label = "Velocity"
    ground_motion_units = "(m/s)"
elif ground_motion_type == "DISP":
    ground_motion_label = "Displacement"
    ground_motion_units = "(m)"

# Download data
julian_day = UTCDateTime(plot_start_time).julday
mseed_url = f"https://seismo.ess.washington.edu/~ahutko/UW.RIZZS/UW.RIZZS..{channel}.{year}.{julian_day}"
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
    #data = tr.data * 1000. # mm/s/s
    data = ( tr.data / 9.8 ) * 100 # percent g
    #data = tr.data
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
    fig = plt.figure(figsize=(13, 6))

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
    ax_plot.set_xlabel('Time (local)', color=text_color, fontweight="bold")
    ax_plot.set_ylabel(f"{ground_motion_label} {ground_motion_units}",
                       color=text_color, fontsize=12, fontweight="bold")
    ax_plot.tick_params(axis='both', which='both', colors=text_color)

    #sec_ax = ax_plot.secondary_yaxis("right",functions=(lambda x: (100.*x)/9.8, lambda x: 9.8*x/100.))
    #sec_ax.set_ylabel("%g")
    
    # Set the spine color to the same as text_color
    for spine in ax_plot.spines.values():
        spine.set_color(text_color)

    ax_plot.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    plt.xticks(rotation=45)

    # --- Insert the PNSN logo in top-left corner above title ---
    # Use fig.add_axes to position it in figure coordinates (0–1)
    logopnsn_ax = fig.add_axes([0.77, 0.82, 0.18, 0.18])  # [left, bottom, width, height]
    logopnsn_ax.imshow(img2)
    logopnsn_ax.axis("off")

    logoS_ax = fig.add_axes([0.035, 0.87, 0.1, 0.1])
    logoS_ax.imshow(img1)
    logoS_ax.axis("off")

    # --- Adjust margins ---
    plt.subplots_adjust(left=0.12, right=0.94, bottom=0.22, top=0.83)

    # --- Adjust the y-axis of seismogram if desired
    try:
        ax_plot.set_ylim([-1*ylimits,ylimits])
        sec_ax = ax_plot.secondary_yaxis("right",functions=(lambda x: (100.*x)/9.8, lambda x: 9.8*x/100.))
        sec_ax.set_ylabel("%g")
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
        plt.savefig(f"seismogram_{network}.{station}.{channel}_{ground_motion_label}.png",
                    dpi=150, bbox_inches='tight')
        print(f"Static seismogram saved as seismogram_{network}.{station}.{channel}_{ground_motion_label}.png")

    else:
        ax_plot.plot(fudged_local_times, data, '-', color=trace_color, linewidth=trace_linewidth)
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

