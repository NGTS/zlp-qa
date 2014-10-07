#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from pylab import *
import matplotlib.colors as colors
import matplotlib.cm as cmx
from astropy.io import fits as pf
from scipy.optimize import leastsq
import argparse

def main(args):
  filename = args.filename
  data_dict = load_data(filename)

  left_edges = 10**np.linspace(2, 5, 10)[:-1]
  right_edges = 10**(np.log10(left_edges) + 3./9.)

  values = range(0,len(left_edges)+1)

  mymap = cm = plt.get_cmap('autumn')
  cNorm  = colors.Normalize(vmin=0, vmax=values[-1])
  scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=mymap)

  levels = array([left_edges[0]] + list(right_edges))

  Z = [[0,0],[0,0]]

  CS3 = plt.contourf(Z, values[::-1],norm=cNorm, cmap=mymap)

  for i in range(0,len(left_edges)):
    colorVal = scalarMap.to_rgba(values[i])
    noisecharacterise(data_dict,fluxrange=[left_edges[i],right_edges[i]],c=colorVal,model=False)

  cbar = colorbar(CS3, ticks=values[::-1])

  nicelist = [int(left_edges[0])] + [int(x) for x in right_edges]

  cbar.ax.set_yticklabels(nicelist[::-1])# vertically oriented colorbar

  if args.output is not None:
    savefig(args.output, bbox_inches='tight')
  else:
    show()

def load_data(filename,mask=[]):
  dateclip = datesplit(filename)

  tmid = pf.getdata(filename, 'imagelist')['TMID']
  flux = pf.getdata(filename, 'flux')

  print 'all nights in data: ',dateclip[:,0]
  if len(mask) > 0:
    dateclip = dateclip[mask]
  print "Nights we're using: ",dateclip[:,0]

  cut = []
  for time in tmid:
    clip = [((time > date[0]) & (time < date[1])) for date in dateclip]
    cut += [any(clip)]
  cut = array(cut)

  tmid = tmid[cut]
  flux = flux[:,cut]

  mean_fluxes = pf.getdata(filename,'CATALOGUE')['FLUX_MEAN']

  meanbias = pf.getdata(filename,'IMAGELIST')['MEANBIAS']

  T = pf.getdata(filename,'IMAGELIST')['T']

  outdict = {'time':tmid,'flux':flux,'mean_fluxes':mean_fluxes[cut],'meanbias':meanbias[cut],'T':T[cut]}

  return outdict

def noisecharacterise(datadict,fname=[],fluxrange=[5000,20000],c='b',model=True):
# Characterises the noise level of bright, non saturated stars from the output of sysrem
# as a function of number of bins


  tmid = datadict['time']

  cadence = np.median(np.diff(tmid))*24*60

