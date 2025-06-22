import argparse
import os
import struct


from fourier import plot_image_spectrum
from show_properties import show_chunk_properties
from strip import strip_ancillary_chunks
from PIL import Image

def read_chunks(path):
    idat_data = b''
    with (open(path, 'rb') as f):
        header = f.read(8)
        if header != b'\x89PNG\r\n\x1A\n':
            print("not a valid png file")
            return

        while True:
            #Length and name
            chunk_length = f.read(4)
            chunk_name = f.read(4)
            #print(chunk_name)
            if chunk_name == b'IEND':
                print("\nReached end of file")
                break

            #Data
            length_decimal = struct.unpack(">I", chunk_length)[0]
            data = f.read(length_decimal)

            if chunk_name == b'IDAT':
                idat_data += data
            else:
                show_chunk_properties(chunk_name, data)

            #CRC
            f.read(4)

        if idat_data:
            show_chunk_properties(b'IDAT', idat_data)


def main():
    parser = argparse.ArgumentParser(description="PNG EXIF tool with spectrum and anonymization")
    parser.add_argument('file', help="Path to PNG file")
    parser.add_argument('--spectrum', action='store_true', help="Show Fourier spectrum of image")
    parser.add_argument('--strip', metavar='OUT', help="Output path for anonymized PNG")
    parser.add_argument('--hide', metavar='DATA', help="Raw data to append after IEND chunk")
    args = parser.parse_args()

    file_path = args.file
    img = Image.open(file_path)
    img.show()
    # Show chunk data
    read_chunks(file_path)

    # Spectrum
    if args.spectrum:
        plot_image_spectrum(file_path)


    if args.strip:
        if args.hide:
            hidden_data = args.hide.encode()
            strip_ancillary_chunks(file_path, args.strip, hidden_data = hidden_data)
            print(f"Anonymized PNG written to {args.strip}")
            read_chunks(args.strip)
        else:
            strip_ancillary_chunks(file_path, args.strip)
            print(f"Anonymized PNG written to {args.strip}")
            read_chunks(args.anon)

if __name__ == '__main__':
    main()


