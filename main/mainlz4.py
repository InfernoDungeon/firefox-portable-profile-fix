import lz4.block
import json

class LZ4Error(Exception):
    pass

class HeaderMismatch(LZ4Error):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

def decompress(jlz4_file):
    jsonlz4_header = b'mozLz40\x00'
    if jlz4_file.read(8) != jsonlz4_header:
        raise HeaderMismatch("Invalid jsonlz4 Header")
    extracted = lz4.block.decompress(jlz4_file.read())
    json_load = json.loads(extracted)
    return json_load

def compress(data):
    compressed_block = lz4.block.compress(str.encode(data))
    return b'mozLz40\x00' + compressed_block