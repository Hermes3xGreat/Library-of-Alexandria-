#!/usr/bin/env python3
"""Sign an APK with v1 (JAR, via the JDK's jarsigner) and v2 (APK Signature
Scheme v2) signatures, aligning stored entries to 4 bytes (like zipalign).
Needs only Java (jarsigner, keytool) and Python's `cryptography`.

usage: apksign.py IN.apk OUT.apk --ks KEYSTORE.p12 --alias ALIAS --pass PASSWORD
       apksign.py --new-key KEYSTORE.p12 --alias ALIAS --pass PASSWORD --dname "CN=Eastern Scroll"
"""
import os, sys, struct, hashlib, zipfile, subprocess, tempfile, shutil, argparse
from cryptography.hazmat.primitives.serialization import pkcs12, Encoding, PublicFormat
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

V2_ID = 0x7109871a
RSA_PKCS1_SHA256 = 0x0103
CHUNK = 1 << 20


def new_key(path, alias, pw, dname):
    subprocess.run(['keytool', '-genkeypair', '-keystore', path, '-storetype', 'PKCS12', '-alias', alias,
                    '-keyalg', 'RSA', '-keysize', '4096', '-validity', '36500', '-storepass', pw, '-keypass', pw,
                    '-dname', dname], check=True, capture_output=True)


def align(src, dst):
    """rewrite the zip with stored entries' data 4-byte aligned (contents unchanged)."""
    with zipfile.ZipFile(src) as zi, open(dst, 'wb') as fo, zipfile.ZipFile(fo, 'w') as zo:
        for info in zi.infolist():
            data = zi.read(info)
            ni = zipfile.ZipInfo(info.filename, info.date_time)
            ni.compress_type = info.compress_type; ni.external_attr = info.external_attr
            ni.create_system = info.create_system
            if info.compress_type == zipfile.ZIP_STORED:
                off = fo.tell() + 30 + len(info.filename.encode('utf-8'))
                ni.extra = b'\0' * ((4 - off % 4) % 4)
            zo.writestr(ni, data)


def lp(b):
    return struct.pack('<I', len(b)) + b


def find_eocd(d):
    i = d.rfind(b'PK\x05\x06', max(0, len(d) - 65557))
    if i < 0:
        raise SystemExit('no end of central directory')
    return i


def v2_sign(src, dst, key, cert):
    d = open(src, 'rb').read()
    eocd = find_eocd(d)
    cd_off = struct.unpack_from('<I', d, eocd + 16)[0]
    entries, cd, end = d[:cd_off], d[cd_off:eocd], d[eocd:]

    def chunk_digests(b):
        out = []
        for i in range(0, len(b), CHUNK):
            c = b[i:i + CHUNK]
            out.append(hashlib.sha256(b'\xa5' + struct.pack('<I', len(c)) + c).digest())
        return out
    digests = chunk_digests(entries) + chunk_digests(cd) + chunk_digests(end)
    top = hashlib.sha256(b'\x5a' + struct.pack('<I', len(digests)) + b''.join(digests)).digest()

    cert_der = cert.public_bytes(Encoding.DER)
    signed = (lp(lp(struct.pack('<I', RSA_PKCS1_SHA256) + lp(top)))   # digests
              + lp(lp(cert_der))                                       # certificates
              + lp(b''))                                               # additional attributes
    sig = key.sign(signed, padding.PKCS1v15(), hashes.SHA256())
    pub = key.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
    signer = lp(signed) + lp(lp(struct.pack('<I', RSA_PKCS1_SHA256) + lp(sig))) + lp(pub)
    value = lp(lp(signer))
    pair = struct.pack('<Q', 4 + len(value)) + struct.pack('<I', V2_ID) + value
    size = len(pair) + 8 + 16
    block = struct.pack('<Q', size) + pair + struct.pack('<Q', size) + b'APK Sig Block 42'
    new_end = bytearray(end)
    struct.pack_into('<I', new_end, 16, cd_off + len(block))
    open(dst, 'wb').write(entries + block + cd + bytes(new_end))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inp', nargs='?'); ap.add_argument('out', nargs='?')
    ap.add_argument('--ks', '--new-key', dest='ks', required=True); ap.add_argument('--alias', required=True)
    ap.add_argument('--pass', dest='pw', required=True); ap.add_argument('--dname', default='CN=Scroll')
    a = ap.parse_args()
    if '--new-key' in sys.argv:
        new_key(a.ks, a.alias, a.pw, a.dname); print('key', a.ks); return
    key, cert, _ = pkcs12.load_key_and_certificates(open(a.ks, 'rb').read(), a.pw.encode())
    tmp = tempfile.mkdtemp()
    try:
        t1 = os.path.join(tmp, 'v1.apk'); shutil.copy(a.inp, t1)
        # strip any old signature first
        t0 = os.path.join(tmp, 'clean.apk')
        with zipfile.ZipFile(t1) as zi, zipfile.ZipFile(t0, 'w') as zo:
            for info in zi.infolist():
                if info.filename.startswith('META-INF/') and info.filename.upper().endswith(('.SF', '.RSA', '.DSA', '.EC', '.MF')):
                    continue
                zo.writestr(info, zi.read(info))
        r = subprocess.run(['jarsigner', '-keystore', a.ks, '-storetype', 'PKCS12', '-storepass', a.pw,
                            '-keypass', a.pw, '-digestalg', 'SHA-256', '-sigalg', 'SHA256withRSA',
                            '-sigfile', 'CERT', t0, a.alias], capture_output=True, text=True)
        if r.returncode:
            raise SystemExit('jarsigner failed: ' + r.stdout + r.stderr)
        t2 = os.path.join(tmp, 'aligned.apk'); align(t0, t2)
        v2_sign(t2, a.out, key, cert)
    finally:
        shutil.rmtree(tmp)
    print('signed', a.out)


if __name__ == '__main__':
    main()
