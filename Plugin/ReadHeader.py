import pyfits, sys

import WorkVariables as W

try : import pywcs 
except ImportError as exc:
    sys.stderr.write("Warning: failed to import settings module ({})".format(exc))



def EsoHeader(header):
  """ the objects is.. pyfits.open(image)[0] """
   
  #0/ DETERMINE the instrument 
  if header.has_key('INSTRUM'): 
     instru=header['INSTRUM']  
  elif header.has_key('INSTRUME'): 
     instru=header['INSTRUME']  
  elif header.has_key('INSTRUMENT'): 
     instru=header['INSTRUMENT']  
  else :  instru=""
  if W.verbose >3 : print "READHEADER my instru : ", instru

  #1/ Call header Class 
  if ("NAOS" in instru) and ("CONICA" in instru)  : 
      W.head = NacoHeader(header) 
  elif "SINFONI" in instru : 
      W.head = SinfoniHeader(header) 
  else: 
      W.head = Header(header) 



class Header:
  def __init__(self,header):
     self.MyHeader= header
     self.InitKey() 
     self.StrehlKey() 
     self.ObservationKey()
     self.WCSKey() 
     self.MoreKey() 


  def InitKey(self):  # for all classes 
    self.diameter=99.      #m
    self.wavelength=99.    #um
    self.obstruction=99.   #% area 
    self.pixel_scale=99.   # arsec/pixel
    self.exptime = 1.     # sec  
  
    self.telescope='UNKNOWN telescope'
    self.date='UNKNOWN date '
    self.date_obs='UNKNOWN obsdate'
    self.instrument= 'UNKNOWN instrument'
    self.company = "UNKNOWN company"  # will be "eso" 


  def StrehlKey(self): # depend on class 
    """diameter wavelenght obstruction pixel_scale"""
    ###############
    ###  WAVELENGHT
    if self.MyHeader.has_key('FILTER'):
       filt = self.MyHeader['FILTER']
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
    if self.MyHeader.has_key('LAMBDA'): 
      self.wavelength=self.MyHeader['LAMBDA']  
    if self.MyHeader.has_key('HIERARCH ESO INS CWLEN'): 
      self.wavelength=self.MyHeader['HIERARCH ESO INS CWLEN']

    ###############""
    ## APERTURE 
    if 'VLT'in self.telescope :
          self.diameter = 8.0
          self.obstruction = 14
    elif 'Baade'in self.telescope :
          self.diameter = 6.0
          self.obstruction = 15
    if self.MyHeader.has_key('TELDIAM'): 
      self.diameter=self.MyHeader['TELDIAM']        
    if self.MyHeader.has_key('TELSECD'): 
      self.obstruction=   (self.MyHeader['TELSECD']/self.diameter)**2        
 

    ###############
    #" SCALE 

        #baade 
    if self.MyHeader.has_key('SCALE'): self.pixel_scale=self.MyHeader['SCALE']         
    if (self.pixel_scale>1e-6) &(self.pixel_scale<1e-3) : # in deg  
        self.pixel_scale*=3600     

        # VLT 
    if self.MyHeader.has_key('HIERARCH ESO INS PIXSCALE'): 
      self.pixel_scale=self.MyHeader['HIERARCH ESO INS PIXSCALE']
    if self.MyHeader.has_key('APPXSCL'): 
      self.pixel_scale=self.MyHeader['APPXSCL']/1000.    
    if self.MyHeader.has_key('CD1_1'):
         if self.MyHeader.has_key('CD2_2'):
            self.pixel_scale=(  abs(float(self.MyHeader['CD1_1']))   +    abs(float(self.MyHeader['CD2_2']))     )/2.  *3600.
         else : 
            self.pixel_scale=  abs(float(self.MyHeader['CD1_1']))  *3600.

    if self.pixel_scale==0 : self.pixel_scale=99.
 

  def ObservationKey(self): # depend on class ESO/ Telescope 
    # COMPANY 
    if any("ESO OBS" in s for s in self.MyHeader.keys()): # because, the HIERARCH disappear when readden by python  
      self.company = "ESO"

    # TELESCOP 
    if self.MyHeader.has_key("TELESCOP") : 
       self.telescope  = self.MyHeader["TELESCOP"]  

    # INSRTU  
    if self.MyHeader.has_key('INSTRUM'): 
       self.instrument=self.MyHeader['INSTRUM']  
    if self.MyHeader.has_key('INSTRUME'): 
       self.instrument=self.MyHeader['INSTRUME']  
    if self.MyHeader.has_key('INSTRUMENT'): 
       self.instrument=self.MyHeader['INSTRUMENT']  

    # REDUCED 
    if self.MyHeader.has_key('HIERARCH ESO PRO TYPE'): 
       self.reduced_type =  self.MyHeader['HIERARCH ESO PRO TYPE'] 


  def WCSKey(self):  # for all classes 
    ####
    # PY WCS f
    try : self.pywcs=pywcs.WCS(self.MyHeader) # for coord transformation 
    except : self.pywcs = None             # we define it anyway  
    """NOTE that if cube, the coors must be a 3. 
      #if len( object.data.shape ) == 3: # if cube, we delete last line and last column 
      #  self.pywcs.wcs.cd=self.pywcs.cd[:-1]
      #  self.pywcs.wcs.cd=self.pywcs.cd[:,:-1]"""
    ##########
    # WCS
    self.CD1_1, self.CD2_2 = 1,1 
    self.CD2_1, self.CD1_2 = 0,0 
    if self.MyHeader.has_key('CD1_1'): 
      self.CD1_1=float(self.MyHeader['CD1_1'] )        
    if self.MyHeader.has_key('CD1_2'): 
      self.CD1_2=float(self.MyHeader['CD1_2'] )        
    if self.MyHeader.has_key('CD2_1'): 
      self.CD2_1=float(self.MyHeader['CD2_1'] )        
    if self.MyHeader.has_key('CD2_2'): 
      self.CD2_2=float(self.MyHeader['CD2_2'] )

    ##############
    #  ZPT 
    self.zpt = 0
    if self.MyHeader.has_key("ZPT"):
      self.zpt=float(self.MyHeader['ZPT'] ) 


  def MoreKey(self): # for all classes too  
    if self.MyHeader.has_key('DATE'): 
      self.date=self.MyHeader['DATE']  
    if self.MyHeader.has_key('DATE-OBS'): 
      self.date_obs=self.MyHeader['DATE-OBS']   
    if self.MyHeader.has_key('BPM'): 
      self.bpm_name=self.MyHeader['BPM']  
       
    if self.MyHeader.has_key('EXPTIME'): 
      self.exptime=self.MyHeader['EXPTIME']  
    if self.MyHeader.has_key('HIERARCH ESO DET DIT'): 
      self.exptime=self.MyHeader['HIERARCH ESO DET DIT']  


        ###############
	##" NACO 

