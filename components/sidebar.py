import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

def render_sidebar(memories):
    """
    Render the sidebar with filters and stats.
    
    Args:
        memories (list): List of memory dictionaries
    """
    st.sidebar.image("static/images/brain-icon.png", width=80)
    st.sidebar.title("Memory Filters")
    
    # Extract date range from memories
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now()
    
    if memories:
        try:
            # Try to get actual date range from memories
            dates = []
            for memory in memories:
                if 'date' in memory:
                    if isinstance(memory['date'], str):
                        dates.append(pd.to_datetime(memory['date']))
                    else:
                        dates.append(memory['date'])
            
            if dates:
                start_date = min(dates).date()
                end_date = max(dates).date()
        except (ValueError, AttributeError):
            pass
    
    # Date range filter
    date_range = st.sidebar.date_input("Date Range", 
                                    [start_date, end_date])
    
    # Memory type filter
    memory_types = set()
    for memory in memories:
        if 'type' in memory:
            memory_types.add(memory['type'])
    
    memory_types = sorted(list(memory_types)) if memory_types else ['document', 'image', 'audio', 'web']
    
    memory_type_filter = st.sidebar.multiselect("Memory Types", 
                                            options=memory_types,
                                            default=memory_types)
    
    # Entity filter if entities exist
    entities = set()
    for memory in memories:
        if 'entities' in memory and memory['entities']:
            for entity in memory['entities']:
                if isinstance(entity, dict):
                    entities.add(entity.get('type', 'unknown'))
                else:
                    entities.add(entity)
    
    if entities:
        entity_filter = st.sidebar.multiselect("Entity Types", 
                                           options=sorted(list(entities)),
                                           default=[])
    
    # Content source filter if sources exist
    sources = set()
    for memory in memories:
        if 'source' in memory:
            sources.add(memory['source'])
    
    if sources:
        source_filter = st.sidebar.multiselect("Content Sources", 
                                            options=sorted(list(sources)),
                                            default=[])
    
    # Index new content
    st.sidebar.markdown("---")
    st.sidebar.subheader("Index New Content")
    
    source_type = st.sidebar.selectbox(
        "Content Source",
        ["Local Files", "Browser History", "Photos", "Notes"]
    )
    
    if source_type == "Local Files":
        folder_path = st.sidebar.text_input("Folder Path", "")
        if st.sidebar.button("Index Folder"):
            if folder_path:
                with st.spinner(f"Indexing files in {folder_path}..."):
                    # Call your indexing function here
                    # new_memories = index_directory(folder_path)
                    # st.session_state.memories.extend(new_memories)
                    st.sidebar.success("Indexing complete!")
            else:
                st.sidebar.error("Please provide a folder path")
    
    # Memory statistics
    st.sidebar.markdown("---")
    st.sidebar.subheader("Memory Stats")
    
    # Count by type
    type_counts = {}
    for memory in memories:
        memory_type = memory.get('type', 'document')
        type_counts[memory_type] = type_counts.get(memory_type, 0) + 1
    
    total_memories = len(memories)
    st.sidebar.metric("Total Memories", total_memories)
    
    col1, col2 = st.sidebar.columns(2)
    col1.metric("Documents", type_counts.get('document', 0))
    col2.metric("Images", type_counts.get('image', 0))
    
    col1, col2 = st.sidebar.columns(2)
    col1.metric("Audio", type_counts.get('audio', 0))
    col2.metric("Web", type_counts.get('web', 0))
    
    # Information about the app
    st.sidebar.markdown("---")
    st.sidebar.info("This is your Personal Memory Search Engine. It helps you organize and search through your digital life.")