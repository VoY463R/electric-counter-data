import cv2 as cv
import numpy as np
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("electric-data-bcc46-firebase-adminsdk-90nfi-09810ff75f.json")
firebase_admin.initialize_app(cred)

class GettingNumbers:
    def __init__(self, img):
        self.image = img
        self.matched_digits = []
        self.scale_percent = 30
        # Minimalny i maksymalny rozmiar konturów cyfr
        self.min_width, self.min_height = 10, 30
        self.max_width, self.max_height = 100, 100
        self.loading_templates()
        self.final_value = ""
        self.db = firestore.client()
        self.doc_ref = self.db.collection("CounterCollection").document()
        self.collection_ref = self.db.collection("CounterCollection")
        
    def finding_digits(self):
        
        #Zdefiniowanie nowych wymiarów zdjęcia
        width = int(self.image.shape[1] * self.scale_percent / 100)
        height = int(self.image.shape[0] * self.scale_percent / 100)
        new_size = (width, height)

        # Zmiana rozmiaru obrazu
        original_cropped = cv.resize(self.image, new_size, interpolation=cv.INTER_AREA)[300:400, 480:700]
        
        # Konwersja na odcienie szarości
        gray_masked_image = cv.cvtColor(original_cropped, cv.COLOR_BGR2GRAY)
        
        # Threshold
        _, thresh_image = cv.threshold(gray_masked_image, 100, 255, cv.THRESH_BINARY_INV)
        
        # Zastosowanie dylacji, aby połączyć segmenty cyfr
        kernel = np.ones((3, 3), np.uint8)
        dilated_image = cv.dilate(thresh_image, kernel, iterations=1)

        # Znalezienie kontur
        contours, _ = cv.findContours(dilated_image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv.boundingRect(contour)

            # Filtrujemy kontury według rozmiaru
            if self.min_width < w < self.max_width and self.min_height < h < self.max_height:
                # Wyciągamy region z konturem (ROI)
                contour_roi = thresh_image[y : y + h, x : x + w]

                # Dopasowanie szablonu i identyfikacja cyfry
                matched_digit = self.match_digit(contour_roi)

                # Wyświetlamy cyfrę i rysujemy prostokąt
                if matched_digit is not None:
                    self.matched_digits.append((matched_digit, x))
                    cv.putText(
                        original_cropped,
                        str(matched_digit),
                        (x, y - 10),
                        cv.FONT_HERSHEY_SIMPLEX,
                        0.9,
                        (0, 255, 0),
                        2,
                    )
                    cv.rectangle(original_cropped, (x, y), (x + w, y + h), (0, 255, 0), 2)

        self.final_value_func(self.matched_digits)
        return original_cropped
        
        
    def match_digit(self, contour_roi):
        best_match = None
        best_score = float("inf")

        # Przeprowadź dopasowanie do każdej cyfry

        for digit, template in self.templates.items():
            # Zmień rozmiar szablonu do wielkości regionu konturu
            resized_template = cv.resize(template, (contour_roi.shape[1], contour_roi.shape[0]))

            # Dopasowanie szablonu (używamy metody TM_SQDIFF, bo chcemy minimalnej różnicy)
            result = cv.matchTemplate(contour_roi, resized_template, cv.TM_SQDIFF)
            score = np.min(result)

            if score < best_score:
                best_score = score
                best_match = digit
                
        return best_match
            
    # Wczytaj szalbony cyfr
    def loading_templates(self):
        self.templates = {}
        for i in range(10):
            digit = cv.imread(f"digits/{i}.jpg", 0)
            inversted_image = cv.bitwise_not(digit)
            self.templates[i] = inversted_image

    #Utworzenie zmiennej final_value zawierającą odczytane dane
    def final_value_func(self,matched_digits):
        final_list = [digit[0] for digit in sorted(matched_digits, key=lambda x: x[1])]
        for digit in final_list:
            self.final_value += str(digit)
            
    def publishing_data(self):
        timestamp = datetime.now().strftime("%y-%m-%d %H:%M:%S")
        message = {
            "Odczytana wartosc": self.final_value,
            "Czas": timestamp,
            "Status": "ok"
        }
        
        self.doc_ref.set(message)
        print("Document ID:", self.doc_ref.id)
        
    def getting_data_firebase(self):
        
        docs = self.collection_ref.stream()
        
        for doc in docs:
            print(f"Dokument ID: {doc.id}, Dane: {doc.to_dict()}")  
        
img = cv.imread("licznik.jpg")

testowanie = GettingNumbers(img)

original_cropped = testowanie.finding_digits()

final_value = testowanie.final_value

print("Odczytana wartość: {}".format(final_value))

testowanie.getting_data_firebase()

cv.imshow("Zidentyfikowane cyfry", original_cropped)

# Zakończenie wyświetlania po wciśnięciu dowolnego klawisza
cv.waitKey(0)