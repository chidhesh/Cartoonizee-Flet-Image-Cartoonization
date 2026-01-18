# 🎨 Cartoonizee – Image Cartoonization App (Flet UI)

Cartoonizee is a Python-based image cartoonization application built using **Flet UI** for the frontend and computer vision techniques for image processing. The application allows users to upload images and convert them into cartoon-style and sketch-style outputs through a modern, cross-platform UI.

---

## 🚀 Features

* Flet-based interactive UI (Desktop / Web capable)
* Upload images and generate:

  * Cartoon images
* Real-time image preview
* Lightweight and responsive design
* Python-powered image processing
* Docker-ready deployment support

---

---

## 🏗️ Project Structure

```
cartoonizee/
│
├── app.py                    # Main application entry (Flet UI)
├── video_api.py              # Optional video cartoonization logic
├── gcloud_utils.py           # Cloud utilities
├── config.yaml               # Application configuration
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker configuration
├── vercel.json               # Deployment configuration
├── LICENSE                   # License file
│
├── assets/                   # UI assets
├── images/                   # UI screenshots
├── storage/                  # Temporary image storage
└── white_box_cartoonizer/    # Core cartoonization algorithms
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/cartoonizee.git
cd cartoonizee
```

### 2️⃣ Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/binactivate        # Linux / macOS
venv\Scripts\activate          # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Flet Application

```bash
python app.py
```

> The Flet UI will launch automatically in a desktop window or browser depending on configuration.

---

## 🐳 Run Using Docker (Optional)

```bash
docker build -t cartoonizee .
docker run cartoonizee
```

---


This keeps the repository clean and professional.

---

## 🧰 Technologies Used

* **Python**
* **Flet UI**
* OpenCV
* NumPy
* Docker
* Git & GitHub

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author & Contact

**Name:** Chidhesh
**LinkedIn:**
🔗 [https://www.linkedin.com/in/chidhesh-kumar-452785298](https://www.linkedin.com/in/chidhesh-kumar-452785298)

---

⭐ If you find this project useful, consider starring the repository.
