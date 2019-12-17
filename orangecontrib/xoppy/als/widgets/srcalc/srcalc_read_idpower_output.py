import numpy
from srxraylib.plot.gol import plot_image, set_qt

set_qt()

filename = "D_IDPower.TXT"

a = numpy.loadtxt(filename,skiprows=5)
f = open(filename,'r')
line = f.readlines()
f.close()



print(a.shape,42*42)

npx = int(line[0])
xps = float(line[1])
npy = int(line[2])
yps = float(line[3])
nMirr = int(line[4])

print("Nx ny nMir",npy,npx,nMirr)

SOURCE = numpy.zeros((npx,npy))
MIRROR1 = numpy.zeros((npx,npy))

ii = -1
for ix in range(npx):
    for iy in range(npy):
        ii += 1
        SOURCE[ix,iy] = a[ii,0]
        MIRROR1[ix, iy] = a[ii, 1]

plot_image(SOURCE,title="Source nx: %d, ny: %d"%(npx,npy),show=True)

hh = numpy.linspace(0,xps,npx)
vv = numpy.linspace(0,yps,npy)
int_mesh = SOURCE

hhh = numpy.concatenate((-hh[::-1], hh[1:]))
vvv = numpy.concatenate((-vv[::-1], vv[1:]))

tmp = numpy.concatenate((int_mesh[::-1, :], int_mesh[1:, :]), axis=0)
int_mesh2 = numpy.concatenate((tmp[:, ::-1], tmp[:, 1:]), axis=1)
totPower = int_mesh2.sum() * (hh[1] - hh[0]) * (vv[1] - vv[0])

plot_image(int_mesh2,hhh,vvv,title="Source Tot Power %f, pow density: %f"%(totPower,int_mesh2.max()),show=True)

# plot_image(MIRROR1,title="Mirror 1",show=True)

"""
	do 75 IB=1,nxp
		do 75 IC=1,nyp
			write(3,2300)(PD(ii,IB,IC),ii=0,nMir)
"""