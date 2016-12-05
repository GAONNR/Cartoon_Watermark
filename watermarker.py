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
    try:
        os.mkdir(name)
    except:
        ' Directory already exists '
    filename = [name + '_sobel', form]
    out = edgeDetector(gray_img)
    out.save(name + "/" + ".".join(filename))

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
    contrast.save(name + "/" + ".".join(filename))

    filename = [name + '_floodfilled', form]
    BG_filled = BGFiller(contrast)
    BG_filled.save(name + "/" + ".".join(filename))

    # filename = [name + '_bggray', form]
    # bg_gray = BG_filled.convert("L")
    # bg_gray.save(name + "/" + ".".join(filename))

    filename = [name + '_nowaifu', form]
    no_waifu = charaRemover(BG_filled, (0x34, 0x98, 0xdb), (0xfc, 0xdb, 0x42))
    no_waifu.save(name + "/" + ".".join(filename))

    filename = [name + '_embed', 'bmp']
    embedded = embedMyMsg(img, no_waifu, (0xfc, 0xdb, 0x42))
    embedded.save(".".join(filename))

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

    while len(tofill) > 0:
        x, y = tofill.pop(0)

        dxy = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for (dx, dy) in dxy:
            if (x + dx < 1) or (x + dx >= width - 2): continue
            if (y + dy < 1) or (y + dy >= height - 2): continue
            R, G, B = img_arr[x + dx, y + dy]
            gray = int(0.3 * R + 0.59 * G + 0.11 * B)

            if (img_arr[x + dx, y + dy] != bgcolor) and (img_arr[x + dx, y + dy] != fill_color):
                img_arr[x + dx, y + dy] = fill_color
                tofill.append((x + dx, y + dy))
    return img

def embedMyMsg(img, no_waifu, msg_color):

    myinput = input("Give me a msg: ")
    mybin = ''.join(format(ord(x), '08b') for x in (myinput + 'endendend'))
    print('Your input: %s' % mybin)
    f = open("embed_log.txt", "w")

    bin_idx = 0

    img_arr = img.load()
    waifu_arr = no_waifu.load()
    width, height = img.size
    for x in range(1, width - 1):
        if (bin_idx >= len(mybin)): break
        for y in range(1, height - 1):
            if (waifu_arr[x, y] == msg_color):
                R, G, B = img_arr[x, y]

                binR = format(R, '08b')
                binG = format(G, '08b')
                binB = format(B, '08b')
                f.write('%d %d: %d %d %d ' % (x, y, B, G, R))

                B = LSBencoder(binB, mybin[bin_idx])
                bin_idx += 1
                if (bin_idx >= len(mybin)):
                    img_arr[x, y] = (R, G, B)
                    break
                G = LSBencoder(binG, mybin[bin_idx])
                bin_idx += 1
                if (bin_idx >= len(mybin)):
                    img_arr[x, y] = (R, G, B)
                    break
                R = LSBencoder(binR, mybin[bin_idx])
                bin_idx += 1
                if (bin_idx >= len(mybin)):
                    img_arr[x, y] = (R, G, B)
                    break
                img_arr[x, y] = (R, G, B)
                f.write('%d %d %d\n' % (B, G, R))
    f.close()
    return img

def LSBencoder(binstr, embit):
    bits_xor = int(binstr[0]) ^ int(binstr[1])
    for idx in range(2, 7):
        bits_xor ^= int(binstr[idx])

    bits_xor ^= int(embit)
    new_binstr = binstr[:-1] + str(bits_xor)
    return int(new_binstr, 2)

if __name__ == "__main__":
    main()
