import streamlit as st

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Student Resource Portal",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure we're binding to all interfaces (0.0.0.0) for deployment
import os
os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
os.environ['STREAMLIT_SERVER_PORT'] = '8501'

import pandas as pd
import os
import json
import base64
from datetime import datetime
from pathlib import Path
import shutil
from PIL import Image
import io

from utils import load_settings, save_settings, get_file_path, create_directory_if_not_exists, validate_email
from admin import show_admin_panel
from models import ResourceRequest, add_request, load_requests

# Custom CSS to match the design in the example
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
    .resource-request-form {
        background-color: #2D2D2D;
        padding: 1.5rem;
        border-radius: 5px;
        margin-top: 1.5rem;
    }
    .request-status {
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
        text-align: center;
    }
    .status-pending {
        background-color: #FFC107;
        color: #000;
    }
    .status-in-progress {
        background-color: #2196F3;
        color: white;
    }
    .status-completed {
        background-color: #4CAF50;
        color: white;
    }
    .status-rejected {
        background-color: #F44336;
        color: white;
    }
    .request-card {
        background-color: #2D2D2D;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #FF5252;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state if not already done
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'settings' not in st.session_state:
    st.session_state.settings = load_settings()
if 'show_request_form' not in st.session_state:
    st.session_state.show_request_form = False
if 'my_requests_email' not in st.session_state:
    st.session_state.my_requests_email = ""
if 'show_my_requests' not in st.session_state:
    st.session_state.show_my_requests = False

# Create required directories
data_dir = Path("data")
uploads_dir = data_dir / "uploads"
create_directory_if_not_exists(data_dir)
create_directory_if_not_exists(uploads_dir)

# Main header
st.markdown('<div class="main-header"><h1>Student Resource Portal</h1><p>Access past exams, study sheets, and helpful tips</p></div>', unsafe_allow_html=True)

# Sidebar content
with st.sidebar:
    # Display logo if available
    try:
        with open("assets/logo.svg", "r") as f:
            svg = f.read()
            st.image(svg, width=200)
    except:
        pass
    
    st.markdown('<h2>StudyHub</h2>', unsafe_allow_html=True)
    
    # Admin Login/Logout Section
    cols = st.columns([1, 1])
    if not st.session_state.is_admin:
        # Login button that opens a modal
        with cols[1]:
            if st.button("Admin Portal", key="admin_login"):
                st.session_state.show_login = True
                
        # Login modal
        if st.session_state.get('show_login', False):
            with st.form("login_form"):
                st.subheader("Admin Login")
                admin_username = st.text_input("Username")
                admin_password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")
                
                if submitted:
                    if admin_username == "llouay26" and admin_password == "LouayX2006@":  # Custom admin credentials
                        st.session_state.is_admin = True
                        st.session_state.show_login = False
                        st.success("Logged in as admin!")
                        st.rerun()
                    else:
                        st.error("Incorrect username or password!")
    else:
        with cols[1]:
            if st.button("Logout"):
                st.session_state.is_admin = False
                st.rerun()
    
    # Request Resources Section
    st.markdown("---")
    st.markdown("### Need a resource?")
    if st.button("Request Resources", key="sidebar_request_btn"):
        st.session_state.show_request_form = True
        st.rerun()
    
    # View My Requests Section
    st.markdown("---")
    st.markdown("### Check Request Status")
    my_requests_email = st.text_input("Enter your email", key="my_requests_email_input")
    if st.button("View My Requests", key="my_requests_btn"):
        if validate_email(my_requests_email):
            st.session_state.my_requests_email = my_requests_email
            st.session_state.show_my_requests = True
            st.rerun()
        else:
            st.error("Please enter a valid email address.")

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

def show_resource_request_form():
    """Display the resource request form"""
    st.markdown('<div class="resource-section"><h2 class="resource-header">Request a Resource</h2>', unsafe_allow_html=True)
    
    settings = st.session_state.settings
    
    # Create three columns for university, semester, and course selection
    col1, col2, col3 = st.columns(3)
    
    # University selection
    universities = settings.get("universities", [])
    if not universities:
        st.warning("No universities available. Admin needs to add universities.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    with col1:
        st.markdown("<p>Select University</p>", unsafe_allow_html=True)
        selected_uni = st.selectbox("University", universities, key="req_university", label_visibility="collapsed")
    
    # Semester selection
    semesters = settings.get("semesters", {}).get(selected_uni, [])
    if not semesters:
        st.warning(f"No semesters available for {selected_uni}. Admin needs to add semesters.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    with col2:
        st.markdown("<p>Select Semester</p>", unsafe_allow_html=True)
        selected_semester = st.selectbox("Semester", semesters, key="req_semester", label_visibility="collapsed")
    
    # Course selection
    courses = settings.get("courses", {}).get(f"{selected_uni}_{selected_semester}", [])
    if not courses:
        st.warning(f"No courses available for {selected_uni}, {selected_semester}. Admin needs to add courses.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    with col3:
        st.markdown("<p>Select Course</p>", unsafe_allow_html=True)
        selected_course = st.selectbox("Course", courses, key="req_course", label_visibility="collapsed")
    
    # Resource type
    resource_types = ["Exams", "Study Sheets", "Tips & Notes"]
    col4, col5 = st.columns(2)
    
    with col4:
        st.markdown("<p>Resource Type</p>", unsafe_allow_html=True)
        selected_resource_type = st.selectbox("Resource Type", resource_types, key="req_resource_type", label_visibility="collapsed")
    
    with col5:
        st.markdown("<p>Priority</p>", unsafe_allow_html=True)
        selected_priority = st.selectbox(
            "Priority", 
            [
                ResourceRequest.PRIORITY_LOW,
                ResourceRequest.PRIORITY_MEDIUM,
                ResourceRequest.PRIORITY_HIGH
            ],
            index=1,  # Default to medium priority
            key="req_priority",
            label_visibility="collapsed"
        )
    
    # Description
    st.markdown("<p>Describe the resource you need</p>", unsafe_allow_html=True)
    description = st.text_area(
        "Description", 
        key="req_description", 
        placeholder="Please provide specific details about the resource you're looking for...",
        label_visibility="collapsed"
    )
    
    # Contact information
    col6, col7 = st.columns(2)
    
    with col6:
        st.markdown("<p>Your Name</p>", unsafe_allow_html=True)
        name = st.text_input("Your Name", key="req_name", label_visibility="collapsed")
    
    with col7:
        st.markdown("<p>Your Email</p>", unsafe_allow_html=True)
        email = st.text_input("Your Email", key="req_email", label_visibility="collapsed")
    
    # Submit button
    if st.button("Submit Request", type="primary", key="submit_request_btn"):
        # Validate inputs
        if not (selected_uni and selected_semester and selected_course and selected_resource_type and description):
            st.error("Please fill in all required fields.")
            return
        
        if not name:
            st.error("Please enter your name.")
            return
        
        if not validate_email(email):
            st.error("Please enter a valid email address.")
            return
        
        # Create and save the request
        request = ResourceRequest(
            university=selected_uni,
            semester=selected_semester,
            course=selected_course,
            resource_type=selected_resource_type,
            description=description,
            name=name,
            email=email,
            priority=selected_priority
        )
        
        if add_request(request):
            st.success("Your request has been submitted successfully! We'll notify you when it's processed.")
            # Clear the form by resetting session state
            st.session_state.show_request_form = False
            st.rerun()
        else:
            st.error("Failed to submit your request. Please try again.")
    
    # Cancel button
    if st.button("Cancel", key="cancel_request_btn"):
        st.session_state.show_request_form = False
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_my_requests():
    """Display user's submitted requests"""
    email = st.session_state.my_requests_email
    
    if not email:
        st.error("Please enter your email address to view your requests.")
        return
    
    st.markdown('<div class="resource-section"><h2 class="resource-header">My Requests</h2>', unsafe_allow_html=True)
    
    # Load all requests
    all_requests = load_requests()
    
    # Filter requests by email
    my_requests = [req for req in all_requests if req.email.lower() == email.lower()]
    
    if not my_requests:
        st.info("You don't have any submitted requests yet.")
        
        if st.button("Make a Request", key="make_request_from_my_requests"):
            st.session_state.show_request_form = True
            st.session_state.show_my_requests = False
            st.rerun()
    else:
        # Sort requests by date (newest first)
        my_requests.sort(key=lambda r: r.created_at, reverse=True)
        
        for req in my_requests:
            # Create a card for each request
            status_class = f"status-{req.status.lower().replace(' ', '-')}"
            
            # Start the card
            st.markdown(f"""
            <div class="request-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h3 style="margin: 0;">{req.course} - {req.resource_type}</h3>
                    <span class="request-status {status_class}">{req.status}</span>
                </div>
                <p><strong>Description:</strong> {req.description}</p>
                <p><strong>Submitted:</strong> {req.created_at[:10]}</p>
                <p><strong>Priority:</strong> {req.priority}</p>
            """, unsafe_allow_html=True)
            
            # Show admin notes if available and not empty
            if req.admin_notes and req.admin_notes.strip():
                st.markdown(f"""
                <div style="background-color: #333; padding: 10px; border-radius: 5px; margin-top: 10px;">
                    <p><strong>Admin Notes:</strong></p>
                    <p>{req.admin_notes}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Close the card
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Button to go back to main view
    if st.button("Back to Resources", key="back_to_resources_btn"):
        st.session_state.show_my_requests = False
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Main content
    settings = st.session_state.settings
    
    # If admin is logged in, show admin panel
    if st.session_state.is_admin:
        show_admin_panel()
        return
    
    # If request form should be shown
    if st.session_state.show_request_form:
        show_resource_request_form()
        return
    
    # If my requests should be shown
    if st.session_state.show_my_requests:
        show_my_requests()
        return
    
    # Student view - Find Study Resources section
    st.markdown('<div class="resource-section"><h2 class="resource-header">Find Study Resources</h2>', unsafe_allow_html=True)
    
    # Create three columns for university, semester, and course selection
    col1, col2, col3 = st.columns(3)
    
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
    
    # Request Resources button
    btn_col1, btn_col2, btn_col3 = st.columns([2, 1, 2])
    with btn_col2:
        st.markdown("<div style='text-align: center; margin-top: 10px;'>Can't find what you need?</div>", unsafe_allow_html=True)
        if st.button("Request a Resource", key="request_resource_btn"):
            st.session_state.show_request_form = True
            st.rerun()
    
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
        
        # Display exams
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
                
                # Close file container
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No exam resources found for this course.")
                
                # Add a button to request exams
                if st.button("Request Exam Resources", key="request_exams_btn"):
                    # Pre-fill the request form with the selected course and resource type
                    st.session_state.show_request_form = True
                    st.session_state.req_university = selected_uni
                    st.session_state.req_semester = selected_semester
                    st.session_state.req_course = selected_course
                    st.session_state.req_resource_type = "Exams"
                    st.rerun()
        
        # Display study sheets
        with tab2:
            sheets_path = resource_path / "sheets"
            create_directory_if_not_exists(sheets_path)
            
            sheets = os.listdir(sheets_path) if os.path.exists(sheets_path) else []
            if sheets:
                # Start file container
                st.markdown('<div class="file-container">', unsafe_allow_html=True)
                
                for sheet in sheets:
                    file_path = sheets_path / sheet
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
                
                # Close file container
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No study sheets found for this course.")
                
                # Add a button to request study sheets
                if st.button("Request Study Sheets", key="request_sheets_btn"):
                    # Pre-fill the request form with the selected course and resource type
                    st.session_state.show_request_form = True
                    st.session_state.req_university = selected_uni
                    st.session_state.req_semester = selected_semester
                    st.session_state.req_course = selected_course
                    st.session_state.req_resource_type = "Study Sheets"
                    st.rerun()
        
        # Display tips and guides
        with tab3:
            tips_path = resource_path / "tips"
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
                
                # Close file container
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No tips or guides found for this course.")
                
                # Add a button to request tips
                if st.button("Request Tips & Guides", key="request_tips_btn"):
                    # Pre-fill the request form with the selected course and resource type
                    st.session_state.show_request_form = True
                    st.session_state.req_university = selected_uni
                    st.session_state.req_semester = selected_semester
                    st.session_state.req_course = selected_course
                    st.session_state.req_resource_type = "Tips & Notes"
                    st.rerun()
        
        st.markdown('</div></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
