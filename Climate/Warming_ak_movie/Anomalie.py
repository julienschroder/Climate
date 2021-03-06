def get_mon_year( x ):
	month, year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[5:]
	return {'month':month, 'year':year, 'fn':x}

def get_year( x ):
	year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[-1:]
	return {'year':year[0], 'fn':x}

def return_means( list_files ):
	out = [rasterio.open(x).read(1) for x in list_files]

	meta = rasterio.open(list_files[0]).meta
	result = np.mean(out,axis=0,dtype=np.float32)

	baseline_path = os.path.join( anomalie_path , 'Baseline')

	if not os.path.exists( baseline_path ):
		os.mkdir( baseline_path )
	

	month = get_mon_year(list_files[0])['month']
	output_filename = os.path.join( baseline_path, 'cru_TS31_1951-2000_%s_average.tif'%(month) )
	
	result[result < -1000] = -9999

	meta.update(nodata=-9999)
	with rasterio.open( output_filename, 'w', **meta ) as out:
	  out.write( result, 1 )

	return output_filename

def return_anomalies(bounds, files ):
	'''This function is able to take files as a list of file that is averaged and then substracted,
	or a single file depending of what is needed''' 

	tif_path = os.path.join( anomalie_path , 'tif_anomalie')
	if not os.path.exists( tif_path ):
		os.mkdir( tif_path )
	
	png_path = os.path.join( anomalie_path , 'png')
	if not os.path.exists( png_path ):
		os.mkdir( png_path )
	

	if type(files) == list :
		out = [rasterio.open(x).read(1) for x in files]
		modeled= np.mean(out,axis=0,dtype=np.float32)
		meta = rasterio.open(files[0]).meta
		month, year = os.path.splitext( os.path.basename( files[0] ) )[0].split( '_' )[5:]
		tif_filename = os.path.join( tif_path,'_'.join([ 'CRU_TS31_anom',str(month) ]) + '.tif' )
		png_filename = os.path.join( png_path, '_'.join([ 'CRU_TS31_anom',str(month) ]) + '.png' )


	else : 
		modeled = rasterio.open(files).read(1)
		month, year = os.path.splitext( os.path.basename( files ) )[0].split( '_' )[5:]
		meta = rasterio.open(files).meta
		tif_filename = os.path.join( tif_path,'_'.join([ 'CRU_TS31_anom',str(year),str(month) ]) + '.tif' )
		png_filename = os.path.join( png_path, '_'.join([ 'CRU_TS31_anomalie',str(year),str(month) ]) + '.png' )


	modeled[modeled < -1000] = None


	base = glob.glob( os.path.join( os.path.join( anomalie_path , 'Baseline'), '*%s_average.tif' %month ))
	base_arr = rasterio.open(base[0]).read(1)

	result = np.subtract(modeled, base_arr)


	#UGLY!! But does the job of ignoring the no data value while plotting
	result[result < -1000] = None
	plt.figure(figsize=(20,11.25))

	#http://matplotlib.org/api/pyplot_summary.html?highlight=colormaps#matplotlib.pyplot.colormaps
	plt.axis('off')

	cmap = cm.RdYlBu_r

	norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)

	
	plt.figtext(.1,.9,'%s - %s'%(month , year), fontsize=40, ha='left')

	img = plt.imshow(result, interpolation='nearest', cmap=cmap, norm=norm)
	plt.colorbar(img, cmap=cmap, norm=norm, boundaries=bounds, ticks=ticks)
	plt.savefig(png_filename)
	

	with rasterio.open( tif_filename, 'w', **meta ) as out:
		out.write( result, 1 )
	
def make_list(df , start , end, month = None):

	if month == None :
		return df.fn[(df.year >= str(start)) & (df.year <= str(end))].tolist()
	else :
		return df.fn[(df.month==str(month)) & (df.year >= str(start)) & (df.year <=str (end))].tolist()

if __name__ == '__main__':

	import matplotlib
	matplotlib.use('Agg')
	import rasterio, fiona, glob, os
	import numpy as np
	import itertools
	from functools import partial
	import pandas as pd
	from pathos import multiprocessing as mp
	import matplotlib.pyplot as plt
	import matplotlib.cm as cm
	import pickle
	import time

	#path = '/Data/Base_Data/Climate/AK_800m/historical/singleBand/CRU/cru_TS31/historical/tas'
	start = 1901
	end = 2009
	yearly_data = '/workspace/Shared/Users/jschroder/AK_warming_movie/Data/Yearly_avg'
	anomalie_path = '/workspace/Shared/Users/jschroder/AK_warming_movie/Data/anomalie_AK_can_peryear'
	if not os.path.exists( anomalie_path ):
		os.mkdir( anomalie_path )
	#path_data = '/Data/Base_Data/Climate/AK_800m/historical/singleBand/CRU/cru_TS31/historical/tas'
	path_data = '/Data/Base_Data/Climate/AK_CAN_2km/historical/singleBand/CRU/cru_TS31/historical/tas'

	l = glob.glob( os.path.join( path_data , '*.tif' ))
	monyear = map( get_mon_year, l )
	df = pd.DataFrame( monyear )
	df = df.sort_values(by=['year', 'month'], ascending=[1, 1])
	
	bounds = np.arange(-5,5,0.1)
	ticks = np.arange(-5,5,1)

	base_list = [make_list(df, 1951 , 2000 , x ) for x in np.unique(df.month)]

	pool = mp.Pool(32)
	pool.map( return_means,base_list)
	pool.close()
	pool.join()
	

	# files = [make_list(df, 2000 , 2009 , x ) for x in np.unique(df.month)]
	files = make_list(df, 2000 , 2009)
	pool = mp.Pool( 32 )
	func = partial(return_anomalies, bounds)
	pool.map( func,files)
	pool.close()
	pool.join()

