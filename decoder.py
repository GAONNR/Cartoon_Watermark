from PIL import Image, ImageFilter, ImageEnhance
import sys, math, os

def main():
    myfile = "mitsuha.png"
    if len(sys.argv) > 1:
        myfile = sys.argv[1]

    try:
        img = Image.open(myfile)
    except:
        print("no file exists")
        sys.exit(1)

    img = img.convert("RGB")
    print(img.size, img.mode)
    x, y = img.size

    gray_img = Image.new("L", img.size, None)

    ### make grayscaled image
    for i in range(x):
        for j in range(y):
            R, G, B = img.getpixel((i, j))
            gray = int(0.3 * R + 0.59 * G + 0.11 * B)
            gray_img.putpixel((i, j), gray)

    name, form = myfile.split('.')
    # try:
    #  os.mkdir(name)
    # except:
    #  ' Directory already exists '
    filename = [name + '_sobel', form]
    out = edgeDetector(gray_img)
    # out.save(name + "/" + ".".join(filename))

    # filename = [name + '_dark', form]
    dark = ImageEnhance.Brightness(out).enhance(0.1)
    width, height = dark.size
    dark_arr = dark.load()
    for x in range(width):
        for y in range(height):
            if dark_arr[x, y] < 5:
                dark_arr[x, y] = 0
    # dark.save(name + "/" + ".".join(filename))

    # filename = [name + '_bright', form]
    bright = ImageEnhance.Brightness(dark).enhance(10.0)
    # bright.save(name + "/" + ".".join(filename))

    filename = [name + '_contrasted', form]
    contrast = ImageEnhance.Contrast(bright).enhance(4)
    # contrast.save(name + "/" + ".".join(filename))

    filename = [name + '_floodfilled', form]
    BG_filled = BGFiller(contrast)
    # BG_filled.save(name + "/" + ".".join(filename))

    # filename = [name + '_bggray', form]
    # bg_gray = BG_filled.convert("L")
    # bg_gray.save(name + "/" + ".".join(filename))

    filename = [name + '_nowaifu', form]
    no_waifu = charaRemover(BG_filled, (0x34, 0x98, 0xdb), (0xfc, 0xdb, 0x42))
    # no_waifu.save(name + "/" + ".".join(filename))

    decoder(img, no_waifu, (0xfc, 0xdb, 0x42))
def edgeDetector(img):
    # im = im.filter(ImageFilter.FIND_EDGES)
    # im.save('mitsuha_edge.png')

    ### use sobel edge detection
    if img.mode != "RGB":
        img = img.convert("RGB")

    out = Image.new("L", img.size, None)
    img_arr = img.load()
    out_arr = out.load()

    ### convolution matrices
    matrix_x = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    matrix_y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
    matrix_size = 3
    matrix_middle = matrix_size/2

    width, height = img.size
    for row in range(width - matrix_size):
        for col in range(height - matrix_size):

            pixel_x = 0
            pixel_y = 0
            for i in range(matrix_size):
                for j in range(matrix_size):
                    # each position in the convolution matrix

                    # find average pixel colour (discard colour info)
                    # of pixel at matrix overlap position
                    val = sum(img_arr[row + i, col + j])/3
                    # apply convolution matrix multiplier
                    # to this value
                    pixel_x += matrix_x[i][j] * val
                    pixel_y += matrix_y[i][j] * val

            new_pixel = math.sqrt(pixel_x * pixel_x + pixel_y * pixel_y)
            out_arr[row + matrix_middle, col + matrix_middle] = int(new_pixel)

    return out

def BGFiller(sample):
    img = sample.convert("RGB")
    img_arr = img.load()
    width, height = img.size
    boundary = 48
    tofill = [(int(width / 100), int(height / 100)), (int(width - width / 100), int(height / 100))]
    fill_color = (0x34, 0x98, 0xdb)

    while len(tofill) > 0:
        x, y = tofill.pop(0)

        dxy = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for (dx, dy) in dxy:
            if (x + dx < 1) or (x + dx >= width - 2): continue
            if (y + dy < 1) or (y + dy >= height - 2): continue

            if (img_arr[x + dx, y + dy] != fill_color) and (img_arr[x + dx, y + dy][0] < boundary):
                img_arr[x + dx, y + dy] = fill_color
                tofill.append((x + dx, y + dy))

    return img

def charaRemover(img, bgcolor, fill_color):
    row, col = input("Give me a coordinate: ").strip().split(' ')
    row = int(row)
    col = int(col)

    img_arr = img.load()
    width, height = img.size
    tofill = [(row, col)]
    boundary = bgcolor

    while len(tofill) > 0:
        x, y = tofill.pop(0)

        dxy = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for (dx, dy) in dxy:
            if (x + dx < 1) or (x + dx >= width - 2): continue
            if (y + dy < 1) or (y + dy >= height - 2): continue

            if (img_arr[x + dx, y + dy] != boundary) and (img_arr[x + dx, y + dy] != fill_color):
                img_arr[x + dx, y + dy] = fill_color
                tofill.append((x + dx, y + dy))
    return img

def decoder(embed, waifu, msg_color):
    width, height = embed.size
    oe = embed.load()
    ow = waifu.load()
    # f = open("res.txt", "w")
    bits = []

    for x in range(width):
        for y in range(height):
            if ow[x, y] == msg_color:

                R, G, B = oe[x, y]
                bR = xorbits(format(R, '08b'))
                bG = xorbits(format(G, '08b'))
                bB = xorbits(format(B, '08b'))

                # f.write('%d%d%d' % (bB, bG, bR))
                bits.append(str(bB))
                bits.append(str(bG))
                bits.append(str(bR))
                # print(x, y, ''.join(bits))

                decoded_str = bits2str(''.join(bits))
                while decoded_str == False:
                    bits = bits[3:]
                    decoded_str = bits2str(''.join(bits))
                if 'endendend' in decoded_str:
                    print('Decoded! String is: %s' % decoded_str[:-9])
                    sys.exit(0)


    # f.write('\n')
    # f.close()

def xorbits(binstr):
    hi = 0
    for i in binstr:
        hi ^= int(i)
    return hi

def bits2str(bits):
    bitslen = len(bits) // 8 * 8
    bits = bits[:bitslen]
    if bitslen == 0: return ''
    n = int(bits, 2)
    try:
        outstr = n.to_bytes((n.bit_length() + 7) // 8, 'big').decode()
    except:
        outstr = False
    return outstr


if __name__ == "__main__":
    main()










'''
from PIL import Image
import sys
embed_path = 'nico/nico_embed.bmp'
waifu_path = 'nico/nico_nowaifu.bmp'
embed = Image.open(embed_path)
waifu = Image.open(waifu_path)
msg_color = (0xfc, 0xdb, 0x42)

def process(binstr):
    hi = 0
    for i in binstr:
        hi ^= int(i)
    return hi

width, height = embed.size
oe = embed.load()
ow = waifu.load()
for x in range(width):
    for y in range(height):
        if ow[x, y] == msg_color:

            R, G, B = oe[x, y]
            bR = process(format(R, '08b'))
            bG = process(format(G, '08b'))
            bB = process(format(B, '08b'))


            sys.stdout.write('%d%d%d' % (bB, bG, bR))

sys.stdout.write('\n')
'''
