from PIL import Image
im = Image.open("rilakkuma.png")
im = im.convert("RGB")
im.save("rillakkuma.png")
'''
print(im.format, im.size, im.mode)
x, y = im.size
for i in range(x):
    for j in range(y):
        R, G, B = im.getpixel((i, j))
        gray = int(0.3 * R + 0.59 * G + 0.11 * B)
        im.putpixel((i, j), (gray, gray, gray))
im.save("mitsuha_gray.png")
'''
