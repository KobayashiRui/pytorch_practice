from PIL import Image
import glob
import sys

class image_aspect():

    def __init__(self, image_file, aspect_width, aspect_height):
        self.img_type = image_file[-3:]
        self.img = Image.open(image_file)
        self.aspect_width = aspect_width
        self.aspect_height = aspect_height
        self.result_image = None

    def change_aspect_rate(self):

        img_width = self.img.size[0]
        img_height = self.img.size[1]

        if img_width > img_height:
            rate = self.aspect_width / img_width
        else:
            rate = self.aspect_height / img_height

        rate = round(rate, 1)
        self.img = self.img.resize((int(img_width * rate), int(img_height * rate)))
        return self

    def past_background(self):
        self.result_image = Image.new("RGB", [self.aspect_width, self.aspect_height], (255, 255, 255))
        self.result_image.paste(self.img, (int((self.aspect_width - self.img.size[0]) / 2), int((self.aspect_height - self.img.size[1]) / 2)))
        return self

    def save_result(self, file_name):
        self.result_image.save(file_name,'JPEG',quality=100)

if __name__ == "__main__":
    image_dir = sys.argv[1]+"*"
    output_image_dir = sys.argv[2]
    file_datas = glob.glob(image_dir)
    for i,image_file in enumerate(file_datas):
        image_aspect(image_file, 416,416)\
            .change_aspect_rate()\
            .past_background()\
            .save_result(output_image_dir+'data'+str(i)+'.jpg')
