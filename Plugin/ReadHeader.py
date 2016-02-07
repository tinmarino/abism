# import pyfits
import sys
import numpy as np

import WorkVariables as W

try:
  import pywcs
  import_pywcs_bool = 1
except ImportError as exc:
  sys.stderr.write("Warning: failed to import settings module ({})".format(exc))
  import_pywcs_bool = 0



def CallHeaderClass(header):
  """ the objects is.. pyfits.open(image)[0] """

  #0/ DETERMINE the instrument
  print ("header type is " + str(type(header)));
  #if header.has_key('INSTRUM'):
  #   instru=header['INSTRUM']
  #elif header.has_key('INSTRUME'):
  #   instru=header['INSTRUME']
  #elif header.has_key('INSTRUMENT'):
  #   instru=header['INSTRUMENT']
  #else :  instru=""
  #if W.verbose >3 : print "READHEADER my instru : ", instru
  #instru = ""

  ##1/ Call header Class
  #if ("NAOS" in instru) and ("CONICA" in instru)  :
  #    W.head = NacoHeader(header)
  #elif "SINFONI" in instru :
  #    W.head = SinfoniHeader(header)
  #else:
  W.head = Header(header)



class Header:
"""
       These are the importants files I retrieve from the header.

    diameter        (real in m)     The primary diameter
    wavelenght      (real in um)    The wavelength of the detection
    obstruction     (real in %)     The percentage in area of the central
obstruction. This is 14%**2 for VLT i guess, TODO check that !!
    pixel_scale     (real in arsec/pixel) The number anguler size of one p
pixel in arcsec
    exptime         (real in sec)   The time of one exposure.  This will not
infer the strehl ratio but the potometry  as well as the zero point.
    zpt             (real in log)   The luminosity of 1 intensity Arbitrary
Unit during one second. The higher the Zero point, the fainter stars (or noise)
you may detect. It depends on the filter AND the airmass.
    pywcs           (pywcs object)  This set of matrices can be used to get the
position on sky of your object.
    telescope       (string)        Name of your telescope
    date            (string)        Date, maybe of last modification
    date_obs        (string)        Data of observation.
    instrument      (string)        Name of the instrument.
    company         (string)        Name of the company owning the telescope:
ESO, CFHT, Carnergie...

    instrument      (string)        Name of the camera. Can be used to
automatially retrieve informations.
    reduced_type    (string)        RAW or REDUCED

    saturation_level  (real ADU)    The ADU of saturation of the CCD, proper to
the science camera.
    non_lineratiry_level (real ADU) The ADU where non linearity starts, I wont
use this value I guess. Or just as a quiet warning.
"""
  def __init__(self):
    pass

  def __init__(self,header):
     self.header = header
     self.InitKey()
     self.ObservationKey()
     self.StrehlKey()
     self.WCSKey()
     self.MoreKey()
     self.DefineGlobalVar()
     self.CallAfter()


  def InitKey(self):  # for all classes
    self.diameter=99.      #m
    self.wavelength=99.    #um
    self.obstruction=99.   #% area
    self.pixel_scale=99.   # arsec/pixel

    self.exptime = 1.     # sec
    self.zpt     =0.
    self.pywcs   = None

    self.telescope='UNKNOWN telescope'
    self.date='UNKNOWN date '
    self.date_obs='UNKNOWN obsdate'
    self.instrument= 'UNKNOWN instrument'
    self.company = "UNKNOWN company"  # will be "eso"

    self.saturation_level    = np.inf # in ADU
    self.non_linearity_level = np.inf

  def ObservationKey(self): # depend on class ESO/ Telescope
    # COMPANY
    if any("ESO OBS" in s for s in self.header.keys()): # because, the HIERARCH disappear when readden by python
      self.company = "ESO"

    # TELESCOP
    #if self.header.has_key("TELESCOP") :
    if "TELESCOP" in self.header:
       self.telescope  = self.header["TELESCOP"]

    # INSRTU
    if self.header.has_key('INSTRUM'):
       self.instrument=self.header['INSTRUM']
    if self.header.has_key('INSTRUME'):
       self.instrument=self.header['INSTRUME']
    if self.header.has_key('INSTRUMENT'):
       self.instrument=self.header['INSTRUMENT']

    self.reduced_type = "RAW"
    # REDUCED
    if self.header.has_key('HIERARCH ESO PRO TYPE'):
       self.reduced_type =  self.header['HIERARCH ESO PRO TYPE']

  def StrehlKey(self): # depend on class
    """diameter wavelenght obstruction pixel_scale"""
    ###############
    ###  WAVELENGHT
    if self.header.has_key('FILTER'):
       filt = self.header['FILTER']
       if filt == 'H' : self.wavelength = 1.6
       if ("U" or "u")  in filt : self.wavelength = 0.365
       if ("B" or "b")  in filt : self.wavelength = 0.445
       if ("V" or "v")  in filt : self.wavelength = 0.551
       if ("R" or "r")  in filt : self.wavelength = 0.658
       if ("I" or "i")  in filt : self.wavelength = 0.806
       if ("Z" or "z")  in filt : self.wavelength = 0.9
       if ("Y" or "y")  in filt : self.wavelength = 1.020
       if ("J" or "j")  in filt : self.wavelength = 1.220
       if ("K" or "k")  in filt : self.wavelength = 2.190
       if ("L" or "l")  in filt : self.wavelength = 3.450
       if ("M" or "m")  in filt : self.wavelength = 4.750
    if self.header.has_key('LAMBDA'):
      self.wavelength=self.header['LAMBDA']
    if self.header.has_key('HIERARCH ESO INS CWLEN'):
      self.wavelength=self.header['HIERARCH ESO INS CWLEN']

    ###############""
    ## APERTURE
    if 'VLT'in self.telescope :
          self.diameter = 8.0
          self.obstruction = 14.
    elif 'Baade'in self.telescope :
          self.diameter = 6.0
          self.obstruction = 15
    elif "Keck" in self.telescope :
       self.diameter = 10.
    if self.header.has_key('TELDIAM'):
      self.diameter=self.header['TELDIAM']
    if self.header.has_key('TELSECD'):
      self.obstruction=   (self.header['TELSECD']/self.diameter)**2


    ###############
    #" SCALE

        #baade
    if self.header.has_key('SCALE'): self.pixel_scale=self.header['SCALE']
    if (self.pixel_scale>1e-6) &(self.pixel_scale<1e-3) : # in deg
        self.pixel_scale*=3600

        # VLT
    if self.header.has_key('HIERARCH ESO INS PIXSCALE'):
      self.pixel_scale=self.header['HIERARCH ESO INS PIXSCALE']
    if self.header.has_key('APPXSCL'):
      self.pixel_scale=self.header['APPXSCL']/1000.
    if self.header.has_key('CD1_1'):
         if self.header.has_key('CD2_2'):
            self.pixel_scale=(  abs(float(self.header['CD1_1']))   +    abs(float(self.header['CD2_2']))     )/2.  *3600.
         else :
            self.pixel_scale=  abs(float(self.header['CD1_1']))  *3600.

    if self.pixel_scale==0 : self.pixel_scale=99.




  def WCSKey(self):  # and zpt for all classes
    ""
    ####
    # PYWCS f
    try :
        def flatten_header(header):
          """
          Attempt to turn an N-dimensional fits header into a 2-dimensional header
          Turns all CRPIX[>2] etc. into new keywords with suffix 'A'

          header must be a pyfits.Header instance
          """

          # astropy.io.fits != pyfits -> sadness
          #if not hasattr(header,'copy')
          #    raise Exception("flatten_header requires a pyfits.Header instance")

          newheader = header.copy()

          for key in newheader.keys():
              try:
                  if int(key[-1]) >= 3 and key[:2] in ['CD','CR','CT','CU','NA']:
                      newheader.rename_key(key,'A'+key,force=True)
              except ValueError:
                  # if key[-1] is not an int
                  pass
              except IndexError:
                  # if len(key) < 2
                  pass
          newheader.update('NAXIS',2)

          return newheader

        self.flathead = flatten_header( self.header )
	# If proj type in more than 8 characters, we cut from 3 dec----tan -> dec--tan
	tmp = self.flathead["CTYPE1"]
	if len (tmp) >8 :
	   self.flathead["CTYPE1"]  = tmp[0:  3 ] + tmp[ len(tmp)-8 +3 :]
	tmp = self.flathead["CTYPE2"]
	if len (tmp) >8 :
	   self.flathead["CTYPE2"] = tmp[0:  3 ] + tmp[ len(tmp)-8 +3 :]
        self.pywcs=pywcs.WCS( self.flathead  ) # for coord transformation

        #No wcs proj ?
        self.wcs_bool = True
        if  ( self.pywcs.all_pix2sky([[0,0]],0 ) == [[1,1]] ).all() :
            self.wcs_bool = False
            self.pywcs.all_pix2sky = lambda x,y : (99,99)


    except  : #includding no pywcs module
       import traceback
       if W.verbose >3 : traceback.print_exc()
       if W.verbose >0 : print "WARNING (just a warning !) I did not manage to get WCS from pywcs\n\n"
       self.wcs_bool = False
       class void : pass
       self.pywcs = void()
       self.pywcs.all_pix2sky = lambda x,y : [[99,99]]*len(x) # this will be later transformed




    ##########
    # WCS
    self.CD1_1, self.CD2_2 = 1,1
    self.CD2_1, self.CD1_2 = 0,0
    if self.header.has_key('CD1_1'):
      self.CD1_1=float(self.header['CD1_1'] )
    if self.header.has_key('CD1_2'):
      self.CD1_2=float(self.header['CD1_2'] )
    if self.header.has_key('CD2_1'):
      self.CD2_1=float(self.header['CD2_1'] )
    if self.header.has_key('CD2_2'):
      self.CD2_2=float(self.header['CD2_2'] )

    ##############
    #  ZPT
    self.zpt = 0
    if self.header.has_key("ZPT"):
      self.zpt=float(self.header['ZPT'] )


  def MoreKey(self): # for all classes too
    if self.header.has_key('DATE'):
      self.date=self.header['DATE']
    if self.header.has_key('DATE-OBS'):
      self.date_obs=self.header['DATE-OBS']
    if self.header.has_key('BPM'):
      self.bpm_name=self.header['BPM']

    if self.header.has_key('EXPTIME'):
      self.exptime=self.header['EXPTIME']
    if self.header.has_key('HIERARCH ESO DET DIT'):
      self.exptime=self.header['HIERARCH ESO DET DIT']


  def DefineGlobalVar(self) :
     return

  def CallAfter(self) :
     return

        ###############
	##" NACO

