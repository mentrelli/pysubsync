# pysubsync 
This python script takes a file .srt of subtitles and changes the 
chronology and/or re-numbers the subtitles, in order to synchronize
the subtitles. The user is expected to provide, in addition to the
input file, one or two bookmarks. If only one bookmark is given, the
subtitles are either all shifted of "hh:mm:ss,mms" (absolute shift),
if the bookmark has the form "hh:mm:ss,mms", either they are shifted
in a way that the subtitle with number ID will be displayed at time
"hh:mm:ss,mms", if the bookmark has the form (ID, "hh:mm:ss,mms").
If the second bookmark is provided, it must have the form 
(ID2, "hh:mm:ss,mms2"). In this case, the subtitle with number ID2 
will be displayed at time "hh:mm:ss,mms2" and the timings of all the
other subtitles will be computed by means of a linear interpolation/
extrapolation after shifting the two bookmarked subtitles.


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

    $ subsync("file.srt", "00:01:10,512")
    
Shifts all the subtitles forward in time of 00:01:10,512
(relative shift). The output file is named "file.subsync.srt".

    $ subsync("file.srt", "-5:10")
    
Shifts all the subtitles backwards in time of 00:05:10,000
(relative shift). The output file is named "file.subsync.srt".
        
    $subsync("file.srt", (10, "20:00,1") )
    
Shifts all the subtitles such that the subtitle with number 10
appears at time 00:20:00,100 (absolute shift). The output file 
is named "file.subsync.srt".
        
    $ subsync("file.srt", (1, "1:11"), (1000, "1:59:59"))
    
Shifts all the subtitles such that the subtitle with number 1
appears at time 00:01:11,000 and the subtitle with number 1000 
appears at time 01:59:59,000 (absolute shifts). The times at 
which all the other subtitles are displayed are computed by 
means of a linear interpolation/extrapolation. The output file 
is called "file.subsync.srt". Both the input file and the output
file are found in the current path.
        
    $ subsync("file.srt", (10, "3:00"), (900, "1:15:00"), d_subno=100, "newfile.srt", path="/media/videos")
    
Shifts all the subtitles such that the subtitle with number 10
appears at time 00:03:00,000 and the subtitle with number 900 
appears at time 01:15:00,000 (absolute shifts). The times at 
which all the other subtitles are displayed are computed by 
means of a linear interpolation/extrapolation. In addition to the
shifts, the numbering of the subtitles is increased by 100 
(this feature might be useful in case of subtitles split in 
multiple files that should be merged in a single file). The 
output file is called "newfile.srt". Both the input file and the
output file are found in the /media/videos.

by Undy, September 20, 2015 (v.1.0) 
         November 2/3, 2015 (v.2.0)   