# needs to be a 1 dimensional array of fluxes
#  flux = pf.getdata(filename, 'flux')
#  tmid = pf.getdata(filename, 'imagelist')['TMID']

  flux = datadict['flux']

  binlow = 0.2
  binhigh = 4.0

  binstep = 0.1

  binrange = [int(np.ceil(10.0**(x))) for x in np.arange(binlow,binhigh,binstep)]

  binrange = sort(array(list(set(binrange))))

  binrange = binrange[binrange < len(flux[0])/3]

  maxflux = fluxrange[1]
  minflux = fluxrange[0]

  zero = 21.18135675

  mag_min = zero - 2.512*log10(maxflux)
  mag_max = zero - 2.512*log10(minflux)
  rms_lim = 1e9

  avflux = median(flux, axis=1)
  stdflux = std(flux, axis=1)
  rms = stdflux
  rms = abs(1.0857*1000.0*stdflux/ avflux)
  print avflux
  print stdflux
  print rms

  sane_keys = [((rms != inf) & (avflux != inf) & (rms != 0) & (rms < rms_lim) & (avflux != 0) & (rms != NaN) & (avflux != NaN) & (avflux < maxflux) & (avflux > minflux))]

  flux_sane = flux[sane_keys].copy()

  print 'Using ',len(flux_sane),' stars between ',mag_min,' and ',mag_max,' kepler mag'
  print 'Using ',len(flux_sane[0]),' time points'

  print max(median(flux_sane, axis=1))
  print min(median(flux_sane, axis=1))

  median_list = [np.median(rms[sane_keys])]
  N_bin_list = [1]
  quartiles = [[np.percentile(rms[sane_keys], 25),np.percentile(rms[sane_keys], 75)]]
  rms_error = [(np.std(rms[sane_keys]))/sqrt(len(rms[sane_keys])*1000)]

  for N in binrange:

    print 'Working with bin size', N

    binned = binning(flux_sane,N)

    avflux = median(binned, axis=1)
    stdflux = std(binned, axis=1)
    rms = stdflux
    rms = abs(1.0857*1000.0*stdflux/ avflux)

    sanity = ((rms != inf) & (avflux != inf) & (rms != 0) & (avflux != 0) & (rms != NaN) & (avflux != NaN) & (avflux < maxflux) & (avflux > minflux))
    rmssane = rms[sanity]
    median_list += [np.median(rmssane)]
    quartiles += [[np.percentile(rmssane, 25),np.percentile(rmssane, 75)]]
    N_bin_list  += [N]
    rms_error += [(np.std(rms[sanity]))/sqrt(1000*len(rms[sanity]))]

  prior = [median_list[0],median_list[-1]]

  N_bin_list = array(N_bin_list)
  median_list = array(median_list)
  rms_error = array(rms_error)
  quartiles = array(quartiles)

  low_quart = quartiles[:,0]
  high_quart = quartiles[:,1]

  m = 15

  output = leastsq(fitnoise,prior,args=(N_bin_list[:m],median_list[:m],rms_error[:m]))

  final = output[0]

  noise_curve = noisemodel(final,N_bin_list)
  white_curve = noisemodel([final[0],0],N_bin_list)
  red_curve = noisemodel([0,final[1]],N_bin_list)

  print final, 'noise results'

  # cadence in minutes

  ax1 = plt.subplot(111)
  ax1.set_ylim(0.4, 21)
  ax1.set_xlim(cadence*N_bin_list[0]*0.9,cadence*N_bin_list[-1]*1.1)
  ax1.errorbar(cadence*N_bin_list,median_list,yerr=rms_error,color=c,linewidth=2.0)
#  ax1.plot(N_bin_list,median_list[0]/sqrt(N_bin_list), 'r-')
  ax1.plot(cadence*N_bin_list,white_curve, '--',color='grey',alpha=0.8)
  if model == True:
    ax1.plot(cadence*N_bin_list,low_quart, 'b-')
    ax1.plot(cadence*N_bin_list,high_quart, 'b-')
    ax1.plot(cadence*N_bin_list,noise_curve, 'r-')
    ax1.plot(cadence*N_bin_list,red_curve, 'r--')
  ax1.set_yscale('log')
  ax1.set_xscale('log')
#  ax1.set_xlabel("Bin length (minutes)")
  ax1.set_xlabel("Bin size (Minutes)")
  ax1.set_ylabel("Fractional RMS (millimags)")
  ax1.set_yticks((0.5,1,2,5,10,20,50,100))
  ax1.set_yticklabels(('0.5','1','2','5','10','20','50','100'))
  ax1.set_xticks((1,5,10,60))
  ax1.set_xticklabels(('1','5','10','60'))

  grid()

def datesplit(filename):
#  returns an array index that can be used a cut an output file in desired dateranges
  time = pf.getdata(filename, 'imagelist')['TMID']
  nights_used = [time[0]]
  for i in range (1,len(time)):
    shift = time[i] - time[i-1]
    if shift > 0.5:
      nights_used += [time[i]]

  nights_used += [1e9]

  nights_used = array(nights_used)

  dateclip = []
  for i in range(len(nights_used)-1):
    dateclip += [nights_used[i:i+2]]
  dateclip = array(dateclip)

  return dateclip

def binning(series,bin):

# bins a time series to the level specified by 'bin'

  bins  = floor(len(series[0,:]) / bin)

  binned = []

  length = len(series[:,0])

  binned = np.zeros((length,bins))

  for i in np.arange(0,length):
    for x in np.arange(0,bins):
      place = x*bin

      summ = 0

      for y in range(0,bin):
        summ += series[i,place+y]

      binned[i,x] = summ/bin 

  return binned

def fitnoise(x,N,data,error):
  noise = noisemodel(x,N)
  return (noise - data)/error

def noisemodel(x,N):

  white = x[0]
  red = x[1]

  curve = ((white*N**-0.5)**2.0 + red**2.0)**0.5

  return curve

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('filename')
  parser.add_argument('-o', '--output', help='Save to output file',
                      required=False)
  main(parser.parse_args())