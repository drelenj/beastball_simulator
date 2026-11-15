#!/usr/bin/env python3
"""Reproducible logo extraction for BEASTBALL: ARCADE.

Input : original Drive logos (never committed) in arcade_claude/.scratch/logos_src/
        or arcade_claude/assets/logos_raw/ (owner drop folder), named exactly as in Drive.
Mapping: scripts/logo_sources.json (franchise -> Drive file id -> source file name).
Output: assets/logos/<slug>_128.webp, <slug>_256.webp  (transparent, aspect preserved, <25 KB each)
        data/team_colors.json   (primary/secondary/accent/number colour + abbreviation per franchise)
        data/logos_manifest.json (provenance + status per franchise)
Run   : python3 -I scripts/extract_logos.py   (from arcade_claude/)
"""
import json, os, sys, io, unicodedata, colorsys
from PIL import Image, ImageFilter, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIRS = [os.path.join(ROOT, '.scratch', 'logos_src'), os.path.join(ROOT, 'assets', 'logos_raw')]
OUT = os.path.join(ROOT, 'assets', 'logos')
DATA = os.path.join(ROOT, 'data')
MAX_BYTES = 25 * 1024

ABBR = {
 'Ala Apex':'APX','Ala Marauders':'MAR','Ashkara Ignivars':'ASH','Bibi Nupi Barbarians':'BNB',
 'Bryjeer Flame Devils':'BFD','Dōmyu Dominators':'DOM','Garahviq Immortals':'GIM','Garvian Guardians':'GAR',
 'Güunlekia Serpents':'GSP','G’Yanka Vanagu':'GYV','Hina’sola Hunters':'HSH','Isu’Kari Sirenwings':'ISW',
 'Kalundu Shockwave':'KSW','Kasuf Bloodravens':'KBR','Khemara Sunscourge':'KSS','Lykessia Wolverines':'LYW',
 'Mbuya Ïmu Moonhawks':'MIM','Ndomiri Sentinels':'NDS','Ndumba Specters':'NSP','Nuk’yl Chiefs':'NUK',
 'Priya Arpaqu':'PRA','Ursiria 65ers':'U65','Wibatu Rangers':'WIB','Xenar Ignite':'XEN',
 'Yukïma Cowhands':'YUK','Zafiren Tidewings':'ZTW'}

def slug(name):
    s = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode().lower()
    return ''.join(c if c.isalnum() else '_' for c in s).strip('_').replace('__', '_')

def find_src(fname):
    for d in SRC_DIRS:
        p = os.path.join(d, fname)
        if os.path.exists(p):
            return p
    return None

def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5

def remove_background(im):
    """Flood-fill a uniform border colour to transparency. Textured borders are kept and
    the logo is masked to a rounded square instead."""
    im = im.convert('RGBA')
    w, h = im.size
    px = im.load()
    border = [px[x, 0][:3] for x in range(0, w, 8)] + [px[x, h - 1][:3] for x in range(0, w, 8)] + \
             [px[0, y][:3] for y in range(0, h, 8)] + [px[w - 1, y][:3] for y in range(0, h, 8)]
    mean = tuple(sum(c[i] for c in border) / len(border) for i in range(3))
    spread = sum(dist(c, mean) for c in border) / len(border)
    near_white = min(mean) > 222
    if spread > 22 and not near_white:  # textured background: rounded-square mask, keep artwork intact
        mask = Image.new('L', (w, h), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=w // 8, fill=255)
        im.putalpha(mask)
        return im, 'textured background kept, rounded-square mask'
    # flood fill on a reduced copy for speed, then scale the mask up
    sw, sh = w // 4, h // 4
    small = im.resize((sw, sh), Image.BILINEAR).convert('RGB')
    sp = small.load()
    tol = 38
    seen = bytearray(sw * sh)
    stack = [(x, 0) for x in range(sw)] + [(x, sh - 1) for x in range(sw)] + [(0, y) for y in range(sh)] + [(sw - 1, y) for y in range(sh)]
    while stack:
        x, y = stack.pop()
        i = y * sw + x
        if seen[i] or dist(sp[x, y], mean) > tol:
            continue
        seen[i] = 1
        if x > 0: stack.append((x - 1, y))
        if x < sw - 1: stack.append((x + 1, y))
        if y > 0: stack.append((x, y - 1))
        if y < sh - 1: stack.append((x, y + 1))
    mask = Image.frombytes('L', (sw, sh), bytes(0 if s else 255 for s in seen))
    mask = mask.resize((w, h), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2))
    im.putalpha(mask)
    return im, 'uniform background %s removed (flood fill, tol %d)' % ('#%02x%02x%02x' % tuple(int(v) for v in mean), tol)

def crop_alpha(im):
    bbox = im.getchannel('A').point(lambda a: 255 if a > 24 else 0).getbbox()
    return im.crop(bbox) if bbox else im

