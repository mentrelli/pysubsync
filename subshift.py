# -*- coding: utf-8 -*-
"""
Created on Sun Sep 20 15:32:49 2015

@author: andrea
"""
#  "Debugging is twice as hard as writing the code in the first place.
#   Therefore, if you write the code as cleverly as possible, you are, by 
#   definition, not smart enough to debug it." 
#                        (Brian Kernighan, The Elements of Programming Style)


# example of usage:
#   subshift("There Will Be Blood.DVDRip.DiAMOND.part1.en.srt", tt_a=((0,4,56,596),(0,4,41,0)), tt_b=((1,12,11,93),(1,9,10,500)), d_subno=0)
#   subshift("There Will Be Blood.DVDRip.DiAMOND.part2.en.srt", tt_a=((0,0,25,961),(1,10,17,500)), tt_b=((1,17,55,773),(2,24,37,0)), d_subno=623)
# or
#   subshift("There Will Be Blood.DVDRip.DiAMOND.part1.en.srt", dm=1, ds=9, dms=774, dir=-1)

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
        
        
def _tt2ms(tt):
    h, m, s, ms = tt
    return 1000*(h*3600+m*60+s) + ms




def subshift(subfile, dh=0, dm=0, ds=0, dms=0, dir=1,
             tt_a=None, tt_b=None, d_subno=0, newsubfile=None):
    """
    Takes a file .srt of subtitles (subfile) and changes the time placement of
    the subtitles, producing a new file (newsubfile).

    If the user provides as input

      tt_a = ( (h_a0, m_a0, s_a0, ms_a0), (h_a1, m_a1, s_a1, ms_a1) ) 

    and

      tt_b = ( (h_b0, m_b0, s_b0, ms_b0), (h_b1, m_b1, s_b1, ms_b1) ),

    the subtitles are repositioned such that the subtitle given at time tt_a[0]
    will be displayed as time tt_a[1], and the subtitle given at time tt_b[0]
    will be displayed at time tt_b[1]. The subtitles are re-positioned on the
    basis of a linear interpolation/extrapolation betwwen the two provided
    subtitles.
    
    If the user, instead of tt_a and tt_b, provides as input any of dh, dm, ds,
    dms, the subtitles are merely shifted of dt=(dh, dm, ds, dms). In this 
    case, dir indicates the time-direction of the translation (forward in time
    if dir=1; backwards in time if dir=-1).
    
    In addition to the repositioning of the subtitles, the numbering of the 
    subtitles may be changed providing d_subno as input, which will be added
    to the original numbering. (This feature might be useful in case of
    subtitles which are split in multiple files should be merged in a single 
    file).
    
    The name of teh output file, if not provided by the user is obtained
    appending '.subshifted' to the name of the file.
    
    The time measures are given in hours, minutes, seconds, milliseconds,
    respectively: (h, m, s, ms).
    
        < by Undy / September 20, 2015 (v.1.0) >
    """
    
    import os
    import re
    
    # check if file exist
    if not os.path.isfile(subfile):
        print "... cannot process the file '{}'.".format(subfile)
        return None
        
    # define output file    
    if newsubfile is None:
        if subfile[-4:]==".srt":
            newsubfile = subfile[:-4] + ".subshifted.srt"
        else:
            newsubfile = subfile + ".subshifted"
    

    # elaborate the time-shift/stretch
    if tt_a is not None and tt_b is not None:
        flag_stretch = True
        ta0, ta1 = _tt2ms(tt_a[0]), _tt2ms(tt_a[1])
        tb0, tb1 = _tt2ms(tt_b[0]), _tt2ms(tt_b[1])
        dt0 = dh, dm, ds, dms0 = 0, 0, 0, abs(ta1-ta0)
        if ta0 > ta1:
            dir = -1
        else:
            dir = 1
        dms1 = (tb1-tb0) - (ta1-ta0)
        shrink = round(float(tb1-tb0)/(ta1-ta0), 3)
        str_dt = _formattime(_int2str(_timeshift((0,)*4, dt0, 1)))
    else:
        flag_stretch, shrink = False, 1
        dt = dh, dm, ds, dms
        str_dt = _formattime(_int2str(_timeshift((0,)*4, dt, 1)))

    str_dir = 'forward' if dir>0 else 'backward'
    
    
    with open(subfile, 'r') as file_in, open(newsubfile, 'w') as file_out:
        
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
                t0 = h0, m0, s0, ms0
                t0 = _str2int(t0)
                if flag_stretch:
                    dt = (0, 0, 0, dms0*dir+dms1*(_tt2ms(t0)-ta0)/(tb0-ta0))
                    t0 = _timeshift(t0, dt, 1)
                else:
                    t0 = _timeshift(t0, dt, dir)
                t0 = _int2str(t0)
                str_t0 = _formattime(t0)
                
                # shift of the final time
                t1 = h1, m1, s1, ms1
                t1 = _str2int(t1)
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
        
    print "... input file:  '{}'".format(subfile)
    print "... output file: '{}'".format(newsubfile)