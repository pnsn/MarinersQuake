# MarinersQuake
Python script to plot a pretty seismogram for media use.  
Don't forget to change the path in the very first line.  This needs packages pytz, requests, and obspy which can be installed with:
pip install pytz obspy requests


The parameters in the code to play with to get the prettiest wiggles:

channel- Choose HNZ, HNN, HNE for vertical, north-south, east-west ground motion.

plot_start_time = datetime(2025, 10, 9, 16, 30, 0).astimezone(pytz.utc)

plot_end_time = datetime(2025, 10, 9, 16, 35, 0).astimezone(pytz.utc)

Frequency of the wiggles:  10-15 Hz was pretty good for Century Link events, maybe try 5-10, 5-15, 10-20.

freqmin = 10.

freqmax = 15.


