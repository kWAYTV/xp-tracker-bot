import os
from src.util.logger import Logger
from src.helper.config import Config

class MedalHandler:
    def __init__(self):
        self.logger = Logger()
        self.config = Config()
        self.base_dir = self.config.medals_output_dir

    # Function to get the medals image path
    async def get_image_path(self, image_name: str):
        path = os.path.join(self.base_dir, f"{image_name}.png")
        if not os.path.isfile(path):
            self.logger.log("WARNING", f"Image {image_name}.png does not exist at the expected location.")
            return None
        self.logger.log("INFO", f"Got image path for {image_name}.png")
        return path
    
    # Function to delete a medal image
    async def delete_image(self, image_name: str):
        path = os.path.join(self.base_dir, f"{image_name}.png")
        if os.path.isfile(path):
            try:
                os.remove(path)
            except Exception as e:
                self.logger.log("ERROR", f"Error while deleting image: {e}")
                return False
            self.logger.log("INFO", f"Successfully deleted image {image_name}.png")
            return True
        else:
            self.logger.log("WARNING", f"Image {image_name}.png does not exist, so it could not be deleted.")
            return False
        
    # Function to delete all images in the output folder
    async def delete_all_images(self):
        for filename in os.listdir(self.base_dir):
            file_path = os.path.join(self.base_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                self.logger.log("WARNING", f"Failed to delete {file_path}. Reason: {e}")
        self.logger.log("INFO", f"Successfully deleted all the residual images.")
        return True