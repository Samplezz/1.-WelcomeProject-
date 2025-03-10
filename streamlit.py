import streamlit as st
import pandas as pd
import os
import json
import base64
from datetime import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import io
import shutil

# Page configuration
st.set_page_config(
    page_title="Student Resource Hub",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure we're binding to all interfaces for deployment
os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
os.environ['STREAMLIT_SERVER_PORT'] = '5000'

# Constants
STATUS_PENDING = "Pending"
STATUS_IN_PROGRESS = "In Progress"
STATUS_COMPLETED = "Completed"
STATUS_REJECTED = "Rejected"

PRIORITY_LOW = "Low"
PRIORITY_MEDIUM = "Medium"
PRIORITY_HIGH = "High"

RESOURCE_TYPES = [
    "Exam", 
    "Assignment", 
    "Lecture Notes", 
    "Study Guide", 
    "Solutions", 
    "Textbook", 
    "Other"
]

# Default settings
DEFAULT_SETTINGS = {
    "universities": ["MIT", "Stanford", "Harvard"],
    "semesters": {
        "MIT": ["Fall 2023", "Spring 2024"],
        "Stanford": ["Fall 2023", "Winter 2024", "Spring 2024"],
        "Harvard": ["Fall 2023", "Spring 2024"]
    },
    "courses": {
        "MIT_Fall 2023": ["Computer Science 101", "Physics 201", "Calculus I"],
        "MIT_Spring 2024": ["Computer Science 102", "Physics 202", "Calculus II"],
        "Stanford_Fall 2023": ["Introduction to AI", "Data Structures", "Machine Learning Basics"],
        "Stanford_Winter 2024": ["Advanced AI", "Algorithms", "Natural Language Processing"],
        "Stanford_Spring 2024": ["Robotics", "Computer Vision", "Deep Learning"],
        "Harvard_Fall 2023": ["Introduction to Programming", "Principles of Economics", "Statistics"],
        "Harvard_Spring 2024": ["Advanced Programming", "Microeconomics", "Data Science"]
    }
}

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 1px solid #444;
        margin-bottom: 2rem;
    }
    .resource-section {
        background-color: #2D2D2D;
        padding: 1.5rem;
        border-radius: 5px;
        margin-bottom: 1.5rem;
    }
    .resource-header {
        border-bottom: 2px solid #FF5252;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .find-resources-btn {
        background-color: #FF5252;
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 4px;
        cursor: pointer;
        text-align: center;
        display: block;
        margin: 1rem auto;
        font-weight: bold;
    }
    .tab-container {
        margin-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF5252 !important;
        color: white !important;
    }
    .download-btn {
        background-color: #FF5252;
        color: white;
        text-decoration: none;
        padding: 0.3rem 0.7rem;
        border-radius: 4px;
        display: inline-block;
        margin-top: 0.5rem;
        font-size: 0.9rem;
        text-align: center;
    }
    .file-card {
        background-color: #2D2D2D;
        border-radius: 5px;
        padding: 0.8rem;
        margin: 0.5rem;
        display: inline-block;
        width: 150px;
        vertical-align: top;
    }
    .file-name {
        font-size: 0.9rem;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        word-wrap: break-word;
        text-align: center;
    }
    .file-container {
        display: flex;
        flex-wrap: wrap;
    }
    .thumbnail-container {
        height: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .file-icon {
        font-size: 3rem;
        text-align: center;
    }
    .sidebar-content {
        background-color: #2D2D2D;
        padding: 1rem;
        border-radius: 5px;
    }
    .admin-btn {
        background-color: #333;
        border: 1px solid #FF5252;
        color: white;
        text-align: center;
        padding: 0.5rem;
        border-radius: 4px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Utility functions
def create_directory_if_not_exists(directory_path):
    """Create a directory if it doesn't exist"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def load_settings():
    """Load settings from the settings.json file"""
    settings_path = Path("data/settings.json")
    
    if not settings_path.exists():
        create_directory_if_not_exists(settings_path.parent)
        with open(settings_path, 'w') as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)
        return DEFAULT_SETTINGS
    
    try:
        with open(settings_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS

def save_settings(settings):
    """Save settings to the settings.json file"""
    settings_path = Path("data/settings.json")
    
    try:
        if not settings_path.parent.exists():
            settings_path.parent.mkdir(parents=True)
            
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving settings: {e}")
        return False

def get_file_path(university, semester, course):
    """Generate a file path for a given university, semester, and course"""
    base_path = Path("data/uploads")
    return base_path / university / semester / course

def format_datetime(iso_datetime):
    """Format ISO datetime string to readable format"""
    try:
        dt = datetime.fromisoformat(iso_datetime)
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return iso_datetime

def file_download_link(file_path, file_name):
    """Generate a download link for a file"""
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    file_size = os.path.getsize(file_path) / 1024  # Size in KB
    short_name = file_name
    if len(short_name) > 20:
        # Truncate name if too long (for display)
        name_parts = os.path.splitext(file_name)
        short_name = name_parts[0][:17] + "..." + name_parts[1]
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}" class="download-btn">Download ({file_size:.1f} KB)</a>'

# Resource Request class
class ResourceRequest:
    def __init__(self, 
                 university=None, 
                 semester=None, 
                 course=None, 
                 resource_type=None, 
                 description=None, 
                 name=None, 
                 email=None, 
                 priority=PRIORITY_MEDIUM,
                 status=STATUS_PENDING,
                 created_at=None,
                 updated_at=None,
                 request_id=None,
                 admin_notes=None,
                 anonymous=False):
        self.university = university
        self.semester = semester
        self.course = course
        self.resource_type = resource_type
        self.description = description
        self.name = name
        self.email = email
        self.priority = priority
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or self.created_at
        self.request_id = request_id or f"{int(datetime.now().timestamp())}"
        self.admin_notes = admin_notes or ""
        self.anonymous = anonymous
        
    def to_dict(self):
        return {
            "university": self.university,
            "semester": self.semester,
            "course": self.course,
            "resource_type": self.resource_type,
            "description": self.description,
            "name": self.name,
            "email": self.email,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "request_id": self.request_id,
            "admin_notes": self.admin_notes,
            "anonymous": self.anonymous
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            university=data.get("university"),
            semester=data.get("semester"),
            course=data.get("course"),
            resource_type=data.get("resource_type"),
            description=data.get("description"),
            name=data.get("name"),
            email=data.get("email"),
            priority=data.get("priority", PRIORITY_MEDIUM),
            status=data.get("status", STATUS_PENDING),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            request_id=data.get("request_id"),
            admin_notes=data.get("admin_notes", ""),
            anonymous=data.get("anonymous", False)
        )

def load_requests():
    """Load resource requests from JSON file"""
    requests_path = Path("data/requests.json")
    
    if not requests_path.exists():
        return []
    
    try:
        with open(requests_path, "r") as f:
            requests_data = json.load(f)
            return [ResourceRequest.from_dict(req) for req in requests_data]
    except Exception as e:
        st.error(f"Error loading requests: {e}")
        return []

def save_requests(requests):
    """Save resource requests to JSON file"""
    requests_path = Path("data/requests.json")
    
    try:
        if not requests_path.parent.exists():
            requests_path.parent.mkdir(parents=True)
            
        requests_data = [req.to_dict() for req in requests]
        
        with open(requests_path, "w") as f:
            json.dump(requests_data, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving requests: {e}")
        return False

def add_request(request):
    """Add a new resource request"""
    requests = load_requests()
    requests.append(request)
    return save_requests(requests)

def update_request(request_id, updates):
    """Update an existing resource request"""
    requests = load_requests()
    for req in requests:
        if req.request_id == request_id:
            for key, value in updates.items():
                setattr(req, key, value)
            req.updated_at = datetime.now().isoformat()
            return save_requests(requests)
    return False

def delete_request(request_id):
    """Delete a resource request"""
    requests = load_requests()
    initial_count = len(requests)
    requests = [req for req in requests if req.request_id != request_id]
    
    if len(requests) < initial_count:
        return save_requests(requests)
    return False

def get_request_stats():
    """Get statistics about resource requests"""
    requests = load_requests()
    
    if not requests:
        return {
            "total": 0,
            "by_status": {},
            "by_priority": {},
            "by_type": {},
            "by_university": {},
            "by_course": {},
            "avg_completion_time": 0
        }
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame([req.to_dict() for req in requests])
    
    # Calculate completion time for completed requests
    completion_times = []
    for req in requests:
        if req.status == STATUS_COMPLETED:
            try:
                created = datetime.fromisoformat(req.created_at)
                updated = datetime.fromisoformat(req.updated_at)
                completion_time = (updated - created).total_seconds() / 86400  # days
                completion_times.append(completion_time)
            except:
                pass
    
    avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
    
    # Prepare stats
    stats = {
        "total": len(requests),
        "by_status": df.status.value_counts().to_dict() if "status" in df.columns else {},
        "by_priority": df.priority.value_counts().to_dict() if "priority" in df.columns else {},
        "by_type": df.resource_type.value_counts().to_dict() if "resource_type" in df.columns else {},
        "by_university": df.university.value_counts().to_dict() if "university" in df.columns else {},
        "by_course": df.course.value_counts().to_dict() if "course" in df.columns else {},
        "avg_completion_time": avg_completion_time
    }
    
    return stats

# Create required directories
data_dir = Path("data")
uploads_dir = data_dir / "uploads"
create_directory_if_not_exists(data_dir)
create_directory_if_not_exists(uploads_dir)

# Initialize session state
if 'settings' not in st.session_state:
    st.session_state.settings = load_settings()
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'show_login' not in st.session_state:
    st.session_state.show_login = False
if 'logged_in_email' not in st.session_state:
    st.session_state.logged_in_email = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

# Admin password (change this in a real app)
ADMIN_PASSWORD = "admin123"

# Main header
st.markdown('<div class="main-header"><h1>Student Resource Hub</h1><p>Access past exams, study sheets, and request missing resources</p></div>', unsafe_allow_html=True)

# Sidebar content
with st.sidebar:
    # Logo and title
    st.image("https://via.placeholder.com/150x150.png?text=SRH", width=150)
    st.markdown('<h2>StudyHub</h2>', unsafe_allow_html=True)
    
    # Navigation
    st.subheader("Navigation")
    nav_option = st.radio(
        "Select Option",
        ["Home", "Find Resources", "Request Resources", "My Requests", "Admin Portal"]
    )
    
    # Update current page based on navigation
    if nav_option == "Home":
        st.session_state.current_page = "home"
    elif nav_option == "Find Resources":
        st.session_state.current_page = "find_resources"
    elif nav_option == "Request Resources":
        st.session_state.current_page = "request_resources"
    elif nav_option == "My Requests":
        st.session_state.current_page = "my_requests"
    elif nav_option == "Admin Portal":
        if not st.session_state.is_admin:
            st.session_state.show_login = True
        st.session_state.current_page = "admin_portal"
    
    # Admin Login/Logout
    if st.session_state.is_admin:
        if st.button("Logout"):
            st.session_state.is_admin = False
            st.session_state.current_page = "home"
            st.rerun()

# Admin Login Modal
if st.session_state.get('show_login', False) and not st.session_state.is_admin:
    with st.form("login_form"):
        st.subheader("Admin Login")
        admin_password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Login")
        with col2:
            cancel = st.form_submit_button("Cancel")
        
        if submitted:
            if admin_password == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.session_state.show_login = False
                st.success("Logged in as admin!")
                st.rerun()
            else:
                st.error("Incorrect password!")
        
        if cancel:
            st.session_state.show_login = False
            st.rerun()

# Function to display resource listing
def show_resources():
    st.markdown('<div class="resource-section"><h2 class="resource-header">Find Study Resources</h2>', unsafe_allow_html=True)
    
    # Create three columns for university, semester, and course selection
    col1, col2, col3 = st.columns(3)
    
    settings = st.session_state.settings
    
    # University selection
    universities = settings.get("universities", [])
    if not universities:
        st.warning("No universities available. Admin needs to add universities.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    with col1:
        st.markdown("<p>Select University</p>", unsafe_allow_html=True)
        selected_uni = st.selectbox("University", universities, label_visibility="collapsed")
    
    # Semester selection
    semesters = settings.get("semesters", {}).get(selected_uni, [])
    if not semesters:
        st.warning(f"No semesters available for {selected_uni}. Admin needs to add semesters.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    with col2:
        st.markdown("<p>Select Semester</p>", unsafe_allow_html=True)
        selected_semester = st.selectbox("Semester", semesters, label_visibility="collapsed")
    
    # Course selection
    courses = settings.get("courses", {}).get(f"{selected_uni}_{selected_semester}", [])
    if not courses:
        st.warning(f"No courses available for {selected_uni}, {selected_semester}. Admin needs to add courses.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    with col3:
        st.markdown("<p>Select Course</p>", unsafe_allow_html=True)
        selected_course = st.selectbox("Course", courses, label_visibility="collapsed")
    
    # Find Resources button
    btn_col1, btn_col2, btn_col3 = st.columns([2, 1, 2])
    with btn_col2:
        find_resources = st.button("Find Resources", type="primary")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display resources if all selections are made
    if selected_uni and selected_semester and selected_course:
        st.markdown(f"<div class='resource-section'><h2>Resources for {selected_course}</h2>", unsafe_allow_html=True)
        
        # Create tabs container with custom CSS
        st.markdown('<div class="tab-container">', unsafe_allow_html=True)
        
        # Define tabs for different resource types
        tab1, tab2, tab3 = st.tabs(["Past Exams", "Study Sheets", "Tips & Guides"])
        
        # Generate file path for resources
        resource_path = get_file_path(selected_uni, selected_semester, selected_course)
        create_directory_if_not_exists(resource_path)
        
        # Display files
        with tab1:
            exam_path = resource_path / "exams"
            create_directory_if_not_exists(exam_path)
            
            exams = os.listdir(exam_path) if os.path.exists(exam_path) else []
            if exams:
                # Start file container
                st.markdown('<div class="file-container">', unsafe_allow_html=True)
                
                for exam in exams:
                    file_path = exam_path / exam
                    file_date = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d')
                    
                    # Create a file card with HTML for better layout control
                    file_html = '<div class="file-card">'
                    
                    # Add thumbnail container
                    file_html += '<div class="thumbnail-container">'
                    if exam.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        # For images, convert to base64 to embed directly in HTML
                        with open(file_path, "rb") as f:
                            img_data = base64.b64encode(f.read()).decode()
                        file_html += f'<img src="data:image/png;base64,{img_data}" style="max-width:100%; max-height:100px;" />'
                    elif exam.lower().endswith(('.pdf')):
                        # For PDFs, show a PDF icon
                        file_html += '<div class="file-icon">📄</div>'
                    else:
                        # For other files show a generic file icon
                        file_html += '<div class="file-icon">📁</div>'
                    file_html += '</div>'
                    
                    # Add file name (shortened if needed)
                    short_name = exam
                    if len(short_name) > 20:
                        name_parts = os.path.splitext(exam)
                        short_name = name_parts[0][:17] + "..." + name_parts[1]
                    file_html += f'<div class="file-name">{short_name}</div>'
                    
                    # Add download button
                    download_link = file_download_link(file_path, exam)
                    file_html += download_link
                    
                    # Add upload date
                    file_html += f'<div style="font-size:0.8rem; text-align:center; margin-top:0.5rem;">Uploaded: {file_date}</div>'
                    
                    # Close file card
                    file_html += '</div>'
                    
                    # Output the HTML
                    st.markdown(file_html, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No exams have been uploaded for this course yet.")
                
                # If admin is viewing, show upload option
                if st.session_state.is_admin:
                    st.write("As an admin, you can upload exam files:")
                    uploaded_file = st.file_uploader("Upload an exam", key="exam_uploader")
                    
                    if uploaded_file:
                        # Save the uploaded file
                        file_path = exam_path / uploaded_file.name
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        st.success(f"Uploaded {uploaded_file.name} successfully!")
                        st.rerun()
        
        with tab2:
            study_path = resource_path / "study_sheets"
            create_directory_if_not_exists(study_path)
            
            study_sheets = os.listdir(study_path) if os.path.exists(study_path) else []
            if study_sheets:
                # Start file container
                st.markdown('<div class="file-container">', unsafe_allow_html=True)
                
                for sheet in study_sheets:
                    file_path = study_path / sheet
                    file_date = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d')
                    
                    # Create a file card with HTML for better layout control
                    file_html = '<div class="file-card">'
                    
                    # Add thumbnail container
                    file_html += '<div class="thumbnail-container">'
                    if sheet.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        # For images, convert to base64 to embed directly in HTML
                        with open(file_path, "rb") as f:
                            img_data = base64.b64encode(f.read()).decode()
                        file_html += f'<img src="data:image/png;base64,{img_data}" style="max-width:100%; max-height:100px;" />'
                    elif sheet.lower().endswith(('.pdf')):
                        # For PDFs, show a PDF icon
                        file_html += '<div class="file-icon">📄</div>'
                    else:
                        # For other files show a generic file icon
                        file_html += '<div class="file-icon">📁</div>'
                    file_html += '</div>'
                    
                    # Add file name (shortened if needed)
                    short_name = sheet
                    if len(short_name) > 20:
                        name_parts = os.path.splitext(sheet)
                        short_name = name_parts[0][:17] + "..." + name_parts[1]
                    file_html += f'<div class="file-name">{short_name}</div>'
                    
                    # Add download button
                    download_link = file_download_link(file_path, sheet)
                    file_html += download_link
                    
                    # Add upload date
                    file_html += f'<div style="font-size:0.8rem; text-align:center; margin-top:0.5rem;">Uploaded: {file_date}</div>'
                    
                    # Close file card
                    file_html += '</div>'
                    
                    # Output the HTML
                    st.markdown(file_html, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No study sheets have been uploaded for this course yet.")
                
                # If admin is viewing, show upload option
                if st.session_state.is_admin:
                    st.write("As an admin, you can upload study sheets:")
                    uploaded_file = st.file_uploader("Upload a study sheet", key="sheet_uploader")
                    
                    if uploaded_file:
                        # Save the uploaded file
                        file_path = study_path / uploaded_file.name
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        st.success(f"Uploaded {uploaded_file.name} successfully!")
                        st.rerun()
        
        with tab3:
            tips_path = resource_path / "tips_guides"
            create_directory_if_not_exists(tips_path)
            
            tips = os.listdir(tips_path) if os.path.exists(tips_path) else []
            if tips:
                # Start file container
                st.markdown('<div class="file-container">', unsafe_allow_html=True)
                
                for tip in tips:
                    file_path = tips_path / tip
                    file_date = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d')
                    
                    # Create a file card with HTML for better layout control
                    file_html = '<div class="file-card">'
                    
                    # Add thumbnail container
                    file_html += '<div class="thumbnail-container">'
                    if tip.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        # For images, convert to base64 to embed directly in HTML
                        with open(file_path, "rb") as f:
                            img_data = base64.b64encode(f.read()).decode()
                        file_html += f'<img src="data:image/png;base64,{img_data}" style="max-width:100%; max-height:100px;" />'
                    elif tip.lower().endswith(('.pdf')):
                        # For PDFs, show a PDF icon
                        file_html += '<div class="file-icon">📄</div>'
                    else:
                        # For other files show a generic file icon
                        file_html += '<div class="file-icon">📁</div>'
                    file_html += '</div>'
                    
                    # Add file name (shortened if needed)
                    short_name = tip
                    if len(short_name) > 20:
                        name_parts = os.path.splitext(tip)
                        short_name = name_parts[0][:17] + "..." + name_parts[1]
                    file_html += f'<div class="file-name">{short_name}</div>'
                    
                    # Add download button
                    download_link = file_download_link(file_path, tip)
                    file_html += download_link
                    
                    # Add upload date
                    file_html += f'<div style="font-size:0.8rem; text-align:center; margin-top:0.5rem;">Uploaded: {file_date}</div>'
                    
                    # Close file card
                    file_html += '</div>'
                    
                    # Output the HTML
                    st.markdown(file_html, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No tips or guides have been uploaded for this course yet.")
                
                # If admin is viewing, show upload option
                if st.session_state.is_admin:
                    st.write("As an admin, you can upload tips and guides:")
                    uploaded_file = st.file_uploader("Upload a tip or guide", key="tip_uploader")
                    
                    if uploaded_file:
                        # Save the uploaded file
                        file_path = tips_path / uploaded_file.name
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        st.success(f"Uploaded {uploaded_file.name} successfully!")
                        st.rerun()

# Show compact request form
def show_request_form():
    st.subheader("Request Missing Resources")
    
    with st.form("resource_request_form"):
        settings = st.session_state.settings
        universities = settings.get("universities", [])
        
        col1, col2 = st.columns(2)
        
        with col1:
            university = st.selectbox("University", universities)
            
            semester_options = settings.get("semesters", {}).get(university, [])
            semester = st.selectbox("Semester", semester_options)
            
            course_key = f"{university}_{semester}"
            course_options = settings.get("courses", {}).get(course_key, [])
            course = st.selectbox("Course", course_options)
            
            resource_type = st.selectbox("Resource Type", RESOURCE_TYPES)
        
        with col2:
            description = st.text_area(
                "Description", 
                placeholder="Briefly describe what resource you need...",
                height=100
            )
            
            name = st.text_input("Your Name (Optional)")
            email = st.text_input("Your Email (Optional)")
            
            anonymous = st.checkbox("Submit Anonymously")
        
        priority = st.select_slider(
            "Priority",
            options=[PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH],
            value=PRIORITY_MEDIUM
        )
        
        submitted = st.form_submit_button("Submit Request")
        
        if submitted:
            if not university or not semester or not course or not resource_type or not description:
                st.error("Please fill in all required fields.")
                return
            
            request = ResourceRequest(
                university=university,
                semester=semester,
                course=course,
                resource_type=resource_type,
                description=description,
                name=name if not anonymous else None,
                email=email if not anonymous else None,
                priority=priority,
                anonymous=anonymous
            )
            
            if add_request(request):
                st.success("Resource request submitted successfully!")
                st.balloons()
                
                # Store the email for easy access to "My Requests"
                if email and not anonymous:
                    st.session_state.logged_in_email = email
            else:
                st.error("Failed to submit request. Please try again later.")

# Show my requests
def show_my_requests():
    st.subheader("My Submitted Requests")
    
    # If the user has already submitted an email in this session, pre-fill it
    default_email = st.session_state.logged_in_email or ""
    
    with st.form("find_requests_form"):
        email = st.text_input("Enter your email to find your requests", value=default_email)
        submitted = st.form_submit_button("Find My Requests")
    
    if submitted and email:
        st.session_state.logged_in_email = email
        requests = load_requests()
        user_requests = [req for req in requests if req.email == email and not req.anonymous]
        
        if not user_requests:
            st.info("No requests found for this email.")
            return
        
        st.write(f"Found {len(user_requests)} requests:")
        
        requests_data = []
        for req in user_requests:
            requests_data.append({
                "Request ID": req.request_id,
                "Date": format_datetime(req.created_at),
                "University": req.university,
                "Course": req.course,
                "Resource Type": req.resource_type,
                "Status": req.status,
                "Priority": req.priority
            })
            
        df = pd.DataFrame(requests_data)
        st.dataframe(df)
        
        request_id = st.selectbox(
            "Select a request to view details:", 
            [req["Request ID"] for req in requests_data]
        )
        
        if request_id:
            selected_request = next((req for req in user_requests if req.request_id == request_id), None)
            if selected_request:
                with st.expander("Request Details", expanded=True):
                    st.write(f"**Description:** {selected_request.description}")
                    st.write(f"**Status:** {selected_request.status}")
                    st.write(f"**Created:** {format_datetime(selected_request.created_at)}")
                    st.write(f"**Last Updated:** {format_datetime(selected_request.updated_at)}")
                    
                    if selected_request.admin_notes:
                        st.write(f"**Admin Notes:** {selected_request.admin_notes}")

# Admin functions
def admin_dashboard():
    st.title("Admin Dashboard")
    
    admin_tabs = st.tabs(["Manage Requests", "Analytics", "Settings"])
    
    with admin_tabs[0]:
        manage_requests()
    
    with admin_tabs[1]:
        request_analytics()
    
    with admin_tabs[2]:
        manage_settings()

# Admin function to manage requests
def manage_requests():
    st.subheader("Manage Resource Requests")
    
    requests = load_requests()
    
    if not requests:
        st.info("No resource requests available.")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            [STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_COMPLETED, STATUS_REJECTED],
            default=[STATUS_PENDING, STATUS_IN_PROGRESS]
        )
    
    with col2:
        priority_filter = st.multiselect(
            "Filter by Priority",
            [PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH],
            default=[PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_LOW]
        )
    
    with col3:
        universities = list(set(req.university for req in requests if req.university))
        university_filter = st.multiselect(
            "Filter by University",
            universities,
            default=universities
        )
    
    # Apply filters
    filtered_requests = [
        req for req in requests 
        if req.status in status_filter 
        and req.priority in priority_filter
        and req.university in university_filter
    ]
    
    if not filtered_requests:
        st.info("No requests match the selected filters.")
        return
    
    # Display requests
    requests_data = []
    for req in filtered_requests:
        name_display = req.name if not req.anonymous else "Anonymous"
        requests_data.append({
            "Request ID": req.request_id,
            "Date": format_datetime(req.created_at),
            "University": req.university,
            "Course": req.course,
            "Resource Type": req.resource_type,
            "Status": req.status,
            "Priority": req.priority,
            "Requester": name_display
        })
    
    st.dataframe(pd.DataFrame(requests_data))
    
    # Request management
    request_id = st.selectbox(
        "Select a request to manage:", 
        [req["Request ID"] for req in requests_data]
    )
    
    if request_id:
        selected_request = next((req for req in requests if req.request_id == request_id), None)
        
        if selected_request:
            with st.expander("Request Details", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**University:** {selected_request.university}")
                    st.write(f"**Semester:** {selected_request.semester}")
                    st.write(f"**Course:** {selected_request.course}")
                    st.write(f"**Resource Type:** {selected_request.resource_type}")
                    st.write(f"**Priority:** {selected_request.priority}")
                    st.write(f"**Status:** {selected_request.status}")
                    
                    if not selected_request.anonymous:
                        st.write(f"**Requester:** {selected_request.name or 'Not provided'}")
                        st.write(f"**Email:** {selected_request.email or 'Not provided'}")
                    else:
                        st.write("**Requester:** Anonymous")
                
                with col2:
                    st.write(f"**Description:** {selected_request.description}")
                    st.write(f"**Created:** {format_datetime(selected_request.created_at)}")
                    st.write(f"**Last Updated:** {format_datetime(selected_request.updated_at)}")
                
                # Update form
                with st.form(f"update_request_{request_id}"):
                    new_status = st.selectbox(
                        "Update Status", 
                        [STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_COMPLETED, STATUS_REJECTED],
                        index=[STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_COMPLETED, STATUS_REJECTED].index(selected_request.status)
                    )
                    
                    new_priority = st.selectbox(
                        "Update Priority",
                        [PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH],
                        index=[PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH].index(selected_request.priority)
                    )
                    
                    admin_notes = st.text_area(
                        "Admin Notes", 
                        value=selected_request.admin_notes or "",
                        height=100
                    )
                    
                    # If this is a completed request, offer option to upload the requested resource
                    upload_resource = False
                    if new_status == STATUS_COMPLETED:
                        upload_resource = st.checkbox("Upload the requested resource now")
                        
                        if upload_resource:
                            uploaded_file = st.file_uploader("Upload resource file", key=f"resource_upload_{request_id}")
                            resource_category = st.selectbox(
                                "Resource Category", 
                                ["exams", "study_sheets", "tips_guides"]
                            )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        update_submitted = st.form_submit_button("Update Request")
                    with col2:
                        delete_submitted = st.form_submit_button("Delete Request")
                
                if update_submitted:
                    updates = {
                        "status": new_status,
                        "priority": new_priority,
                        "admin_notes": admin_notes
                    }
                    
                    success = update_request(request_id, updates)
                    
                    # Handle resource upload if selected
                    if success and new_status == STATUS_COMPLETED and upload_resource and 'uploaded_file' in locals() and uploaded_file:
                        # Create directory structure for this resource
                        resource_path = get_file_path(
                            selected_request.university, 
                            selected_request.semester, 
                            selected_request.course
                        )
                        category_path = resource_path / resource_category
                        create_directory_if_not_exists(category_path)
                        
                        # Save the uploaded file
                        file_path = category_path / uploaded_file.name
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Update admin notes to include file info
                        file_info = f"\n\nUploaded resource: {uploaded_file.name} (in {resource_category})"
                        update_request(request_id, {"admin_notes": admin_notes + file_info})
                        
                        st.success(f"Request updated and resource uploaded successfully!")
                    elif success:
                        st.success("Request updated successfully!")
                    else:
                        st.error("Failed to update request.")
                    
                    st.experimental_rerun()
                
                if delete_submitted:
                    if delete_request(request_id):
                        st.success("Request deleted successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to delete request.")

# Admin function for analytics
def request_analytics():
    st.subheader("Request Analytics")
    
    stats = get_request_stats()
    
    if stats["total"] == 0:
        st.info("No request data available for analytics.")
        return
    
    # Basic stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Requests", stats["total"])
    
    with col2:
        pending_count = stats["by_status"].get(STATUS_PENDING, 0)
        st.metric("Pending Requests", pending_count)
    
    with col3:
        completed_count = stats["by_status"].get(STATUS_COMPLETED, 0)
        st.metric("Completed Requests", completed_count)
    
    with col4:
        completion_rate = round((completed_count / stats["total"]) * 100, 1) if stats["total"] > 0 else 0
        st.metric("Completion Rate", f"{completion_rate}%")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Requests by Status")
        
        if stats["by_status"]:
            fig = px.pie(
                values=list(stats["by_status"].values()),
                names=list(stats["by_status"].keys()),
                title="Request Status Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No status data available.")
    
    with col2:
        st.subheader("Requests by Priority")
        
        if stats["by_priority"]:
            fig = px.bar(
                x=list(stats["by_priority"].keys()),
                y=list(stats["by_priority"].values()),
                title="Requests by Priority Level"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No priority data available.")
    
    # Add more charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Requests by Resource Type")
        
        if stats["by_type"]:
            sorted_types = sorted(stats["by_type"].items(), key=lambda x: x[1], reverse=True)
            types = [x[0] for x in sorted_types]
            counts = [x[1] for x in sorted_types]
            
            fig = px.bar(
                x=types,
                y=counts,
                title="Most Requested Resource Types"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No resource type data available.")
    
    with col2:
        st.subheader("Requests by University")
        
        if stats["by_university"]:
            sorted_unis = sorted(stats["by_university"].items(), key=lambda x: x[1], reverse=True)
            unis = [x[0] for x in sorted_unis]
            counts = [x[1] for x in sorted_unis]
            
            fig = px.bar(
                x=unis,
                y=counts,
                title="Requests by University"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No university data available.")

# Admin function to manage settings
def manage_settings():
    st.subheader("Settings Management")
    
    settings = st.session_state.settings
    
    # Universities
    with st.expander("Manage Universities", expanded=True):
        universities = settings.get("universities", [])
        
        st.write("Current Universities:")
        for i, uni in enumerate(universities):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"{i+1}. {uni}")
            with col2:
                if st.button("Remove", key=f"remove_uni_{i}"):
                    # Check if university has semesters before removing
                    if uni in settings.get("semesters", {}):
                        del settings["semesters"][uni]
                        
                        # Also remove courses for this university
                        for key in list(settings.get("courses", {}).keys()):
                            if key.startswith(f"{uni}_"):
                                del settings["courses"][key]
                    
                    universities.remove(uni)
                    settings["universities"] = universities
                    save_settings(settings)
                    st.session_state.settings = settings
                    st.experimental_rerun()
        
        # Add new university
        with st.form("add_university_form"):
            new_uni = st.text_input("New University Name")
            submit = st.form_submit_button("Add University")
            
            if submit and new_uni:
                if new_uni not in universities:
                    universities.append(new_uni)
                    settings["universities"] = universities
                    
                    # Initialize semesters for this university
                    if "semesters" not in settings:
                        settings["semesters"] = {}
                    settings["semesters"][new_uni] = []
                    
                    save_settings(settings)
                    st.session_state.settings = settings
                    st.success(f"Added university: {new_uni}")
                    st.experimental_rerun()
                else:
                    st.error("University already exists")

    # Semesters management
    with st.expander("Manage Semesters", expanded=True):
        university = st.selectbox("Select University", settings.get("universities", []), key="sem_uni_select")
        
        if university:
            semesters = settings.get("semesters", {}).get(university, [])
            
            st.write(f"Current Semesters for {university}:")
            for i, sem in enumerate(semesters):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"{i+1}. {sem}")
                with col2:
                    if st.button("Remove", key=f"remove_sem_{i}"):
                        # Check if semester has courses before removing
                        sem_key = f"{university}_{sem}"
                        if sem_key in settings.get("courses", {}):
                            del settings["courses"][sem_key]
                        
                        semesters.remove(sem)
                        settings["semesters"][university] = semesters
                        save_settings(settings)
                        st.session_state.settings = settings
                        st.experimental_rerun()
            
            # Add new semester
            with st.form("add_semester_form"):
                new_sem = st.text_input("New Semester Name")
                submit = st.form_submit_button("Add Semester")
                
                if submit and new_sem:
                    if new_sem not in semesters:
                        if "semesters" not in settings:
                            settings["semesters"] = {}
                        if university not in settings["semesters"]:
                            settings["semesters"][university] = []
                        
                        settings["semesters"][university].append(new_sem)
                        
                        # Initialize courses for this semester
                        sem_key = f"{university}_{new_sem}"
                        if "courses" not in settings:
                            settings["courses"] = {}
                        settings["courses"][sem_key] = []
                        
                        save_settings(settings)
                        st.session_state.settings = settings
                        st.success(f"Added semester: {new_sem}")
                        st.experimental_rerun()
                    else:
                        st.error("Semester already exists")

    # Courses management
    with st.expander("Manage Courses", expanded=True):
        uni_col, sem_col = st.columns(2)
        
        with uni_col:
            university = st.selectbox("Select University", settings.get("universities", []), key="course_uni_select")
        
        if university:
            with sem_col:
                semester_options = settings.get("semesters", {}).get(university, [])
                semester = st.selectbox("Select Semester", semester_options, key="course_sem_select")
            
            if semester:
                sem_key = f"{university}_{semester}"
                courses = settings.get("courses", {}).get(sem_key, [])
                
                st.write(f"Current Courses for {university}, {semester}:")
                for i, course in enumerate(courses):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"{i+1}. {course}")
                    with col2:
                        if st.button("Remove", key=f"remove_course_{i}"):
                            courses.remove(course)
                            settings["courses"][sem_key] = courses
                            save_settings(settings)
                            st.session_state.settings = settings
                            st.experimental_rerun()
                
                # Add new course
                with st.form("add_course_form"):
                    new_course = st.text_input("New Course Name")
                    submit = st.form_submit_button("Add Course")
                    
                    if submit and new_course:
                        if new_course not in courses:
                            if "courses" not in settings:
                                settings["courses"] = {}
                            if sem_key not in settings["courses"]:
                                settings["courses"][sem_key] = []
                            
                            settings["courses"][sem_key].append(new_course)
                            save_settings(settings)
                            st.session_state.settings = settings
                            st.success(f"Added course: {new_course}")
                            st.experimental_rerun()
                        else:
                            st.error("Course already exists")

# Homepage content
def show_homepage():
    st.header("Welcome to Student Resource Hub")
    
    # Display a welcome message and instructions
    st.markdown("""
    The Student Resource Hub helps you find and request resources for your university courses. 
    
    **Features:**
    - Find study materials for your courses
    - Request missing resources
    - Track your requests
    - Share resources with your classmates
    
    Get started by using the navigation options on the left sidebar.
    """)
    
    # Show some quick stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        stats = get_request_stats()
        completed_count = stats["by_status"].get(STATUS_COMPLETED, 0)
        st.metric("Resources Available", completed_count)
    
    with col2:
        settings = st.session_state.settings
        course_count = 0
        for semester_courses in settings.get("courses", {}).values():
            course_count += len(semester_courses)
        st.metric("Courses Covered", course_count)
    
    with col3:
        uni_count = len(settings.get("universities", []))
        st.metric("Universities", uni_count)
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Find Resources", key="quick_find"):
            st.session_state.current_page = "find_resources"
            st.rerun()
    
    with col2:
        if st.button("Request Resources", key="quick_request"):
            st.session_state.current_page = "request_resources"
            st.rerun()

# Main app logic
if st.session_state.current_page == "home":
    show_homepage()
elif st.session_state.current_page == "find_resources":
    show_resources()
elif st.session_state.current_page == "request_resources":
    show_request_form()
elif st.session_state.current_page == "my_requests":
    show_my_requests()
elif st.session_state.current_page == "admin_portal":
    if st.session_state.is_admin:
        admin_dashboard()
    else:
        st.warning("Please log in to access the admin portal.")
        st.session_state.show_login = True

# Footer
st.markdown("---")
st.markdown("© 2025 Student Resource Hub. All rights reserved.")
