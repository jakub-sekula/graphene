from datetime import datetime
import contextlib
import os,shutil,time


def generate_filename(extension):
   time = datetime.now().strftime("%H-%M-%S_%d-%b-%Y")
   
   if extension != "":
      fname = f"Capture_{time}.{str(extension)}"
      return fname

   return f"Capture_{time}"


def movefile(src,dest,filename):
	filesize = os.path.getsize(os.path.join(src,filename))/1024**2 # in Mbytes

	print(f"\nMoving file \"{filename}\" ({filesize:.0f}MB) from {src} to {dest}...")
	starttime = time.time()
	shutil.move(os.path.join(src,filename),os.path.join(dest,filename))
	endtime = time.time()
	elapsed_time = endtime - starttime
	average_speed = filesize / elapsed_time
	print(f"Move completed in {elapsed_time:.2f}s at average speed of {average_speed:.2f} MB/s\n")


@contextlib.contextmanager
def change_directory(path):
    """A context manager which changes the working directory to the given
    path, and then changes it back to its previous value on exit.

    """
    prev_cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(prev_cwd)