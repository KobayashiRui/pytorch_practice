import glob
import sys

img_dir = sys.argv[1]+"*"
output_file = "./train.txt"
file_datas = glob.glob(img_dir)

with open(output_file, mode='w') as f:
    for img_file in (file_datas):
        f.write("data/custom/"+img_file+"\n")

