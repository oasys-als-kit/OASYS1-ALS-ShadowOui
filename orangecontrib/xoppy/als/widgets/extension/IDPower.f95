	PROGRAM IDPower
!	RR it can also calculate the power transmitted through a foil
!	in this case:	miType(1) should be 8. 
!					anM(1)	set to the thickness of the foil in Nanometers
!	Dimensions of Matrices and vectors controlled by
!	maxMirr			! Maximum number of mirrors
!	maxPoO!			! Max. # points in OC Files
!	mDim			! Dimension matrices maxMirror+1

	
	implicit real*8 (a-H,k,L,O-Z)
	common/und/itype,n,k3,kx,ky,lamdar,len,phase
	common/angle/sinphi(400),cosphi(400),dphi,dAlpha,nAlpha,nphi1,nphi2
	common/beam/gamma,cur,sigx2,sigy2,sigu,sigv,fu,fv,gsiguv,nSig
	common/const/apmin,apmax,mode,icalc,iharm,iAng
	common/screen/d,xpmin,dxp,ypmin,dyp,fac,nyp,nxp
	common/scale/emin,de,ne,ne1,ne2
	common/calc/bri1(201,201),bri2(201,201),bri3(201,201),bri0(201,201)
	common/slit/xps,yps
!	Definitions for the reflectivity
	integer, parameter :: maxMirr=6			! Maximum number of mirrors
	real*8 anM(maxMirr)						! Mirror angles
	real*8 thic(maxMirr)					! Filter and crystal thickness
	integer miType(maxMirr), resu					! 8 is a filter, 9 is a crystal
	character*10 com(maxMirr)				! Mirror Coating
	character*1 iPom(maxMirr)				! s,p or f
	integer nMir							! Actual number of mirrors
	character*10240 root1


	data pi/3.141592653589/,IDEBUG/0/
!
!	 ***************************************************************
!	                   IDPower  -  VERSION 2.1		R. Reininger
!	                   
!	a program to calculate ID power absorbed on optical elements
!	
!	   Based on: URGENT by R.P. WALKER & B.DIVIACCO
!	
!	 ****************************************************************
!	


	!root1='./reflect/'

	open (unit=1, file="IDPower.TXT",STATUS='unknown')
	open (unit=2, file='O_IDPower.TXT',STATUS='unknown')
	open (unit=3, file='D_IDPower.TXT',STATUS='unknown')

    READ(1,'(a)') root1
	READ(1,*) ky
	READ(1,*) energy
	READ(1,*) cur
	READ(1,*) sigmx
	READ(1,*) sigy
	READ(1,*) sigx1
	READ(1,*) sigy1
	READ(1,*) n	
	READ(1,*) period
	READ(1,*) d
	READ(1,*) nMir

	READ(1,*) anM(1)
	READ(1,*) miType(1)
	READ(1,*) thic(1)
	READ(1,*) com(1)
	READ(1,*) iPom(1)
	READ(1,*) anM(2)
	READ(1,*) miType(2)
	READ(1,*) thic(2)
	READ(1,*) com(2)
	READ(1,*) iPom(2)
	READ(1,*) anM(3)
	READ(1,*) miType(3)
	READ(1,*) thic(3)
	READ(1,*) com(3)
	READ(1,*) iPom(3)
	READ(1,*) anM(4)
	READ(1,*) miType(4)
	READ(1,*) thic(4)
	READ(1,*) com(4)
	READ(1,*) iPom(4)
	READ(1,*) anM(5)
	READ(1,*) miType(5)
	READ(1,*) thic(5)
	READ(1,*) com(5)
	READ(1,*) iPom(5)
	READ(1,*) anM(6)
	READ(1,*) miType(6)
	READ(1,*) thic(6)
	READ(1,*) com(6)
	READ(1,*) iPom(6)
	READ(1,*) xps
	READ(1,*) yps
	READ(1,*) nxp
	READ(1,*) nyp
	READ(1,*) mode
	READ(1,*) iharm
	READ(1,*) icalc
	READ(1,*) itype
	READ(1,*) nSig
	READ(1,*) nPhi
	READ(1,*) nAlpha
	READ(1,*) dAlpha
	READ(1,*) nOmega
	READ(1,*) dOmega
	READ(1,*) xpc
	READ(1,*) ypc
	READ(1,*) ne
	READ(1,*) emin
	READ(1,*) emax
	READ(1,*) kx
	READ(1,*) phase
	Close (1)




	print *, "ky = ", ky
	print *, "energy = ", energy
	print *, "cur = ", cur
	print *, "sigmx = ", sigmx
	print *, "sigy = ", sigy
	print *, "sigx1 = ", sigx1
	print *, "sigy1 = ", sigy1
	print *, "n	 = ", n
	print *, "period = ", period
	print *, "d = ", d
	print *, "nMir = ", nMir
	print *, "anM(1) = ", anM(1)
	print *, "miType(1) = ", miType(1)
	print *, "thic(1) = ", thic(1)
	print *, "com(1) = ", com(1)
	print *, "iPom(1) = ", iPom(1)
	print *, "anM(2) = ", anM(2)
	print *, "miType(2) = ", miType(2)
	print *, "thic(2) = ", thic(2)
	print *, "com(2) = ", com(2)
	print *, "iPom(2) = ", iPom(2)
	print *, "anM(3) = ", anM(3)
	print *, "miType(3) = ", miType(3)
	print *, "thic(3) = ", thic(3)
	print *, "com(3) = ", com(3)
	print *, "iPom(3) = ", iPom(3)
	print *, "anM(4) = ", anM(4)
	print *, "miType(4) = ", miType(4)
	print *, "thic(4) = ", thic(4)
	print *, "com(4) = ", com(4)
	print *, "iPom(4) = ", iPom(4)
	print *, "anM(5) = ", anM(5)
	print *, "miType(5) = ", miType(5)
	print *, "thic(5) = ", thic(5)
	print *, "com(5) = ", com(5)
	print *, "iPom(5) = ", iPom(5)
	print *, "anM(6) = ", anM(6)
	print *, "miType(6) = ", miType(6)
	print *, "thic(6) = ", thic(6)
	print *, "com(6) = ", com(6)
	print *, "iPom(6) = ", iPom(6)
	print *, "xps = ", xps
	print *, "yps = ", yps
	print *, "nxp = ", nxp
	print *, "nyp = ", nyp
	print *, "mode = ", mode
	print *, "iharm = ", iharm
	print *, "icalc = ", icalc
	print *, "itype = ", itype
	print *, "nSig = ", nSig
	print *, "nPhi = ", nPhi
	print *, "nAlpha = ", nAlpha
	print *, "dAlpha = ", dAlpha
	print *, "nOmega = ", nOmega
	print *, "dOmega = ", dOmega
	print *, "xpc = ", xpc
	print *, "ypc = ", ypc
	print *, "ne = ", ne
	print *, "emin = ", emin
	print *, "emax = ", emax
	print *, "kx = ", kx
	print *, "phase = ", phase

	call CALC_REF_S(anM,miType,com,iPom,nMir,root1,kx,thic)				!Read opt. cons. files
	write (*,*) " "
