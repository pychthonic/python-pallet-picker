from PIL import Image
import re
import sys
import time

"""This script takes in an image and finds its color pallet, that is,
its 6 most common colors. It then creates a new image with the pallet
on the left and the original image on the right.
Next step is making it object-oriented, less messy, and adding
comments to explain why the code does things certain ways. Also need
to make it account for when there are less than 8 colors in the
palette. None of these changes will be hard, but I have to go to bed
since it's a work night so I'll have to finish it some time this week.
"""

def similar_color(color1: tuple, color2: tuple) -> bool:
    if (abs(color1[0] - color2[0]) < 6 and
            abs(color1[1] - color2[1]) < 6 and
            abs(color1[2] - color2[2]) < 6):
        return True
    else:
        return False

def different_color(color1: tuple, color2: tuple) -> bool:
    if (abs(color1[0] - color2[0]) > 50 or
            abs(color1[1] - color2[1]) > 50 or
            abs(color1[2] - color2[2]) > 50):
        return True
    else:
        return False

def get_next_most_used_color(pixel_list: list,
                             list_of_most_used_colors: list = []) -> tuple:
    color_dict = {}
    t1 = time.time()
    for pixel1 in pixel_list:
        too_close_to_already_listed_color = False
        if list_of_most_used_colors:
            for color in list_of_most_used_colors:
                if not different_color(pixel1, color):
                    too_close_to_already_listed_color = True
                    break
        if too_close_to_already_listed_color:
            continue
        color_dict[pixel1] = -1
        for pixel2 in pixel_list:
            if similar_color(pixel1, pixel2):
                color_dict[pixel1] += 1
    t2 = time.time()
    print(f"time: {t2 - t1} seconds")
    most_used_color = next(iter(color_dict))

    for color_key in color_dict.keys():
        if color_dict[color_key] > color_dict[most_used_color]:
            most_used_color = color_key

    return most_used_color

def get_pallet_dimensions(PIL_instance):
    original_width = PIL_instance.size[0]
    original_height = PIL_instance.size[1]
    print(f"original_width = {original_width}")
    print(f"original_height = {original_height}")
    pallet_width = original_width // 5
    pallet_height = original_height // 2
    return pallet_width, pallet_height


filename = "penguins.jpeg"

if filename.count(".") != 1:
    print(f"Invalid image filename. Exiting.")
    sys.exit()

filename_parts = re.search(r'(\w+)\.(\w+)', filename)

image_type = filename_parts.group(2)

if image_type not in ('jpg', 'jpeg', 'png'):
    print(f"Invalid image filename. Exiting.")
    sys.exit()

new_filename = filename_parts.group(1) + "_with_pallet." + filename_parts.group(2)

print(f"new filename: {new_filename}")

im = Image.open(filename, 'r')

print(f"im.size = {im.size}")

current_pixel_count = im.size[0] * im.size[1]

while current_pixel_count > 20000:
    new_size = (int((im.size[0]/20) * 19), int((im.size[1]/20) * 19))
    im = im.resize((new_size), Image.ANTIALIAS)
    current_pixel_count = im.size[0] * im.size[1]

im2 = Image.open(filename, 'r')
while current_pixel_count > 1000:
    new_size = (int((im2.size[0]/20) * 19), int((im2.size[1]/20) * 19))
    im2 = im2.resize((new_size), Image.ANTIALIAS)
    current_pixel_count = im2.size[0] * im2.size[1]

print(f"\nimage size: {im.size}")
print(f"# of pixels: {im.size[0] * im.size[1]}")

low_rez_filename = filename_parts.group(1) + "_low_rez." + filename_parts.group(2)

im.save(low_rez_filename)

pixel_list = list(im.getdata())

pixel_list_low_rez = list(im2.getdata())
print(f"len_pixel_list = {len(pixel_list)}")


list_of_most_used_colors = []

for i in range(1):
    next_color = get_next_most_used_color(pixel_list_low_rez,
                                          list_of_most_used_colors)
    list_of_most_used_colors.append(next_color)
    print(f"\ncolor #{i + 1}: {next_color}")

for i in range(8):
    next_color = get_next_most_used_color(pixel_list, list_of_most_used_colors)
    list_of_most_used_colors.append(next_color)
    print(f"\ncolor #{i + 3}: {next_color}")

im.close()

im = Image.open(filename, 'r')

pallet_width, pallet_height = get_pallet_dimensions(im)
pallet_color_height = im.size[1] // 8
last_pallet_color_height = im.size[1] - (im.size[1] // 8)

new_image_background = Image.new('RGB', (im.size[0] + pallet_width, im.size[1]))
new_image_background.paste(im, (pallet_width, 0))

pallet = Image.new('RGB', (pallet_width, im.size[1]))

for j in range(7):
    new_color_image = Image.new(
        'RGB',
        (pallet_width, pallet_color_height),
        list_of_most_used_colors[j])
    pallet.paste(new_color_image, (0, j * pallet_color_height))
    new_color_image.close()

last_color_image = Image.new('RGB',
                             (pallet_width, last_pallet_color_height),
                             list_of_most_used_colors[7])
pallet.paste(last_color_image, (0, 7 * pallet_color_height))
last_color_image.close()

pallet.save(f'newpallet.{image_type}')

new_image_background.paste(pallet, (0, 0))


pallet.close()

new_image_background.save(new_filename)
new_image_background.close()
im.close()
im2.close()








