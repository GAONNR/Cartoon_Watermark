from PIL import Image
import sys
origin_path = 'nico.bmp'
embed_path = 'nico/nico_embed.bmp'
f_path = 'compare.txt'
msg_color = (0xfc, 0xdb, 0x42)
origin = Image.open(origin_path)
embed = Image.open(embed_path)
f = open(f_path, "w")

width, height = origin.size
oa = origin.load()
oe = embed.load()
for x in range(width):
    for y in range(height):
        oR, oG, oB = oa[x, y]
        eR, eG, eB = oe[x, y]

        boR = format(oR, '08b')[7]
        boG = format(oG, '08b')[7]
        boB = format(oB, '08b')[7]
        beR = format(eR, '08b')[7]
        beG = format(eG, '08b')[7]
        beB = format(eB, '08b')[7]
        printstr = '%s%s%s%s%s%s  ' % (boB, beB, boG, beG, boR, beR)
        f.write(printstr)
        if boR != beR or boG != beG or boB != beB:
            print('%d %d' % (x, y))

f.close()
