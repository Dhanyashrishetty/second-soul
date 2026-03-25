# Second Soul - Charity Website

This is the final, fully functional version of the Second Soul charity application.

## 🚀 Features

### 1. User Authentication
-   **Register**: Create an account with detailed information (Name, Email, Phone, Address).
-   **Login**: Secure login with email and password.
-   **Guest Access**: "Continue as Guest" button allows limited access without an account.
-   **Logout**: Secure logout functionality.

### 2. Dashboard
-   **Central Hub**: View statistics (NGOs, Volunteers, Donations).
-   **Navigation Cards**: Quick access to all main features.

### 3. NGO Registration
-   **Detailed Form**: Register NGOs with name, owner info, registration number, and description.
-   **QR Code**: Upload a QR code for donations.
-   **Directory**: View list of all registered NGOs with their QR codes.

### 4. Volunteer Registration
-   **Sign Up**: Join as a volunteer with skills and availability.
-   **Community**: View a list of other active volunteers.

### 5. Donations
-   **Donate Item**: Form to donate items (Clothes, Books, etc.) with image upload.
-   **Donate Money**: Select an NGO, view their QR code, and enter amount.
-   **Guest Donations**: Guests can donate by providing name/email/phone.
-   **Vouchers**: Receive a unique "Gift Voucher" code after a monetary donation.

### 6. Activities
-   **Transparency**: View tables of all registered NGOs, Volunteers, and recent Donations.

## 🛠️ Setup & Run

1.  **Install Dependencies** (if not already installed):
    ```bash
    pip install flask flask-cors flask-sqlalchemy
    ```

2.  **Run the Application**:
    ```bash
    python app.py
    ```
    *The database `charity.db` will be automatically created on the first run.*

3.  **Access the Website**:
    Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

## ⚠️ Troubleshooting

-   **"Button Not Working"**: Ensure you have refreshed the page (CRTL+F5) to clear any old cache.
-   **Database Errors**: If you see database errors, delete `charity.db` and restart the app to recreate it cleanly.
-   **Images Not Loading**: Ensure the `static/uploads` folder exists (the app creates it automatically).

## 📝 Usage Guide

1.  **Start as Guest**: Click "Continue as Guest" on the home page.
2.  **Browse**: Go to "NGOs" to see who you can help.
3.  **Donate**: Go to "Donate", select "Donate Money", choose an NGO (QR code appears), enter amount, and Submit.
4.  **Register**: Go back Home, click "Register", fill details. Login to access the full Dashboard.
