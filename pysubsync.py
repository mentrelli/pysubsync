#!/usr/bin/python

#   PySubSync
#       A small utility that takes a file .srt of subtitles and changes
#       the chronology and/or re-numbers the subtitles
#
#
#   Copyright (C) 2015, Andrea Mentrelli <andrea.mentrelli@unibo.it>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#
#   --------------------------------------------------------------------
#
#   history version: 
#     v.1.0 - September 20, 2015
#     v.2.0 - November 2/3, 2015
#
#   --------------------------------------------------------------------
#
#   Reminder from the author to the author:
#    "Debugging is twice as hard as writing the code in the first place.
#     Therefore, if you write the code as cleverly as possible, you are,
#     by definition, not smart enough to debug it." 
#                   (Brian Kernighan, The Elements of Programming Style)


import os
import sys
import re

def _timeshift(t, dt, flag_dir=1):
    
    h, m, s, ms = t    
    dh, dm, ds, dms = dt
    
    if flag_dir < 0:
        dh, dm, ds, dms = -dh, -dm, -ds, -dms
    elif flag_dir == 0:
        dh, dm, ds, dms = (0,)*4
    
    ms1 = ms + dms
    while ms1 >= 1000:
        ms1 -= 1000
        ds += 1
    while ms1 < 0:
        ms1 += 1000
        ds -= 1
        
    s1 = s + ds
    while s1 >= 60:
        s1 -= 60
        dm += 1
    while s1 < 0:
        s1 += 60
        dm -= 1
        
    m1 = m + dm
    while m1 >= 60:
        m1 -= 60
        dh += 1
    while m1 < 0:
        m1 += 60
        dh -= 1
        
    h1 = h + dh
    
    if h1 < 0:
        h1, m1, s1, ms1 = (0,)*4
    
    return (h1, m1, s1, ms1)

        
def _str2int(args):
    
    return [ int(a) for a in args]


def _int2str(args):
    
    return [ str(i) for i in args]
    

def _formattime(tt):
    
    h, m, s, ms = tt
    return h.zfill(2) + ":" + m.zfill(2) + ":" + s.zfill(2) + "," + ms.zfill(3)
        
        
def _str2ms(str_time):
    
    pattern = "^([-+]?)(\d{0,2}:)?(\d{0,2}:)(\d{0,2})?([,.]\d*)*"
    timing = re.match(pattern, str_time)
    
    if timing is not None:
        sgn, h, m, s, ms = timing.groups()
        if h is not None:
            h = int(h[:-1])
        else:
            h = 0
        m, s = int(m[:-1]), int(s)
        if ms is not None:
            ms = int(ms[1:].ljust(3,'0'))
        else:
            ms = 0
        if sgn=="-":
            fwd = -1
        else:
            fwd = 1
        tt = h, m, s, ms
        return _tt2ms(tt)*fwd
    else:
        sys.exit("ERROR: cannot parse time string '"+str_time+"'")


def _tt2ms(tt):
    
    h, m, s, ms = tt
    return 1000*(h*3600+m*60+s) + ms


def _idx2ms(filename_in, isub):
    
    with open(filename_in, 'r') as file_in:
        pattern_subno = "^(\d+)[\s|\t|\n]$"
        pattern_timing = "^(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->"+\
        "\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})"
        
        isub_found = False
    
        for line in file_in:
            
            m_timing = re.match(pattern_timing, line)
            m_subno  = re.match(pattern_subno, line)
            
            if isub_found and m_timing is not None:
                h0, m0, s0, ms0, h1, m1, s1, ms1 = m_timing.groups()
                tt = _str2int((h0, m0, s0, ms0))
                return _tt2ms(tt)
                
            elif m_subno is not None:
                subno = int(m_subno.groups()[0])
                if subno==isub:
                    isub_found = True
            