class NacoHeader(Header):
  def StrehlKey(self):
    if W.verbose > 3 :print  "READ HEAR NACO \n"
    self.wavelength=self.header['HIERARCH ESO INS CWLEN']
    self.diameter = 8.0
    self.obstruction = 14
    self.pixel_scale=self.header['HIERARCH ESO INS PIXSCALE']


  def ObservationKey(self): # company, tel,instru, reduced ?
    self.company = "ESO"
    if self.header.has_key("TELESCOP") : # NACO will be changed soon
       self.telescope  = self.header["TELESCOP"]

    self.instrument="NaCo"

    self.reduced_type="RAW"
    if self.header.has_key('HIERARCH ESO PRO TYPE'):
       self.reduced_type =  self.header['HIERARCH ESO PRO TYPE']

  def CallAfter(self) :
    self.Saturation()


  def Saturation(self) :
    if self.header.has_key( 'HIERARCH ESO DET NCORRS NAME' ) :
      self.ncor = self.header[ 'HIERARCH ESO DET NCORRS NAME' ]
      if self.header.has_key( 'HIERARCH ESO DET MODE NAME' ) :
         self.read_mode  = self.header[ 'HIERARCH ESO DET MODE NAME' ]
         bias = -np.inf
	 fullwell = np.inf # in case
	 if self.ncor == "Double_RdRstRd" :
	    bias, fullwell = 0.,15000.
	 elif self.ncor == "FowlerNsamp" :
	    bias, fullwell = 0.,7500.
	 elif self.ncor == "Uncorr":
	    bias = -8000.
	    if self.read_mode == "HighDynamic" :
	      fullwell = 15000.
	    if self.read_mode == "HighWellDepth" :
	      fullwell = 22000.
	    if self.read_mode == "HighBackground" :
	      fullwell = 28000.

	 self.saturation_level    = fullwell + bias
	 self.non_linearity_level = 0.6 * fullwell +  bias

	     # bias + 0.6 (fw+bias)



        ###############
	## SinfONI

