import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def app():
    st.title("👨‍⚕️ Specialists")
    st.markdown("Browse all available specialists and their detailed profiles.")

    # Enhanced specialists data with contact info and ratings
    specialists_data = [
        {
            "name": "Dr. Sarah Smith",
            "specialty": "Cardiology",
            "experience": 10,
            "phone": "+1 (555) 123-4567",
            "email": "sarah.smith@medcenter.com",
            "clinic": "Heart Care Center",
            "address": "123 Medical Plaza, Suite 200",
            "rating": 4.8,
            "total_reviews": 156,
            "availability": "Mon-Fri 9AM-5PM",
            "education": "MD, Harvard Medical School",
            "languages": ["English", "Spanish"]
        },
        {
            "name": "Dr. Michael Johnson",
            "specialty": "Dermatology",
            "experience": 7,
            "phone": "+1 (555) 234-5678",
            "email": "michael.johnson@skincare.com",
            "clinic": "Advanced Dermatology",
            "address": "456 Health Street, Floor 3",
            "rating": 4.6,
            "total_reviews": 89,
            "availability": "Tue-Sat 8AM-6PM",
            "education": "MD, Stanford University",
            "languages": ["English", "French"]
        },
        {
            "name": "Dr. Emily Lee",
            "specialty": "Neurology",
            "experience": 15,
            "phone": "+1 (555) 345-6789",
            "email": "emily.lee@neurocenter.com",
            "clinic": "Neurological Institute",
            "address": "789 Brain Avenue, Suite 100",
            "rating": 4.9,
            "total_reviews": 203,
            "availability": "Mon-Thu 7AM-4PM",
            "education": "MD, Johns Hopkins University",
            "languages": ["English", "Mandarin"]
        },
        {
            "name": "Dr. Raj Patel",
            "specialty": "Pediatrics",
            "experience": 5,
            "phone": "+1 (555) 456-7890",
            "email": "raj.patel@kidshealth.com",
            "clinic": "Children's Medical Center",
            "address": "321 Child Care Drive",
            "rating": 4.7,
            "total_reviews": 134,
            "availability": "Mon-Fri 8AM-5PM, Sat 9AM-2PM",
            "education": "MD, University of California",
            "languages": ["English", "Hindi", "Gujarati"]
        },
        {
            "name": "Dr. Jennifer Kim",
            "specialty": "Orthopedics",
            "experience": 12,
            "phone": "+1 (555) 567-8901",
            "email": "jennifer.kim@bonehealth.com",
            "clinic": "Sports Medicine Center",
            "address": "654 Fitness Boulevard",
            "rating": 4.5,
            "total_reviews": 98,
            "availability": "Mon-Wed-Fri 6AM-3PM",
            "education": "MD, Mayo Clinic",
            "languages": ["English", "Korean"]
        }
    ]

    # Display specialist profiles
    st.subheader("👨‍⚕️ Specialist Profiles")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        specialty_filter = st.selectbox("Filter by Specialty", 
                                       ["All"] + list(set([doc["specialty"] for doc in specialists_data])))
    with col2:
        rating_filter = st.selectbox("Filter by Rating", 
                                    ["All", "4.5+ Stars", "4.7+ Stars", "4.8+ Stars"])

    # Filter specialists
    filtered_specialists = specialists_data
    if specialty_filter != "All":
        filtered_specialists = [doc for doc in filtered_specialists if doc["specialty"] == specialty_filter]
    
    if rating_filter != "All":
        min_rating = float(rating_filter.split("+")[0])
        filtered_specialists = [doc for doc in filtered_specialists if doc["rating"] >= min_rating]

    # Display specialist cards
    for specialist in filtered_specialists:
        with st.expander(f"👨‍⚕️ {specialist['name']} - {specialist['specialty']} ⭐ {specialist['rating']}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**🏥 Clinic:** {specialist['clinic']}")
                st.markdown(f"**📍 Address:** {specialist['address']}")
                st.markdown(f"**⏰ Availability:** {specialist['availability']}")
            
            with col2:
                st.markdown(f"**📞 Phone:** {specialist['phone']}")
                st.markdown(f"**📧 Email:** {specialist['email']}")
                st.markdown(f"**🎓 Education:** {specialist['education']}")
            
            with col3:
                st.markdown(f"**⭐ Rating:** {specialist['rating']}/5.0 ({specialist['total_reviews']} reviews)")
                st.markdown(f"**📅 Experience:** {specialist['experience']} years")
                st.markdown(f"**🗣️ Languages:** {', '.join(specialist['languages'])}")
            
            # Rating visualization
            rating_percentage = (specialist['rating'] / 5.0) * 100
            st.progress(rating_percentage / 100)
            st.caption(f"Patient satisfaction: {rating_percentage:.0f}%")

    st.divider()

    # Summary statistics
    st.subheader("📊 Specialist Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Specialists", len(specialists_data))
    with col2:
        avg_rating = sum([doc["rating"] for doc in specialists_data]) / len(specialists_data)
        st.metric("Average Rating", f"{avg_rating:.1f}/5.0")
    with col3:
        total_reviews = sum([doc["total_reviews"] for doc in specialists_data])
        st.metric("Total Reviews", total_reviews)
    with col4:
        avg_experience = sum([doc["experience"] for doc in specialists_data]) / len(specialists_data)
        st.metric("Avg Experience", f"{avg_experience:.1f} years")

    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Specialists by Specialty")
        specialty_counts = {}
        for doc in specialists_data:
            specialty_counts[doc["specialty"]] = specialty_counts.get(doc["specialty"], 0) + 1
        
        fig = px.bar(
            x=list(specialty_counts.keys()),
            y=list(specialty_counts.values()),
            title="Number of Specialists per Specialty",
            color=list(specialty_counts.keys()),
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig.update_layout(showlegend=False, xaxis_title="Specialty", yaxis_title="Number of Specialists")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⭐ Rating Distribution")
        ratings = [doc["rating"] for doc in specialists_data]
        names = [doc["name"].split()[1] for doc in specialists_data]  # Last names only
        
        fig = go.Figure(data=go.Bar(
            x=names,
            y=ratings,
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        ))
        fig.update_layout(
            title="Specialist Ratings",
            xaxis_title="Specialist",
            yaxis_title="Rating (out of 5)",
            yaxis=dict(range=[4.0, 5.0])
        )
        st.plotly_chart(fig, use_container_width=True)





