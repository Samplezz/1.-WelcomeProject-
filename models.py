"""
Models for the Student Resource Portal
Contains data structures and methods for resource requests
"""
import json
import os
from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st

class ResourceRequest:
    """Model for a resource request"""
    
    STATUS_PENDING = "Pending"
    STATUS_IN_PROGRESS = "In Progress"
    STATUS_COMPLETED = "Completed"
    STATUS_REJECTED = "Rejected"
    
    PRIORITY_LOW = "Low"
    PRIORITY_MEDIUM = "Medium"
    PRIORITY_HIGH = "High"
    
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
                 admin_notes=None):
        """Initialize a resource request"""
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
        self.request_id = request_id
        self.admin_notes = admin_notes or ""
        
    def to_dict(self):
        """Convert request to dictionary for JSON serialization"""
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
            "admin_notes": self.admin_notes
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create request from dictionary"""
        return cls(
            university=data.get("university"),
            semester=data.get("semester"),
            course=data.get("course"),
            resource_type=data.get("resource_type"),
            description=data.get("description"),
            name=data.get("name"),
            email=data.get("email"),
            priority=data.get("priority", cls.PRIORITY_MEDIUM),
            status=data.get("status", cls.STATUS_PENDING),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            request_id=data.get("request_id"),
            admin_notes=data.get("admin_notes", "")
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
        # Create directory if not exists
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
    
    # Generate a unique ID for the request if not already set
    if not request.request_id:
        # Use timestamp + count as ID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        request.request_id = f"REQ-{timestamp}-{len(requests) + 1}"
    
    requests.append(request)
    return save_requests(requests)

def update_request(request_id, updates):
    """Update an existing resource request"""
    requests = load_requests()
    updated = False
    
    for i, req in enumerate(requests):
        if req.request_id == request_id:
            # Update the request
            for key, value in updates.items():
                setattr(req, key, value)
            
            # Update the updated_at timestamp
            req.updated_at = datetime.now().isoformat()
            updated = True
            break
    
    if updated:
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
        if req.status == ResourceRequest.STATUS_COMPLETED:
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
