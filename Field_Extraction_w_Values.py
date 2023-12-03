import matplotlib.pyplot as plt
import numpy as np
import os 
import scipy as scipy
import scipy.ndimage
import sys
from mpl_toolkits.axes_grid1 import make_axes_locatable
# import matplotlib.patches as patches
from scipy.interpolate import LinearNDInterpolator

def interpolate(x, y, array):
    # x = np.linspace(610, 660, 1000)
    # y = np.linspace(0, 1.0, 101)
    X, Y = np.meshgrid(x, y)
    x_interp = np.linspace(615, 655, 1000)
    y_interp = np.linspace(0.0, 1.00, 101)
    points = np.column_stack((X.ravel(), Y.ravel()))
    
    interp_func = LinearNDInterpolator(points, array.ravel())
    
    X_interp, Y_interp = np.meshgrid(x_interp, y_interp)
    points_interp = np.column_stack((X_interp.ravel(), Y_interp.ravel()))
    Z_interp = interp_func(points_interp)
    
    # Reshape Z_interp back to the 2D shape
    Z_interp = Z_interp.reshape(X_interp.shape)
    
    return(X_interp, Y_interp, Z_interp)

root = os.getcwd()

################################## PARAMETERS ##############################################

period = 396
gratingthickness = 127
dutycycle = 0.6
ridgewidth = period * dutycycle
gratingindex = 1.63
sio2index = 1.49
coverindex = 1.33
aloxindex = 1.6
loss = 0.0
film_thickness = 450
ITOwg = 100
aloxthickness = 50

nharm = 30
TEamp = 1
TMamp = 0

zmin = -500 
zmax = 700 - gratingthickness
xmin = -period
xmax = period
xstep = 1
zstep = 1

lambda1 = 591.5

################################## DATA READ IN / SIMULATE ##############################################

simulate = True

if simulate:
        args = (f'period = {period}; gratingthickness = {gratingthickness}; dutycycle = {dutycycle};'
                f'ridgewidth = {ridgewidth}; lambda1 = {lambda1}; zmin = {zmin}; nharm = {nharm};'
                f'gratingindex = {gratingindex}; coverindex = {coverindex}; sio2index = {sio2index}; TEamp = {TEamp}; TMamp = {TMamp};'
                f'zmax = {zmax}; xmin = {xmin}; xmax = {xmax}; xstep = {xstep}; zstep = {zstep}; ITOwg = {ITOwg};'
                f'aloxthickness = {aloxthickness}; aloxindex = {aloxindex};')

        lua_script = 'Field_Extraction.lua'
        os.system(f'S4 -a "{args}" {lua_script}')

datafile = 'field.csv'
data = np.genfromtxt(datafile, delimiter=',')

datafile_eps = 'eps_r.csv'
data2 = np.genfromtxt(datafile_eps, delimiter=',')

################################## ANALYSIS ##############################################

x = np.arange(xmin, xmax+1, xstep)
z = np.arange(zmin, zmax+1, zstep)

flipped_data = np.flipud(data)
slice = flipped_data[200:202, 0:]
sum = np.sum(np.abs(slice))

subarray_height, subarray_width = slice.shape
yheight = -100

mask_ITO = data2 > sio2index**2
mask_alox = (sio2index**2 < data2) & (data2 < 4)
mask_sub = data2 == sio2index**2
mask_cover = data2 < sio2index**2

summed_ITO = np.sum(mask_ITO)
summed_alox = np.sum(mask_alox)
summed_sub = np.sum(mask_sub)
summed_cover = np.sum(mask_cover)

data_field_ITO = (data * mask_ITO)
data_field_alox = (data * mask_alox)
data_field_sub = (data * mask_sub)
data_field_cover = (data * mask_cover)

data_ITO = (np.sum(np.abs(data_field_ITO)) / np.sum(np.abs(data)) )
data_alox = (np.sum(np.abs(data_field_alox)) / np.sum(np.abs(data)) )
data_sub = (np.sum(np.abs(data_field_sub))  / np.sum(np.abs(data)) ) 
data_cover = (np.sum(np.abs(data_field_cover)) / np.sum(np.abs(data)) )

################################### PLOTTING ##############################################

fig, ax = plt.subplots(figsize=[10,7])
mycmap1 = plt.get_cmap('gnuplot2')
k = ax.pcolor(x, z, np.flipud(data*(1)), cmap=mycmap1)
ax.contour(x, z, np.flipud(mask_ITO), colors='k', linewidths=2)
ax.contour(x, z, np.flipud(mask_alox), colors='k', linewidths=2)
ax.set_xlabel('X Position (nm)', fontsize=28, fontweight='bold')
ax.set_ylabel('Z Position (nm)', fontsize=28, fontweight='bold')
ax.tick_params(axis='both', labelsize=25)

# rect = patches.Rectangle(
#     (-period, yheight),  # (x, y) position of the bottom-left corner of the box
#     subarray_width,  # Width of the box
#     subarray_height,  # Height of the box
#     linewidth=1,
#     edgecolor='r',  # Red color for the box
#     facecolor='none'  # No fill color
# )
# ax.add_patch(rect)

field_label_TE = r'$\bf{E_{y}} (a.u.)$' 
field_label_TM = r'$\bf{E_{z}} (a.u.)$' 
glass_label = r'$\bf{SiO_{2}}$'

plt.xlim([xmin, xmax])
# plt.text(0.05, 0.1, glass_label, fontsize=35, fontweight='bold', color='w', transform=ax.transAxes)
# plt.text(0.05, 0.46, 'ITO', fontsize=35, fontweight='bold', color='w', transform=ax.transAxes)
# plt.text(0.05, 0.8, 'Air', fontsize=35, fontweight='bold', color='w', transform=ax.transAxes)
# plt.text(0.7, 0.1, f'{np.round(sum,2)}', fontsize=28, fontweight='bold', color='w', transform=ax.transAxes)

cbar = fig.colorbar(k, pad=0.04)
cbar.set_ticks(ticks=[np.amax(data), 0, np.amin(data)], 
                 labels=[f'{int(np.amax(data))}', '0', 
                         f'{int(np.amin(data))}'], 
                         fontsize=28)
plt.tight_layout()

if TEamp == 1:
        cbar.set_label(field_label_TE, size=28)
        plt.savefig(f'TE_{lambda1}.png')
else:
        cbar.set_label(field_label_TM, size=28)
        plt.savefig(f'TM_{lambda1}.png')