!
!	CONSTANTS
!
	if(itype.eq.2)kx=0.0
	gamma=energy/0.000511
	lamdar=period*1.0D+10/(2.0*gamma*gamma)
	K2=(kx*kx)+(ky*ky)
	k3=1.0+(K2/2.0)
	len=n*period
	LAMDA1=lamdar*k3
	E1=12398.5/LAMDA1
	pTot=0.0725*n*K2*energy*energy*cur/period
	GK=0.0
	if(kx.lt.1.0E-04.or.ky.lt.1.0E-04)then
	  k=kx+ky
	  GK=k*((k**6)+(24.*(k**4)/7.)+(4.*k*k)+(16./7.))/((1.+(k*k))**3.5)
	endif
	if(abs(kx-ky).lt.1.0E-04)then
	  k=kx
	  GK=32.0/7.0*k/(1.0+k*k)**3.0
	endif
	PD=0.1161*(energy**4)*n*k*GK*cur/period
	if(itype.eq.2)then
	  pTot=pTot*2.0
	  PD=PD*2.0
	endif
!
!	DEFAULT VALUES
!
	if(nPhi.eq.0)nPhi=20
	if(nSig.eq.0)nSig=4
	if(nAlpha.eq.0)nAlpha=15
	if(dAlpha.eq.0.0)dAlpha=2.0
	if(nOmega.eq.0)nOmega=16
	if(dOmega.eq.0.0)dOmega=2.0
	if(mode.lt.0)then
	  IDEBUG=1
	  mode=-mode
	endif
!
!	SET IRRELEVANT parameters to ZERO
!
	if(mode.eq.1.or.mode.eq.6)then
	  ne=0
	  emax=0.0
	endif
	if(mode.eq.6)emin=0.0
	if(mode.eq.6.or.icalc.eq.3)nPhi=0
	if(icalc.eq.3.or.mode.eq.5.or.(mode.eq.6.and.icalc.eq.2))nSig=0
	if(itype.eq.1.and.(mode.ne.1.or.icalc.ne.1))nAlpha=0
	if(itype.eq.2.and.icalc.eq.3)nAlpha=0
	if(itype.eq.1.and.icalc.ne.3.and.(mode.ne.1.or.icalc.ne.1)) dAlpha=0.0
	if(itype.eq.2.or.icalc.ne.1.or.mode.eq.1.or.mode.eq.6)then
	  nOmega=0
	  dOmega=0.0
	endif
!
!	PRINT INPUT data ETC.
!
	write(6,500)
	if(itype.eq.1)write(6,1000)period,kx,ky,n
	if(itype.eq.2)write(6,1001)period,ky,phase,n
	write(6,1200)energy,cur,sigmx,sigy,sigx1,sigy1
	write(6,1300)d,xps,yps,2*nxp+1,2*nyp+1
	write(6,1400)iharm, nSig
	write(6,1600)E1,7.12*energy*energy*ky/period, abs(-E1*iharm)
	write(6,1800)pTot,PD
	if(itype.eq.1)write(2,1000)period,kx,ky,n
	if(itype.eq.2)write(2,1001)period,ky,phase,n
	write(2,1200)energy,cur,sigmx,sigy,sigx1,sigy1
	write(2,1300)d,xps,yps,2*nxp+1,2*nyp+1
	write(2,1400)iharm, nSig
	write(2,1600)E1,7.12*energy*energy*ky/period, abs(-E1*iharm)
	write(2,1800)pTot,PD
	

	do ii=1,nMir
		if(miType(ii).eq.8 ) then
			write(6,1701)ii, thic(ii),iPom(ii),com(ii)
			write(2,1701)ii, thic(ii),iPom(ii),com(ii)
		else if(miType(ii).eq.9) then
			write(6,1702)ii, anM(ii), thic(ii),iPom(ii),com(ii)
			write(2,1702)ii, anM(ii), thic(ii),iPom(ii),com(ii)
		else
			write(6,1700)ii, anM(ii),iPom(ii), com(ii)
			write(2,1700)ii, anM(ii),iPom(ii),com(ii)
		endif
	enddo
	write (*,*)" "
	phase=phase*(pi/180.0)
!	
!	ANGULAR (iAng=1) or SPATIAL (iAng=0) UNITS
!	
	iAng=0
	if(d.eq.0.0)then
	  iAng=1
	  d=1.0
	endif
!	
!	ERROR CHECK 
!	
	if(itype.lt.1.or.itype.gt.2)goto 900
	if(mode.lt.1.or.mode.gt.6)goto 900
	if(icalc.lt.0.or.icalc.gt.3)goto 900
	if(mode.eq.5.and.icalc.eq.3)goto 900
	if(mode.eq.6.and.icalc.eq.3)goto 900
	if(itype.eq.2.and.(mode.eq.3.or.mode.eq.5.or.mode.eq.6))goto 900
	if(iharm.lt.-10000.or.iharm.gt.10000)goto 900
	if(nxp.lt.0.or.nxp.gt.50.or.nyp.lt.0.or.nyp.gt.50)goto 900
	if(nPhi.gt.100.or.nAlpha.gt.100)goto 900
	if(itype.eq.2.and.nPhi.gt.25)goto 900
	if(mode.ge.2.and.mode.le.5.and.emin.le.0.0)goto 900
	if(icalc.eq.1.and.mode.ne.1.and.mode.ne.6.and.itype.ne.2)then
	  if(nOmega.gt.5000)goto 900
	  if((nOmega/dOmega).lt.4.0)goto 900
	endif
	if(sigx1.eq.0.0.or.sigy1.eq.0.0)then
	  if(mode.lt.5.and.icalc.ne.3)goto 900
	  if(mode.eq.6.and.icalc.eq.1)goto 900
	endif
