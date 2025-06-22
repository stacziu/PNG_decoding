from PIL import Image
import os
from piexif import dump


def create_png_with_exif():
    cwd = os.getcwd()
    file_path = os.path.join(cwd, '')

    # Open the original image
    img = Image.open(file_path)

    # Create proper EXIF data
    exif_dict = {
        "0th": {
            # Standard EXIF tags (see piexif documentation for full list)
            271: "Camera Make",  # Make
            272: "Camera Model",  # Model
            306: "2023:01:01 12:00:00",  # DateTime
        },
        "Exif": {
            33434: (1, 10),  # ExposureTime
            33437: (28, 10),  # FNumber
            34855: 100,  # ISOSpeedRatings
        },
        "1st": {},
        "thumbnail": None
    }

    # Convert the dictionary to proper EXIF bytes
    exif_bytes = dump(exif_dict)

    # Save with EXIF
    output_path = os.path.join(cwd, 'exif.png')
    img.save(output_path, exif=exif_bytes)
    print(f"Saved image with EXIF to {output_path}")


if __name__ == "__main__":
    create_png_with_exif()