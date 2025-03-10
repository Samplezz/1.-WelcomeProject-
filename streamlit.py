import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Student Resource Hub",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    "universities": ["Example University"],
    "semesters": {"Example University": ["Semester 1", "Semester 2"]},
    "courses": {"Example University_Semester 1": ["Introduction to Computer Science", "Calculus I"]}
}

# Utility functions
def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def load_settings():
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

def format_datetime(iso_datetime):
    try:
        dt = datetime.fromisoformat(iso_datetime)
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return iso_datetime

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
    requests = load_requests()
    requests.append(request)
    return save_requests(requests)

def update_request(request_id, updates):
    requests = load_requests()
    for req in requests:
        if req.request_id == request_id:
            for key, value in updates.items():
                setattr(req, key, value)
            req.updated_at = datetime.now().isoformat()
            return save_requests(requests)
    return False

def delete_request(request_id):
    requests = load_requests()
    initial_count = len(requests)
    requests = [req for req in requests if req.request_id != request_id]
    
    if len(requests) < initial_count:
        return save_requests(requests)
    return False

def get_request_stats():
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

# Initialize session state
if 'settings' not in st.session_state:
    st.session_state.settings = load_settings()
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False

# Admin password (in a real app, this would be more secure)
ADMIN_PASSWORD = "admin123"

# Sidebar
st.sidebar.title("Student Resource Hub")

# Admin login section
with st.sidebar.expander("Admin Login"):
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if password == ADMIN_PASSWORD:
            st.session_state.admin_authenticated = True
            st.success("Login successful!")
        else:
            st.error("Incorrect password")

# Navigation
if st.session_state.admin_authenticated:
    st.sidebar.subheader("Admin Navigation")
    admin_option = st.sidebar.radio(
        "Select Option",
        ["Manage Requests", "Request Analytics", "Settings"]
    )
else:
    st.sidebar.subheader("Navigation")
    user_option = st.sidebar.radio(
        "Select Option",
        ["Submit Resource Request", "My Requests"]
    )

# Main content
st.title("Student Resource Hub")

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
            else:
                st.error("Failed to submit request. Please try again later.")

# Show my requests
def show_my_requests():
    st.subheader("My Submitted Requests")
    
    with st.form("find_requests_form"):
        email = st.text_input("Enter your email to find your requests")
        submitted = st.form_submit_button("Find My Requests")
    
    if submitted and email:
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
                    
                    if update_request(request_id, updates):
                        st.success("Request updated successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to update request.")
                
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

# Main app logic
if st.session_state.admin_authenticated:
    # Admin view
    if admin_option == "Manage Requests":
        manage_requests()
    elif admin_option == "Request Analytics":
        request_analytics()
    elif admin_option == "Settings":
        manage_settings()
else:
    # User view
    if user_option == "Submit Resource Request":
        show_request_form()
    elif user_option == "My Requests":
        show_my_requests()

# Footer
st.markdown("---")
st.markdown("© 2023 Student Resource Hub. All rights reserved.")