!	
!	ELECTRON beam
!	
	sigx2=sigmx*sigmx
	sigy2=sigy*sigy
	sigu2=((sigx1*sigx1)+(sigmx*sigmx/(d*d)))*1.0D-06
	sigv2=((sigy1*sigy1)+(sigy*sigy/(d*d)))*1.0D-06
	sigu=dsqrt(sigu2)
	sigv=dsqrt(sigv2)
	if(sigu2.ne.0.0)fu=0.5/sigu2
	if(sigv2.ne.0.0)fv=0.5/sigv2
	gsiguv=gamma*dmin1(sigu,sigv)
!	
!	ACCEPTANCE : DETERMINE MIN. and MAX. EMISSION ANGLES 
!	
	xe1=(xpc-(xps/2.0))*1.0D-03/d
	xe2=(xpc+(xps/2.0))*1.0D-03/d
	xemax=dmax1(dabs(xe1),dabs(xe2))+(nSig*sigu)
	ye1=(ypc-(yps/2.0))*1.0D-03/d
	ye2=(ypc+(yps/2.0))*1.0D-03/d
	yemax=dmax1(dabs(ye1),dabs(ye2))+(nSig*sigv)
	apmax=gamma*gamma*((xemax*xemax)+(yemax*yemax))
	if(xe1.gt.0.0.and.xe2.gt.0.0)then
	  xemin=xe1-(nSig*sigu)
	else
	  if(xe1.lt.0.0.and.xe2.lt.0.0)then
	    xemin=-xe2-(nSig*sigu)
	  else
	    xemin=0.0
	  endif
	endif
	if(xemin.lt.0.0)xemin=0.0
	if(ye1.gt.0.0.and.ye2.gt.0.0)then
	  yemin=ye1-(nSig*sigv)
	else
	  if(ye1.lt.0.0.and.ye2.lt.0.0)then
	    yemin=-ye2-(nSig*sigv)
	  else
	    yemin=0.0
	  endif
	endif
	if(yemin.lt.0.0)yemin=0.0
	apmin=gamma*gamma*((xemin*xemin)+(yemin*yemin))

	if(xpc.eq.0.0.and.ypc.eq.0.0)then
		fac=4.0
		xpmin=0.0
		ypmin=0.0
		if(nxp.gt.0)dxp=(xps/(2.0*nxp))
		if(nyp.gt.0)dyp=(yps/(2.0*nyp))
	else
		fac=1.0
		xpmin=xpc-(xps/2.0)
		ypmin=ypc-(yps/2.0)
		if(nxp.gt.0)dxp=xps/nxp
		if(nyp.gt.0)dyp=yps/nyp
	endif
	if(nxp.eq.0.or.nyp.eq.0)fac=0.0
	nxp=nxp+1
	nyp=nyp+1
!	
!	call ANALYSIS PROGRAM
!	
	call SUB5(IDEBUG)

	STOP
900	write(6,9000)
	write(2,9000)
	STOP

500	format(' ****** IDPower Version 2.1,          R. Reininger ******'//&
           ' ****** Based on Urgent by R.P.Walker & B.Diviacco ******')
	
1000	format(/' Undulator : Period = ',F7.5,' m,',2X,'kx = ',F7.4,',',2X,'ky = ',F7.4',',2X,'n = ',I3)
1001	format(/' CROSSED-UNDULATOR : period = ',F7.5,2X,'k = ',F7.4,2X,'phase = ',F6.1,2X,'n = ',I3)
1200	format(/' Electron beam : Energy = ',F6.3,' GeV,',2X,'Current = ',F5.3,&
                ' A,'/1X,'sigmx = ',F6.4,' mm,',2X,'sigy = ',F6.4,' mm,',2X, &
            'sigx1 = ',F6.4,' mrad,',2X,'sigy1 = ',F6.4,' mrad')
1300	format(/' Acceptance : d = ',F8.3,' m,',2X,'XSize = ',F7.3,' mm,',&
               2X,'YSize = ',F7.3,' mm,',2X,/1X'nxp = 'I2',',2X,'nyp = ',I2)
1400	format(/' iharm = ',I5,',',1X,'nSig = ',I3)
1500    format(1X,'nPhi = ',I3,1X,'nSig = ',I3,1X,'nAlpha = ',I3,1X,&
              'dAlpha = ',F4.1,1X,'nOmega = ',I4,1X,'dOmega = ',F4.1)
1600	format(/' E1 = ',F9.3,' eV,',2X,' Ec= ', F11.2, ' eV,',  &
                '  Highest harmonic=',F11.2,' eV'/)
