📝 NoteShare

NoteShare is a web-based platform that allows users to register, upload, and download study notes.
Built using the Django framework, it provides a simple, secure, and efficient way for learners to share academic materials online.

🚀 Live Demo
https://noteshare-icya.onrender.com

📚 Features

✅ User authentication (Register / Login / Logout)
✅ Upload and manage personal notes
✅ Download shared notes from other users
✅ Responsive front-end built with HTML & CSS
✅ Secure file and data storage using modern cloud tools
🛠️ Use only your local storage to upload file for now as it has some error while uploading from drive(cloud).

🛠️ Tech Stack
Layer	        Technology Used
Frontend	    HTML, CSS
Backend	      Django (Python)
Database	    PostgreSQL via Neon.tech
File Storage  Supabase Storage
Deployment	  Render.com

⚙️ Installation & Setup (Local Development)

Follow these steps if you’d like to run the project locally:

1️⃣ Clone the repository
git clone https://github.com/KriXsh-09/NoteShare.git

2️⃣ Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
# OR
source venv/bin/activate  # On macOS/Linux

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Configure environment variables
Create a .env file in the project root and include the following:
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=your-neon-database-url
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-api-key

5️⃣ Apply migrations
python manage.py migrate

6️⃣ Run the server
python manage.py runserver

Now open http://127.0.0.1:8000/ to view it in your browser.

📁 Folder Structure

NoteShare/
├── NoteShare/            # Main Django project folder
│   ├── settings.py       # Django settings (configured for Render)
│   ├── urls.py           # URL routing
│   └── wsgi.py           # WSGI configuration for deployment
├── notes/                # App handling notes upload/download
├── templates/            # HTML templates
├── static/               # CSS and static files
├── requirements.txt      # Dependencies
├── manage.py             # Django management script
└── README.md             # Project documentation

🌐 Deployment Overview

Hosting: Render.com
Database: Neon.tech PostgreSQL
File Storage: Supabase Storage
Render automatically installs dependencies, runs migrations, and starts the Gunicorn server as configured.

🧠 Future Enhancements

Solve all the Existing Error
Add note categorization and tags
Add profile customization for users

👨‍💻 Author

Krishna Raj Prince
kkakrot09@gmail.com
https://github.com/KriXsh-09

📄 License

This project is licensed under the MIT License — feel free to modify and share!

