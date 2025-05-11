import turtle
from PIL import Image

def preprocess_image(image_path, output_size=(100, 100)):
    img = Image.open(image_path)
    img = img.convert("L")  
    img = img.resize(output_size)  
    return img

def draw_with_turtle(image, block_size=10):
    turtle.speed(0)  
    turtle.bgcolor("white")  
    turtle.colormode(255)  

    turtle.penup()
    start_x = -image.width * block_size // 2
    start_y = image.height * block_size // 2
    turtle.goto(start_x, start_y)

    for y in range(image.height):
        for x in range(image.width):
            pixel_intensity = image.getpixel((x, y))


            turtle.goto(start_x + x * block_size, start_y - y * block_size)


            turtle.pendown()
            draw_pattern(pixel_intensity, block_size)
            turtle.penup()

    turtle.done()


def draw_pattern(intensity, block_size):
    turtle.fillcolor(intensity, intensity, intensity)
    turtle.begin_fill()

    if intensity < 85:
        turtle.circle(block_size // 2)
    elif intensity < 170:

        for _ in range(4):
            turtle.forward(block_size)
            turtle.right(90)
    else:
        for _ in range(4):
            turtle.forward(block_size)
            turtle.backward(block_size)
            turtle.right(90)

    turtle.end_fill()


def main():
    image_path = "Sushi.png"  
    output_size = (50, 50)  
    block_size = 10 
    img = preprocess_image(image_path, output_size)

    draw_with_turtle(img, block_size)
    
main()