class SinfoniHeader(Header):
  def StrehlKey(self):
    if W.verbose > 3 : print  "READ HEAR SINFONI \n"
    self.wavelength=float(self.header['HIERARCH ESO INS GRAT1 WLEN'])/1000
    self.diameter = 8.0
    self.obstruction = 14.

    def pixel_scale() :
      # PIXEL SCALE FROM CD matrix
      if self.header.has_key('CD1_1'):
           if self.header.has_key('CD2_2'):
              self.pixel_scale=(  abs(float(self.header['CD1_1']))   +    abs(float(self.header['CD2_2']))     )/2.  *3600.
           else :
              self.pixel_scale=  abs(float(self.header['CD1_1']))  *3600.

      # PIXEL SCALE FROM HEADER OPT1.NAME
      opt1=1.
      if self.header.has_key('HIERARCH ESO INS OPTI1 NAME'):
         opt1=float(self.header['HIERARCH ESO INS OPTI1 NAME'])
         self.pixel_scale= np.sqrt( 2 ) /2  *opt1
      if self.pixel_scale==0 : self.pixel_scale=99.
      self.sinf_pixel_scale = opt1

    pixel_scale()




  def ObservationKey(self): # company, tel,instru, reduced ?
    self.company = "ESO"
    if self.header.has_key("TELESCOP") : # NACO will be changed soon
       self.telescope  = self.header["TELESCOP"]





    self.instrument="SINFONI"

    self.reduced_type="RAW"
    if self.header.has_key('HIERARCH ESO PRO TYPE'):
       self.reduced_type =  self.header['HIERARCH ESO PRO TYPE']


  def DefineGlobalVar(self):
      W.type["phot"] = 'fit' #  PHOTOMETRY type
      W.type["noise"] = 'fit'
      W.type["fit"]  = "Gaussian2D"
      return






