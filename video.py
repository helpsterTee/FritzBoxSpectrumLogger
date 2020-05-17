import ffmpeg
import sys, os
import glob
import pathlib

if len(sys.argv) < 3:
    print("Please use start and end timestamp, e.g.: python video.py 1589720364 1589725364")
else:
    start = int(sys.argv[1])
    end = int(sys.argv[2])

    path = str(pathlib.Path(__file__).parent.absolute())
    flist = glob.glob('./output/*.png')
    range_list = []

    # write text file for input to ffmpeg
    outfile = open('./output/tmplist.txt', 'w')
    for f in sorted(flist):
        int_f = int(f[9:-4])
        if int_f >= start and int_f <= end:
            outfile.write("file '"+path+f[1:]+"'\n")
            outfile.write("duration 0.6\n")
    outfile.close()

    stream = ffmpeg.input(path+'/output/tmplist.txt', format='concat', safe=0)
    stream = ffmpeg.output(stream, path+"/output/"+sys.argv[1]+"_"+sys.argv[2]+".mp4")
    ffmpeg.run(stream)