def subsync(filename_in, bmark0, bmark1=None,  d_subno=0, \
                                          filename_out=None, path=None):
    """
    Takes a file .srt of subtitles (filename_in) and changes the 
    chronology and/or re-numers the subtitles, producing a new file 
    (filename_out).
    
    
    Input arguments:
    
    - filename_in  > input filename
    
    - bmark0       > tuple (num, "hh:mm:ss,mms") for the first bookmark
                     (absolute shift), or string "[-+]hh:mm:ss,mms" for
                     a relative shift.
    
    - bmark1       > tuple (num, "hh:mm:ss,mms") for the second bookmark
                     (absolute shift) [optional]
    
    - d_subno      > increment to subtitle numbers [optional, default:0]
    
    - filename_out > output file [optional, default: 
                                              `filename_in`.subsync.srt]
    
    - path         > working directory
    
    
    
    Examples of Usage:
    
    > subsync("file.srt", "00:01:10,512")
    
        Shifts all the subtitles forward in time of 00:01:10,512
        (relative shift). The output file is named "file.subsync.srt".
        
    > subsync("file.srt", "-5:10")
    
        Shifts all the subtitles backwards in time of 00:05:10,000
        (relative shift). The output file is named "file.subsync.srt".
        
    > subsync("file.srt", (10, "20:00,1") )
    
        Shifts all the subtitles such that the subtitle with number 10
        appears at time 00:20:00,100 (absolute shift). The output file 
        is named "file.subsync.srt".
        
    > subsync("file.srt", (1, "1:11"), (1000, "1:59:59"))
    
        Shifts all the subtitles such that the subtitle with number 1
        appears at time 00:01:11,000 and the subtitle with number 1000 
        appears at time 01:59:59,000 (absolute shifts). The subtitles 
        are shifted on the basis of a linear interpolation/extrapolation
        between the two provided bookmarks. The output file is called 
        "file.subsync.srt". Both the input file and the output file are 
        found in the current path.
        
    > subsync("file.srt", (10, "3:00"), (900, "1:15:00"), d_subno=100,
              "newfile.srt", path="/media/videos")
    
        Shifts all the subtitles such that the subtitle with number 10
        appears at time 00:03:00,000 and the subtitle with number 900 
        appears at time 01:15:00,000 (absolute shifts). The subtitles 
        are shifted on the basis of a linear interpolation/extrapolation
        between the two provided bookmarks. In addition to the shifts,
        the numbering of the subtitles is increased by 100 (this feature
        might be useful in case of subtitles split in multiple files
        that should be merged in a single file). The output file is 
        called "newfile.srt". Both the input file and the output file 
        are found in the /media/videos.
        
                      by Undy, September 20, 2015 (v.1.0) 
                               November 2/3, 2015 (v.2.0)   
        
    """

    # set the path
    if path is None:
        path = './'
    elif path[-1] != os.path.sep:
        path += os.path.sep
    if not os.path.isdir(path):
        print "... path '{}' not found.".format(path)
        return None
    
    # check if input file exists
    if not os.path.isfile(filename_in):
        print "... cannot process the file '{}'.".format(filename_in)
        return None
        
    # set output file
    if filename_out is None:
        if filename_in[-4:]==".srt":
            filename_out = filename_in[:-4] + ".subsync.srt"
        else:
            filename_out = filename_in + ".subsync"
    
    # set full path to input and output files
    filename_in = path + filename_in
    filename_out = path + filename_out
    
    # get original/shifted position of the first bookmark
    if type(bmark0) is str:
        ta0, ta1 = 0, _str2ms(bmark0)
    elif type(bmark0) is tuple:
        if len(bmark0)==1:
            ta0, ta1 = 0, _str2ms(bmark0[0])
        else:
            ta0, ta1 = _idx2ms(filename_in, bmark0[0]), _str2ms(bmark0[1])
    
    # compute shift of the first bookmark
    dt = dh, dm, ds, dms0 = 0, 0, 0, abs(ta1-ta0)
    (dir, str_dir) = (-1, 'backward') if ta1<ta0 else (1, 'forward')
    
    # get otiginal/shifted position of the second bookmark
    if type(bmark1) is tuple:
        tb0, tb1 = _idx2ms(filename_in, bmark1[0]), _str2ms(bmark1[1])
        dms1 = (tb1-tb0) - (ta1-ta0)
        flag_stretch, shrink = True, round(float(tb1-tb0)/(ta1-ta0), 3)
    else:
        dms1 = 0
        flag_stretch, shrink = False, 1.0
        
    str_dt = _formattime(_int2str(_timeshift((0,)*4, dt, 1)))    
    
    print "... processing..."
    
    with open(filename_in, 'r') as file_in, open(filename_out, 'w') as file_out:
        
        pattern_subno = "^(\d+)[\s|\t|\n]$"
        pattern_timing = "^(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->"+\
        "\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})"
        
        icount = 0
    
        for line in file_in:
            
            m_timing = re.match(pattern_timing, line)
            m_subno  = re.match(pattern_subno, line)

            if m_timing is not None:
                icount += 1
                h0, m0, s0, ms0, h1, m1, s1, ms1 = m_timing.groups()
                
                # shift of the starting time
                t0 = _str2int((h0, m0, s0, ms0))
                if flag_stretch:
                    dt = (0, 0, 0, dms0*dir+dms1*(_tt2ms(t0)-ta0)/(tb0-ta0))
                    t0 = _timeshift(t0, dt, 1)
                else:
                    t0 = _timeshift(t0, dt, dir)
                t0 = _int2str(t0)
                str_t0 = _formattime(t0)
                
                # shift of the final time
                t1 = _str2int((h1, m1, s1, ms1))
                if flag_stretch:
                    dt = (0, 0, 0, dms0*dir+dms1*(_tt2ms(t1)-ta0)/(tb0-ta0))
                    t1 = _timeshift(t1, dt, 1)
                else:
                    t1 = _timeshift(t1, dt, dir)
                t1 = _int2str(t1)
                str_t1 = _formattime(t1)
                
                line = str_t0 + " --> " + str_t1 + "\n"
                
            elif m_subno is not None and d_subno <> 0:
                subno = int(m_subno.groups()[0])
                subno += d_subno
                
                line = str(subno) + "\n"

            file_out.write(line)
            
    print "... processed {} subtitles".format(icount),
    if d_subno == 0:
        print "(no renumbering)"
    else:
        print "(subtitles renumbered by adding {})".format(d_subno)
    if flag_stretch:
        print "... subtitles shifted {} in time of {}, with a stretching factor of {}".format(str_dir, str_dt, shrink)
    else:
        print "... subtitles shifted {} in time of {}, with no stretching".\
        format(str_dir, str_dt)
        
    print "... input file:  '{}'".format(filename_in)
    print "... output file: '{}'".format(filename_out)
    

