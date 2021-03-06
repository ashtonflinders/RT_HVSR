#!/Users/aflinders/anaconda3/bin/python

#from obspy.clients.fdsn import Client
from obspy.clients.earthworm import Client
from obspy import UTCDateTime
import datetime
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
import sys

import matplotlib.dates as mdates

ntwk = "HV"
stn =  sys.argv[1]
chn =  sys.argv[2]

def get_fdsn_station_day(network,station, channel, time_step=1,nperseg=2560, nfft=2560):

    time_now = UTCDateTime.now()
    time_then = time_now - datetime.timedelta(hours=time_step)

    #client = Client("IRIS")
    client = Client("130.118.86.189", 16022)

    
    compE = client.get_waveforms(network, station, "--", chn + 'E', time_then, time_now)[0]
    compN = client.get_waveforms(network, station, "--", chn + 'N', time_then, time_now)[0]
    compZ = client.get_waveforms(network, station, "--", chn + 'Z', time_then, time_now)[0]
    
    Fs=1/compE.stats.delta
    array_length=np.min([len(compE.data),len(compN.data),len(compZ.data)])-1
    
    f, t, specE = signal.spectrogram(compE.data[0:array_length], Fs,nperseg=nperseg,nfft=nfft)
    f, t, specN = signal.spectrogram(compN.data[0:array_length], Fs,nperseg=nperseg,nfft=nfft)
    f, t, specZ = signal.spectrogram(compZ.data[0:array_length], Fs,nperseg=nperseg,nfft=nfft)
   
    t = int(time_then.strftime('%s')) + t
    HVSR = np.log10(((specE*specN)**.5)/specZ)

    return t, f, HVSR

plt.ion()
fig=plt.figure()
plt.ylabel('Frequency (Hz)')

refresh_rate=20
while True:
    t, f, HVSR = get_fdsn_station_day(ntwk,stn,chn,time_step=2)
    
    time_stamps = [datetime.datetime.fromtimestamp(i) for i in t]
    plt.gcf().clear()
    plt.pcolormesh(time_stamps, f, HVSR, cmap='plasma_r', vmin=-2, vmax=4)
    axes = plt.gca()
    axes.set_ylim([.1,10])
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.show()
    
    plt.pause(refresh_rate)


