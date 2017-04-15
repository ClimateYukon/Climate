import os 
import glob
import imageio
result_directory = '/workspace/Shared/Users/jschroder/TMP/'
TMP = '/workspace/Shared/Users/jschroder/AK_warming_movie/Data/Average_process/*'
official = '/workspace/Shared/Users/jschroder/AK_warming_movie/Data/centered_running_avg_processed_CRUTS32_official/*'
os.chdir(result_directory)

for directory in glob.glob(official):
	os.chdir(os.path.join(directory,'png'))
	#os.chdir(directory)
	l=glob.glob('*.png')
	year = os.path.splitext( os.path.basename( l[0]) )[0].split( '_' )[-3]
	a = os.path.splitext( os.path.basename( l[0]) )[0].split( '_' )[2]
	b = os.path.splitext( os.path.basename( l[0]) )[0].split( '_' )[1]
	norm = os.path.splitext( os.path.basename( l[0]) )[0].split( '_' )[-1]
	CRU = os.path.splitext( os.path.basename( l[0]) )[0].split( '_' )[5]
	gif = 'AK_%s%s_1950_2000_CRU%s_%s_norm1%s.gif'%(b,a,CRU,year,norm)
	mp = 'AK_%s%s_1950_2000_CRU%s_%s_norm1%s.mp4'%(b,a,CRU,year,norm)
	cmd = '*.png'
	os.system('ffmpeg -y -f image2 -r 2 -s hd1080 -pix_fmt yuv420p -pattern_type glob -i  "%s" "%s"' %(cmd,mp))
	os.system('convert -background white -alpha remove -layers OptimizePlus -delay 30x100 -size 1080x920 "%s" -loop 0 "%s"'%(cmd,gif))
	# convert -background white -alpha remove -layers OptimizePlus -delay 25x100 -size 1080x920 *.png -loop 0 ps1.gif


# year = os.path.splitext( os.path.basename( directory) )[0].split( '_' )[-3]
# method = os.path.splitext( os.path.basename( directory) )[0].split( '_' )[2]
# norm = os.path.splitext( os.path.basename( directory) )[0].split( '_' )[-1]

#l = glob.glob( '*.png' )
# output = 'warming_ak_movie_%s_%s_norm1%s.mp4' %(method,year,norm)
# cmd = '*.png'
# os.system('ffmpeg -y -f image2 -r 3 -s hd1080 -pix_fmt yuv420p -pattern_type glob -i  "%s" "%s"' %(cmd,output))
# directory = '/workspace/Shared/Users/jschroder/AK_warming_movie/Data/anomalie_AK_can/png'
# os.chdir(directory)

# l = glob.glob( '*.png' )