if __name__ == "__main__":

    import argparse

    class ArgParser(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write('error: %s\n' % message)
            self.print_help()
            sys.exit(2)

    parser = ArgParser()
    parser.add_argument('-i','--inputfile', help="input .srt file", type=str, required=False)
    parser.add_argument('-o','--outputfile', help="output file", type=str, required=False)
    parser.add_argument('-p','--path', help="working directory", type=str, required=False)
    parser.add_argument('-s0','--subtitle0', help="1st bookmark (ID)", type=int, required=False)
    parser.add_argument('-t0','--timing0', help="1st bookmark (timing after sync)", type=str, required=False)
    parser.add_argument('-s1','--subtitle1', help="2nd bookmark (ID)", type=int, required=False)
    parser.add_argument('-t1','--timing1', help="2nd bookmark (timing after sync)", type=str, required=False)
    parser.add_argument('-d','--d_subno', help="increment to subtitle numbers", type=int, required=False)
    parser.add_argument('-L', action='store_true', help="show licence information", required=False)

    args = vars(parser.parse_args())
    
    # licence information
    if args['L']:
        run = False
        try:
            f = open('LICENSE', 'r')
            GPLv3 = f.read()
            print GPLv3
        except:
            print "*** licence file (LICENSE) is missing. ***"
    else:
        run = True
           
    # argument: path
    if args['path'] is None:
        path = os.getcwd()
    else:
        path = args['path']
        
    # argument: filename_in
    if args['inputfile'] is None:
        filename_in = None
    else:
        filename_in = args['inputfile']

    # argument: filename_out
    if args['outputfile'] is None:
        filename_out = None
    else:
        filename_out = args['outputfile']
        
    # argument: bmark0
    if args['subtitle0'] is None:
        s0 = None
    else:
        s0 = args['subtitle0']
    
    if args['timing0'] is None:
        t0 = None
    else:
        t0 = args['timing0']
        
    if s0 is not None and t0 is not None:
        bmark0 = (s0, t0)
    elif t0 is not None:
        bmark0 = t0
    else:
        bmark0 = None
        
    # argument: bmark1
    if args['subtitle1'] is None:
        s1 = None
    else:
        s1 = args['subtitle1']
    
    if args['timing1'] is None:
        t1 = None
    else:
        t1 = args['timing1']
        
    if s1 is not None and t1 is not None:
        bmark1 = (s1, t1)
    else:
        bmark1 = None
        
    # argument: d_subno
    if args['d_subno'] is None:
        d_subno = 0
    else:
        d_subno = args['d_subno']
        
    # subsync call        
    if run:
        subsync(filename_in=filename_in, bmark0=bmark0, bmark1=bmark1, \
                d_subno=d_subno, filename_out=filename_out, path=path)
