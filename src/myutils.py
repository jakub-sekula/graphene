from datetime import datetime
import contextlib
import os,shutil,time,sys
import msvcrt


def generate_filename(extension, *args):
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

    if (elapsed_time > 0):
        average_speed = filesize / elapsed_time
    else:
        average_speed=0.00

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
    

class TimeoutExpired(Exception):
    pass

def input_with_timeout(prompt, timeout, timer=time.monotonic):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    endtime = timer() + timeout
    result = []
    while timer() < endtime:
        if msvcrt.kbhit():
            result.append(msvcrt.getwche()) #XXX can it block on multibyte characters?
            if result[-1] == '\r':
                return ''.join(result[:-1])
        time.sleep(0.04) # just to yield to other processes/threads
    raise TimeoutExpired