########################################################################################################################################
################################################################################################################################################################################################################################################################################
########################################################################################################################################
########################################################################################################################################
########################################################################################################################################
########################################################################################################################################
################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################
########################################################################################################################################
########################################################################################################################################
########################################################################################################################################
########################################################################################################################################




















def get_mon_year( x ):
	month, year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[5:]
	return {'month':month, 'year':year, 'fn':x}

def get_year( x ):
	year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[-1:]
	return {'year':year[0], 'fn':x}

def return_means( list_files ):
	out = [rasterio.open(x).read(1) for x in list_files]

	meta = rasterio.open(list_files[0]).meta
	result = np.mean(out,axis=0,dtype=np.float32)

	baseline_path = os.path.join( anomalie_path , 'Baseline')

	if not os.path.exists( baseline_path ):
		os.mkdir( baseline_path )
	
	output_filename = os.path.join( baseline_path, 'cru_TS31_1951-2000_average.tif') 
	
	result[result < -1000] = -9999

	meta.update(nodata=-9999)
	with rasterio.open( output_filename, 'w', **meta ) as out:
	  out.write( result, 1 )

	return output_filename

def return_anomalies(bounds, files ):
	'''This function is able to take files as a list of file that is averaged and then substracted,
	or a single file depending of what is needed''' 

	tif_path = os.path.join( anomalie_path , 'tif_anomalie')
	if not os.path.exists( tif_path ):
		os.mkdir( tif_path )
	
	png_path = os.path.join( anomalie_path , 'png')
	if not os.path.exists( png_path ):
		os.mkdir( png_path )
	


	out = [rasterio.open(x).read(1) for x in files]
	modeled= np.mean(out,axis=0,dtype=np.float32)
	meta = rasterio.open(files[0]).meta
	month, year = os.path.splitext( os.path.basename( files[0] ) )[0].split( '_' )[5:]
	tif_filename = os.path.join( tif_path,'_'.join([ 'CRU_TS31_anom',str(year) ]) + '.tif' )
	png_filename = os.path.join( png_path, '_'.join([ 'CRU_TS31_anom',str(year) ]) + '.png' )


	modeled[modeled < -1000] = None


	base = glob.glob( os.path.join( os.path.join( anomalie_path , 'Baseline'), '*_average.tif' ))
	base_arr = rasterio.open(base[0]).read(1)

	result = np.subtract(modeled, base_arr)


	#UGLY!! But does the job of ignoring the no data value while plotting
	result[result < -1000] = None
	plt.figure(figsize=(20,11.25))

	#http://matplotlib.org/api/pyplot_summary.html?highlight=colormaps#matplotlib.pyplot.colormaps
	plt.axis('off')

	cmap = cm.RdYlBu_r

	norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)

	
	plt.figtext(.1,.9,' %s'%(month , year), fontsize=40, ha='left')

	img = plt.imshow(result, interpolation='nearest', cmap=cmap, norm=norm)
	plt.colorbar(img, cmap=cmap, norm=norm, boundaries=bounds, ticks=ticks)
	plt.savefig(png_filename)
	

	with rasterio.open( tif_filename, 'w', **meta ) as out:
		out.write( result, 1 )
	
def make_list(df , start , end, month = None):

	if month == None :
		return df.fn[(df.year >= str(start)) & (df.year <= str(end))].tolist()
	else :
		return df.fn[(df.month==str(month)) & (df.year >= str(start)) & (df.year <=str (end))].tolist()

if __name__ == '__main__':

	import matplotlib
	matplotlib.use('Agg')
	import rasterio, fiona, glob, os
	import numpy as np
	import itertools
	from functools import partial
	import pandas as pd
	from pathos import multiprocessing as mp
	import matplotlib.pyplot as plt
	import matplotlib.cm as cm
	import pickle
	import time
  	start = 1951
  	end = 2009
	yearly_data = '/workspace/Shared/Users/jschroder/AK_warming_movie/Data/run_avg3_tif/run_avg'
	anomalie_path = '/workspace/Shared/Users/jschroder/AK_warming_movie/Data/anomalie_AK_can_peryear_withoutmonth'
	if not os.path.exists( anomalie_path ):
		os.mkdir( anomalie_path )
	#path_data = '/Data/Base_Data/Climate/AK_800m/historical/singleBand/CRU/cru_TS31/historical/tas'
	path_data = '/Data/Base_Data/Climate/AK_CAN_2km/historical/singleBand/CRU/cru_TS31/historical/tas'

	l = glob.glob( os.path.join( path_data , '*.tif' ))
	monyear = map( get_mon_year, l )
	df = pd.DataFrame( monyear )
	df = df.sort_values(by=['year', 'month'], ascending=[1, 1])
	
	bounds = np.arange(-5,5,0.1)
	ticks = np.arange(-5,5,1)

	base_list = [make_list(df, 1951 , 2000 )]

	pool = mp.Pool(32)
	pool.map( return_means,base_list)
	pool.close()
	pool.join()
	
	print 'done with baseline'
	k = 5
	files = [make_list(df,start,j) for j in range(start + k, end+k ,k)]
	#files = [make_list(df,i,j) for i,j in zip(range(start, end, k),range(start + k, end + k ,k))]
	pool = mp.Pool( 32 )
	func = partial(return_anomalies, bounds)
	pool.map( func,files)
	pool.close()
	pool.join()

