import streamlit as st
import os
from pathlib import Path
import shutil
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from utils import load_settings, save_settings, get_file_path, create_directory_if_not_exists, format_datetime
from models import load_requests, update_request, delete_request, ResourceRequest, get_request_stats

def manage_universities():
    """Admin interface for managing universities"""
    st.subheader("Manage Universities")
    
    settings = st.session_state.settings
    universities = settings.get("universities", [])
    
    # Display existing universities
    st.write("Current Universities:")
    for i, uni in enumerate(universities):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"{i+1}. {uni}")
        with col2:
            if st.button("Remove", key=f"remove_uni_{i}"):
                # Check if university has semesters before removing
                if uni in settings.get("semesters", {}):
                    for semester in settings["semesters"][uni]:
                        key = f"{uni}_{semester}"
                        if key in settings.get("courses", {}):
                            settings["courses"].pop(key, None)
                    settings["semesters"].pop(uni, None)
                universities.remove(uni)
                save_settings(settings)
                st.rerun()
    
    # Add new university
    st.write("Add New University:")
    new_uni = st.text_input("University Name", key="new_uni_input")
    if st.button("Add University"):
        if new_uni and new_uni not in universities:
            universities.append(new_uni)
            settings["universities"] = universities
            if "semesters" not in settings:
                settings["semesters"] = {}
            settings["semesters"][new_uni] = []
            save_settings(settings)
            st.success(f"Added {new_uni} to universities!")
            st.rerun()
        elif new_uni in universities:
            st.error(f"{new_uni} already exists!")
        else:
            st.error("Please enter a university name!")

def manage_semesters():
    """Admin interface for managing semesters for each university"""
    st.subheader("Manage Semesters")
    
    settings = st.session_state.settings
    universities = settings.get("universities", [])
    
    if not universities:
        st.warning("No universities available. Please add a university first.")
        return
    
    # Select university
    selected_uni = st.selectbox("Select University", universities, key="semester_uni_select")
    
    if selected_uni:
        if "semesters" not in settings:
            settings["semesters"] = {}
        if selected_uni not in settings["semesters"]:
            settings["semesters"][selected_uni] = []
        
        semesters = settings["semesters"][selected_uni]
        
        # Display existing semesters
        st.write(f"Current Semesters for {selected_uni}:")
        for i, semester in enumerate(semesters):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"{i+1}. {semester}")
            with col2:
                if st.button("Remove", key=f"remove_sem_{i}"):
                    # Check if courses exist for this semester before removing
                    key = f"{selected_uni}_{semester}"
                    if key in settings.get("courses", {}):
                        settings["courses"].pop(key, None)
                    semesters.remove(semester)
                    save_settings(settings)
                    st.rerun()
        
        # Add new semester
        st.write(f"Add New Semester for {selected_uni}:")
        new_semester = st.text_input("Semester Name", key="new_semester_input")
        if st.button("Add Semester"):
            if new_semester and new_semester not in semesters:
                semesters.append(new_semester)
                settings["semesters"][selected_uni] = semesters
                save_settings(settings)
                st.success(f"Added {new_semester} to {selected_uni} semesters!")
                st.rerun()
            elif new_semester in semesters:
                st.error(f"{new_semester} already exists for {selected_uni}!")
            else:
                st.error("Please enter a semester name!")