def fit(im, longest):
    w, h = im.size
    s = longest / max(w, h)
    return im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)

def save_webp(im, path):
    for q, aq in ((88, 80), (80, 80), (70, 70), (60, 60), (50, 50), (40, 40), (30, 30), (20, 25)):
        buf = io.BytesIO()
        im.save(buf, 'WEBP', quality=q, method=6, alpha_quality=aq)
        if buf.tell() <= MAX_BYTES:
            break
    with open(path, 'wb') as f:
        f.write(buf.getvalue())
    return buf.tell(), q

def lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = c
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)

def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)

def hx(c):
    return '#%02x%02x%02x' % tuple(int(v) for v in c)

def palette(im):
    """Dominant colours from opaque logo pixels: quantize, then rank by count with a bonus for
    saturation (so the team colour beats outline black/white), skipping near-duplicates."""
    small = fit(im, 160)
    a = small.getchannel('A')
    rgb = Image.new('RGB', small.size, (0, 0, 0))
    rgb.paste(small.convert('RGB'), mask=a)
    pixels = [p for p, al in zip(rgb.get_flattened_data(), a.get_flattened_data()) if al > 200]
    tmp = Image.new('RGB', (len(pixels), 1))
    tmp.putdata(pixels)
    q = tmp.quantize(colors=10, method=Image.MEDIANCUT)
    pal = q.getpalette()
    counts = sorted(q.getcolors(), reverse=True)
    cands = []
    for n, idx in counts:
        c = tuple(pal[idx * 3: idx * 3 + 3])
        h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in c))
        score = n * (0.35 + s * (1 - abs(l - 0.5) * 1.2))
        if l > 0.9 or l < 0.07:
            score *= 0.12  # outline white/black rarely is the team colour; keep it for secondary/accent
        cands.append((score, n, c))
    cands.sort(reverse=True)
    chosen = []
    for _, n, c in cands:
        if all(dist(c, d) > 70 for d in chosen):
            chosen.append(c)
        if len(chosen) == 3:
            break
    while len(chosen) < 3:
        chosen.append((255, 255, 255) if lum(chosen[0]) < 0.4 else (20, 20, 20))
    return chosen, len(pixels)

def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(DATA, exist_ok=True)
    sources = json.load(open(os.path.join(ROOT, 'scripts', 'logo_sources.json'), encoding='utf-8'))
    colors, manifest, total = {}, [], 0
    for s in sources:
        fr = s['franchise']
        sl = slug(fr)
        p = find_src(s['source'])
        entry = {'franchise': fr, 'sourceFile': s['source'], 'driveFileId': s['driveId'], 'match': s['match']}
        if not p:
            entry.update(status='TEMPORARY', outputs=[], note='source not found locally; palette is TEMPORARY')
            manifest.append(entry)
            continue
        im = Image.open(p)
        im, bgnote = remove_background(im)
        im = crop_alpha(im)
        (c1, c2, c3), npx = palette(im)
        # jersey: primary body, number in whichever of secondary/white/black reads best
        num_opts = [c2, (255, 255, 255), (16, 16, 16), c3]
        num = max(num_opts, key=lambda c: contrast(c1, c) + (0.8 if c == c2 else 0))
        if contrast(c1, num) < 3.0:
            num = max(num_opts, key=lambda c: contrast(c1, c))
        outs = []
        for size in (128, 256):
            fn = '%s_%d.webp' % (sl, size)
            nbytes, q = save_webp(fit(im, size), os.path.join(OUT, fn))
            total += nbytes
            outs.append({'file': 'assets/logos/' + fn, 'bytes': nbytes, 'webpQuality': q})
        colors[fr] = {'abbr': ABBR[fr], 'slug': sl, 'primary': hx(c1), 'secondary': hx(c2), 'accent': hx(c3),
                      'number': hx(num), 'numberContrast': round(contrast(c1, num), 2),
                      'palette': 'EXTRACTED', 'sourceFile': s['source']}
        entry.update(status='MAPPED', outputs=outs, background=bgnote, sourcePixelsSampled=npx)
        manifest.append(entry)
        print('%-24s %s %s %s num %s (%.1f:1)  %s' % (fr, hx(c1), hx(c2), hx(c3), hx(num), contrast(c1, num), [o['bytes'] for o in outs]))
    json.dump({'_note': 'Colours extracted from the franchise logos by scripts/extract_logos.py; number colour chosen for >=3:1 contrast on primary.',
               'teams': colors}, open(os.path.join(DATA, 'team_colors.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump({'_note': 'Provenance of every shipped logo sprite. Originals are not committed.',
               'driveFolder': '1Y8JhgMbo1-yZD6Z7tOaM7AQliE4CqiFN', 'totalLogoBytes': total, 'logos': manifest},
              open(os.path.join(DATA, 'logos_manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('total logo bytes', total)

if __name__ == '__main__':
    main()
