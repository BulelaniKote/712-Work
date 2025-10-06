import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules.utilis import get_medical_specialists

def app():
    st.title("👨‍⚕️ Specialists")
    st.markdown("Browse all available specialists and their detailed profiles.")

    # Get specialists data from BigQuery
    specialists_data = get_medical_specialists()
    
    if not specialists_data:
        st.warning("No specialists data available. Please ensure the specialists table is uploaded to BigQuery.")
        return
    
    # Transform the data to match the expected format
    formatted_specialists = []
    for specialist in specialists_data:
        formatted_specialists.append({
            "name": f"Dr. {specialist.get('FirstName', '')} {specialist.get('LastName', '')}",
            "specialty": specialist.get('Specialty', 'Unknown'),
            "phone": specialist.get('Contact', 'N/A'),
            "email": specialist.get('Email', 'N/A'),
            "rating": float(specialist.get('Rating', 4.5)),
            "specialist_id": specialist.get('SpecialistID', ''),
            "first_name": specialist.get('FirstName', ''),
            "last_name": specialist.get('LastName', '')
        })

    # Display specialist profiles
    st.subheader("👨‍⚕️ Specialist Profiles")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        specialty_filter = st.selectbox("Filter by Specialty", 
                                       ["All"] + list(set([doc["specialty"] for doc in formatted_specialists])))
    with col2:
        rating_filter = st.selectbox("Filter by Rating", 
                                    ["All", "4.0+ Stars", "4.2+ Stars", "4.5+ Stars"])

    # Filter specialists
    filtered_specialists = formatted_specialists
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
                st.markdown(f"**👨‍⚕️ Name:** {specialist['name']}")
                st.markdown(f"**🏥 Specialty:** {specialist['specialty']}")
                st.markdown(f"**🆔 ID:** {specialist['specialist_id']}")
            
            with col2:
                st.markdown(f"**📞 Phone:** {specialist['phone']}")
                st.markdown(f"**📧 Email:** {specialist['email']}")
                st.markdown(f"**⭐ Rating:** {specialist['rating']}/5.0")
            
            with col3:
                # Rating visualization
                rating_percentage = (specialist['rating'] / 5.0) * 100
                st.progress(rating_percentage / 100)
                st.caption(f"Patient satisfaction: {rating_percentage:.0f}%")

    st.divider()

    # Summary statistics
    st.subheader("📊 Specialist Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Specialists", len(formatted_specialists))
    with col2:
        avg_rating = sum([doc["rating"] for doc in formatted_specialists]) / len(formatted_specialists)
        st.metric("Average Rating", f"{avg_rating:.1f}/5.0")
    with col3:
        unique_specialties = len(set([doc["specialty"] for doc in formatted_specialists]))
        st.metric("Specialties", unique_specialties)
    with col4:
        high_rated = len([doc for doc in formatted_specialists if doc["rating"] >= 4.5])
        st.metric("High Rated (4.5+)", high_rated)

    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Specialists by Specialty")
        specialty_counts = {}
        for doc in formatted_specialists:
            specialty_counts[doc["specialty"]] = specialty_counts.get(doc["specialty"], 0) + 1
        
        if specialty_counts:
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
        if formatted_specialists:
            ratings = [doc["rating"] for doc in formatted_specialists]
            names = [doc["last_name"] for doc in formatted_specialists]  # Last names only
            
            fig = go.Figure(data=go.Bar(
                x=names,
                y=ratings,
                marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'][:len(names)]
            ))
            fig.update_layout(
                title="Specialist Ratings",
                xaxis_title="Specialist",
                yaxis_title="Rating (out of 5)",
                yaxis=dict(range=[0, 5.0])
            )
            st.plotly_chart(fig, use_container_width=True)





