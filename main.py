import cv2
import imutils
import easyocr
import numpy as np
import time
from bs4 import BeautifulSoup
import requests


def vid_cap(vid):
    try:
        ret, frame = vid.read()
        image_name = "plate.png"
        cv2.imwrite(image_name, frame)
    except Exception:
        print("Could not save image from the webcam")


def plate_rec():
    plate_number = "-1"
    try:
        # read in an image, grayscale it and blur. Makes it easier to detect the numberplate.
        img = cv2.imread('plate.png')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # apply noise-reduction filter and find the edges in the image
        bfilter = cv2.bilateralFilter(gray, 11, 17, 17)
        edged = cv2.Canny(bfilter, 30, 200)

        # find contours and apply mask
        keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(keypoints)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]  # store top 10 contours

        # check if the contours are a square (number plates are squares)
        location = None
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 10, True)
            if len(approx) == 4:
                location = approx
                break

        # more mask and filter to single out the number plate in the image by painting the rest of the image with black
        mask = np.zeros(gray.shape, np.uint8)
        cv2.drawContours(mask, [location], 0, 255, -1)
        new_image = cv2.bitwise_and(img, img, mask=mask)

        # crops the numberplate out to make it easier for OCR to read
        x, y = np.where(mask == 255)
        x1, y1 = np.min(x), np.min(y)
        x2, y2 = np.max(x), np.max(y)
        cropped_image = gray[x1:x2 + 1, y1:y2 + 1]

        # OCR to read the text from the numberplate
        reader = easyocr.Reader(['sw'])
        result = reader.readtext(cropped_image)
        result = result[0]

        print(result[1])
        plate_number = result[1].replace(" ", "")

    except Exception:
        print("Something when wrong in the plate-recognition process")

    if plate_number == "-1":
        print("Could not read the numberplate")

    return plate_number


def web_scrape(plate_number):
    try:
        url = "https://biluppgifter.se/fordon/" + plate_number  # biluppgifter.se url to the car
        page = requests.get(url).text
        doc = BeautifulSoup(page, "html.parser")

        # scrapes the link to merinfo.se about the owner of the car
        items = doc.findAll('a', href=True, class_="gtm-merinfo")
        tag = items[0]

        # html-page of the owner on merinfo.se
        owner_url = tag.get('href')
        owner_page = requests.get(owner_url).text
        owner_doc = BeautifulSoup(owner_page, "html.parser")

        # extracts the name of the owner
        title = owner_doc.find('title')
        owner_info = title.string.split(') ', 1)
        owner_info = owner_info[0] + ')'

        print(owner_info)

    except Exception:
        print("Something went wrong while trying to scrape the owner information")


if __name__ == '__main__':
    video = cv2.VideoCapture(0)
    while True:
        vid_cap(video)
        plate_number = plate_rec()
        web_scrape(plate_number)
        time.sleep(1)
