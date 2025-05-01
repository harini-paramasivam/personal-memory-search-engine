import streamlit as st
import pandas as pd
from streamlit_timeline import timeline

def render_timeline(memories):
    """
    Render the memories timeline.
    
    Args:
        memories (list): List of memory dictionaries
    """
    st.markdown("<h2 class='timeline-header'>Your Memory Timeline</h2>", unsafe_allow_html=True)
    
    if not memories:
        st.info("No memories to display in timeline. Try indexing some content or modifying your search.")
        return
    
    # Prepare timeline data
    timeline_data = {
        "title": {
            "text": {
                "headline": "Your Digital Memories",
                "text": "Explore your personal history through documents, images, and more"
            }
        },
        "events": []
    }
    
    for memory in memories:
        # Skip if missing required fields
        if 'title' not in memory or 'date' not in memory:
            continue
            
        # Get color based on memory type
        color = "#3E7CB9"  # Default color (document)
        if 'type' in memory:
            if memory['type'] == 'image':
                color = "#FF924C"
            elif memory['type'] == 'audio':
                color = "#8867CA"
            elif memory['type'] == 'web':
                color = "#71D999"
        
        # Parse date
        try:
            if isinstance(memory['date'], str):
                date = pd.to_datetime(memory['date'])
            else:
                date = memory['date']
                
            timeline_data["events"].append({
                "start_date": {
                    "month": date.month,
                    "day": date.day,
                    "year": date.year
                },
                "text": {
                    "headline": memory['title'],
                    "text": memory.get('content', '')
                },
                "group": memory.get('type', 'document'),
                "background": {"color": color}
            })
        except (ValueError, AttributeError):
            # Skip entries with invalid dates
            continue
    
    # Display timeline if we have events
    if timeline_data["events"]:
        timeline(timeline_data, height=600)
    else:
        st.info("No timeline data available with the current filters.")