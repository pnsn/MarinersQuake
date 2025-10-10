# MarinersQuake
Python script to plot a pretty seismogram for media use.  
This script will download data that gets updated at 6 seconds past the minute for the previous minute.

Don't forget to change the path in the very first line.  This needs packages pytz, requests, and obspy which can be installed with:\
pip install pytz obspy requests


The parameters in the code to play with to get the prettiest wiggles:\
channel- Choose HNZ, HNN, or HNE for vertical, north-south, east-west ground motion.

UTC time (will get converted to local time):\
plot_start_time = datetime(2025, 10, 9, 16, 30, 0).astimezone(pytz.utc)\
plot_end_time = datetime(2025, 10, 9, 16, 35, 0).astimezone(pytz.utc)

Frequency of the wiggles:  10-15 Hz was pretty good for Century Link events, maybe try 5-10, 5-15, 10-20.\
freqmin = 10.\
freqmax = 15.

Manually set the y-axis limits in mm/s^2.  Default (commented out) is to auto-scale.\
#ylimits = 1.5

Choose/replace the logo.  Top uses PNSNWebpageLogo.jpg, bottom uses PNSNLogo_RGB_Main.png.\
#img2 = mpimg.imread("PNSNLogo_RGB_Main.png")\
img2 = mpimg.imread("PNSNWebpageLogo.jpg")


![Using PNSNWebpageLogo.jpg](https://github.com/pnsn/MarinersQuake/blob/main/seismogram_UW.RIZZS.HNZ_Acceleration.png)


![Using PNSNLogo_RGB_Main.png](https://github.com/pnsn/MarinersQuake/blob/main/seismogram_UW.RIZZS.HNN_Acceleration.png)



