
EXIF_TAGS = {
    0x010F: "Make",
    0x0110: "Model",
    0x0132: "DateTime",
    0x8769: "ExifOffset",
    0x8827: "ISO",
    0x829A: "ExposureTime",
    0x829D: "FNumber",
    0x0112: "Orientation"
}

TYPE_SIZES = {
    1: 1,  # BYTE
    2: 1,  # ASCII
    3: 2,  # SHORT
    4: 4,  # LONG
    5: 8,  # RATIONAL
    7: 1,  # UNDEFINED
    9: 4,  # SLONG
    10: 8  # SRATIONAL
}