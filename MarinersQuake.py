#!/home/ahutko/miniconda3/bin/python

import pytz
from datetime import datetime, timedelta
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

def normalize_rgb(r, g, b):
    """Normalize RGB colors for Matplotlib."""
    return (r / 255.0, g / 255.0, b / 255.0)

# Define your station details
network = "UW"
station = "KDK"
location = "--"
channel = "HNN"

# Define start and end times using Python's datetime in UTC
plot_start_time = datetime(2024, 6, 10, 21, 20, 0).astimezone(pytz.utc)
plot_end_time = datetime(2024, 6, 10, 21, 22, 0).astimezone(pytz.utc)
padding = 5 / 0.005  # Calculate padding based on the lowest corner of the response removal filter

# Adjust start and end times for data fetching to include padding
data_start_time = plot_start_time - timedelta(seconds=padding)
data_end_time = plot_end_time + timedelta(seconds=padding)

# Define frequency bands for the response removal
pre_filt = (0.005, 0.006, 30.0, 35.0)

# Set filter parameters
filter_type = 'bandpass'
freqmin = 10.
freqmax = 15.

# Define colors and linewidth
trace_color = normalize_rgb(12,44,86)
text_color = normalize_rgb(0,92,92)
trace_linewidth = 0.2

# Define the ground motion type, options are: DISP, VEL, ACC, DEF
ground_motion_type = "ACC"
ground_motion_label = {}
ground_motion_label['DISP'] = 'displacement'

# Initialize client to access data from the IRIS data service
client = Client("IRIS")

try:
    # Fetch waveform and station information for response removal
    st = client.get_waveforms(network, station, location, channel,
                              UTCDateTime(data_start_time), UTCDateTime(data_end_time))
    inv = client.get_stations(network=network, station=station, location=location, channel=channel,
                              starttime=UTCDateTime(data_start_time), endtime=UTCDateTime(data_end_time), level='response')

    # Remove the instrument response and apply filter
    st.remove_response(inventory=inv, output=ground_motion_type, pre_filt=pre_filt, water_level=60, plot=False)
    st.filter(filter_type, freqmin=freqmin, freqmax=freqmax)

    # Trim the stream to the desired plotting window
    st.trim(UTCDateTime(plot_start_time), UTCDateTime(plot_end_time))

    # Extract data for plotting
    tr = st[0]
    data = tr.data
    times = [datetime.utcfromtimestamp(plot_start_time.timestamp() + t) for t in tr.times()]

    # Define the Pacific Time Zone
    pacific_tz = pytz.timezone('America/Los_Angeles')
    
    # Calculate dynamic time offset based on date and daylight saving
    offset = pacific_tz.utcoffset(times[0]).total_seconds() / 3600

    # Adjust times to Pacific Time dynamically considering daylight savings
    fudged_local_times = [t + timedelta(hours=offset) for t in times]
    fudged_plot_start_time = plot_start_time + timedelta(hours=offset)
    print(offset, times[0], fudged_local_times[0])

    # Create a figure for plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(fudged_local_times, data, '-', color=trace_color, linewidth=trace_linewidth)

    # Set title and labels
    ax.set_title(f'Seismogram from PNSN station {station} (North-South motion) {fudged_plot_start_time.strftime("%Y-%m-%d")}', color=text_color, fontsize=12)
    ax.set_xlabel('Time (Pacific Time)', color=text_color)
    ax.set_ylabel('Acceleration (m/s^2)', color=text_color)

    # Change axis and tick colors
    ax.tick_params(axis='both', which='both', colors=text_color)
    
    # Set the spine color to the same as text_color
    for spine in ax.spines.values():
        spine.set_color(text_color)

    # Set the date format on the x-axis
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save and display the plot
    plt.savefig("seismogram_acceleration1.png")
    print("Acceleration seismogram saved as 'seismogram_acceleration1.png'.")

except Exception as e:
    print("Failed to process the seismogram:", str(e))




