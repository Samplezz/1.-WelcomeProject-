# Student Resource Hub

A comprehensive student resource management platform that enables seamless material request and administration through an intuitive Streamlit web interface.

## Key Features

- **Resource Browsing & Downloading**: Access and download educational resources organized by university, semester, and course
- **Resource Request System**: Submit requests for missing materials
- **Admin Dashboard**: Manage resources, track requests, and monitor usage analytics
- **Secure Authentication**: Admin-only areas protected with password

## Getting Started

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   streamlit run streamlit.py
   ```

## Project Structure

- `streamlit.py`: Main application file with Streamlit UI components
- `models.py`: Data models for resource requests
- `utils.py`: Utility functions for file management and settings
- `admin.py`: Admin panel functionality
- `data/`: Directory containing application data (requests, settings)
- `assets/`: Directory for storing uploaded resource files


