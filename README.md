
# Django Project Management Application

A backend-focused project management application built with Django.  
It features a complete user authentication system, full CRUD (Create, Read, Update, Delete) functionality for projects, and a detailed Role-Based Access Control (RBAC) system.  
The user interface is progressively enhanced with **HTMX** to provide a dynamic, single-page feel for key actions.

---

## 🚀 Core Features

- **User Authentication**  
  Secure user sign-up, login, and logout functionality.

- **Project CRUD**  
  Authenticated users can create, view, update, and delete projects based on their assigned permissions.

- **Role-Based Access Control (RBAC)**
  - **Owner**: Full control over the project, including managing users and deleting the project.
  - **Editor**: Can view and edit project details but cannot delete the project or manage users.
  - **Reader**: Can only view project details and its members.

- **Dynamic UI with HTMX**  
  Key actions like creating projects and managing users are handled via AJAX requests, providing a smooth user experience without full page reloads.

---

## 🧱 Technical Stack

- **Backend**: Python, Django  
- **Frontend**: HTML, HTMX  
- **Database**: SQLite (default for development)

---

## ⚙️ Setup and Installation

Follow these instructions to get the project running on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name
```

### 2. Create and Activate a Virtual Environment

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows:**
```bash
python -m venv .venv
.\.venv\Scriptsctivate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations

```bash
python manage.py migrate
```

### 5. Create a Superuser (Optional)

```bash
python manage.py createsuperuser
```

You will be prompted to enter a username, email, and password.

### 6. Run the Development Server

```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 📝 How to Use the Application

### 🔐 Sign Up / Create First User

- Navigate to the running application.
- Click the "Sign Up" link and create your first user account.
- This user will become the **Owner** of any project they create.

### ➕ Create a New Project

- Once logged in, you will be on the main projects page.
- Click the **"Create New Project"** button. The form appears dynamically via HTMX.
- Fill in the project details and click **"Save Project"**.
- The project list updates instantly.

### 👥 Manage Users in a Project

- Click a project to go to its **Project Detail** page.
- As the **Owner**, you will see a **"Manage Users"** button.
- Click it to open the user management interface.

### ➕ Add a Second User as an Editor

- Open an incognito/private browser window and sign up with a new username.
- Return to your main browser where you're logged in as the project Owner.
- Go to the "Manage Users" page.
- Enter the second user's username, choose **'Editor'**, and click **"Add User"**.
- The user appears in the **Current Members** list.

### 🔒 Verify Role Permissions

- Log out of the Owner account and log in as the **Editor**.
- Visit the project’s detail page.

As an **Editor**, you should:
- ✅ See and use the "Edit Project" button

As an **Editor**, you should **NOT**:
- ❌ See the "Manage Users" button  
- ❌ See the "Delete Project" button

This confirms that Role-Based Access Control is functioning as intended.

---

## ✅ Final Notes

- This project emphasizes clean code structure, secure authentication, and minimal UI with high interactivity using HTMX.
- Ideal for demonstrating backend logic with modern frontend enhancement.
