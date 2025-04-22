import os
import struct

class PNGchunk:
    def __init__(self, name, characteristics):
        self.name = name
        self.characteristics = characteristics

    def __str__(self):
        return f"{self.name}: {self.characteristics}"

def read_critical_chunks(path):
    chunks = []
    with (open(path, 'rb') as f):
        header = f.read(8)
        if header != b'\x89PNG\r\n\x1A\n':
            print("not a valid png file")
            return

        while True:
            #checking Length and Chunk type
            chunk_length = f.read(4)
            chunk_name = f.read(4)

            if len(chunk_length) < 4:
                return chunks

            if len(chunk_name) < 4:
                return chunks

            length_decimal = struct.unpack(">I", chunk_length)[0]

            #parsing Chunk data according to type of chunk

            if chunk_name == b'IHDR':
                chunks.append(parse_IHDR(f.read(length_decimal)))

            if chunk_name == b'PLTE':
                if length_decimal % 3 != 0:
                    print("Invalid PLTE chunk")
                    break
                chunks.append(parse_PLTE(f.read(length_decimal)))

            #CRC - going to the next chunk
            f.read(4)

        return chunks

def parse_IHDR(data):
    characteristics = []
    for chunk_data in struct.unpack(">IIBBBBB", data):
        characteristics.append(chunk_data)

    return PNGchunk("IHDR", characteristics)

def parse_PLTE(data):
    num_colors = len(data) // 3
    string_format = f'{num_colors * 3}B'
    rgb_val = struct.unpack(string_format, data)
    palette = []

    for i in range(0, len(rgb_val), 3):
        palette.append(tuple(rgb_val[i : i + 3]))

    return PNGchunk("PLTE", palette)


if __name__ == "__main__":
    cwd = os.getcwd()
    file_path = os.path.join(cwd, 'test_file.png')
    file = open(file_path, "rb")


    listOfChunks = read_critical_chunks(file_path)
    for chunk in listOfChunks:
        print(chunk)