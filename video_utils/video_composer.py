import PIL
import skvideo.io as skv
import skimage.io as ski
from skimage import color
import numpy as np
import os
import glob

class Movie:
    def __init__(self, directory, fformat='.png', cleanup=True):
        self.directory = directory
        self.filename = ""
        self.format = fformat
        self.framerate = 24
        self.cleanup = cleanup

    def create_video(self):
        '''
        composes video from .fformat files, requires ffmpeg
        '''
        fileList = glob.glob(os.path.join(self.directory, '*' + self.format))
        if len(fileList) == 0:
            #TODO error
            print("No files in provided directory!")
            return
        total_movie = []
        fileList.sort(key=lambda x: os.path.basename(x))
        print("Merging up the files. This might take a moment...")
        for filename in fileList:
            print(filename)
            img = ski.imread(filename)
            for i in range(self.framerate):
                total_movie.append(img)
        total_movie = np.array(total_movie)
        skv.vwrite(os.path.join(self.directory, 'movie.mkv'), total_movie)
        self.do_cleanup(fileList)

    def do_cleanup(self, filenames):
        print("Cleaning up the files ...")
        for filename in filenames:
            try:
                os.remove(filename)
            except OSError:
                pass


if __name__ == "__main__":
    mv = Movie('./Screenshots')
    mv.create_video()
