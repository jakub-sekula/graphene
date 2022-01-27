import os,shutil,time

SRC = "G:\\"
DEST = "C:\\Users\\UVis\\Desktop"
FILENAME = "Capture-21-22-00.avi"

def move(src,dest,filename):
	print(f"Moving file {filename} from {src} to {dest}...")
	filesize = os.path.getsize(os.path.join(src,filename))
	starttime = time.time()
	shutil.move(os.path.join(src,filename),os.path.join(dest,filename))
	endtime = time.time()
	elapsed_time = endtime - starttime
	average_speed = (filesize/1024**2) / elapsed_time
	print(f"Move completed in {elapsed_time:.2f}s at average speed of {average_speed:.2f} MB/s")

move(SRC,DEST,FILENAME)

for i in range(6):
	print(f"Cooling down, {6-i} seconds left...")
	time.sleep(1)

move(DEST,SRC,FILENAME)
