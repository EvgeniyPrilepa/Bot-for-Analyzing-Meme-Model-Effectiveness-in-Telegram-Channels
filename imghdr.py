import struct

def what(file, h=None):
    if h is None:
        with open(file, 'rb') as f:
            h = f.read(32)
    
    if len(h) < 2:
        return None
        
    if h.startswith(b'\xff\xd8'):
        return 'jpeg'
    if len(h) >= 8 and h.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    if len(h) >= 6 and h.startswith(b'GIF8'):
        return 'gif'
    if len(h) >= 2 and h.startswith(b'BM'):
        return 'bmp'
    if len(h) >= 12 and h.startswith(b'RIFF') and h[8:12] == b'WEBP':
        return 'webp'
    if len(h) >= 4 and h.startswith(b'\x00\x00\x01\x00'):
        return 'ico'
    return None