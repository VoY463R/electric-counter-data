import cv2 as cv
import numpy as np
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("electric-data-bcc46-firebase-adminsdk-90nfi-09810ff75f.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
doc_ref = db.collection("CounterCollection").document()


# Odczytanie cyfr z zdjęcia
def finding_digits(img):
    # Zdefiniowanie współczynnika skalowania
    scale_percent = 30
    matched_digits = []

    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    new_size = (width, height)

    # Zmiana rozmiaru obrazu
    original_cropped = cv.resize(img, new_size, interpolation=cv.INTER_AREA)[300:400, 480:700]

    # Konwersja na odcienie szarości
    gray_masked_image = cv.cvtColor(original_cropped, cv.COLOR_BGR2GRAY)

    # Threshold
    _, thresh_image = cv.threshold(gray_masked_image, 100, 255, cv.THRESH_BINARY_INV)

    # Zastosowanie dylacji, aby połączyć segmenty cyfr
    kernel = np.ones((3, 3), np.uint8)
    dilated_image = cv.dilate(thresh_image, kernel, iterations=1)

    # Znalezienie kontur
    contours, _ = cv.findContours(
        dilated_image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE
    )

    # Minimalny i maksymalny rozmiar konturów cyfr
    min_width, min_height = 10, 30
    max_width, max_height = 100, 100

    for contour in contours:
        x, y, w, h = cv.boundingRect(contour)

        # Filtrujemy kontury według rozmiaru
        if min_width < w < max_width and min_height < h < max_height:
            # Wyciągamy region z konturem (ROI)
            contour_roi = thresh_image[y : y + h, x : x + w]

            # Dopasowanie szablonu i identyfikacja cyfry
            matched_digit = match_digit(contour_roi)

            # Wyświetlamy cyfrę i rysujemy prostokąt
            if matched_digit is not None:
                matched_digits.append((matched_digit, x))
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

    final_value_func(matched_digits)
    return original_cropped


# Funkcja do dopasowania szablonu
def match_digit(contour_roi):
    best_match = None
    best_score = float("inf")

    # Przeprowadź dopasowanie do każdej cyfry

    for digit, template in templates.items():
        # Zmień rozmiar szablonu do wielkości regionu konturu
        resized_template = cv.resize(
            template, (contour_roi.shape[1], contour_roi.shape[0])
        )

        # Dopasowanie szablonu (używamy metody TM_SQDIFF, bo chcemy minimalnej różnicy)
        result = cv.matchTemplate(contour_roi, resized_template, cv.TM_SQDIFF)
        score = np.min(result)

        if score < best_score:
            best_score = score
            best_match = digit

    return best_match


# Wczytaj szalbony cyfr
def loading_templates():
    templates = {}
    for i in range(10):
        digit = cv.imread(f"digits/{i}.jpg", 0)
        inversted_image = cv.bitwise_not(digit)
        templates[i] = inversted_image
    return templates

#Utworzenie zmiennej final_value zawierającą odczytane dane
def final_value_func(matched_digits):
    final_list = [digit[0] for digit in sorted(matched_digits, key=lambda x: x[1])]
    global final_value
    for digit in final_list:
        final_value += str(digit)
        
# Wysłanie wiadomości
def publish_data(value):
    timestamp = datetime.now().strftime("%y-%m-%d %H:%M:%S")
    message = {
        "Odczytana wartosc": value,
        "Czas": timestamp,
        "Status": "ok"
    }
    
    doc_ref.set(message)

    print("Document ID:", doc_ref.id)

def getting_data_firebase():
    
    collection_ref = db.collection("CounterCollection")

    docs = collection_ref.stream()

    for doc in docs:
        print(f"Dokument ID: {doc.id}, Dane: {doc.to_dict()}")

# Wartość odczytana
final_value = ""

# Odczyt obrazu
img = cv.imread("licznik.jpg")

templates = loading_templates()

original_cropped = finding_digits(img)

getting_data_firebase()

print("Odczytana wartość: {}".format(final_value))

cv.imshow("Zidentyfikowane cyfry", original_cropped)

# Zakończenie wyświetlania po wciśnięciu dowolnego klawisza
cv.waitKey(0)
