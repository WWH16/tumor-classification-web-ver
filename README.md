# Tumor Classification System

<img src="https://icongr.am/feather/layers.svg?size=24" align="absmiddle" /> **Project Overview**  
The **Tumor Classification System** is a full-stack web application designed to assist in the early detection and classification of tumors. The system provides an intuitive interface for medical professionals and researchers to upload diagnostic data, receive classification results, and print comprehensive reports. Built with security and user experience in mind, it features a complete authentication flow and a dedicated dashboard for managing classifications.

## <img src="https://icongr.am/feather/star.svg?size=24" align="absmiddle" /> Key Features

* **Brain Tumor Classification:** Upload MRI scans to receive instant predictions ('Tumor' or 'No Tumor') powered by a pre-trained VGG16 Convolutional Neural Network (CNN) model using TensorFlow/Keras.
* **Patient Record Management:** Securely store and manage patient information alongside their MRI classifications, including age, sex, medical history, and clinical notes.
* **Interactive Dashboard:** View real-time analytics, including total classifications, monthly/weekly trends, average model confidence scores, diagnosis distribution, and a 30-day activity chart.
* **Advanced History & Filtering:** Search through past classifications by name, diagnosis, sex, or date range. Supports pagination, editing, and bulk deletion.
* **Export & Reporting:** Export classification history to CSV or generate professional, printable PDF/print reports for individual patient records.
* **Secure Authentication:** Full user authentication flow ensuring data privacy, where each user only accesses their own processed records.

## <img src="https://icongr.am/feather/cpu.svg?size=24" align="absmiddle" /> Tech Stack

* <img src="https://icongr.am/feather/server.svg?size=16" align="absmiddle" /> **Backend:** Python, Django
* <img src="https://icongr.am/feather/activity.svg?size=16" align="absmiddle" /> **Machine Learning:** TensorFlow, Keras (VGG16 architecture), OpenCV (Image Preprocessing), NumPy
* <img src="https://icongr.am/feather/database.svg?size=16" align="absmiddle" /> **Database:** SQLite
* <img src="https://icongr.am/feather/layout.svg?size=16" align="absmiddle" /> **Frontend:** HTML, CSS, JavaScript (Django Templates)

## <img src="https://icongr.am/feather/image.svg?size=24" align="absmiddle" /> Application Previews

### Landing Page
<img src="assets/landing.png" alt="Landing Page" width="800"/>

### Authentication
**Sign In**
<img src="assets/sigin.png" alt="Sign In Page" width="800"/>

**Sign Up**
<img src="assets/signup.png" alt="Sign Up Page" width="800"/>

### Dashboard
<img src="assets/dashboard.png" alt="User Dashboard" width="800"/>

### Tumor Classification Flow
**Classification Form**
<img src="assets/classificationform.png" alt="Classification Form" width="800"/>

**Classification Results**
<img src="assets/classificationresult_1.png" alt="Classification Result 1" width="800"/>
<img src="assets/classificationresult_2.png" alt="Classification Result 2" width="800"/>

### Reporting
**Printable Results**
<img src="assets/printingofresult_1.png" alt="Printing Result 1" width="800"/>
<img src="assets/printingofresult_2.png" alt="Printing Result 2" width="800"/>

## <img src="https://icongr.am/feather/tool.svg?size=24" align="absmiddle" /> Setup & Installation

1. <img src="https://icongr.am/feather/download.svg?size=16" align="absmiddle" /> Clone the repository.
2. <img src="https://icongr.am/feather/terminal.svg?size=16" align="absmiddle" /> Install the required dependencies: `pip install -r requirements.txt`
3. <img src="https://icongr.am/feather/database.svg?size=16" align="absmiddle" /> Apply database migrations: `python manage.py migrate`
4. <img src="https://icongr.am/feather/play.svg?size=16" align="absmiddle" /> Start the development server: `python manage.py runserver`
