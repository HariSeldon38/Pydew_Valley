from csv import reader
from os import walk
import pygame

def import_csv_layout(path):
    terrain_map = []
    with open(path, "r") as level_map:
        layout = reader(level_map, delimiter = ",")
        for row in layout:
            terrain_map.append(list(row))
    return terrain_map

def import_folder(path):
    surface_list = []

    for _,__, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list

def import_folder_with_names(path):
    surface_dict = {}
    for _,__, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_dict[image.split(".")[0]] = image_surf

    return surface_dict

def split_text_by_space(text, max_length=24):
    """
    Splits a string into multiple lines based on two rules:
    1. If the string contains newline characters (`\n`), it will split at those first.
    2. Each resulting line will be further split if its length exceeds `max_length`,
       breaking at the last space before the limit. Leading spaces on new lines are removed.

    Parameters:
        text (str): The input string to split.
        max_length (int): Maximum allowed length per line (default is 24).

    Returns:
        list[str]: A list of lines, each no longer than `max_length`, split cleanly at spaces or newlines.
    """
    lines = []
    for raw_line in text.split('\n'):
        while len(raw_line) > max_length:
            split_index = raw_line.rfind(' ', 0, max_length)
            if split_index == -1:
                split_index = max_length
            lines.append(raw_line[:split_index])
            raw_line = raw_line[split_index:].lstrip()
        lines.append(raw_line)
    return lines

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((100, 100))
    print(import_folder('../graphics/water'))