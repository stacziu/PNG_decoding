import struct
import matplotlib.pyplot as plt
from datetime import datetime
from exif_tags import EXIF_TAGS, TYPE_SIZES

def show_chunk_properties(chunk_name : bytes, data : bytes):
    if chunk_name == b'IHDR':
        show_IHDR(data)
    elif chunk_name == b'PLTE':
        show_PLTE(data)
    elif chunk_name == b'IDAT':
        show_IDAT(data)
    elif chunk_name == b'eXIf':
        show_eXIf(data)
    elif chunk_name == b'iCCP':
        show_iCCP(data)
    elif chunk_name == b'pHYs':
        show_pHYs(data)
    elif chunk_name == b'gAMA':
        show_gAMA(data)

def show_IHDR(data : bytes):
    width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(">II5B", data)
    if compression == 0:
        compression = "Deflate"
    print(f"\nSzerokość: {width}, Wysokość: {height}")
    print(f"Głębia bitowa: {bit_depth}, Typ koloru: {color_type}")
    print(f"Kompresja: {compression}, Filtr: {filter_method}, Przeplot: {interlace}")

def show_PLTE(data : bytes):
    num_colors = len(data) // 3 #Ilosc kolorow - dlugosc danych // 3
    format = f'{num_colors * 3}B'
    rgb_val = struct.unpack(format, data)
    palette = [] #lista do przechowywania krotki (R, G, B)

    for i in range(0, len(rgb_val), 3):
        palette.append(tuple(rgb_val[i : i + 3]))


    fig, ax = plt.subplots(figsize=(6, num_colors * 0.3)) # (szerokosc, wysokosc) -> zwraca pole figure i axis do wykresu
    for idx, (r, g, b) in enumerate(palette):
        ax.barh(idx, 1, color=(r / 255, g / 255, b / 255)) # ustalenie slupka dla kazdej wartosci w palecie
    plt.axis('off') # usuniecie wartosci na osiach
    ax.set_xlim(0, 1)
    ax.set_title("Paleta kolorów PLTE")
    plt.tight_layout()
    plt.show()

def show_IDAT(data : bytes):
    print(f"\nŁączna długość chunków IDAT: {len(data)} bajtów")

def read_value(data : bytes, data_type : int, count : int, offset : int, endian : str):
    """
    funkcja sluzaca do odczytywania wartosci patrząc na tag zapisu IFD
    data_type - rodzaj danych
    count - ilosc tych danych (np. 13 znakow typu ASCII)
    offset - pozycja od ktorej zaczyna sie IFD
    endian - podany na poczatku chunka exif - sposob odczytywania bajtow
    """

    def unpack(format, offset):
        #Do zwracania pojedynczych wartosci
        size = struct.calcsize(format) # obliczenie bajtów tego formatu
        return struct.unpack(endian + format, data[offset:offset + size])[0]

    if data_type in (1, 7):  # BYTE, UNDEFINED
        return data[offset:offset + count]
    elif data_type == 2:  # ASCII
        return data[offset:offset + count].rstrip(b'\x00').decode('ascii')
    elif data_type == 3:  # SHORT
        return struct.unpack(endian + 'H' * count, data[offset:offset + 2 * count]) if count > 1 else unpack('H', offset)
    elif data_type == 4:  # LONG
        return struct.unpack(endian + 'I' * count, data[offset:offset + 4 * count]) if count > 1 else unpack('I', offset)
    elif data_type == 5:  # RATIONAL - 2 LONGs
        values = []
        for i in range(count):
            num = unpack('I', offset + i * 8)
            den = unpack('I', offset + i * 8 + 4)
            values.append(num / den if den != 0 else float('inf'))
        return values[0] if count == 1 else values
    elif data_type == 9:  # SLONG
        return struct.unpack(endian + 'i' * count, data[offset:offset + 4 * count]) if count > 1 else unpack('i', offset)
    elif data_type == 10:  # SRATIONAL - 2 SLONGs
        values = []
        for i in range(count):
            num = unpack('i', offset + i * 8)
            den = unpack('i', offset + i * 8 + 4)
            values.append(num / den if den != 0 else float('inf'))
        return values[0] if count == 1 else values

    return f"Niewspierany typ danych: {data_type}"

