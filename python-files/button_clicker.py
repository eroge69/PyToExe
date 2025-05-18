import autopy
import time
import numpy
import cv2
from PIL import ImageGrab

def get_screenshot():
    """
    This function captures a screenshot, and converts it to HSV format.
    :return: The array that the image is stored as
    """
    # Dimensions of screenshot 2100, 3360
    # Dimensions of my screen 1050, 1670
    image = ImageGrab.grab()
    image.save("screenshot.png", "PNG")

    # change image to BGR format
    image = cv2.imread("screenshot.png")

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return hsv_image

def analyze_screenshot(image, boundaries):
    """
    This function will analyze the screenshot for pixels with the
    specific boundaries.

    :param image: The image that is to be analyzed
    :param boundaries: The list of HSV values that are being searched for
    :return: A version of the image where the correct color pixels are white,
        and any other pixel that is not the desired color is black.
    """
    for (lower_bound, upper_bound) in boundaries:
        # Convert the limits into numpy arrays
        lower = numpy.array(lower_bound)
        upper = numpy.array(upper_bound)

        # Find the colors within the orange boundaries (uses HSV)
        # The inRange function changes anything in the range to white
        #  everything else turns black
        mask = cv2.inRange(image, lower, upper)

        # Restores the image back to original colors, but anything not
        # within the bounds is black
        output = cv2.bitwise_and(image, image, mask=mask)

    return mask


def find_button_coords():
    """
    This function will locate the center of the button at the time the
    function is called.

    :return: x_coord, y_coord
        A tuple containing the x and y
        coordinates of the center of the button
    """
    # Get the mouse out of the way
    autopy.mouse.move(0, 0)
    time.sleep(.1)

    # Get the HSV formatted screenshot
    image = get_screenshot()

    # Values are stored as HSV
    orange_boundaries = [([13, 203, 187], [13, 203, 187])]

    # Analyze the screenshot to find specific colored pixels
    analzyed_image = analyze_screenshot(image, orange_boundaries)

    # Get location of desired pixels
    indices = numpy.where(analzyed_image == [255])

    # Get mean of x location and y location to find center of circle
    x_location = numpy.mean(indices[1])
    y_location = numpy.mean(indices[0])

    # Divided by 2 to scale to my screen
    return x_location / 2, y_location / 2


def find_and_click_button():
    """
    This function will locate the position of the button, using
    find_button_coords, and clicks the center of the button once. At
    the end of the function, the mouse is moved to (0, 0) to get out of
    the way.

    :return: x_coord, y_coord
        A tuple of information containg the location
        of the center of the button before it was clicked.
    """
    x, y = find_button_coords()

    # Move the mouse to the specific location
    autopy.mouse.move(x, y)

    # Wait for autopy to move the mouse
    time.sleep(.1)

    # Click
    autopy.mouse.click()

    autopy.mouse.move(0, 0)
    time.sleep(.1)

    return x, y

def calculate_distance():
    """
    This function calculates the number of pixels that the button moves
    when the button is clicked.

    :return: x_coord, y_coord, x_dist, y_dist
        A tuple of information containing the current coordinates of the
        center of the button (x_coord anf y_coord) and the distance that
        the button moved (x_dist and y_dist)
    """

    # Clicks the button once
    x1, y1 = find_and_click_button()

    time.sleep(.3)

    # Find the coords of the button again
    x2, y2 = find_button_coords()

    time.sleep(.3)

    x_dist = x2 - x1
    y_dist = y2 - y1

    print(f"Distance calcualted: x: {x_dist} y: {y_dist}")

    return x2, y2, x_dist, y_dist

def predict_and_click_button_location(iterations):
    """
    This function will predict the location of the center of the circle
    and will click the predicted location.

    :param iterations: The number of times to click the button based on predictions
    :return: None
    """

    time.sleep(.3)

    curr_x, curr_y, x_dist, y_dist = calculate_distance()

    for i in range(0, iterations):
        autopy.mouse.move(curr_x, curr_y)
        time.sleep(.25)
        autopy.mouse.click()

        curr_x += x_dist
        curr_y += y_dist

        if curr_x < 0 or curr_y < 0:
            break

def main():
    """
    This where the main loop occurs.
    """
    
    while (True):
        predict_and_click_button_location(5)





if __name__ == "__main__":
    main()