1700    format(' Mirror ', I1,'   angle = ',G9.4,7x,'Pol = ',A2,5x 'Coating = ',A9)
1701    format(' Filter ', I1,' thick.(nm)= ',G12.5,1x,'Pol = ',A2,5x 'Coating = ',A9)
1702    format(' Crystal ', I1,' angle = ',G9.4,7x, 'thick.(nm)=',G12.5,1x, 'Pol = ',A2,5x 'Coating = ',A9)
1800	format(1X,'Total Power = ',F9.3,' W,',2X,'Power Density = 'F10.3,' W/mrad**2'/)
9000	format(//' *** INVALID INPUT parameters ***')
	Close (2)
	Close (3)

	end
! ***************************************************************C
!	-----------------------
	SUBROUTINE SUB5(IDEBUG)
!	-----------------------
	implicit real*8 (a-H,k,L,O-Z)
	common/und/itype,n,k3,kx,ky,lamdar,len,phase
	common/angle/sinphi(400),cosphi(400),dphi,dAlpha,nAlpha,nphi1,nphi2
	common/beam/gamma,cur,sigx2,sigy2,sigu,sigv,fu,fv,gsiguv,nSig
	common/const/apmin,apmax,mode,icalc,iharm,iAng
	common/screen/d,xpmin,dxp,ypmin,dyp,fac,nyp,nxp
	common/scale/emin,de,ne,ne1,ne2
	common/calc/bri1(0:200,0:200),bri2(0:200,0:200),bri3(201,201),bri0(201,201)
	common/slit/xps,yps

	integer, parameter :: maxMirr=6			! Maximum number of mirrors
	integer, parameter :: maxPoOC=1500		! Max. # points in OC Files
	real*8 eRef(maxMirr,maxPoOC)			! Matrix to store energies corresponding to  ref 
	real*8 ref(maxMirr,maxPoOC)				! Matrix to store reflectivities
	integer nRef(maxMirr)					! Number of points in eRef and ref
	integer	nMir							! Used number of mirrors
	common/reflectivities/eRef,ref,nRef,nMir

	integer, parameter :: mDim=maxMirr+1	! Dimension power matrices 
	real*8 PD(0:mDim,51,51),spec1(0:mDim),spec2(0:mDim),pTot(0:mDim)
	real*8 pDTot(0:mDim),DELTAP(0:mDim),deltaF(0:mDim), pToti(0:mDim)
	real*8 XPMM(51),YPMM(51)
	real*8 refl(maxMirr)

	data pi/3.141592653589/
	F4=1.8095D-14*n*n*(gamma**4)*cur/(len*d*d)
	F6=4.55D+10*n*gamma*gamma*cur/(d*d)
	if(icalc.eq.1)then
	  F5=F4/(2.0*pi*sigu*sigv)
	  F7=F6/(2.0*pi*sigu*sigv)
	endif
	ARGMAX=nSig*nSig/2.0
!	
!	POWER and TOTAL FLUX DENSITY DISTRIBUTION INTEGRATED OVER ACCEPTANCE 
!	mode  = 6
!	icalc = 1 - FINITE EMITTANCE
!	      = 2 - ZERO EMITTANCE
!	
	write(6,*) "*****************************************************"
	write(6,*) "   Igor will resume after this ends, please wait."
	write(6,*) "*****************************************************"
	write(6,*) " "
	write(6,*) "Calculating harmonic #:"

	do 10 IB=1,nxp
		do 10 IC=1,nyp
			do 10 IDM=0,nMir
				PD(IDM,IB,IC)=0.0
10	continue
	if(fac.eq.1.0)then
	  IB0=(nxp+1)/2
	  IC0=(nyp+1)/2
	else
	  IB0=1
	  IC0=1
	endif
	do ii=0,nMir
		pTot(ii)=0.0
		pDTot(ii)=0.0
	enddo
	ICOUNT=0
	if(iharm.gt.0)then
	  I=iharm-1
	else
	  I=0
	endif
	xemax=dabs(xpmin+((nxp-1)*dxp))
	if(dabs(xpmin).gt.xemax)xemax=dabs(xpmin)
	xemax=xemax/(1000.0*d)
	dxe=sigu
	nxe=(xemax/dxe)+1+nSig
	yemax=dabs(ypmin+((nyp-1)*dyp))
	if(dabs(ypmin).gt.yemax)yemax=dabs(ypmin)
	yemax=yemax/(1000.0*d)
	dye=sigv
	nye=(yemax/dye)+1+nSig
	if(nxe.gt.200.or.nye.gt.200)goto 999	!RR was 200
!	
!	VARY HARMONIC NUMBER
!	
20	I=I+1

	if(iharm.gt.0.or.IDEBUG.eq.1)then
	  write(6,1000)I
	endif
	ICOUNT=ICOUNT+1
	do ii=0,nMir
		pToti(ii)=0.0
	enddo
!	
!	CALCULATE POWER DENSITY function FOR GIVEN I
!	     
	if(icalc.eq.1)call PDF(dxe,dye,nxe,nye,I)	!Non zero emittance
!	
!	VARY POSITION in ACCEPTANCE
!	
	do 200 IB=1,nxp
		W1=1.0
		if(IB.eq.1.or.IB.eq.nxp)W1=0.5
		XPMM(IB)=xpmin+((IB-1)*dxp)
		xp=XPMM(IB)/1000.0
		do 200 IC	=1,nyp
			W2=1.0
			if(IC.eq.1.or.IC.eq.nyp)W2=0.5
			YPMM(IC)=ypmin+((IC-1)*dyp)
			YP=YPMM(IC)/1000.0
			alp2=gamma*gamma*((xp*xp)+(YP*YP))/(d*d)
			LAMDA=lamdar*(k3+alp2)/I
			E=12398.5/LAMDA
!	   
!	ADD THE CONTRIBUTION OF THE GIVEN HARMONIC 
!	TO THE POWER DENSITY AT THE GIVEN POSITION
!	BY DIRECT CALCULATION (icalc=2) or INCLUDING ELECTRON beam 
!	       EMITTANCE (icalc=1)
!	
	  		sump=0.0
	  		do 64 id=-nxe,nxe
	  			wx=1.0
	  			if(id.eq.-nxe.or.id.eq.nxe)wx=0.5
	  			xe1=id*dxe
	  			u=(xp/d)-xe1
	  			do 64 ie=-nye,nye
	  				wy=1.0
	  				if(ie.eq.-nye.or.ie.eq.nye)wy=0.5
	  				ye1=ie*dye
	  				v=(YP/d)-ye1
	  				arg=(u*u*fu)+(v*v*fv)
	  				if(arg.gt.ARGMAX)goto 64
	  				p=dexp(-arg)
	  				sump=sump+(wx*wy*bri1(IABS(id),IABS(ie))*p)
64	  		continue
	  		DELTAP(0)=F5*sump*dxe*dye
			call reflec(E,refl, nMir)
			do ii=1,nMir
			  DELTAP(ii)=refl(ii)*DELTAP(ii-1)
			enddo
!	
			do ii=0,nMir
			  PD(ii,IB,IC)=PD(ii,IB,IC)+DELTAP(ii)
			  pToti(ii)=pToti(ii)+(W1*W2*DELTAP(ii))
			enddo
			if(DELTAP(0).gt.(0.005*PD(0,IB,IC)))ICOUNT=0
			if(IB.eq.IB0.and.IC.eq.IC0)then
				do ii=0,nMir
		   		 spec1(ii)=DELTAP(ii)
		 		enddo
			endif

200	continue
	do ii=0,nMir
	  spec2(ii)=fac*pToti(ii)*dxp*dyp
	  pDTot(ii)=pDTot(ii)+spec1(ii)
	  pTot(ii)=pTot(ii)+spec2(ii)
	enddo
	if(spec2(0).gt.(0.005*pTot(0)))ICOUNT=0
!	
!	INCLUDE HIGHER HARMONICS ?
!	
	if(iharm.gt.0)goto 74
	if(iharm.eq.0.and.ICOUNT.lt.2)goto 20
	if(iharm.lt.0.and.I.lt.-iharm)goto 20
74	IMAX=I
!
    write(3,*) nxp
    write(3,*) xps
    write(3,*) nyp
    write(3,*) yps
    write(3,*) nMir
	do 75 IB=1,nxp
		do 75 IC=1,nyp
			write(3,2300)(PD(ii,IB,IC),ii=0,nMir)
75	continue
!	
!	PRINT POWER DENSITY and INTEGRATED POWER FOR EACH HARMONIC 
!	
	E1=12398.5/(lamdar*k3)
	do 100 I=1,IMAX
		EI=E1*I
100	continue
	ii=0
	if(iharm .lt. 0) write(2,2000) pTot(ii), IMAX
	if(iharm .ge. 0) write(2,2001) pTot(ii), iharm
	write (2,4700)
	do ii=1,nMir
		write(2,5000) ii, pTot(ii),pTot(ii-1)-pTot(ii)
	enddo

101   continue

	return
999	write(6,9999)
	write(2,9999)
	STOP
	
!1000 	format(CHAR( 0 ),1X,'ANGULAR DISTRIBUTION - HARMONIC ',I3, 1X,$)
1000 	format(I5, 7X,$)
1100	format(/2X,'x (MM)',4X,'Y (MM)',5X,'E (EV)',3X,'POWER DENSITY',7X/)
1300	format(1X,F8.3,2X,F8.3,2X,F9.3,2X,E13.6,2X,E13.6)
2000 	format(/1X, G10.5, ' W emitted on: harmonics 1 to ',I4)
2001 	format(/1X, G10.5, ' W emitted on: harmonics ',I4)
2100	format(/1X,' p.d. SO   p.d. M1   p.d. M2   p.d. M3   p.d. M4   p.d. M5'/)
2300	format(1X,7(1X,E13.6E3))
4700    format(/1X,'              Pow. ref(W)    Pow. abs.(W)' )
5000	format(1X,'Mirror ',I1, 2(5x,F11.4))
5500	format('   FLUX 0       FLUX 1       FLUX 2       FLUX 3      FLUX 4       FLUX 5      ')
9999	format(/' *** ERROR in SUB 5 : ARRAY SIZE EXCEEDED ***')
	end
!

! ***************************************************************
	SUBROUTINE reflec(energy,outpu,nMir)
!	This is a subroutine needed in SUB5
!	It will interpolate at energy the reflectivities of mirror nMir based on
!	the values stored in the matrices eRef and ref. 
!	The result is returned in the vector outpu

	real *8 energy,outpu(nMir)

	integer, parameter :: maxMirr=6			! Maximum number of mirrors
	integer, parameter :: maxPoOC=1500		! Max. # points in OC Files
	real*8 eRef(maxMirr,maxPoOC)			! Matrix to store energies corresponding to  ref 
	real*8 ref(maxMirr,maxPoOC)				! Matrix to store reflectivities
	integer nRef(maxMirr)					! Number of points in eRef and ref
	integer	nMir1							! Used number of mirrors
	common/reflectivities/eRef,ref,nRef, nMir1

	do j=1,nMir
	  call HUNT(eRef,nRef(j),energy,jlo,j,maxMirr )
	  outpu(j) = (energy*(ref(j,jlo)-ref(j,jlo+1)) +(eRef(j,jlo)*ref(j,jlo+1)-&
			eRef(j,jlo+1)*ref(j,jlo)))/(eRef(j,jlo)-eRef(j,jlo+1))

	enddo
	return
	end		
	
! ***************************************************************
      SUBROUTINE HUNT(xx,n,x,jlo,in,maxMirr)
!	Subroutine from Numerical Recipes to find in and ordered table.
	real*8 xx(maxMirr,n),x
      LOGICAL ascnd
      ascnd=xx(in,n).gt.xx(in,1)
      if(jlo.le.0.or.jlo.gt.n)then
        jlo=0
        jhi=n+1
        goto 3
      endif
      inc=1
      if(x.ge.xx(in,jlo).eqv.ascnd)then
1       jhi=jlo+inc
        if(jhi.gt.n)then
          jhi=n+1
        else if(x.ge.xx(in,jhi).eqv.ascnd)then
          jlo=jhi
          inc=inc+inc
          goto 1
        endif
      else
        jhi=jlo
2       jlo=jhi-inc
        if(jlo.lt.1)then
          jlo=0
        else if(x.lt.xx(in,jlo).eqv.ascnd)then
          jhi=jlo
          inc=inc+inc
          goto 2
        endif
      endif
3     if(jhi-jlo.eq.1)return
      jm=(jhi+jlo)/2
      if(x.gt.xx(in,jm).eqv.ascnd)then
        jlo=jm
      else
        jhi=jm
      endif
      goto 3
      end

!	 ***************************************************************

	SUBROUTINE CALC_REF_S(anM,miType,com,iPom,nMir,root,akx,th)
!	It will create the reflectivities tables.

	implicit none
	Integer nMir
	real *8 anM(nMir), th(nMir)						! Mirror angles
	character*10 com(nMir)					! Mirror coatings
	character*1 iPom(nMir)					! Polarization or filter
	integer miType(nMir)
	character *10240 root, root_D				! File names of OC files

	integer, parameter :: maxMirr=6			! Maximum number of mirrors
	integer, parameter :: maxPoOC=1500		! Max. # points in OC Files
	real*8 eRef(maxMirr,maxPoOC)			! Matrix to store energies corresponding to  ref 
	real*8 ref(maxMirr,maxPoOC)				! Matrix to store reflectivities
	integer nRef(maxMirr)					! Number of points in eRef and ref
	integer	nnMir,j							! Used number of mirrors. Here its loaded in common
	integer iblank
	common/reflectivities/eRef,ref,nRef,nnMir

	real*8 stheta,ctheta,sttheta, sTheta2
	real*8 n,k,toDeg,akx,pi
	integer i, ipos

	nnMir=nMir
	pi=3.141592653589
	toDeg=pi/180.
	ipos=index(root,'  ')

	do j=1,nMir
	  ! root_D=root(:ipos-1)//com(j)
	  root_D=root(1:iblank(root))//com(j)
	  stheta = sin(anM(j)* toDeg)
	  ctheta = cos(anM(j)* toDeg)
	  sTheta2 = stheta*stheta
	  sttheta = stheta2/ctheta
	  print*,">>>>>>>>>>>>>>>>>>>>>> opening file ",root_D
	  print*,">>>>>>>>>>>>>>>>>>>>>> directory **"//root(1:iblank(root_D))//"**"
	  print*,">>>>>>>>>>>>>>>>>>>>>> file ",com(j)
	  OPEN (20,FILE=root_D,STATUS='OLD')
	    do I=1,maxPoOC
	      READ (20,*,end=300) eRef(j,I), n, k
		  n=1.-n
		  if (miType(j).eq.8 .or.miType(j).eq.9) then
			call Crystal(eref(j,I),n,k,ctheta,stheta2,&
                 iPom(j),ref(j,i),akx,th(j))
		  else  if ((iPom(j).ne.'F').or.(iPom(j).ne.'f')) then
	       call CALC_R(n,k,stheta,ctheta,sttheta,iPom(j),ref(j,I),akx)
		  endif
	    enddo
300	  nRef(j)=I-1
	  CLOSE(20)
	enddo
	return
	end		
	
!	 ***************************************************************
	SUBROUTINE CALC_R(n,k,stheta,ctheta,sttheta,iPom,r,akx)
!	This subroutine performs the actual reflectivity calculation
!	akx means whe have p pol in the ID
	real *8 n,k,stheta,ctheta,sttheta,r,akx
	character*1 iPom
	real *8 nks1, nks2, a, b2
	nks2 = n**2 - k**2 - stheta**2
	nks1 = sqrt(nks2**2 + (2*n*k)**2)
	a = sqrt((nks1 + nks2)/2)
	b2 = (nks1 - nks2)/2
	r = ((a-ctheta)**2 + b2)/((a+ctheta)**2 + b2)
	if (akx.ne.0.) then
		r = r*(1+((a-sttheta)**2 + b2)/((a+sttheta)**2 + b2))/2
		return
	endif
	if ((iPom.eq.'S').or.(iPom.eq.'s')) return
	if ((iPom.eq.'P').or.(iPom.eq.'p')) then
		r = r*((a-sttheta)**2 + b2)/((a+sttheta)**2 + b2)
		return
	endif


	end
!	 ***************************************************************
	SUBROUTINE Crystal(en,n,k,ctheta1,stheta2,iPom,r,akx,th)
	Implicit none
!	This subroutine performs the actual reflectivity calculation.
	real *8 en,n,k,stheta,ctheta1,stheta2,r,akx,th
	character*1 iPom
	real *8 nks1, nks2, a, b2
	real*8 ctheta3
	complex*8 n2,ctheta2,betaexp, betaexp2, ii
	complex*8 r12s,r23s,t12s,t23s,ttots,rtots, rtotp
	complex*8 r12p,r23p,t12p,t23p,ttotp
	real*8 pi
	pi= 3.141592653589

	ii=cmplx(0.,1.)

	n2= cmplx(n,k)
	ctheta2=sqrt(1-stheta2/(n2*n2))
	ctheta3=ctheta1
	betaexp=exp(2*pi*(en/1239.852)*n2*th*ctheta2*ii)
	betaexp2=betaexp*betaexp
	r12S=(ctheta1-n2*ctheta2) / (ctheta1+n2*ctheta2)
	r23S=(n2*ctheta2-ctheta3) / (n2*ctheta2+ctheta3)
	rtots=(r12S+r23S*betaexp2) / (1+r12S*r23S*betaexp2)

	t12s=(2*ctheta1) / (ctheta1+n2*ctheta2)
	t23s=(2*n2*ctheta2) / (n2*ctheta2+ctheta3)
	ttots=(t12s*t23s*betaexp) / (1+r12S*r23S*betaexp2)

	r12p=(ctheta1-ctheta2/n2) / (ctheta1+ctheta2/n2)
	r23p=(ctheta2/n2-ctheta3) / (ctheta2/n2+ctheta3)
	rtotp=(r12p+r23p*betaexp2) / (1+r12p*r23p*betaexp2)

	t12p=(2*ctheta1) / (ctheta1+ctheta2/n2)
	t23p=(2*ctheta2/n2) / (ctheta2/n2+ctheta3)
	ttotp=(t12p*t23p*betaexp) / (1+r12p*r23p*betaexp2)

	if ((iPom.eq.'S').or.(iPom.eq.'s')) then
		r=abs(ttots)
	else if ((iPom.eq.'P').or.(iPom.eq.'p')) then
		r=abs(ttotp)
	else if (akx.ne.0. .or. iPom.eq.'f') then
		r=(abs(ttots)+abs(ttotp))/2
	end if
	r=r*r
!	print *, iPom, en, n, k , r
	return

	end






!	 ***************************************************************
!	-------------------------------------
	SUBROUTINE PDF(dxe,dye,nxe,nye,I)
!	-------------------------------------
	implicit real*8 (a-H,k,L,O-Z)
	common/und/itype,n,k3,kx,ky,lamdar,len,phase
	common/beam/gamma,cur,sigx2,sigy2,sigu,sigv,fu,fv,gsiguv,nSig
	common/calc/bri1(0:200,0:200),bri2(0:200,0:200),bri3(0:200,0:200),bri0(0:200,0:200)
!	
!	SET UP ARRAY OF VALUES OF POWER and FLUX DENSITY
!	INTEGRATED OVER THE LINEWIDTH
!	
	do 15 id=0,nxe
		xe1=id*dxe
		do 15 ie=0,nye
			ye1=ie*dye
			theta=dsqrt((xe1*xe1)+(ye1*ye1))
			alp=gamma*theta
			alp2=alp*alp
			cosphi=0.0
			sinphi=1.0
			if(theta.gt.1.0D-06)then
	  			cosphi=xe1/theta
	  			sinphi=ye1/theta
			endif
			call BRIGHT(alp,cosphi,sinphi,I,s0,dum,dum,dum)
			bri1(id,ie)=s0/(k3+alp2)
			bri2(id,ie)=s0/I
			bri3(id,ie)=0.0
			bri0(id,ie)=0.0
15	continue
	return
	end
!	 ***************************************************************
!	-----------------------------
	function sinc(alp2,alp2i,r,n)
!	-----------------------------
	implicit real*8 (a-H,O-Z)
	data pi/3.141592653589/
!	
!	CALCULATE THE LINESHAPE function
!	
	sinc=1.0
	x=n*pi*(alp2-alp2i)/r
	if(dabs(x).lt.1.0D-06)return
	sinc=dsin(x)/x
	sinc=sinc*sinc
	return
	end
!	 ***************************************************************
!	----------------------------------------------------------
	SUBROUTINE BRIGHT(alpha,cosphi,sinphi,I,s0,S1,S2,S3)
!	----------------------------------------------------------
	implicit real*8 (a-H,k,L,O-Z)
	common/und/itype,n,k3,kx,ky,lamdar,len,phase
	data KMIN/0.001/
	if(I.le.0.or.alpha.lt.0.0)goto 40
	if(kx.lt.KMIN.and.ky.lt.KMIN)goto 40
	if(kx.lt.KMIN.and.ky.gt.KMIN)goto 10
	if(kx.gt.KMIN.and.ky.lt.KMIN)goto 20
	if(kx.gt.KMIN.and.ky.gt.KMIN)goto 30
10	call BRIGH1(alpha,cosphi,sinphi,ky,I,AXR,AYR,s0,S1,S2,S3)
	return
20	call BRIGH1(alpha,sinphi,-cosphi,kx,I,AXR,AYR,s0,S1,S2,S3)
	S1=-S1
	S2=-S2
	return
30	call BRIGH3(alpha,cosphi,sinphi,kx,ky,I,s0,S1,S2,S3)
	return
40	write(6,9000)
9000	format(//' *** ERROR in BRIGHT : INVALID parameters  ***')
	end

!	 ***************************************************************
!	-------------------------------------------------------
	SUBROUTINE BRIGH1(alpha,cosphi,sinphi,k,I,AXR,AYR,s0,S1,S2,S3)
!	-------------------------------------------------------
	implicit real*8 (a-H,j,k,O-Z)
	common/Jdata/jnx(10000),jny(10000),J0X,J0Y,maxx,maxy
	data nmax/20000/,tol1/1.0D-05/,tol2/1.0D-05/
!	
!	CALCULATE THE UNDULATOR RADIATION BRIGHTNESS function
!	FOR a PLANE TRAJECTORY
!	USING THE BESSEL function APPROXIMATION

!	CALCULATE VARIABLES x, Y

	a=1.0+((k*k)/2.0)+(alpha*alpha)
	x=I*2.0*k*alpha*cosphi/a
	Y=I*k*k/(4.0*a)
	if(dabs(x).lt.tol1)goto 10
!	
!	CALCULATE A0, A1 in THE GENERAL CASE
!	
	call JSET(jnx,J0X,x,tol2,maxx,nmax)
	call JSET(jny,J0Y,Y,tol2,maxy,nmax)
	call Jsum1(x,Y,sum1,sum2,I,maxx,maxy)
	A0=sum1
	A1=((2.0*I*sum1)+(4.0*sum2))/x
	goto 30
!	
!	CALCULATE A0, A1 WHEN x = 0.0
!	
10	call JSET(jny,J0Y,Y,tol2,maxy,nmax)
	if(((I+1)/2).gt.maxy)return
	if(I.eq.((I/2)*2))goto 20
	N1=(-I-1)/2
	N2=(-I+1)/2
	A0=0.0
	A1=JY(N1)+JY(N2)
	goto 30
20	n=-I/2
	A0=JY(n)
	A1=0.0
!	
!	CALCULATE STOKES parameters
!	
30	AXR=2.0*I/a*(A0*alpha*cosphi-k*A1/2.0)
	AYR=2.0*I/a*(A0*alpha*sinphi)
	s0=AXR*AXR+AYR*AYR
	S1=AXR*AXR-AYR*AYR
	S2=2.0*AXR*AYR
	S3=0.0
	return
	end
	
!	
!	 ***************************************************************
!	-----------------------------------------------------------
	SUBROUTINE BRIGH3(alpha,cosphi,sinphi,kx,ky,I,s0,S1,S2,S3)
!	-----------------------------------------------------------
	implicit real*8 (a-H,j,k,O-Z)
	integer Q
	common/Jdata/jnx(10000),jny(10000),J0X,J0Y,maxx,maxy
	data nmax/10000/,tol1/1.0D-05/,tol2/1.0D-05/
!	
!	CALCULATE THE UNDULATOR RADIATION BRIGHTNESS function
!	FOR a GENERAL ELLIPTICAL/HELICAL TRAJECTORY
!	USING THE BESSEL function APPROXIMATION
!	
	S0R =0.0
	S0I =0.0
	S1R =0.0
	S1I =0.0
	SM1R=0.0
	SM1I=0.0
!	
!	CALCULATE VARIABLES x, Y, PHI
!	
	a=1.0+((kx*kx)/2.0)+((ky*ky)/2.0)+(alpha*alpha)
	x=I*2.0*alpha*dsqrt(((kx*sinphi)**2)+((ky*cosphi)**2))/a
	Y=I*((ky*ky)-(kx*kx))/(4.0*a)
	PHI=dataN2((kx*sinphi),(ky*cosphi))
	if(x.lt.tol1.and.dabs(Y).lt.tol1)goto 30
	if(x.lt.tol1)goto 10 
	if(dabs(Y).lt.tol1)goto 20
!	
!	       SET UP BESSEL functionS in THE GENERAL CASE
!	
	call JSET(jnx,J0X,x,tol2,maxx,nmax)
	call JSET(jny,J0Y,Y,tol2,maxy,nmax)
!	
!	do THE sumS
!	
	Q=0
	call Jsum2(S0R,S0I,PHI,I,Q)
	Q=-1
	call Jsum2(SM1R,SM1I,PHI,I,Q)
	Q=1
	call Jsum2(S1R,S1I,PHI,I,Q)
	goto 40
!	
!	CALCULATE s0,S1,SM1 WHEN x = 0.0
!	
10	call JSET(jny,J0Y,Y,tol2,maxy,nmax)
	if(I.eq.((I/2)*2))goto 15
	N1=(-I-1)/2
	N2=(-I+1)/2
	S1R =JY(N1)
	SM1R=JY(N2)
	goto 40
15	n=-I/2
	S0R =JY(n)
	goto 40
!	
!	CALCULATE s0,S1,SM1 WHEN Y = 0.0
!	
20	N1=I
	N2=I+1
	N3=I-1
	call JSET(jnx,J0X,x,tol2,maxx,nmax)
	S0R = DCOS(N1*PHI)*JX(N1)
	S0I =-dsin(N1*PHI)*JX(N1)
	S1R = DCOS(N2*PHI)*JX(N2)
	S1I =-dsin(N2*PHI)*JX(N2)
	SM1R= DCOS(N3*PHI)*JX(N3)
	SM1I=-dsin(N3*PHI)*JX(N3)
	goto 40
!	
!	CALCULATE s0,S1,SM1 WHEN x = 0.0 and Y = 0.0
!	
30	if(I.eq.1)SM1R=1.0
!	
!	CALCULATE STOKES parameter
!	
40	AXR=((2.0*S0R*alpha*cosphi)-(ky*(S1R+SM1R)))*I/a
	AXI=((2.0*S0I*alpha*cosphi)-(ky*(S1I+SM1I)))*I/a
	AYR=((2.0*S0R*alpha*sinphi)+(kx*(S1I-SM1I)))*I/a
	AYI=((2.0*S0I*alpha*sinphi)-(kx*(S1R-SM1R)))*I/a
	s0=AXR*AXR+AXI*AXI+AYR*AYR+AYI*AYI
	S1=AXR*AXR+AXI*AXI-AYR*AYR-AYI*AYI
	S2=2.0*(AXR*AYR+AXI*AYI)
	S3=2.0*(AXI*AYR-AXR*AYI)
	return
	end
!	
!	 ***************************************************************
!	--------------------------------------
	SUBROUTINE Jsum1(x,Y,S1,S2,I,maxx,maxy)
!	--------------------------------------
	implicit real*8 (a-H,j,O-Z)
!	
!	CALCULATE sumS S1 and S2
!	
	S1=0.0
	if(I.le.maxx)S1=JY(0)*JX(I)
	S2=0.0
	SIGN=1.0
	do 10 n=1,maxy
	SIGN=-SIGN
	N1=(2*n)+I
	N2=(-2*n)+I
	J1=JY(n)
	J2=JX(N1)
	J3=JX(N2)
	S1=S1+(J1*(J2+(J3*SIGN)))
	S2=S2+(n*J1*(J2-(J3*SIGN)))
10	continue
	return
	end
!	 ***************************************************************C
!	------------------------------
	SUBROUTINE Jsum2(SR,SI,PHI,I,Q)
!	------------------------------
	implicit real*8 (a-H,j,k,O-Z)
	integer p,Q
	common/Jdata/jnx(10000),jny(10000),J0X,J0Y,maxx,maxy
	SR=0.0
	SI=0.0
	do 10 p=-maxy,maxy
	n=I+(2*p)+Q
	if(IABS(n).gt.maxx)goto 10
	F=JX(n)*JY(p)
	SR=SR+(DCOS(n*PHI)*F)
	SI=SI-(dsin(n*PHI)*F)
10	continue
	return
	end
!	 ***************************************************************C
!	--------------
	function JX(n)
!	--------------
	implicit real*8 (a-H,j,O-Z)
	common/Jdata/jnx(10000),jny(10000),J0X,J0Y,maxx,maxy
	JX=0.0
	if(IABS(n).gt.maxx)return
	if(n.ne.0)goto 10
	JX=J0X
	return
10	SIGN=1.0
	N1=n
	if(n.gt.0)goto 20
	N1=-n
	if(N1.ne.((N1/2)*2))SIGN=-1.0
20	JX=jnx(N1)*SIGN
	return
	end
!	
!	 ***************************************************************
!	--------------
	function JY(n)
!	--------------
	implicit real*8 (a-H,j,O-Z)
	common/Jdata/jnx(10000),jny(10000),J0X,J0Y,maxx,maxy
	JY=0.0
	if(IABS(n).gt.maxy)return
	if(n.ne.0)goto 10
	JY=J0Y
	return
10	SIGN=1.0
	N1=n
	if(n.gt.0)goto 20
	N1=-n
	if(N1.ne.((N1/2)*2))SIGN=-1.0
20	JY=jny(N1)*SIGN
	return
	end
!	
!	 ***************************************************************
!	----------------------------------------
	SUBROUTINE JSET(jnx,J0X,X0,tol,MAX,nmax)
!	----------------------------------------
	implicit real*8 (a-H,j,O-Z)
	DIMENSION jnx(1)
	data BIGNO/1.0D+10/,BIGNI/1.0D-10/
!	
!	SET UP ARRAY OF BESSEL functionS UP TO ORDER MAX
!	SUCH THAT JMAX (x) < tol and MAX > x
!	USING MILLER'S DOWNWARD RECURRENCE ALGORITHM
!	MODIFIED FORM OF NUMERICAL RECIpiES ROUTINE BESSJN
!	       NB] ARGUMENT CAN BE NEGATIVE
!	
	x=dabs(X0)
	if(x.le.0.1)then
	  M=4
	else
	  if(x.le.1.0)then
	    M=8
	  else
	    M=2*((INT(1.18*x)+13)/2)
	  endif
	endif
	if(M.gt.nmax)goto 999
!	
        TOX=2.0/x
        Isum=0
        sum=0.
        BJP=0.
        BJ=1.
	jnx(M)=1.0
        do 10 N1=M,1,-1
	n=N1-1
        BJN=N1*TOX*BJ-BJP
        BJP=BJ
        BJ=BJN
        if(dabs(BJ).gt.BIGNO)then
          BJ=BJ*BIGNI
          BJP=BJP*BIGNI
          sum=sum*BIGNI
  	  do 20 I=N1,M
          jnx(I)=jnx(I)*BIGNI
20	  continue
        endif
	if(n.ne.0)jnx(n)=BJ
        if(Isum.ne.0)sum=sum+BJ
        Isum=1-Isum
10      continue
        sum=(2.0*sum)-BJ
	J0X=BJ/sum
	SIGN=1.0
	do 30 n=1,M
	SIGN=-SIGN
        jnx(n)=jnx(n)/sum
	if(X0.lt.0.0)jnx(n)=jnx(n)*SIGN
	if(n.le.dabs(x).or.jnx(n).gt.tol)MAX=n
30	continue
	return
999	write(6,9999)
	write(2,9999)
	STOP
9999	format(//' *** OVERFLOW OF BESSEL function ARRAY ***')
        end

!C +++
!C 	integer 	function 	iblank
!C
!C	purpose		Returns the last non-white spot in the string.
!C
!C	input		a fortran character string.
!C	output		Index of the last non-white char in the string.
!C			If there are no empty spaces in the string, then
!C			the lenght is simply returned.
!C	hacker		Mumit Khan
!C ---
	function iblank (str)
    implicit real*8 (a-H,O-Z)
	character*(*) 	str
	integer 	index, ilen, iblank
!c
!c if the last character in the declared string isn't a white space, simply
!c return the length.
!c
	index = 1
	ilen = len (str)
	if (str(ilen:ilen).NE.' ') then
	    index = ilen + 1
	    goto 20
	endif
!c
 10	continue
	if (str(index:index).NE.' ') then
	    index = index + 1
	    goto 10
	endif
 20	continue
	iblank = index - 1
	return
	end