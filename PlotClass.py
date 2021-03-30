#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np

class Plots:
    def __init__(plot, name):
        plot.name=plot
        rootname = 'dorado'
    class _SpicyFourier(Figure):
        rootname = 'dorado'
    def __init__(self, *args, figtitle='Spicy Fourier', **kwargs):
    
        super().__init__(*args, **kwargs)
        self.text(0.5, 0.95, figtitle, ha='center')
        fig = plt.figure(FigureClass=Fourier, figtitle='Spicy Fourier')
        plt.style.use('dark_background')
        plt.ylabel("Amplitude")
        plt.xlabel("Time [s]")
        plt.plot( color="gold")
        ax = fig.subplots()
        ax.plot([1, 2])

    class _Fourier(Figure):
        rootname = 'dorado'
    def __init__(self, *args, figtitle='Fourier', **kwargs):
    
        super().__init__(*args, **kwargs)
        self.text(0.5, 0.95, figtitle, ha='center')
        fig = plt.figure(FigureClass=Fourier, figtitle=' Fourier')
        plt.style.use('bmh')
        plt.ylabel("Amplitude")
        plt.xlabel("Time [s]")
        plt.plot
        ax = fig.subplots()
        ax.plot([1, 2])

    class _Plotter(object):
        def __init__(self, xval=None, yval=None):
       # xval= = np.linspace(0, 0.5, 500)
        #yval= = np.sin(40 * 2 * np.pi * t) + 0.5 * np.sin(90 * 2 * np.pi * t)
        plt.style.use('dark_background')

        def plotthing(self):
        f = plt.figure()
        sp = f.add_subplot(111)
        sp.plot(self.xval, self.yval, 'o-')
        return f
    
        #t = np.linspace(0, 0.5, 500)
        #s = np.sin(40 * 2 * np.pi * t) + 0.5 * np.sin(90 * 2 * np.pi * t)
        plt.style.use('dark_background')

        plt.title('Spicy Fourier')
        plt.ylabel("Amplitude")
        plt.xlabel("Time [s]")
        plt.plot(t, s, color="gold")
        plt.show()
        
    class _LightCurvesSpicy
        def __init__(self, x=None, y1=None, y2=None, y3=None):
        plt.rcParams.update(plt.rcParamsDefault)
        plt.style.use('dark_background')
        fig = plt.figure()
        ax = fig.add_subplot(111)
        #x = np.linspace(0, 4*np.pi, 200)
        #y1 = np.sin(x)
        #y2 = 1.5*np.sin(x)
        #y3 = 2*np.sin(x)
        # Plot data
        ax.plot(x, y1, label='A = 1', color="gold")#color="darkviolet")
        ax.plot(x, y2, label='A = 1.5',color="darkorange" )#color="red"
        ax.plot(x, y3, label='A = 2',color="orangered")#color="cyan"
        ax.legend(loc=(1.02, 0.65))
        ax.set_xlabel('x-axis')
        ax.set_ylabel('y-axis')
        ax.set_title("Spicy")
        plt.grid()
        # Save plot
        plt.show()
        
    class _LightCurves
        def __init__(self, x=None, y1=None, y2=None, y3=None):
        plt.rcParams.update(plt.rcParamsDefault)
        plt.style.use('bmh')
        fig = plt.figure()
        ax = fig.add_subplot(111)
        #x = np.linspace(0, 4*np.pi, 200)
        #y1 = np.sin(x)
        #y2 = 1.5*np.sin(x)
        #y3 = 2*np.sin(x)
        # Plot data
        ax.plot(x, y1, label='A = 1')#color="darkviolet")
        ax.plot(x, y2, label='A = 1.5')#color="red"
        ax.plot(x, y3, label='A = 2')#color="cyan"
        ax.legend(loc=(1.02, 0.65))
        ax.set_xlabel('x-axis')
        ax.set_ylabel('y-axis')
        ax.set_title("Not Spicy")
        plt.grid()
        # Save plot
        plt.show()
    
    class _SpicyScatter
        def __init__(self, x=None, y1=None, y2=None, y3=None):
        plt.rcParams.update(plt.rcParamsDefault)
        plt.style.use('dark_background')
        # Scatterplot - Color Change
        #x = np.random.randn(50)
        #y1 = np.random.randn(50)
        #y2= np.random.randn(50)
        #y3= np.random.randn(50)

# Plot
        plt.scatter(x,y1,label='A = 1', color="gold", marker='x')#color="darkviolet")
        plt.scatter(x,y2,label='A = 1.5',color="darkorange", marker='*' )#color="red")
        plt.scatter(x,y3, label='A = 2',color="orangered")#color="cyan"
        plt.rcParams.update({'figure.figsize':(10,8), 'figure.dpi':100})

# Decorate
        plt.legend(loc=(1.02, 0.65))
        plt.title('Spicy Scatter')
        plt.xlabel('x-axis')
        plt.ylabel('y-axis')
        plt.grid()
# Save plot
        plt.show()
    
    class _Scatter
        def __init__(self, x=None, y1=None, y2=None, y3=None):
        plt.rcParams.update(plt.rcParamsDefault)
        plt.style.use('bmh')
        # Scatterplot - Color Change
        #x = np.random.randn(50)
        #y1 = np.random.randn(50)
        #y2= np.random.randn(50)
        #y3= np.random.randn(50)

# Plot
        plt.scatter(x,y1,label='A = 1')#color="darkviolet")
        plt.scatter(x,y2,label='A = 1.5' )#color="red")
        plt.scatter(x,y3, label='A = 2')#color="cyan"
        plt.rcParams.update({'figure.figsize':(10,8), 'figure.dpi':100})

# Decorate
        plt.legend(loc=(1.02, 0.65))
        plt.title('Scatter')
        plt.xlabel('x-axis')
        plt.ylabel('y-axis')
        plt.grid()
# Save plot
        plt.show()

