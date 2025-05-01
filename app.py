import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import time
import os
import json
from datetime import datetime, timedelta
import random
from PIL import Image
import io
import base64

# Set page configuration
st.set_page_config(
    page_title="Personal Memory Search Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        background: linear-gradient(45deg, #FF5852, #FF924C, #FFCC47, #71D999, #36CFC9, #3E7CB9, #8867CA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 800;
        margin-bottom: 30px;
    }
    .memory-card {
        border-radius: 15px;
        border: 1px solid rgba(130, 130, 130, 0.2);
        padding: 20px;
        margin-bottom: 20px;
        transition: transform 0.3s;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .memory-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .memory-document {
        border-left: 5px solid #3E7CB9;
    }
    .memory-image {
        border-left: 5px solid #FF924C;
    }
    .memory-audio {
        border-left: 5px solid #8867CA;
    }
    .memory-web {
        border-left: 5px solid #71D999;
    }
    .search-box {
        border-radius: 30px !important;
        border: 2px solid #3E7CB9 !important;
        padding: 20px !important;
        font-size: 1.2rem !important;
    }
    .stButton button {
        border-radius: 30px;
        background-color: #3E7CB9;
        color: white;
        font-weight: bold;
        padding: 0.5rem 2rem;
        font-size: 1rem;
    }
    .timeline-header {
        font-size: 1.8rem;
        color: #3E7CB9;
        margin-top: 30px;
    }
    .entity-pill {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 15px;
        margin-right: 5px;
        margin-bottom: 5px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .entity-person {
        background-color: #FFD0D5;
        color: #C9184A;
    }
    .entity-location {
        background-color: #D0F0FD;
        color: #0077B6;
    }
    .entity-organization {
        background-color: #D8E2DC;
        color: #457B9D;
    }
    .entity-date {
        background-color: #FADDE1;
        color: #EA526F;
    }
    .entity-unknown {
        background-color: #E6E6E6;
        color: #666666;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------
# Functions for search and indexing
# ---------------------------------

def simple_search(query, memories, top_k=10):
    """Simple keyword-based search"""
    query_terms = query.lower().split()
    results = []
    
    for memory in memories:
        score = 0
        
        # Check title
        if 'title' in memory:
            title = memory['title'].lower()
            for term in query_terms:
                if term in title:
                    score += 10  # Higher weight for title matches
        
        # Check content
        if 'content' in memory:
            content = memory['content'].lower()
            for term in query_terms:
                score += content.count(term) * 2
        
        # Check entities
        if 'entities' in memory and memory['entities']:
            for entity in memory['entities']:
                if isinstance(entity, dict):
                    entity_text = entity.get('text', '').lower()
                else:
                    entity_text = str(entity).lower()
                    
                for term in query_terms:
                    if term in entity_text:
                        score += 5  # Higher weight for entity matches
        
        if score > 0:
            results.append((memory, score))
    
    # Sort by score
    results.sort(key=lambda x: x[1], reverse=True)
    
    # Return top k memories
    return [memory for memory, _ in results[:top_k]]

def generate_sample_data(num_items=50):
    """Generate sample data for demonstration"""
    memory_types = ['document', 'image', 'audio', 'web']
    entity_types = ['person', 'location', 'organization', 'date']
    
    sample_titles = [
        "Meeting with Marketing Team", "Project Proposal Draft", 
        "Vacation Photos from Hawaii", "Research Notes on AI", 
        "Birthday Party Recording", "Tax Documents 2023",
        "Home Renovation Plans", "Recipe Collection", 
        "Travel Itinerary - Europe Trip", "Podcast Interview",
        "Family Reunion Photos", "Book Notes - Think Again",
        "Website Design Mockups", "Personal Budget Spreadsheet",
        "Medical Records", "Conference Presentation",
        "Wine Tasting Notes", "Hiking Trip Photos",
        "Car Maintenance Records", "Movie Reviews"
    ]
    
    sample_content_templates = [
        "This document contains {topic} that I worked on in {timeframe}.",
        "Notes from my research about {topic} that I found very interesting.",
        "Collection of {topic} that I want to remember for future reference.",
        "Important information about {topic} that I need for {purpose}.",
        "Ideas and thoughts about {topic} that came up during {activity}."
    ]
    
    sample_topics = [
        "artificial intelligence", "renewable energy", "digital photography",
        "home improvement", "financial planning", "machine learning",
        "nutrition and diet", "travel destinations", "productivity techniques",
        "web development", "mental health", "sustainability practices"
    ]
    
    sample_people = [
        "John Smith", "Emma Johnson", "Michael Brown", "Lisa Davis",
        "Robert Wilson", "Sarah Miller", "David Anderson", "Jennifer Thomas"
    ]
    
    sample_organizations = [
        "Acme Corp", "TechNova", "Global Solutions", "Evergreen Industries",
        "Summit Enterprises", "Horizon Healthcare", "Pinnacle Partners", "Quantum Research"
    ]
    
    sample_locations = [
        "New York", "San Francisco", "Tokyo", "London", "Paris",
        "Sydney", "Toronto", "Berlin", "Singapore", "Barcelona"
    ]
    
    # Create sample memories
    memories = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*2)  # 2 years of data
    
    for i in range(num_items):
        # Generate random date within the range
        memory_date = start_date + timedelta(
            days=random.randint(0, (end_date - start_date).days)
        )
        
        # Random memory type
        memory_type = random.choice(memory_types)
        
        # Random title or combination of titles
        title = random.choice(sample_titles)
        
        # Generate content
        content_template = random.choice(sample_content_templates)
        topic = random.choice(sample_topics)
        timeframe = f"{random.choice(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])} {memory_date.year}"
        activity = random.choice(["a meeting", "my research", "a workshop", "a conversation", "my travels"])
        purpose = random.choice(["work", "personal projects", "planning", "reference", "learning"])
        
        content = content_template.format(
            topic=topic,
            timeframe=timeframe,
            activity=activity,
            purpose=purpose
        )
        
        # Add more specific content based on type
        if memory_type == 'document':
            content += f" This document is {random.randint(1, 20)} pages long and covers key points about {topic}."
        elif memory_type == 'image':
            content += f" This image captures {random.choice(['an important moment', 'a beautiful scene', 'a key diagram', 'a memorable event'])} related to {topic}."
        elif memory_type == 'audio':
            content += f" This audio recording is {random.randint(1, 120)} minutes long and includes discussions about {topic}."
        elif memory_type == 'web':
            content += f" This webpage contains valuable information about {topic} that I bookmarked for future reference."
        
        # Generate random entities
        entities = []
        # Add 1-3 random people
        for _ in range(random.randint(1, 3)):
            entities.append({"type": "person", "text": random.choice(sample_people)})
        
        # Add 0-2 random organizations
        for _ in range(random.randint(0, 2)):
            entities.append({"type": "organization", "text": random.choice(sample_organizations)})
        
        # Add 0-2 random locations
        for _ in range(random.randint(0, 2)):
            entities.append({"type": "location", "text": random.choice(sample_locations)})
        
        # Create the memory object
        memory = {
            "id": i,
            "title": title,
            "type": memory_type,
            "date": memory_date,
            "content": content,
            "entities": entities,
            "sentiment": random.uniform(-1, 1),  # Random sentiment score
            "source": random.choice(["Local Drive", "Cloud Storage", "Email", "Browser", "Mobile Device"]),
            "file_size": random.randint(10, 10000) if memory_type != 'web' else None
        }
        
        memories.append(memory)
    
    return memories

# ---------------------------------
# UI Components
# ---------------------------------

def render_search_box():
    """Render search box and return query"""
    col1, col2 = st.columns([5,1])
    
    with col1:
        search_query = st.text_input("", 
                                     placeholder="Ask me anything about your digital memories...", 
                                     label_visibility="collapsed", 
                                     key="search_box")
    
    with col2:
        search_button = st.button("🔍 Search")
    
    if search_button and search_query:
        return search_query
    
    return None

def render_timeline(memories):
    """Render a visual timeline of memories"""
    st.markdown("<h2 class='timeline-header'>Your Memory Timeline</h2>", unsafe_allow_html=True)
    
    if not memories:
        st.info("No memories to display in timeline. Try indexing some content or modifying your search.")
        return
    
    # Group memories by month
    memory_df = pd.DataFrame(memories)
    
    # Convert date strings to datetime objects if needed
    if 'date' in memory_df.columns:
        if memory_df['date'].dtype == 'object':
            memory_df['date'] = pd.to_datetime(memory_df['date'])
        
        # Create month column
        memory_df['month'] = memory_df['date'].dt.strftime('%Y-%m')
        
        # Sort by date
        memory_df = memory_df.sort_values('date')
        
        # Group by month and count
        monthly_counts = memory_df.groupby(['month', 'type']).size().reset_index(name='count')
        
        # Pivot to get types as columns
        timeline_data = monthly_counts.pivot_table(
            index='month', 
            columns='type', 
            values='count',
            fill_value=0
        ).reset_index()
        
        # Create a bar chart
        fig = px.bar(
            timeline_data, 
            x='month',
            y=['document', 'image', 'audio', 'web'],
            title="Memory Timeline",
            labels={'value': 'Number of Memories', 'month': 'Month', 'variable': 'Type'},
            color_discrete_map={
                'document': '#3E7CB9',
                'image': '#FF924C',
                'audio': '#8867CA',
                'web': '#71D999'
            }
        )
        
        fig.update_layout(
            legend_title_text='Memory Type',
            xaxis_title="Timeline",
            yaxis_title="Count",
            barmode='stack',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show a more detailed view of recent memories
        st.subheader("Recent Memories")
        recent_df = memory_df.sort_values('date', ascending=False).head(5)
        
        for _, memory in recent_df.iterrows():
            memory_type = memory['type']
            memory_class = f"memory-card memory-{memory_type}"
            
            st.markdown(f"<div class='{memory_class}'>", unsafe_allow_html=True)
            st.markdown(f"#### {memory['title']}")
            st.markdown(f"*{memory['date'].strftime('%B %d, %Y')}*")
            
            # Truncate content if too long
            content = memory['content']
            if len(content) > 150:
                content = content[:150] + "..."
            st.markdown(content)
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("No date information available in memories.")

def render_connections(memories):
    """Render a network graph of memory connections"""
    st.markdown("<h2 class='timeline-header'>Memory Connections</h2>", unsafe_allow_html=True)
    
    if not memories:
        st.info("No memories to display in connections view. Try indexing some content or modifying your search.")
        return
    
    # Create a simplified network graph based on memory types and entities
    memory_df = pd.DataFrame(memories)
    
    # Create nodes for visualization
    nodes = []
    for i, memory in enumerate(memories[:20]):  # Limit to 20 for performance
        x = random.uniform(-10, 10)
        y = random.uniform(-10, 10)
        
        color = '#3E7CB9'  # Default color (document)
        if memory['type'] == 'image':
            color = '#FF924C'
        elif memory['type'] == 'audio':
            color = '#8867CA'
        elif memory['type'] == 'web':
            color = '#71D999'
            
        nodes.append({
            'index': i,
            'id': memory.get('id', i),
            'title': memory.get('title', f"Memory {i}"),
            'type': memory.get('type', 'document'),
            'x': x,
            'y': y,
            'color': color
        })
    
    # Create links between memories that share entities or are close in time
    links = []
    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
            memory_i = memories[i]
            memory_j = memories[j]
            
            # Connect if same type
            if memory_i['type'] == memory_j['type']:
                links.append({
                    'source': i,
                    'target': j,
                    'value': 1
                })
            
            # Connect if they share entities
            if ('entities' in memory_i and 'entities' in memory_j 
                    and memory_i['entities'] and memory_j['entities']):
                entities_i = [e['text'] if isinstance(e, dict) else e for e in memory_i['entities']]
                entities_j = [e['text'] if isinstance(e, dict) else e for e in memory_j['entities']]
                
                if set(entities_i) & set(entities_j):  # If there's an intersection
                    links.append({
                        'source': i,
                        'target': j,
                        'value': 2  # Stronger connection for shared entities
                    })
    
    # Create a Plotly figure for the network graph
    node_trace = px.scatter(
        nodes, x='x', y='y', 
        color='type',
        text='title',
        color_discrete_map={
            'document': '#3E7CB9',
            'image': '#FF924C',
            'audio': '#8867CA',
            'web': '#71D999'
        }
    )
    
    fig = node_trace.update_traces(
        marker=dict(size=15, line=dict(width=2, color='white')),
        mode='markers+text',
        textposition='top center'
    )
    
    # Add edges to the graph
    for link in links:
        source = nodes[link['source']]
        target = nodes[link['target']]
        
        opacity = 0.3 if link['value'] == 1 else 0.6
        
        fig.add_shape(
            type="line",
            x0=source['x'], y0=source['y'],
            x1=target['x'], y1=target['y'],
            line=dict(color="#888888", width=1),
            opacity=opacity
        )
    
    fig.update_layout(
        title="Memory Connection Network",
        showlegend=True,
        height=600,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show a legend explaining the connections
    st.markdown("""
    **Connection Types:**
    - **Same Type:** Memories of the same type (document, image, etc.)
    - **Shared Entities:** Memories that mention the same people, places, or organizations
    """)

def render_gallery(memories):
    """Render gallery view of memories"""
    st.markdown("<h2 class='timeline-header'>Memory Gallery</h2>", unsafe_allow_html=True)
    
    if not memories:
        st.info("No memories to display in gallery. Try indexing some content or modifying your search.")
        return
    
    # Display memories in a grid
    memory_limit = min(9, len(memories))  # Limit to 9 for the gallery view
    
    for i, memory in enumerate(memories[:memory_limit]):
        if i % 3 == 0:
            cols = st.columns(3)
        
        with cols[i % 3]:
            # Default to document type if not specified
            memory_type = memory.get('type', 'document')
            memory_class = f"memory-card memory-{memory_type}"
            
            # Create a card for the memory
            st.markdown(f"<div class='{memory_class}'>", unsafe_allow_html=True)
            
            st.markdown(f"#### {memory.get('title', 'Untitled Memory')}")
            
            # Format date if available
            if 'date' in memory:
                try:
                    if isinstance(memory['date'], str):
                        date_str = memory['date']
                    else:
                        date_str = memory['date'].strftime('%B %d, %Y')
                    
                    st.markdown(f"*{date_str}*")
                except (ValueError, AttributeError):
                    pass
            
            # Show content excerpt
            content = memory.get('content', '')
            if content:
                if len(content) > 150:
                    content = content[:150] + "..."
                st.markdown(content)
            
            # Display entity tags if available
            if 'entities' in memory and memory['entities']:
                for entity in memory['entities']:
                    entity_type = entity.get('type', 'unknown')
                    entity_text = entity.get('text', entity)
                    if isinstance(entity, str):
                        entity_type = 'unknown'
                        entity_text = entity
                        
                    st.markdown(f"<span class='entity-pill entity-{entity_type}'>{entity_text}</span>", 
                               unsafe_allow_html=True)
            
            # For image type, create a placeholder image
            if memory_type == 'image':
                # Create a simple colored rectangle as a placeholder
                fig, ax = plt.subplots(figsize=(3, 2))
                color = np.random.rand(3,)
                ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=color))
                ax.axis('off')
                st.pyplot(fig)
            
            st.markdown("</div>", unsafe_allow_html=True)

def render_sidebar(memories):
    """Render sidebar with filters and stats"""
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
                    entity_type = entity.get('type', 'unknown')
                    entities.add(entity_type)
    
    if entities:
        entity_filter = st.sidebar.multiselect("Entity Types", 
                                             options=sorted(list(entities)),
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
                    time.sleep(2)  # Simulate indexing
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

# ---------------------------------
# Main Application
# ---------------------------------

# Main header
st.markdown("<h1 class='main-header'>Personal Memory Search Engine</h1>", unsafe_allow_html=True)

# Initialize session state
if 'memories' not in st.session_state:
    # Generate sample data for demonstration
    st.session_state.memories = generate_sample_data(50)

# Render search box and get query
query = render_search_box()

# Process search if query exists
if query:
    with st.spinner('Searching your memories...'):
        search_results = simple_search(query, st.session_state.memories)
        st.session_state.current_results = search_results
        st.success(f'Found {len(search_results)} results')

# Main content tabs
tabs = st.tabs(["Timeline", "Connections", "Analytics", "Gallery"])

# Render different views in tabs
with tabs[0]:
    render_timeline(st.session_state.get('current_results', st.session_state.memories))

with tabs[1]:
    render_connections(st.session_state.get('current_results', st.session_state.memories))

with tabs[2]:
    # Analytics tab
    st.markdown("<h2 class='timeline-header'>Memory Analytics</h2>", unsafe_allow_html=True)
    
    memories_to_analyze = st.session_state.get('current_results', st.session_state.memories)
    
    # Create a DataFrame for analysis
    if memories_to_analyze:
        df = pd.DataFrame(memories_to_analyze)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Memory types distribution
            if 'type' in df.columns:
                type_counts = df['type'].value_counts().reset_index()
                type_counts.columns = ['Type', 'Count']
                
                fig = px.pie(type_counts, values='Count', names='Type', 
                           title='Memory Type Distribution',
                           color='Type', 
                           color_discrete_map={
                               'document': '#3E7CB9',
                               'image': '#FF924C',
                               'audio': '#8867CA',
                               'web': '#71D999'
                           })
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Sentiment over time
            if 'sentiment' in df.columns and 'date' in df.columns:
                df['month'] = pd.to_datetime(df['date']).dt.strftime('%B %Y')
                monthly_sentiment = df.groupby('month')['sentiment'].mean().reset_index()
                
                fig = px.bar(monthly_sentiment, x='month', y='sentiment',
                           title='Average Sentiment By Month',
                           color='sentiment',
                           color_continuous_scale=['#FF5852', '#FFCC47', '#71D999'])
                st.plotly_chart(fig, use_container_width=True)
        
        # Entity distribution
        if 'entities' in df.columns:
            st.subheader("Entity Distribution")
            
            # Extract entities
            all_entities = []
            entity_types = []
            
            for memory in memories_to_analyze:
                if 'entities' in memory and memory['entities']:
                    for entity in memory['entities']:
                        if isinstance(entity, dict):
                            all_entities.append(entity.get('text', 'Unknown'))
                            entity_types.append(entity.get('type', 'unknown'))
            
            if all_entities:
                # Create DataFrame for entities
                entity_df = pd.DataFrame({
                    'text': all_entities,
                    'type': entity_types
                })
                
                # Count by type
                entity_type_counts = entity_df['type'].value_counts().reset_index()
                entity_type_counts.columns = ['Entity Type', 'Count']
                
                # Plot
                fig = px.bar(entity_type_counts, x='Entity Type', y='Count',
                           title='Entity Types Distribution',
                           color='Entity Type',
                           color_discrete_map={
                               'person': '#C9184A',
                               'location': '#0077B6',
                               'organization': '#457B9D',
                               'date': '#EA526F',
                               'unknown': '#666666'
                           })
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for analytics. Try indexing some content or performing a search.")

with tabs[3]:
    render_gallery(st.session_state.get('current_results', st.session_state.memories))

# Render sidebar
render_sidebar(st.session_state.memories)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Personal Memory Search Engine v1.0</p>", unsafe_allow_html=True)