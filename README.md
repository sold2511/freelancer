# 🧑‍💻 Freelancer Marketplace - Real-Time Job Portal

🌟 Objective
The objective of this project is to create a dynamic freelancing platform that connects clients and freelancers. The platform enables clients to post job opportunities, review proposals, and hire freelancers, while freelancers can browse jobs, submit proposals, and manage their work. It aims to streamline the freelancing process with features like real-time chat, notifications, and role-specific dashboards, ensuring a seamless and efficient experience for both clients and freelancers.



📆 Core Features
- 🔐 User Authentication (Client & Freelancer)
- 📃 Job Posting by Clients
- 📨 Proposal Submission by Freelancers
- ✅ Proposal Status Update by Clients
- 🔔 Real-time Notifications via Django Channels (WebSockets)
- 📱 Push Notifications via Firebase Cloud Messaging (FCM)
- 📥 Save Device Tokens for Authenticated Users
- 📬 Toast Notifications + Notification Badge on Update
- 📦 Firebase Integration via Service Account

🧰 Tech Stack

- **Backend**: Django, Django Channels, Redis
- **Frontend**: HTML, TailwindCSS, JavaScript
- **Real-time**: WebSockets (Channels), Redis
- **Push Notification**: Firebase FCM v1 API
- **Database**:  PostgreSQL (prod-ready)
- **Others**: Gunicorn, Daphne, Nginx (optional deployment)


🏗️ Project Structure (Key Apps)

freelancer_project/
│
├── accounts/ # User auth & profiles
├── jobs/ # Jobs & proposals
├── notification/ # Real-time & push notifications
├── freelancer_project/ # Core Django settings
├── static/ # CSS, JS
├── templates/ # Shared templates
├── secrets/ # Firebase service account
├── media/ # Uploaded files
├── db.sqlite3
└── manage.py

📅 Deployment Guide

1. Clone the repository
2. Set up virtual environment
3. Install dependencies
4. Create `.env` or use `python-decouple` for secrets
5. Apply migrations
6. Create superuser
7. Run the server

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver


📍 License

This project is for academic and educational use.