def manage_courses():
    """Admin interface for managing courses for each university and semester"""
    st.subheader("Manage Courses")
    
    settings = st.session_state.settings
    universities = settings.get("universities", [])
    
    if not universities:
        st.warning("No universities available. Please add a university first.")
        return
    
    # Select university
    selected_uni = st.selectbox("Select University", universities, key="course_uni_select")
    
    if selected_uni:
        if "semesters" not in settings:
            settings["semesters"] = {}
        if selected_uni not in settings["semesters"]:
            settings["semesters"][selected_uni] = []
        
        semesters = settings["semesters"][selected_uni]
        
        if not semesters:
            st.warning(f"No semesters available for {selected_uni}. Please add a semester first.")
            return
        
        # Select semester
        selected_semester = st.selectbox("Select Semester", semesters, key="course_sem_select")
        
        if selected_semester:
            key = f"{selected_uni}_{selected_semester}"
            if "courses" not in settings:
                settings["courses"] = {}
            if key not in settings["courses"]:
                settings["courses"][key] = []
            
            courses = settings["courses"][key]
            
            # Display existing courses
            st.write(f"Current Courses for {selected_uni}, {selected_semester}:")
            for i, course in enumerate(courses):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"{i+1}. {course}")
                with col2:
                    if st.button("Remove", key=f"remove_course_{i}"):
                        # Remove course files
                        course_path = get_file_path(selected_uni, selected_semester, course)
                        if os.path.exists(course_path):
                            shutil.rmtree(course_path)
                        courses.remove(course)
                        save_settings(settings)
                        st.rerun()
            
            # Add new course
            st.write(f"Add New Course for {selected_uni}, {selected_semester}:")
            new_course = st.text_input("Course Name", key="new_course_input")
            if st.button("Add Course"):
                if new_course and new_course not in courses:
                    courses.append(new_course)
                    settings["courses"][key] = courses
                    save_settings(settings)
                    
                    # Create course directories
                    course_path = get_file_path(selected_uni, selected_semester, new_course)
                    create_directory_if_not_exists(course_path)
                    create_directory_if_not_exists(course_path / "exams")
                    create_directory_if_not_exists(course_path / "sheets")
                    create_directory_if_not_exists(course_path / "tips")
                    
                    st.success(f"Added {new_course} to {selected_uni}, {selected_semester} courses!")
                    st.rerun()
                elif new_course in courses:
                    st.error(f"{new_course} already exists for {selected_uni}, {selected_semester}!")
                else:
                    st.error("Please enter a course name!")

def upload_resources():
    """Admin interface for uploading resources for each course"""
    st.subheader("Upload Resources")
    
    settings = st.session_state.settings
    universities = settings.get("universities", [])
    
    if not universities:
        st.warning("No universities available. Please add a university first.")
        return
    
    # Select university
    selected_uni = st.selectbox("Select University", universities, key="upload_uni_select")
    
    if selected_uni:
        if "semesters" not in settings:
            st.warning(f"No semesters available for {selected_uni}. Please add a semester first.")
            return
            
        if selected_uni not in settings["semesters"]:
            st.warning(f"No semesters available for {selected_uni}. Please add a semester first.")
            return
        
        semesters = settings["semesters"][selected_uni]
        
        if not semesters:
            st.warning(f"No semesters available for {selected_uni}. Please add a semester first.")
            return
        
        # Select semester
        selected_semester = st.selectbox("Select Semester", semesters, key="upload_sem_select")
        
        if selected_semester:
            key = f"{selected_uni}_{selected_semester}"
            if "courses" not in settings or key not in settings["courses"]:
                st.warning(f"No courses available for {selected_uni}, {selected_semester}. Please add a course first.")
                return
            
            courses = settings["courses"][key]
            
            if not courses:
                st.warning(f"No courses available for {selected_uni}, {selected_semester}. Please add a course first.")
                return
            
            # Select course
            selected_course = st.selectbox("Select Course", courses, key="upload_course_select")
            
            if selected_course:
                # Select resource type
                resource_type = st.selectbox("Select Resource Type", ["Exams", "Study Sheets", "Tips & Notes"], key="resource_type_select")
                
                # Map resource type to directory
                type_to_dir = {
                    "Exams": "exams",
                    "Study Sheets": "sheets",
                    "Tips & Notes": "tips"
                }
                
                dir_name = type_to_dir[resource_type]
                
                # Get resource path
                resource_path = get_file_path(selected_uni, selected_semester, selected_course) / dir_name
                create_directory_if_not_exists(resource_path)
                
                # Display existing resources
                st.write(f"Current {resource_type} for {selected_course}:")
                existing_files = os.listdir(resource_path) if os.path.exists(resource_path) else []
                
                if existing_files:
                    for i, file in enumerate(existing_files):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(f"{i+1}. {file}")
                        with col2:
                            if st.button("Delete", key=f"delete_file_{i}"):
                                file_path = resource_path / file
                                if os.path.exists(file_path):
                                    os.remove(file_path)
                                    st.success(f"Deleted {file}!")
                                    st.rerun()
                else:
                    st.info(f"No {resource_type.lower()} uploaded yet.")
                
                # Upload new resource
                st.write(f"Upload New {resource_type} for {selected_course}:")
                uploaded_file = st.file_uploader(f"Choose a file for {resource_type}", key=f"file_upload_{dir_name}")
                
                if uploaded_file is not None:
                    # Save the uploaded file
                    file_path = resource_path / uploaded_file.name
                    
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    st.success(f"File {uploaded_file.name} uploaded successfully!")
                    st.rerun()

