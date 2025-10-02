import pygame
import csv

class ItemCSVLoader:
    def __init__(self, filepath):
        self.items = {}
        self.image_cache = {}
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
        item_id = item_id.lower()
        if item_id in self.image_cache:
            return self.image_cache[item_id]

        path = self.items.get(item_id, {}).get("image_path")
        if path:
            try:
                image = pygame.image.load(path).convert_alpha()
                self.image_cache[item_id] = image
                return image
            except Exception as e:
                print(f"[ItemCSVLoader] Failed to load image for '{item_id}': {e}")
        return None

    def clear_cache(self):
        self.image_cache = {}