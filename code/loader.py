import pygame
import csv

class ItemCSVLoader:
    def __init__(self, filepath):
        self.items = {}
        self._load(filepath)

    def _load(self, filepath):
        with open(filepath, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.items[row["id"]] = {
                    "name": row["name"],
                    "description": row["desc"],
                    "image_path": row["image_path"]
                }

    def get_name(self, item_id):
        return self.items.get(item_id, {}).get("name", "No name available.")

    def get_description(self, item_id):
        return self.items.get(item_id, {}).get("description", "No description available.")

    def get_image(self, item_id):
        path = self.items.get(item_id, {}).get("image_path")
        if path:
            return pygame.image.load(path).convert_alpha()
        return None
