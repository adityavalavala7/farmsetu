# 🌱 FarmSetu – From Farm to Family

**FarmSetu** is a farmer-to-customer agricultural marketplace designed to connect local farmers directly with customers. It helps farmers reach nearby buyers while making fresh agricultural produce more accessible.

## 🚀 Key Features

### 👨‍🌾 For Farmers
- Farmer registration and login.
- Create and manage farmer profiles.
- Add, update and delete crop listings.
- Upload crop images.
- Manage crop prices and available stock.
- Receive and manage customer orders.
- Track sales, commissions and earnings.
- Receive customer ratings and reviews.

### 🛒 For Customers
- Customer registration and login.
- Explore nearby farmers and available crops.
- Search and filter agricultural products.
- Find farmers based on distance.
- Select a preferred search radius.
- Add products to cart.
- Place orders for home delivery or farmer pickup.
- Track order status.
- Rate and review completed orders.

## 💰 Revenue Model
- 4.5% commission on completed order items.
- Cash on Delivery.
- Cash on Pickup.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Web framework |
| HTML5 | Structure |
| CSS3 | Styling |
| JavaScript | Interactivity |
| PostgreSQL | Production database |
| SQLite | Local development |
| Cloudinary | Image storage |
| Vercel | Deployment |

## 📍 Initial Target Location

Bhimavaram, Andhra Pradesh, India, and surrounding villages.

## 📂 Project Structure

```text
farmsetu/
├── accounts/
├── config/
├── marketplace/
├── templates/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── manage.py
├── requirements.txt
└── README.md
```

## ⚙️ Local Setup

1. Clone the repository:

```bash
git clone https://github.com/adityavalavala7/farmsetu.git
cd farmsetu
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure the required environment variables in `.env`.

5. Apply migrations:

```bash
python manage.py migrate
```

6. Start the development server:

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`.

## 🔮 Future Scope
- Progressive Web App (PWA).
- Android application.
- Online payment integration.
- Advanced analytics for farmers.
- Expansion to additional regions.

## 🎯 Vision

To empower local farmers, simplify agricultural trade and build a stronger connection between farmers and consumers.

**FarmSetu – From Farm to Family.**

## 👨‍💻 Repository

[GitHub – FarmSetu](https://github.com/adityavalavala7/farmsetu)
