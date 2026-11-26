#!/usr/bin/env python3
"""Read or change versionCode / versionName in a compiled (binary)
AndroidManifest.xml. The string pool is rebuilt, so the new versionName can
have any length.

usage: axml.py MANIFEST                      (print package, versionCode, versionName)
       axml.py MANIFEST --code N --name X    (rewrite in place)
"""
import struct, sys

RES_STRING_POOL, RES_XML_START_ELEMENT = 0x0001, 0x0102
TYPE_STRING, TYPE_INT_DEC = 0x03, 0x10
UTF8_FLAG = 1 << 8


def _len8(b, o):
    n = b[o]; o += 1
    if n & 0x80:
        n = ((n & 0x7f) << 8) | b[o]; o += 1
    return n, o


def _len16(b, o):
    n = struct.unpack_from('<H', b, o)[0]; o += 2
    if n & 0x8000:
        n = ((n & 0x7fff) << 16) | struct.unpack_from('<H', b, o)[0]; o += 2
    return n, o


class Manifest:
    def __init__(self, data):
        self.d = bytearray(data)
        t, hs, size = struct.unpack_from('<HHI', self.d, 0)
        assert t == 0x0003, 'not a binary XML file'
        self.pool_off = hs
        self._read_pool()

    def _read_pool(self):
        d, o = self.d, self.pool_off
        t, hs, size, n, nstyle, flags, sstart, ystart = struct.unpack_from('<HHIIIIII', d, o)
        assert t == RES_STRING_POOL
        assert nstyle == 0, 'styled strings not supported'
        self.utf8 = bool(flags & UTF8_FLAG)
        self.flags, self.pool_size, self.pool_hs = flags, size, hs
        offs = struct.unpack_from(f'<{n}I', d, o + hs)
        self.strings = []
        for so in offs:
            p = o + sstart + so
            if self.utf8:
                _, p = _len8(d, p); bl, p = _len8(d, p)
                self.strings.append(bytes(d[p:p + bl]).decode('utf-8'))
            else:
                cl, p = _len16(d, p)
                self.strings.append(bytes(d[p:p + cl * 2]).decode('utf-16-le'))

    def _write_pool(self):
        data, offs = bytearray(), []
        for s in self.strings:
            offs.append(len(data))
            if self.utf8:
                eb = s.encode('utf-8')
                for n in (len(s), len(eb)):
                    data += bytes([n]) if n < 0x80 else bytes([0x80 | (n >> 8), n & 0xff])
                data += eb + b'\0'
            else:
                n = len(s.encode('utf-16-le')) // 2
                data += struct.pack('<H', n) if n < 0x8000 else struct.pack('<HH', 0x8000 | (n >> 16), n & 0xffff)
                data += s.encode('utf-16-le') + b'\0\0'
        while len(data) % 4:
            data += b'\0'
        n = len(self.strings)
        sstart = self.pool_hs + 4 * n
        size = sstart + len(data)
        pool = struct.pack('<HHIIIIII', RES_STRING_POOL, self.pool_hs, size, n, 0, self.flags, sstart, 0)
        pool += b'\0' * (self.pool_hs - 28) + struct.pack(f'<{n}I', *offs) + data
        o = self.pool_off
        self.d[o:o + self.pool_size] = pool
        self.pool_size = size
        struct.pack_into('<I', self.d, 4, len(self.d))

    def _manifest_attrs(self):
        """yield (offset_of_attr, name) for attributes of <manifest>."""
        d, o = self.d, self.pool_off + self.pool_size
        while o < len(d):
            t, hs, size = struct.unpack_from('<HHI', d, o)
            if t == RES_XML_START_ELEMENT:
                name = struct.unpack_from('<I', d, o + 20)[0]
                if self.strings[name] == 'manifest':
                    astart, asize, acount = struct.unpack_from('<HHH', d, o + 16 + 8)
                    base = o + 16 + astart
                    for k in range(acount):
                        ao = base + k * asize
                        yield ao, self.strings[struct.unpack_from('<I', d, ao + 4)[0]]
                    return
            o += size

    def get(self):
        out = {}
        for ao, nm in self._manifest_attrs():
            raw, _, _, dtype, val = struct.unpack_from('<IHBBI', self.d, ao + 8)
            out[nm] = self.strings[val] if dtype == TYPE_STRING else val
        return out

    def set(self, code=None, name=None):
        for ao, nm in list(self._manifest_attrs()):
            if nm == 'versionCode' and code is not None:
                struct.pack_into('<IHBBI', self.d, ao + 8, 0xffffffff, 8, 0, TYPE_INT_DEC, int(code))
            if nm == 'versionName' and name is not None:
                idx = len(self.strings); self.strings.append(name)
                struct.pack_into('<IHBBI', self.d, ao + 8, idx, 8, 0, TYPE_STRING, idx)
        self._write_pool()


    def _element_attrs(self):
        """yield (element_name, attr_offset, attr_name) for every element."""
        d, o = self.d, self.pool_off + self.pool_size
        while o < len(d):
            t, hs, size = struct.unpack_from('<HHI', d, o)
            if t == RES_XML_START_ELEMENT:
                el = self.strings[struct.unpack_from('<I', d, o + 20)[0]]
                astart, asize, acount = struct.unpack_from('<HHH', d, o + 24)
                for k in range(acount):
                    ao = o + 16 + astart + k * asize
                    yield el, ao, self.strings[struct.unpack_from('<I', d, ao + 4)[0]]
            o += size

    def _set_str(self, ao, value):
        idx = len(self.strings); self.strings.append(value)
        struct.pack_into('<IHBBI', self.d, ao + 8, idx, 8, 0, TYPE_STRING, idx)

    def rebrand(self, package=None, label=None):
        """New application id and/or label. Components named relative to the
        old package (".MainActivity") are made absolute so the code still loads."""
        old = self.get()['package']
        for el, ao, nm in list(self._element_attrs()):
            raw, _, _, dtype, val = struct.unpack_from('<IHBBI', self.d, ao + 8)
            if package and el == 'manifest' and nm == 'package':
                self._set_str(ao, package)
            elif package and el in ('activity', 'service', 'receiver', 'provider', 'application', 'activity-alias') \
                    and nm in ('name', 'targetActivity') and dtype == TYPE_STRING and self.strings[val].startswith('.'):
                self._set_str(ao, old + self.strings[val])
            elif label and el in ('application', 'activity') and nm == 'label' and dtype == TYPE_STRING:
                self._set_str(ao, label)
        self._write_pool()


if __name__ == '__main__':
    p = sys.argv[1]
    m = Manifest(open(p, 'rb').read())
    a = sys.argv[2:]
    if a:
        code = a[a.index('--code') + 1] if '--code' in a else None
        name = a[a.index('--name') + 1] if '--name' in a else None
        m.set(code, name)
        open(p, 'wb').write(m.d)
        m = Manifest(bytes(m.d))
    g = m.get()
    print({k: g.get(k) for k in ('package', 'versionCode', 'versionName')})