def parse_ifd(data : bytes, offset : int, endian : str):
    """

    bierze offset do danych, dane, endian i zwraca liste zawartości IFD oraz offset do następnego segmentu

    lancuch Exif
    IFD0 --> ExifSubIFD
     |
     |
     v
    nextIFD --> nextIFD --> ...

    budowa IFD:
    2 bajty - tag
    2 bajty - typ danych
    4 bajty - ilosc danych
    4 bajty - offset nastepnego
    """

    entries = []
    count = struct.unpack(endian + 'H', data[offset:offset+2])[0]
    for i in range(count):
        entry_offset = offset + 2 + i * 12
        tag, data_type, val_count, val_offset = struct.unpack(endian + 'HHII', data[entry_offset:entry_offset+12])
        total_size = val_count * TYPE_SIZES.get(data_type, 1)

        #gdy wartosc mniejsza rowna 4 to wartosc zapisana jest w ostatnich 4 bajtach tiff headera
        value_offset = entry_offset + 8 if total_size <= 4 else val_offset
        value = read_value(data, data_type, val_count, value_offset, endian)

        entries.append((tag, data_type, val_count, value))

    next_ifd_offset = struct.unpack(endian + 'I', data[offset + 2 + count*12:offset + 2 + count*12 + 4])[0]
    return entries, next_ifd_offset

def show_eXIf(data : bytes):
    if len(data) < 8:
        print("Nagłówek jest za krótki")
        return

    byte_order = data[:2]
    if byte_order == b'II':
        endian = '<'
    elif byte_order == b'MM':
        endian = '>'
    else:
        endian = None

    if not endian:
        print("Nieprawidłowa kolejność bajtów")

    magic = struct.unpack(endian + 'H', data[2:4])[0]
    if magic != 0x2A:
        print("Nieprawidłowy nagłówek TIFF")
        return

    # wyswietlenie IFD0 / dowolnie innego
    first_ifd_offset = struct.unpack(endian + 'I', data[4:8])[0]
    entries, next_ifd = parse_ifd(data, first_ifd_offset, endian)
    exif_offset = None
    print("\n")
    for tag, t, count, value in entries:
        name = EXIF_TAGS.get(tag, f"Unknown tag: {tag}")
        if tag == 0x0132:
            value = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")

        if tag == 0x8769:
            exif_offset = value
        print(f"{name} ({tag}) - {value}")

    # gdy istnieje ExifOffset wyświetl SubIFD
    if exif_offset:
        print("\n")
        entries, _ = parse_ifd(data, exif_offset, endian)
        for tag, t, count, value in entries:
            name = EXIF_TAGS.get(tag, f"Unknown tag: {tag}")
            print(f"{name} ({tag}) - {value}")

    # wyswietlane kolejnych
    while next_ifd:
        entries, next_ifd = parse_ifd(data, next_ifd, endian)
        for tag, t, count, value in entries:
            name = EXIF_TAGS.get(tag, f"Unknown tag: {tag}")
            print(f"{name} ({tag}) - {value}")

def show_gAMA(data : bytes):
    if len(data) != 4:
        print(f"Nieprawidłowa długośc chunku gAMA: {len(data)} bajtów")
        return

    gamma_value = struct.unpack(">I", data)[0]
    gamma_float = gamma_value / 100000.0
    print(f"\nWartość korekcji gamma: {gamma_float} (przechowywana jako: {gamma_value})")

def show_iCCP(data : bytes):

    profile_name, rest = data.split(b'\x00', 1)
    profile_name = profile_name.decode('ascii')

    if len(rest) < 1:
        print("Nieprawidłowy chunk iCCp")
        return

    compression_method = rest[0]
    compressed_profile = rest[1:]
    if compression_method == 0:
        compression_method = "Deflate"
    print(f"\nNazwa profilu ICC: {profile_name}")
    print(f"Metoda kompresji: {compression_method}")
    print(f"Zkompresowana długość danych profilu: {len(compressed_profile)} bajtów")

def show_pHYs(data):
    if len(data) != 9:
        print("\nNieprawidłowy chunk pHYs")
        return
    else:
        ppux, ppuy, unit = struct.unpack(">IIB", data)
        unit_str = "piksel/metr" if unit == 1 else "brak"
        print(f"\nDPI: {ppux}x{ppuy} ({int(ppux/39.3701)}), Jednostka: {unit_str}")
