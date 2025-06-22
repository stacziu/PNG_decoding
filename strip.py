import struct

def strip_ancillary_chunks(input_path, output_path, hidden_data = None):
    def is_critical(chunk_name):
        return chunk_name in (b'IHDR', b'PLTE', b'IDAT', b'IEND')

    with open(input_path, 'rb') as file_in, open(output_path, 'wb') as file_out:
        # Write signature
        sig = file_in.read(8)
        file_out.write(sig)

        while True:
            # Read chunk length and name
            length_bytes = file_in.read(4)
            if not length_bytes:
                break
            length = struct.unpack('>I', length_bytes)[0]
            name = file_in.read(4)
            data = file_in.read(length)
            crc = file_in.read(4)

            # Write only critical
            if is_critical(name):
                file_out.write(length_bytes)
                file_out.write(name)
                file_out.write(data)
                file_out.write(crc)

            if name == b'IEND':
                if hidden_data:
                    file_out.write(hidden_data)
                break
