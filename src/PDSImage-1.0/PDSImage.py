#! /usr/local/bin/python

import os, sys, string, numarray, re, decimal

class PDSImage:
    """PDSImage.
    
    Read single-band NASA PDS <http://pds.jpl.nasa.gov/documents>
    image file, query header information and extract binary image 
    data in a format suitable for PIL.  Works for Pathfinder and 
    Mars Exploration Rover images, maybe others.
    
    Examples:
    
    QUERY PDS HEADER
    ================
    
    from PDSImage import *
    print PDSImage('648405R.IMG').getAttribs('/image/sample_bit_mask')
    
    CREATE CSV SPREADSHEET FROM PDSImage
    ====================================
    
    from PDSImage import *
    import csv
    p = PDSImage('648405R.IMG')
    w = csv.writer(open('648405R.IMG', 'w'))
    
    for i in p._im:
        w.writerow(i)
        
    CONVERT PDSimage TO TIFF USING PIL
    ==================================
    
    import Image as I
    from PDSImage import *
    
    p = PDSImage('648405R.IMG')
    I.fromstring('L', p.getDimensions(), p.getImage(), 'raw', 'L').save('p.tif')
    
    """

    def __init__(self, fn='', dim=(1024,1024)):
        """Initialize PDSImage.
        
        Keyword arguments:
        fn -- file name (default '')
        dim -- x,y tuple (default (1024,1024))
        
        With no arguments, creates an empty 1024x1024 PDSImage.
        """
            
        self._attribs = {}
        self._lut = []
        self._dim = dim
        
        self._zeroarray = numarray.zeros(dim)
        self._im = numarray.zeros(dim, type=numarray.Int16)
        self._im8 = numarray.zeros(dim, type=numarray.Int8)
        if fn != '':
            self.getPDSFile(fn)

    def __add__(self, other):
        """Add PDSImage."""
        self.__tempIMG = PDSImage(dim=self._dim)
        self.__tempIMG._im = self._im + other._im
        self.__tempIMG._im8 = self._im8 + other._im8
        return self.__tempIMG 
       
    def __sub__(self, other):
        """Subtract PDSImage."""
        self.__tempIMG = PDSImage(dim=self._dim)
        self.__tempIMG._im = self._im - other._im
        if self.__tempIMG._im < 0:
            self.__tempIMG._im = self.__tmpIMG._im + abs(self.__tmpIMG._im.min())
        self.__tempIMG._im8 = self._im8 - other._im8
        return self.__tempIMG 
        
        
    def __div__(self, other):
        """Divide PDSImage."""
        self.__tempIMG = PDSImage(dim=self._dim)
        self.__tempIMG._im = self._im / other._im
        self.__tempIMG._im8 = self._im8 / other._im8
        return self.__tempIMG 
        

    def getPDSFile(self, fn):
        """Read PDSImage file."""
       
        NF = ['N/A', 'NULL', 'UNK']   
        LINENUM = 0
        pointers = {}
        
        f = open(fn, 'rb')
        f.seek(0,2)
        if f.tell() == 0:
            # Empty file
            return
        else:
            f.seek(0)

        
        while 1:
            l = f.readline().split()
            LINENUM += 1
            # Exit if this is actually a VICAR file...
            if LINENUM == 1 and l[0][:7] == 'LBLSIZE':
                break
    
            # End of header?
            if len(l) == 1 and l[0] == 'END':
                break
            # Skip blank lines and comments
            if not l:
                continue
            if l[0] == '/*':
                continue
        
            # Where is the IMAGE?
            if len(l) > 2 and l[0] == 'RECORD_BYTES':
                rb = int(l[2])
            if len(l) > 2 and l[0] == 'LABEL_RECORDS':
                lr = int(l[2])
            if len(l) > 2 and l[0][0] == '^' :
                pointers[l[0][1:]] = l[2]
    
            # Flatten lines
            if  len(l) > 2 and  l[1] == '=' and l[2][0] == '"':
                while l[-1][-1] != '"':
                    l += f.readline().split()
                l[2] = string.join(l[2:])[1:-1]
                l = l[:3]    
            if  len(l) > 2 and  l[1] == '=' and l[2][0] == '(':
                while l[-1][-1] != ')':
                    l += f.readline().split()
                l[2] = string.join(l[2:])[1:-1]
                l = l[:3]

            # Drill down into GROUPs and OBJECTs
            if l[0] == "GROUP" or l[0] == "OBJECT":
                g = {}
                gn = l[2] 
                while l[0] != "END_GROUP" and l[0] != "END_OBJECT":
                    l = f.readline().split()
                    if l[0][:4] == "END_":
                        continue
                    if  len(l) > 2 and  l[1] == '=' and l[2][0] == '"':
                        while l[-1][-1] != '"':
                            l += f.readline().split()
                        l[2] = string.join(l[2:])[1:-1]
                        l = l[:3]
                    if  len(l) > 2 and  l[1] == '=' and l[2][0] == '(':
                        while l[-1][-1] != ')':
                            l += f.readline().split()
                        l[2] = string.join(l[2:])[1:-1]
                        l = l[:3]
                    # Add group and object items to attributes
                    if len(l) > 2 and re.match(r"^[\-\+]?([0-9]*\.)?[0-9]+([eE][\-\+]?[0-9]+)?\b$", l[2]):
                        if (decimal.Decimal(l[2]) - int(decimal.Decimal(l[2]))) > 0:
                            l[2] = float(l[2])
                        else:
                            l[2] = int(decimal.Decimal(l[2]))
                    if len(l) > 2 and l[2] not in NF:
                        g[l[0]] = l[2]
                # How far down the rabbit hole do you wanna go?
                for z in g.keys():
                    if z[-5:].upper() == '_NAME' and z[:-5] in g.keys():
                        counter = 0
                        for y in g[z].split(','):
                            aname = '%s_%s' % (z[:-5].split('_')[-1],y.replace('"', '').lstrip().rstrip().replace(' ', '_').replace('-','_'))
                            if g[z[:-5]].split(',')[counter].lstrip()[0] == '"':
                                datum = g[z[:-5]].split(',')[counter].lstrip().rstrip()[1:-1]
                            else:
                                datum = g[z[:-5]].split(',')[counter].lstrip().split(' ')[0]
                            if re.match(r"^[\-\+]?([0-9]*\.)?[0-9]+([eE][\-\+]?[0-9]+)?\b$", datum):
                                if (decimal.Decimal(datum) - int(decimal.Decimal(datum))) > 0:
                                    datum = float(datum)
                                else:
                                    datum = int(decimal.Decimal(datum))
                            g[aname] = datum
                            counter += 1
                self._attribs[gn] = g
            # Add to top level attributes
            else:
                if len(l) > 2 and l[0] != "END_GROUP" and l[0] != "END_OBJECT" and l[0] != "END":
                    if re.match(r"^[\-\+]?([0-9]*\.)?[0-9]+([eE][\-\+]?[0-9]+)?\b$", l[2]):
                        if (decimal.Decimal(l[2]) - int(decimal.Decimal(l[2]))) > 0:
                            l[2] = float(l[2])
                        else:
                            l[2] = int(decimal.Decimal(l[2]))
                    if len(l) > 2 and l[2] not in NF:
                        self._attribs[l[0]] = l[2]

        self._dim = (self.getAttribs('/image/line_samples'),self.getAttribs('/image/lines'))
        if self.getAttribs('/image/bands') == 1 and self.getAttribs('/image/sample_type')[:3] == 'MSB':
            # Go to the beginning of the IMAGE    
            f.seek((int(pointers['IMAGE']) - 1) * rb)
            isize = self.getAttribs('image/line_samples') * self.getAttribs('image/lines') * self.getAttribs('image/sample_bits') / 8
            try:
                self._im = numarray.fromstring(f.read(isize), numarray.Int16, (self.getAttribs('image/lines'),self.getAttribs('image/line_samples')))
                if sys.byteorder != 'big':
                    self._im.byteswap()
                    self._im8 = numarray.array(self._im / 16 + 1, type=numarray.Int8)
            except:
                pass

    
    def getAttribs(self, e=''):
        """Query PDS header.

        Keyword arguments:
        e -- search string (default '').  
        
        For member of PDS GROUP or OBJECT, separate GROUP name 
        and GROUP MEMBER name with '/'.  For instance, 
        'image/bands' (or even '/image/bands').

        Without arguments, returns header as a dictionary.  
        """
        s = 'self._attribs'
        if e == '':
            return self._attribs
        else:
            if e[0] == '/':
                e = e[1:]
            l = e.upper().split('/')
            for i in l:
                s = '%s[\'%s\']' % (s, i)
            try:
                x = eval(s)
            except:
                x = ''
            return x

    def getDimensions(self):
        """Get dimensions of image (tuple)."""
        return self._dim

    def getImage(self):
        """Get string version of 8-bit image, suitable for PIL."""
        return self._im8.tostring()


    def get16Image(self):
        """Get string version of 16-bit image."""
        return numarray.array(self._im, type=numarray.Int16).tostring()


    def setLUT(self, fn=''):
        """Applies lookup table to derive 8-bit.
        
        Keyword argumets:
        f -- Lookup table file name (default '').
        
        A properly formed lookup table file is a tab-delimited 
        file with two columns for input values and mapped values.  
        """
        try:
            f = open(fn).readlines()
            x = []
            for i in range(len(f)):
                x.append(int(f[i].split()[-1]))
            LUT = array(x)
            self._im8 = LUT[p._im]
        except:
            self._im8 = numarray.array(self._im / 16 + 1, type=numarray.Int8)
            
