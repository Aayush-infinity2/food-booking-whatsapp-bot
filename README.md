# LPU Food Booking Bot
# 🍔 LPU Campus Food Booking WhatsApp Bot & Admin Portal
Flask-based food ordering MVP with a WhatsApp chatbot, MySQL order storage,
an admin dashboard, and a student ordering portal.
> A smart, AI-powered food ordering ecosystem for university campuses. Students can order food on WhatsApp in natural everyday language, while restaurant managers control orders, inventory stock, and sales analytics through a modern dark-glass web portal.
## Start locally
---
1. Create a MySQL database named `food_booking_bot` and run `database/schema.sql`.
2. Copy the required credentials into `.env` (this file must never be committed).
3. Install packages: `venv\\Scripts\\pip install -r requirements.txt`
4. For an existing database, run: `venv\\Scripts\\python -m database.migrate`
5. Start the app: `venv\\Scripts\\python app.py`
## 🌟 What is This Project?
Open `/student/login` for the student portal and `/admin/login` for the admin dashboard.
Imagine wanting to order food on your campus without standing in long queues or downloading complex apps. With **LPU Food Bot**, all you do is send a message on **WhatsApp** like:
## Current scope
> *"Order a hot and spicy pizza from Tripti for 1:00 PM"*
Student login, menu search, cart, pickup selection, order history, cancellation,
WhatsApp ordering, and admin order management are implemented in this MVP.
Natural-language food requests on WhatsApp use Gemini when `GEMINI_API_KEY` is configured;
the bot still supports the numbered menu flow if Gemini is unavailable.
Generate a valid API key in Google AI Studio and replace the current value in `.env` to enable
Gemini intent extraction.
AI recommendations, RAG, live notifications, demand prediction, and queue-based
slot recommendations require a separate data/AI phase after real order history exists.
The AI understands what you want, checks campus menus, compares prices, confirms your order, and sends your ticket straight to the restaurant kitchen!
Restaurant owners get a **real-time Admin Portal** where they can see incoming orders, update prep statuses (`Preparing` ➔ `Ready`), mark out-of-stock items, and view sales trends.
---
## ✨ Key Features
### 📱 1. For Students (WhatsApp Chatbot)
- 💬 **Natural Language Ordering**: Talk like a human! Order by food name, restaurant, or campus block.
- 💰 **Cheapest Price Recommendations**: Ask *"suggest burgers"* and get campus options sorted from cheapest to premium.
- 🚫 **Out-of-Stock Alerts**: Instant notification if an item is sold out at a restaurant.
- 🔄 **Easy Order Switching & Reset**: Type `cancel`, `reset`, or `menu` anytime to change your order or return home.
- ⏰ **Pickup Slot Scheduling**: Choose pickup slots (`10:00 AM`, `11:00 AM`, `12:00 PM`, etc.) to skip counter waiting times.
### 👑 2. For Restaurant Admins (Web Portal)
- 🎨 **Modern Dark-Glass Dashboard**: Sleek visual interface for monitoring live orders.
- ⚡ **Real-Time Order Tracking**: Update order status from `Pending` ➔ `Preparing` ➔ `Ready` ➔ `Completed`.
- ☕ **Inventory Stock Control**: Toggle menu items **In Stock** / **Out of Stock** with one click.
- 📊 **Sales & Trend Analytics**: 7-day order volume charts, status breakdown doughnuts, and top-selling food rankings.
- 👥 **Student & Menu Catalog Directories**: Searchable database of all campus students and menu items.
---
## 🧠 How It Works (Simple 4-Step Flow)
```text
  [ 📱 Student ]
        │ Sends: "Order biryani from Tripti"
        ▼
  [ 🤖 Gemini AI / Smart NLP ]
        │ Extracts: Item="Biryani", Restaurant="Tripti"
        ▼
  [ 🗄️ Campus Menu & Stock Engine ]
        │ Checks Price (₹120) & Stock (In Stock)
        ▼
  [ 🍳 Restaurant Admin Portal ]
        │ Order #104 appears live! Status: "Preparing" ➔ "Ready"
```
---
## 💬 Example WhatsApp Conversations
### 🔹 Example A: Natural Language Ordering
```text
Student : Order a paneer burger from Tripti
Bot     : 🍽 Selected Item: Paneer Burger
          🏪 Restaurant: Tripti
          💰 Price: ₹70
          -------------------------
          Enter Quantity (e.g. 1, 2, 3...)
Student : 2
Bot     : Choose Pickup Slot:
          1️⃣ 10:00 AM
          2️⃣ 11:00 AM
          3️⃣ 12:00 PM
          4️⃣ 01:00 PM
Student : 3
Bot     : 🧾 Order Summary
          Restaurant: Tripti | Item: Paneer Burger (Qty: 2)
          Pickup Slot: 12:00 PM | Total: ₹140
          Reply YES to confirm or NO to cancel.
```
### 🔹 Example B: Price Comparison Recommendation
```text
Student : suggest burgers
Bot     : 🍔 Here are the best Burger options across campus (sorted by price):
          1️⃣ Veg Burger — ₹50
             🏪 Tripti · Boys Hostel
          2️⃣ Cheese Burger — ₹65
             🏪 Basant · Block 34
          3️⃣ Paneer Burger — ₹70
             🏪 Tripti · Boys Hostel
          Reply with option number (e.g. 1, 2...) to select.
```
---
## 💻 How to Use the Admin Web Portal
1. Open **`/admin/login`** in your browser.
2. Enter default admin credentials:
   - **Username**: `admin`
   - **Password**: `admin123`
