# MarinersQuake
Python script to plot a pretty seismogram for media use.  
This script will download data that gets updated at 6 seconds past the minute for the previous minute.

Don't forget to change the path in the very first line.  This needs packages pytz, requests, and obspy which can be installed with:\
pip install pytz obspy requests


The parameters in the code to play with to get the prettiest wiggles:\
channel- Choose HNZ, HNN, or HNE for vertical, north-south, east-west ground motion.

Time window (Pacific time) of wiggles for the entire plot and then the portion to be animated in 1:1 time:\
plot_start_time_local = pacific.localize(datetime(2025, 10, 10, 22, 7, 5))
plot_end_time_local = pacific.localize(datetime(2025, 10, 10, 22, 7, 30))
video_start_local = pacific.localize(datetime(2025, 10, 10, 22, 7, 12))
video_end_local   = pacific.localize(datetime(2025, 10, 10, 22, 7, 30))


Frequency of the wiggles:  10-15 Hz was pretty good for Century Link events, maybe try 5-10, 5-15, 10-20.\
freqmin = 10.\
freqmax = 15.

Manually set the y-axis limits in mm/s^2.  Default (commented out) is to auto-scale.\
#ylimits = 1.5

Frames per second: animation fps.  Set = 0 to skip the animation and just make an image. \
   20 is a reasonable fps if your plotting less than a minute of data.

Using ylimits = 1.5:\
![Using PNSNWebpageLogo.jpg](https://github.com/pnsn/MarinersQuake/blob/main/seismogram_UW.RIZZS.HNN_Acceleration.png)

ylimits is commented out (amplitudes auto-scaled to fit figure):\
![Using PNSNLogo_RGB_Main.png](https://github.com/pnsn/MarinersQuake/blob/main/seismogram_UW.RIZZS.HNZ_Acceleration.png)

Resulting animation, video here starts at 12sec and goes till 30sec:
![UW.RIZZS_animation.mp4](https://github.com/pnsn/MarinersQuake/blob/main/UW.RIZZS_animation.mp4)


