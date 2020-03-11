from PIL import Image
import re
import sys
import time


class PalletPicker:
    """This class takes in an image and finds its color pallet, that is,
    its 8 most common dominant colors.

    The way it works is -- It opens an image and uses pillow to
    convert its pixels into a list of tuples. It then goes through
    the list 8 times, creating a dictionary each time whose keys are
    every pixel tuple it finds, and whose values are how many of the
    other pixels in the list are very close to it in hue. For a high-
    resolution image, this would take days if not weeks - for example,
    if the image has 4 million pixels, the number of comparisons each
    time through the loop would be 4,000,000,000,000 comparisons. So I
    had to create lower resolution versions of the image, since I don't
    think making a computer work for 5 weeks to get a color pallet is a
    good use of resources. I also noticed that after a high enough
    resolution, the palette generated becomes indistinguishable from
    higher resolution versions.

    It then creates a new image with the pallet on the left and the
    original image on the right.

    I should be able to speed the program up by making the
    dictionary once, and then finding the 8 most used colors that are
    also different from each other in hue.
    """
    def __init__(self, filename):

        self.filename = filename

        if self.filename.count(".") != 1:
            print(f"Invalid image filename. Exiting.")
            sys.exit()

        self.filename_parts = re.search(r'(\w+)\.(\w+)', self.filename)

        im = Image.open(self.filename, 'r')
        im2_low_rez = Image.open(self.filename, 'r')

        self.list_of_most_used_colors = []

        self.image_type = self.filename_parts.group(2)

        if self.image_type not in ('jpg', 'jpeg', 'png'):
            print(f"Invalid image filename. Exiting.")
            sys.exit()

        self.new_filename = self.filename_parts.group(
            1) + "_with_pallet." + self.filename_parts.group(2)

        print(f"new filename: {self.new_filename}")

        print(f"im.size = {im.size}")

        self.current_pixel_count_main = im.size[0] * im.size[1]

        while self.current_pixel_count_main > 20000:
            new_size = (
            int((im.size[0] / 20) * 19), int((im.size[1] / 20) * 19))
            im = im.resize(new_size, Image.ANTIALIAS)
            self.current_pixel_count_main = im.size[0] * im.size[1]

        # Create a low rez version for the first pass through -- I
        # noticed that since the first color almost always appears
        # much more often than the other colors, I could lower the
        # resolution for a first pass -- this speeds up the algorithm
        # considerably, since the first pass is always the slowest.

        self.current_low_rez_pixel_count = (im2_low_rez.size[0]
                                            * im2_low_rez.size[1])
        while self.current_low_rez_pixel_count > 1000:
            new_size = (
            int((im2_low_rez.size[0] / 20) * 19),
            int((im2_low_rez.size[1] / 20) * 19))
            im2_low_rez = im2_low_rez.resize(new_size,
                                                       Image.ANTIALIAS)
            self.current_low_rez_pixel_count = (im2_low_rez.size[0]
                                   * im2_low_rez.size[1])

        self.pixel_list_original = list(im.getdata())

        self.pixel_list_low_rez = list(im2_low_rez.getdata())

        print(f"\nimage size: {im.size}")
        print(f"# of pixels: {im.size[0] * im.size[1]}")

        self.low_rez_filename = self.filename_parts.group(
            1) + "_low_rez." + self.filename_parts.group(2)

        im.save(self.low_rez_filename)

        print(f"len_pixel_list = {len(self.pixel_list_original)}")

        first_color = self.get_next_most_used_color(
            self.pixel_list_low_rez)
        self.list_of_most_used_colors.append(first_color)
        print(f"\ncolor #1: {first_color}")

        for i in range(2, 9):
            next_color = self.get_next_most_used_color(
                self.pixel_list_original)
            self.list_of_most_used_colors.append(next_color)
            print(f"\ncolor #{i}: {next_color}")

        im.close()

        im = Image.open(filename, 'r')

        self.pallet_width, self.pallet_height = self.get_pallet_dimensions(
            im)
        self.pallet_color_height = im.size[1] // 8
        self.last_pallet_color_height = (im.size[1]
                                         - (im.size[1] // 8))

        new_image_background = Image.new('RGB', (
            im.size[0] + self.pallet_width, im.size[1]))
        new_image_background.paste(im, (self.pallet_width, 0))

        pallet = Image.new('RGB', (self.pallet_width, im.size[1]))

        for j in range(7):
            new_color_image = Image.new(
                'RGB',
                (self.pallet_width, self.pallet_color_height),
                self.list_of_most_used_colors[j])
            pallet.paste(new_color_image, (0, j * self.pallet_color_height))
            new_color_image.close()

        last_color_image = Image.new(
            'RGB',
            (self.pallet_width, self.last_pallet_color_height),
            self.list_of_most_used_colors[7])
        pallet.paste(last_color_image, (0, 7 * self.pallet_color_height))
        last_color_image.close()

        pallet.save(f'newpallet.{self.image_type}')

        new_image_background.paste(pallet, (0, 0))

        pallet.close()

        new_image_background.save(self.new_filename)
        new_image_background.close()
        im.close()
        im2_low_rez.close()

    def get_next_most_used_color(self, pixel_list) -> tuple:
        color_dict = {}
        t1 = time.time()
        for pixel1 in pixel_list:
            too_close_to_already_listed_color = False
            if self.list_of_most_used_colors:
                for color in self.list_of_most_used_colors:
                    if not PalletPicker.different_color(pixel1, color):
                        too_close_to_already_listed_color = True
                        break
            if too_close_to_already_listed_color:
                continue
            color_dict[pixel1] = -1
            for pixel2 in pixel_list:
                if PalletPicker.similar_color(pixel1, pixel2):
                    color_dict[pixel1] += 1
        t2 = time.time()
        print(f"time: {t2 - t1} seconds")

        # Load first key/value pair from color_dict:
        most_used_color = next(iter(color_dict))

        for color_key in color_dict.keys():
            if color_dict[color_key] > color_dict[most_used_color]:
                most_used_color = color_key

        return most_used_color

    @staticmethod
    def similar_color(color1: tuple, color2: tuple) -> bool:
        """Returns True if color1 and color2 (expressed as RGB pixel
        tuples) are close hues.
        """
        if (abs(color1[0] - color2[0]) < 6 and
                abs(color1[1] - color2[1]) < 6 and
                abs(color1[2] - color2[2]) < 6):
            return True
        else:
            return False

    @staticmethod
    def different_color(color1: tuple, color2: tuple) -> bool:
        """Returns True if color1 and color2 (expressed as RGB pixel
        tuples) are not close to each other in the color spectrum.
        """
        if (abs(color1[0] - color2[0]) > 50 or
                abs(color1[1] - color2[1]) > 50 or
                abs(color1[2] - color2[2]) > 50):
            return True
        else:
            return False

    @staticmethod
    def get_pallet_dimensions(PIL_instance):
        original_width = PIL_instance.size[0]
        original_height = PIL_instance.size[1]
        pallet_width = original_width // 5
        pallet_height = original_height // 2
        return pallet_width, pallet_height


if __name__ == '__main__':
    picture_with_pallet = PalletPicker('corral_reef.jpeg')



