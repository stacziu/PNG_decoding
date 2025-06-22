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
            #Dlugosc i nazwa
            chunk_length = f.read(4)
            chunk_name = f.read(4)

            if chunk_name == b'IEND':
                print("\nReached end of file")
                break

            #Dane
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
    parser = argparse.ArgumentParser(description="Program do analizy plików PNG")
    parser.add_argument('file', help="Ścieżka do pliku PNG")
    parser.add_argument('--spectrum', action='store_true', help="Pokazanie widm obrazu")
    parser.add_argument('--strip', metavar='OUT', help="Pozbycie się niekrytycznych czunków PNG, zapis do OUT")
    parser.add_argument('--hide', metavar='DATA', help="Dane do schowania za IEND")
    args = parser.parse_args()

    file_path = args.file
    img = Image.open(file_path)
    img.show()

    read_chunks(file_path)

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
            read_chunks(args.strip)

if __name__ == '__main__':
    main()


