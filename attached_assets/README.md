# Student Resource Portal

A Streamlit application for organizing and accessing educational resources by university, semester, and course.

## Features

- Three-tier navigation system: university, semester, and course
- Resource categories: past exams, study sheets, and tips/guides
- Admin portal for resource management
- Visual previews of resources with thumbnail gallery
- File download capability
- File renaming functionality for admins

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/student-resource-portal.git
cd student-resource-portal

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run main.py
```

## Usage

### Student View
- Select university, semester, and course
- Browse and download resources by category

### Admin Portal
- Access the admin panel with admin credentials
- Manage universities, semesters, and courses
- Upload and organize resources
- Rename files as needed

## Directory Structure

```
.
├── main.py                   # Main application file
├── admin.py                  # Admin portal functionality
├── utils.py                  # Utility functions
├── data/                     # Data storage directory
│   ├── settings.json         # Application settings
│   └── uploads/              # Uploaded resources
├── assets/                   # Assets for the application
└── .streamlit/               # Streamlit configuration
    └── config.toml           # Streamlit configuration file
```

## Technologies

- Python
- Streamlit
- Pandas

## License

MIT

## Author

Your Name