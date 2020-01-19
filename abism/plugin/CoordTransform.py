

def decimal2hms(RADeg, delimiter):
    """Converts decimal degrees to string in Hours:Minutes:Seconds format with
    user specified delimiter.

    @type RADeg: float
    @param RADeg: coordinate in decimal degrees
    @type delimiter: string
    @param delimiter: delimiter character in returned string
    @rtype: string
    @return: coordinate string in H:M:S format

    """

    hours = (RADeg/360.0)*24
    # if hours < 10 and hours >= 1:
    if 1 <= hours < 10:
        sHours = '0'+str(hours)[0]
    elif hours >= 10:
        sHours = str(hours)[:2]
    elif hours < 1:
        sHours = '00'
    else:
        return 'nan'

    if str(hours).find('.') == -1:
        mins = float(hours)*60.0
    else:
        mins = float(str(hours)[str(hours).index('.'):])*60.0
    # if mins<10 and mins>=1:
    if 1 <= mins < 10:
        sMins = '0'+str(mins)[:1]
    elif mins >= 10:
        sMins = str(mins)[:2]
    elif mins < 1:
        sMins = '00'
    else:
        return 'nan'

    secs = (hours-(float(sHours)+float(sMins)/60.0))*3600.0
    # if secs < 10 and secs>0.001:
    if 0.001 < secs < 10:
        sSecs = '0'+str(secs)[:str(secs).find('.')+4]
    elif secs < 0.0001:
        sSecs = '00.001'
    else:
        sSecs = str(secs)[:str(secs).find('.')+4]
    if len(sSecs) < 5:
        sSecs = sSecs+'00'      # So all to 3dp

    if float(sSecs) == 60.000:
        sSecs = '00.00'
        sMins = str(int(sMins)+1)
    if int(sMins) == 60:
        sMins = '00'
        sDeg = str(int(sDeg)+1)

    return sHours+delimiter+sMins+delimiter+sSecs


def decimal2dms(decDeg, delimiter):
    """Converts decimal degrees to string in Degrees:Minutes:Seconds format
    with user specified delimiter.

    @type decDeg: float
    @param decDeg: coordinate in decimal degrees
    @type delimiter: string
    @param delimiter: delimiter character in returned string
    @rtype: string
    @return: coordinate string in D:M:S format

    """
    # Positive
    if decDeg > 0:
        # if decDeg < 10 and decDeg>=1:
        if 1 <= decDeg < 10:
            sDeg = "0"+str(decDeg)[0]
        elif decDeg >= 10:
            sDeg = str(decDeg)[:2]
        elif decDeg < 1:
            sDeg = "00"
        else:
            return 'nan'

        if str(decDeg).find(".") == -1:
            mins = float(decDeg)*60.0
        else:
            mins = float(str(decDeg)[str(decDeg).index("."):])*60
        # if mins<10 and mins>=1:
        if 1 <= mins < 10:
            sMins = "0"+str(mins)[:1]
        elif mins >= 10:
            sMins = str(mins)[:2]
        elif mins < 1:
            sMins = "00"
        else:
            return 'nan'

        secs = (decDeg-(float(sDeg)+float(sMins)/60.0))*3600.0
        # if secs<10 and secs>0:
        if 0 < secs < 10:
            sSecs = "0"+str(secs)[:str(secs).find(".")+3]
        elif secs < 0.001:
            sSecs = "00.00"
        else:
            sSecs = str(secs)[:str(secs).find(".")+3]
        if len(sSecs) < 5:
            sSecs = sSecs+"0"   # So all to 2dp

        if float(sSecs) == 60.00:
            sSecs = "00.00"
            sMins = str(int(sMins)+1)
        if int(sMins) == 60:
            sMins = "00"
            sDeg = str(int(sDeg)+1)

        return "+"+sDeg+delimiter+sMins+delimiter+sSecs

    else:
        # if decDeg>-10 and decDeg<=-1:
        if -10 < decDeg <= -1:
            sDeg = "-0"+str(decDeg)[1]
        elif decDeg <= -10:
            sDeg = str(decDeg)[:3]
        elif decDeg > -1:
            sDeg = "-00"
        else:
            return 'nan'

        if str(decDeg).find(".") == -1:
            mins = float(decDeg)*-60.0
        else:
            mins = float(str(decDeg)[str(decDeg).index("."):])*60
        # if mins<10 and mins>=1:
        if 1 <= mins < 10:
            sMins = "0"+str(mins)[:1]
        elif mins >= 10:
            sMins = str(mins)[:2]
        elif mins < 1:
            sMins = "00"
        else:
            return 'nan'

        secs = (decDeg-(float(sDeg)-float(sMins)/60.0))*3600.0
        # if secs>-10 and secs<0:
        # so don't get minus sign
        if -10 < secs < 0:
            sSecs = "0"+str(secs)[1:str(secs).find(".")+3]
        elif secs > -0.001:
            sSecs = "00.00"
        else:
            sSecs = str(secs)[1:str(secs).find(".")+3]
        if len(sSecs) < 5:
            sSecs = sSecs+"0"   # So all to 2dp

        if float(sSecs) == 60.00:
            sSecs = "00.00"
            sMins = str(int(sMins)+1)
        if int(sMins) == 60:
            sMins = "00"
            sDeg = str(int(sDeg)-1)

        return sDeg+delimiter+sMins+delimiter+sSecs


def hms2decimal(RAString, delimiter):
    """Converts a delimited string of Hours:Minutes:Seconds format into decimal
    degrees.

    @type RAString: string
    @param RAString: coordinate string in H:M:S format
    @type delimiter: string
    @param delimiter: delimiter character in RAString
    @rtype: float
    @return: coordinate in decimal degrees

    """
    # is it in HH:MM:SS format?
    if delimiter == "":
        RABits = str(RAString).split()
    else:
        RABits = str(RAString).split(delimiter)
    if len(RABits) > 1:
        RAHDecimal = float(RABits[0])
        if len(RABits) > 1:
            RAHDecimal = RAHDecimal+(float(RABits[1])/60.0)
        if len(RABits) > 2:
            RAHDecimal = RAHDecimal+(float(RABits[2])/3600.0)
        RADeg = (RAHDecimal/24.0)*360.0
    else:
        RADeg = float(RAString)

    return RADeg


def dms2decimal(decString, delimiter):
    """Converts a delimited string of Degrees:Minutes:Seconds format into
    decimal degrees.

    @type decString: string
    @param decString: coordinate string in D:M:S format
    @type delimiter: string
    @param delimiter: delimiter character in decString
    @rtype: float
    @return: coordinate in decimal degrees

    """
    # is it in DD:MM:SS format?
    if delimiter == "":
        decBits = str(decString).split()
    else:
        decBits = str(decString).split(delimiter)
    if len(decBits) > 1:
        decDeg = float(decBits[0])
        if decBits[0].find("-") != -1:
            if len(decBits) > 1:
                decDeg = decDeg-(float(decBits[1])/60.0)
            if len(decBits) > 2:
                decDeg = decDeg-(float(decBits[2])/3600.0)
        else:
            if len(decBits) > 1:
                decDeg = decDeg+(float(decBits[1])/60.0)
            if len(decBits) > 2:
                decDeg = decDeg+(float(decBits[2])/3600.0)
    else:
        decDeg = float(decString)

    return decDeg
