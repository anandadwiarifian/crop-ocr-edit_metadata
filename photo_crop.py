import os
from dataclasses import dataclass

from PIL import Image


@dataclass
class Position:
    x_axis: int
    y_axis: int


@dataclass
class CropSize:
    width: int
    height: int


@dataclass
class CropBox:
    left: int
    upper: int
    right: int
    lower: int

    @classmethod
    def from_position_and_size(cls, pos: Position, size: CropSize) -> "CropBox":
        """
        Create a crop box tuple based on position and size.

        Args:
            pos (Position): X, Y coordinate of the top-left corner
            size (CropSize): Width, Height of the crop box
        """
        return cls(pos.x_axis, pos.y_axis, pos.x_axis + size.width, pos.y_axis + size.height)

    def to_tuple(self):
        return (self.left, self.upper, self.right, self.lower)


def crop_photos(input_dir: str, output_dir: str, crop_boxes: list[CropBox]):
    """
    Crop multiple photos in a directory using specified crop boxes and save them to an output directory.

    Args:
        input_dir (str): Path to directory containing source images to crop
        output_dir (str): Path to directory where cropped images will be saved
        crop_boxes (list[CropBox]): List of CropBox objects defining the regions to crop from each image

    The function will:
    1. Create the output directory if it doesn't exist
    2. Process all JPG, JPEG and PNG files in the input directory
    3. Apply each crop box to each image
    4. Save cropped images with names like: original_name_[crop_index].extension
    """

    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            img_path = os.path.join(input_dir, filename)
            img = Image.open(img_path)

            for i, crop_box in enumerate(crop_boxes):
                name, ext = os.path.splitext(filename)
                new_filename = f"{name}_{i}{ext}"

                cropped = img.crop(crop_box.to_tuple())

                save_path = os.path.join(output_dir, new_filename)
                cropped.save(save_path)

                print(f"Cropped: {new_filename}")
