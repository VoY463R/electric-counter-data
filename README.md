# Python Smart Meter OCR

### An application for reading and saving data from electric meters using image recognition and Firebase and then displaying the stored data using Flask.

The project is used to remotely monitor the status of electricity consumption given by the electric meter. The whole project mainly uses technologies such as Optical character recognition (OCR), FireBase databases and Flask micro-framework.

## Features
- Reads numbers from analog electric meters using OCR (OpenCV)
- Saves data to a Firebase database in real time.
- Provides data visualization and history tracking.

## Technologies
- Python
- OpenCV
- FireBase
- Flask

## Requirements
- Python 3.8+
- Python Virtual Environment
- Firebase (access key file) 

## Installation

1. Clone the repository:
```bash
git clone https://github.com/VoY463R/electric-counter-data
cd electric-counter-data
```
2. Create and Activate Virtual Environment:
```bash
python3 -m venv venv
venv\Scripts\activate
```
3. Install dependecies:
```bash
pip install -r requirements.txt
```
4. Configure environment variables: Create a .env file with the necessary configuration:
```bash
SECRET_KEY=your_secret_key
SQLALCHEMY_DATABASE_URI=your_database_uri
```
5. Set up Firebase credentials:
- Download your Firebase credentials JSON file.
- Place the JSON file in the root directory and name it `firebase-key.json`.

## Usage

1. Run the application:
```bash
python init.py
```
2. Access the app at http://127.0.0.1:5000

## Issues & Contribution
Contributions are welcome! Please open an issue or submit a pull request if you'd like to contribute.