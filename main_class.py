import cv2 as cv
import numpy as np
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import logging

cred = credentials.Certificate(
    "electric-data-bcc46-firebase-adminsdk-90nfi-09810ff75f.json")
firebase_admin.initialize_app(cred)


class GettingNumbers:
    def __init__(self, img):
        self.image = img
        self.matched_digits_with_positions = []
        self.scale_percent = 30
        self.min_width, self.min_height = 10, 30
        self.max_width, self.max_height = 100, 100
        self.loading_templates()
        self.final_value = ""


    def finding_digits(self):
        """
        The method responsible for finding 7-segment digits from a photo returning a photo with the read digits and their location.
        """

        width = int(self.image.shape[1] * self.scale_percent / 100)
        height = int(self.image.shape[0] * self.scale_percent / 100)
        new_size = (width, height)

        original_cropped = cv.resize(self.image, new_size, interpolation=cv.INTER_AREA)[
            300:400, 480:700
        ]

        ## Conversion to shades of gray
        gray_masked_image = cv.cvtColor(original_cropped, cv.COLOR_BGR2GRAY)

        # Threshold
        _, thresh_image = cv.threshold(
            gray_masked_image, 100, 255, cv.THRESH_BINARY_INV
        )

        # Use of dilation to connect segments of digits
        kernel = np.ones((3, 3), np.uint8)
        dilated_image = cv.dilate(thresh_image, kernel, iterations=1)

        # Finding the contours
        contours, _ = cv.findContours(
            dilated_image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:
            x, y, w, h = cv.boundingRect(contour)

            # Filter outlines by size
            if (
                self.min_width < w < self.max_width
                and self.min_height < h < self.max_height
            ):
                # We pull out the region with the contour (ROI)
                contour_roi = thresh_image[y : y + h, x : x + w]

                # Template matching and digit identification
                matched_digit = self.match_digit(contour_roi)

                # Display a number and draw a rectangle
                if matched_digit is not None:
                    self.matched_digits_with_positions.append((matched_digit, x))
                    cv.putText(
                        original_cropped,
                        str(matched_digit),
                        (x, y - 10),
                        cv.FONT_HERSHEY_SIMPLEX,
                        0.9,
                        (0, 255, 0),
                        2,
                    )
                    cv.rectangle(
                        original_cropped, (x, y), (x + w, y + h), (0, 255, 0), 2
                    )

        self.final_value_func(self.matched_digits_with_positions)
        self.image = None
        return original_cropped

    def match_digit(self, contour_roi):
        """The method responsible for matching the number seen in the picture using the method of least squares.
        Args:
            contour_roi (_type_): region with the contour of the analyzed number
        """
        best_match = None
        best_score = float("inf")

        # Conduct a match for each digit
        for digit, template in self.templates.items():
            # Resize the template to the size of the outline region
            resized_template = cv.resize(
                template, (contour_roi.shape[1], contour_roi.shape[0])
            )

            # Template matching (we use the TM_SQDIFF method because we want minimal difference)
            result = cv.matchTemplate(contour_roi, resized_template, cv.TM_SQDIFF)
            score = np.min(result)

            if score < best_score:
                best_score = score
                best_match = digit

        return best_match

    def loading_templates(self):
        """Loading a template with 7-segment digits in the range 0-9"""
        self.templates = {}
        for i in range(10):
            digit = cv.imread(f"digits/{i}.jpg", 0)
            if digit is None:
                logging.error(f"Template for digit {i} not found.")
            inversted_image = cv.bitwise_not(digit)
            self.templates[i] = inversted_image

    def final_value_func(self, matched_digits_with_positions):
        """Method that returns the final digits ordered in the same order as in the image
        Args:
            matched_digits_with_positions (_list_): List of matched numbers from the photo along with the value of the coordinate x, e.g. (digit=100, x=20)
        """
        final_list = [digit[0] for digit in sorted(matched_digits_with_positions, key=lambda x: x[1])]
        self.final_value = "".join(map(str, final_list))
        saved_value = self.final_value
        self.final_value = ""

        return saved_value
            
class FireBase:
    def __init__(self, final_value = None):
        self.value = final_value
        self.db = firestore.client()
        self.doc_ref = self.db.collection("CounterCollection").document()
        self.collection_ref = self.db.collection("CounterCollection")

    def publishing_data(self, value=None):
        """Sending the read number to the FireBase server.

        Args:
            value (_type_, optional): Value to be sent. Default value read from the photo.
        """
        if value is None:
            value = self.value
        timestamp = datetime.now().strftime("%y-%m-%d %H:%M:%S")
        message = {"Readed Value": value, "Time": timestamp, "Status": "ok"}
        try:
            self.doc_ref.set(message)
            logging.info("Sending successfully completed. Document ID: %s", self.doc_ref.id)
        except Exception as e:
            logging.error(f"Error when sending data to FireBase server: {e}")


    def getting_data_firebase(self):
        """Downloading all data from Firebase"""
        data = []
        try:
            docs = self.collection_ref.stream()
            for doc in docs:
                data.append(doc.to_dict())
        except Exception as e:
            logging.error(f"Error while downloading data from FireBase server {e}")
        finally:
            return data

