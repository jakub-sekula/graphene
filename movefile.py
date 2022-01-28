import time
from myutils import generate_filename, movefile

SRC = "D:\\"
DEST = "C:\\Users\\UVis\\Desktop"
FILENAME = "Capture-21-22-00.avi"

print("------------------------------------------------------------------------------")
print("This will benchmark the SSD and RAM disk by moving a large file back and forth")
print("------------------------------------------------------------------------------")

movefile(SRC,DEST,FILENAME)

timeout = 2

for i in range(timeout):
	print(f"Cooling down, {timeout-i} seconds left...")#, end='\r')
	time.sleep(1)

movefile(DEST,SRC,FILENAME)