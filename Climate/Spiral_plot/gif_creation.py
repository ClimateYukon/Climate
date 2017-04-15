import os 
import glob

result_directory = '/workspace/Shared/Users/jschroder/TMP/'
TMP = '/workspace/Shared/Users/jschroder/AK_warming_movie/Data/Average_process/*'
official = '/workspace/Shared/Users/jschroder/TMP/spiral_Arctic'
os.chdir(result_directory)


os.chdir(official)
#os.chdir(directory)
l=glob.glob('*.png')
# year = os.path.splitext( os.path.basename( l[0]) )[0].split( '_' )[-3]
# a = os.path.splitext( os.path.basename( l[0]) )[0].split( '_' )[2]
# b = os.path.splitext( os.path.basename( l[0]) )[0].split( '_' )[1]
# norm = os.path.splitext( os.path.basename( l[0]) )[0].split( '_' )[-1]
# CRU = os.path.splitext( os.path.basename( l[0]) )[0].split( '_' )[5]
gif = '/workspace/UA/jschroder/spiral_movie_Arctic_low.gif'
cmd = '*.png'
#os.system('ffmpeg -y -f image2 -r 2 -s hd1080 -pix_fmt yuv420p -pattern_type glob -i  "%s" "%s"' %(cmd,mp))
os.system('convert -background white -alpha remove -layers OptimizePlus -delay 1x100 -size 640x480 "%s" -loop 0 "%s"'%(cmd,gif))
# convert -background white -alpha remove -layers OptimizePlus -delay 25x100 -size 1080x920 *.png -loop 0 ps1.gif