class NacoHeader(Header): 
  def __init__(self,header):
     self.MyHeader= header
     self.InitKey() 
     self.StrehlKey() 
     self.ObservationKey()
     self.WCSKey() 
     self.MoreKey() 
  def StrehlKey(self):
    if W.verbose > 3 :print  "READ HEAR NACO \n"
    self.wavelength=self.MyHeader['HIERARCH ESO INS CWLEN']
    self.diameter = 8.0
    self.obstruction = 14
    self.pixel_scale=self.MyHeader['HIERARCH ESO INS PIXSCALE']


  def ObservationKey(self): # company, tel,instru, reduced ? 
    self.company = "ESO"
    if self.MyHeader.has_key("TELESCOP") : # NACO will be changed soon  
       self.telescope  = self.MyHeader["TELESCOP"]  

    self.instrument="NaCo"  

    self.reduced_type="RAW"
    if self.MyHeader.has_key('HIERARCH ESO PRO TYPE'): 
       self.reduced_type =  self.MyHeader['HIERARCH ESO PRO TYPE'] 
 
    
        ###############
	## SinfONI  

class SinfoniHeader(Header): 
  def __init__(self,header):
     self.MyHeader= header
     self.InitKey() 
     self.StrehlKey() 
     self.ObservationKey()
     self.WCSKey() 
     self.MoreKey() 
  def StrehlKey(self):
    if W.verbose > 3 : print  "READ HEAR SINFONI \n"
    self.wavelength=float(self.MyHeader['HIERARCH ESO INS GRAT1 WLEN'])/1000
    self.diameter = 8.0
    self.obstruction = 14.
    self.pixel_scale=99.
    #self.pixel_scale=self.MyHeader['HIERARCH ESO TEL FOCU SCALE']

    # bite 
    if self.MyHeader.has_key('CD1_1'):
         if self.MyHeader.has_key('CD2_2'):
            self.pixel_scale=(  abs(float(self.MyHeader['CD1_1']))   +    abs(float(self.MyHeader['CD2_2']))     )/2.  *3600.
         else : 
            self.pixel_scale=  abs(float(self.MyHeader['CD1_1']))  *3600.

    if self.pixel_scale==0 : self.pixel_scale=99.

  def ObservationKey(self): # company, tel,instru, reduced ? 
    self.company = "ESO"
    if self.MyHeader.has_key("TELESCOP") : # NACO will be changed soon  
       self.telescope  = self.MyHeader["TELESCOP"]  

    self.instrument="SINFONI"  

    self.reduced_type="RAW"
    if self.MyHeader.has_key('HIERARCH ESO PRO TYPE'): 
       self.reduced_type =  self.MyHeader['HIERARCH ESO PRO TYPE'] 
 