def manage_requests():
    """Admin interface for managing resource requests"""
    st.subheader("Manage Resource Requests")
    
    # Load all resource requests
    requests = load_requests()
    
    if not requests:
        st.info("No resource requests found.")
        return
    
    # Filter options
    status_filter = st.multiselect(
        "Filter by Status", 
        [
            ResourceRequest.STATUS_PENDING,
            ResourceRequest.STATUS_IN_PROGRESS,
            ResourceRequest.STATUS_COMPLETED,
            ResourceRequest.STATUS_REJECTED
        ],
        default=[ResourceRequest.STATUS_PENDING, ResourceRequest.STATUS_IN_PROGRESS]
    )
    
    priority_filter = st.multiselect(
        "Filter by Priority",
        [
            ResourceRequest.PRIORITY_LOW,
            ResourceRequest.PRIORITY_MEDIUM,
            ResourceRequest.PRIORITY_HIGH
        ],
        default=[]
    )
    
    # Apply filters
    filtered_requests = requests
    if status_filter:
        filtered_requests = [req for req in filtered_requests if req.status in status_filter]
    if priority_filter:
        filtered_requests = [req for req in filtered_requests if req.priority in priority_filter]
    
    if not filtered_requests:
        st.info("No requests match the selected filters.")
        return
    
    # Sort requests: high priority first, then by creation date (newest first)
    priority_order = {
        ResourceRequest.PRIORITY_HIGH: 1,
        ResourceRequest.PRIORITY_MEDIUM: 2,
        ResourceRequest.PRIORITY_LOW: 3
    }
    
    filtered_requests.sort(key=lambda r: (priority_order.get(r.priority, 999), r.created_at), reverse=True)
    
    # Display requests
    for i, request in enumerate(filtered_requests):
        with st.expander(f"Request #{request.request_id} - {request.course} ({request.status})", expanded=(i == 0)):
            cols = st.columns([1, 1])
            
            with cols[0]:
                st.markdown(f"**University:** {request.university}")
                st.markdown(f"**Semester:** {request.semester}")
                st.markdown(f"**Course:** {request.course}")
                st.markdown(f"**Resource Type:** {request.resource_type}")
                st.markdown(f"**Description:** {request.description}")
                
            with cols[1]:
                st.markdown(f"**Requested by:** {request.name}")
                st.markdown(f"**Email:** {request.email}")
                st.markdown(f"**Priority:** {request.priority}")
                st.markdown(f"**Created:** {format_datetime(request.created_at)}")
                st.markdown(f"**Last Updated:** {format_datetime(request.updated_at)}")
            
            # Update form
            with st.form(key=f"update_request_{request.request_id}"):
                st.subheader("Update Request")
                
                new_status = st.selectbox(
                    "Status", 
                    [
                        ResourceRequest.STATUS_PENDING,
                        ResourceRequest.STATUS_IN_PROGRESS,
                        ResourceRequest.STATUS_COMPLETED,
                        ResourceRequest.STATUS_REJECTED
                    ],
                    index=[
                        ResourceRequest.STATUS_PENDING,
                        ResourceRequest.STATUS_IN_PROGRESS,
                        ResourceRequest.STATUS_COMPLETED,
                        ResourceRequest.STATUS_REJECTED
                    ].index(request.status)
                )
                
                new_priority = st.selectbox(
                    "Priority",
                    [
                        ResourceRequest.PRIORITY_LOW,
                        ResourceRequest.PRIORITY_MEDIUM,
                        ResourceRequest.PRIORITY_HIGH
                    ],
                    index=[
                        ResourceRequest.PRIORITY_LOW,
                        ResourceRequest.PRIORITY_MEDIUM,
                        ResourceRequest.PRIORITY_HIGH
                    ].index(request.priority)
                )
                
                admin_notes = st.text_area("Admin Notes", value=request.admin_notes)
                
                cols_btn = st.columns([1, 1, 1])
                with cols_btn[0]:
                    update_btn = st.form_submit_button("Update")
                with cols_btn[2]:
                    delete_btn = st.form_submit_button("Delete Request", type="secondary")
                
                if update_btn:
                    updates = {
                        "status": new_status,
                        "priority": new_priority,
                        "admin_notes": admin_notes
                    }
                    
                    if update_request(request.request_id, updates):
                        st.success("Request updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update request.")
                
                if delete_btn:
                    if delete_request(request.request_id):
                        st.success("Request deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete request.")

