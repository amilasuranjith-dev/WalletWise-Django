# WalletWise 💰
> Smart Personal Finance Manager

WalletWise is a modern, lightweight web application built with Django that helps users track their income, expenses, and overall financial health. It provides a centralized solution to monitor account balances, categorize spending, and generate simple financial summaries.

## ✨ Features (MVP)
* **User Authentication:** Secure registration, login, and session management.
* **Account Management:** Track multiple financial accounts (e.g., Cash Wallet, Savings, Bank Accounts) and their current balances.
* **Category Management:** Organize spending using default system categories (Food, Transport, Salary) or create custom user-specific categories.
* **Transaction Tracking:** Record income and expenses. Transactions automatically and safely update account balances using atomic database transactions.
* **Dashboard Overview:** Get a quick glance at Total Income, Total Expenses, Current Balance, and recent transactions.

## 🛠️ Tech Stack
* **Backend Framework:** Django 
* **Database:** MySQL
* **Frontend:** HTML, CSS (Bootstrap/Tailwind via Django Templates)
* **Environment Management:** `python-dotenv`

---

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing.

### Prerequisites
* Python 3.10+
* MySQL Server
* Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/WalletWise-Django.git
   cd WalletWise-Django
   ```

2. **Create a MySQL Database:**
   Open your MySQL client and run:
   ```sql
   CREATE DATABASE wallet_wise;
   ```

3. **Set up a Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

4. **Install Dependencies:**
   *(Note: A requirements.txt will be added in future updates. For now, install manually)*
   ```bash
   pip install django mysqlclient python-dotenv
   ```

5. **Configure Environment Variables:**
   Create a `.env` file in the root directory of the project and add your database credentials and Django secret key:
   ```env
   SECRET_KEY=your_django_secret_key
   DB_NAME=wallet_wise
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_HOST=127.0.0.1
   DB_PORT=3306
   ```

6. **Run Database Migrations:**
   ```bash
   python manage.py migrate
   ```

7. **Start the Development Server:**
   ```bash
   python manage.py runserver
   ```
   Navigate to `http://127.0.0.1:8000` in your browser.

---

## 🗺️ Future Roadmap
* **v2:** Reports and Analytics (Monthly trends, widgets)
* **v3:** Budget Planning System (Category limits)
* **v4:** Recurring Transactions (Automated salary/bills)
* **v5:** Savings Goal Tracker

## 📄 License
This project is for educational and portfolio purposes.