3. Navigation Options:
   - 📊 **Dashboard**: Live orders list with quick status update buttons.
   - 📈 **Analytics**: Interactive sales volume graphs and top 5 best-selling food items.
   - ☕ **Menu Catalog**: Toggle any item **In Stock** or **Out of Stock**.
   - 🎓 **Student Directory**: View registered student profiles.
---
## 🛠️ Technology Stack
- **Backend**: Python 3.11+, Flask Web Framework
- **Database**: MySQL (Local / Aiven Cloud MySQL)
- **AI & NLP**: Google Gemini 2.0 Flash API + Local Regex Fallback Engine
- **WhatsApp Integration**: Meta WhatsApp Cloud API (`graph.facebook.com`)
- **Frontend UI**: HTML5, Vanilla CSS3 (Dark Glassmorphism), Bootstrap 5, DataTables.js, Chart.js
---
## 🚀 Quick Local Setup Guide
### 1. Clone & Install Dependencies
```bash
git clone https://github.com/YOUR_USERNAME/food-booking-whatsapp-bot.git
cd food-booking-whatsapp-bot
# Install required Python libraries
pip install -r requirements.txt
```
### 2. Configure Environment Variables
Create a `.env` file in the root folder with:
```env
ACCESS_TOKEN=your_meta_whatsapp_token
PHONE_NUMBER_ID=your_whatsapp_phone_number_id
VERIFY_TOKEN=food_booking_bot
GEMINI_API_KEY=your_gemini_api_key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
SECRET_KEY=food_booking_secret_key_2026
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_NAME=food_booking_bot
```
### 3. Initialize Database
Run our automated database installer:
```bash
python init_db.py
```
### 4. Run the Application
```bash
python app.py
```
Open your browser at **`http://127.0.0.1:5000/admin/login`**!
---
## ☁️ Cloud Deployment
- **Web Server**: Deployed on [Render.com](https://render.com/) with Gunicorn (`web: gunicorn app:app`).
- **Database**: Hosted on [Aiven.io Cloud MySQL](https://aiven.io/).
- **WhatsApp Webhook**: Connected via Meta Developer Portal at `https://your-domain.onrender.com/webhook`.
---
## 📜 License
Developed for LPU Campus Food Outlets. Open-source and free for educational use.
