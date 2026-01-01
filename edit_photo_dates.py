import os
import re
from datetime import datetime

import piexif
import pytesseract
from PIL import Image


def extract_text_from_image(image_path: str) -> str:
    """
    Extract all text from an image using OCR.

    Args:
        image_path (str): Path to the image file

    Returns:
        str: Extracted text from the image
    """
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        raise Exception(f"Error processing {os.path.basename(image_path)}") from e


def get_in_out_timestamp(text: str) -> tuple[datetime, datetime]:
    try:
        date_match = re.search(r' Arbi .{3}, (.{11})', text).group(1).strip()  # ty:ignore[possibly-missing-attribute]
        in_time_match = re.search(r'\nIN (\d{2}:\d{2} [AP]M)', text).group(1).strip()  # ty:ignore[possibly-missing-attribute]
        out_time_match = re.search(r'\nIN \d{2}:\d{2} [AP]M.*?(\d{2}:\d{2} [AP]M)', text).group(1).strip()  # ty:ignore[possibly-missing-attribute]

        return (
            datetime.strptime(f"{date_match} {in_time_match}", "%d %b %Y %I:%M %p"),
            datetime.strptime(f"{date_match} {out_time_match}", "%d %b %Y %I:%M %p")
        )
    except AttributeError as e:
        raise Exception(f"regex error for text: {text}") from e
    except ValueError as e:
        raise Exception(f"date parsing error for text: {text}") from e


def edit_photo_date(image_path: str, new_date: datetime):
    """
    Edit the EXIF date metadata of a photo.

    Args:
        image_path (str): Path to the image file
        new_date (datetime): New date to set in the photo metadata
    """
    try:
        exif_dict = piexif.load(image_path)

        date_str = new_date.strftime("%Y:%m:%d %H:%M:%S")
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = date_str.encode('utf-8')
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = date_str.encode('utf-8')
        exif_dict['0th'][piexif.ImageIFD.DateTime] = date_str.encode('utf-8')

        exif_bytes = piexif.dump(exif_dict)

        im = Image.open(image_path)
        im.save(image_path, exif=exif_bytes)

        print(f"Updated date metadata for {os.path.basename(image_path)} to {date_str}")

    except Exception as e:
        raise Exception(f"Error processing {os.path.basename(image_path)}") from e


def batch_set_photo_dates_with_checkout_time(directory: str):
    """
    Edit EXIF date metadata for all photos in a directory.

    Args:
        directory (str): Directory containing the photos
        new_date (datetime): New date to set in the photos' metadata
    """
    failed = []

    for filename in os.listdir(directory):
        if filename.lower().endswith(('.jpg', '.jpeg')):
            try:
                print(f"Processing {filename}")
                image_path = os.path.join(directory, filename)
                _, checkout_time = get_in_out_timestamp(
                    extract_text_from_image(image_path)
                )
                edit_photo_date(image_path, checkout_time)
            except:  # noqa: E722
                failed.append(filename)

    print(f"failed photos: {failed}")