def request_analytics():
    """Admin interface for viewing request analytics"""
    st.subheader("Resource Request Analytics")
    
    stats = get_request_stats()
    
    if stats["total"] == 0:
        st.info("No request data available for analytics.")
        return
    
    # Create a dashboard layout
    col1, col2 = st.columns(2)
    
    # Total requests and completion rate
    with col1:
        st.markdown(f"### Total Requests: {stats['total']}")
        
        completed = stats["by_status"].get(ResourceRequest.STATUS_COMPLETED, 0)
        completion_rate = (completed / stats["total"]) * 100 if stats["total"] > 0 else 0
        
        st.markdown(f"### Completion Rate: {completion_rate:.1f}%")
        
        # Average completion time
        if stats["avg_completion_time"] > 0:
            st.markdown(f"### Avg. Completion Time: {stats['avg_completion_time']:.1f} days")
    
    # Status breakdown
    with col2:
        status_counts = stats["by_status"]
        if status_counts:
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Requests by Status",
                color_discrete_sequence=px.colors.qualitative.Set1
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Priority breakdown
    col3, col4 = st.columns(2)
    
    with col3:
        priority_counts = stats["by_priority"]
        if priority_counts:
            fig = px.bar(
                x=list(priority_counts.keys()),
                y=list(priority_counts.values()),
                title="Requests by Priority",
                labels={"x": "Priority", "y": "Count"},
                color=list(priority_counts.keys()),
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Resource type breakdown
    with col4:
        type_counts = stats["by_type"]
        if type_counts:
            fig = px.bar(
                x=list(type_counts.keys()),
                y=list(type_counts.values()),
                title="Requests by Resource Type",
                labels={"x": "Resource Type", "y": "Count"},
                color=list(type_counts.keys()),
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # University and course breakdown
    st.subheader("Request Distribution")
    
    uni_counts = stats["by_university"]
    if uni_counts:
        fig = px.treemap(
            names=list(uni_counts.keys()),
            parents=[""] * len(uni_counts),
            values=list(uni_counts.values()),
            title="Requests by University",
            color=list(uni_counts.values()),
            color_continuous_scale="RdBu"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Request table view
    st.subheader("Raw Request Data")
    
    # Load all requests for the table
    requests = load_requests()
    if requests:
        # Convert to DataFrame for table display
        df = pd.DataFrame([req.to_dict() for req in requests])
        
        # Select only the columns we want to display
        display_cols = ["request_id", "university", "course", "resource_type", 
                     "priority", "status", "created_at"]
        
        if all(col in df.columns for col in display_cols):
            display_df = df[display_cols].copy()
            
            # Format dates
            if "created_at" in display_df.columns:
                display_df["created_at"] = display_df["created_at"].apply(format_datetime)
            
            # Rename columns for better display
            display_df.columns = [col.replace("_", " ").title() for col in display_df.columns]
            
            st.dataframe(display_df, use_container_width=True)

def show_admin_panel():
    """Display the admin panel"""
    st.markdown('<div class="main-header"><h1>Admin Portal</h1><p>Manage universities, semesters, courses, and upload resources</p></div>', unsafe_allow_html=True)
    
    # Add custom styling for admin panel
    st.markdown("""
    <style>
        .admin-section {
            background-color: #2D2D2D;
            padding: 1.5rem;
            border-radius: 5px;
            margin-bottom: 1.5rem;
        }
        .admin-btn {
            background-color: #FF5252 !important;
            color: white !important;
        }
        div[data-testid="stForm"] {
            background-color: #2D2D2D;
            padding: 1rem;
            border-radius: 5px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Create tabs for different admin functions with custom styling
    tabs = st.tabs([
        "Universities", 
        "Semesters", 
        "Courses", 
        "Upload Resources", 
        "Resource Requests",
        "Request Analytics"
    ])
    
    with tabs[0]:
        manage_universities()
    
    with tabs[1]:
        manage_semesters()
    
    with tabs[2]:
        manage_courses()
    
    with tabs[3]:
        upload_resources()
    
    with tabs[4]:
        manage_requests()
    
    with tabs[5]:
        request_analytics()
