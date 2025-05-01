import os
import json
import pandas as pd
from datetime import datetime
from core.document_parser import parse_document
from core.image_analyzer import analyze_image
import hashlib

def index_directory(directory_path, allowed_extensions=None):
    """
    Index files in a directory and add them to the memory database.
    
    Args:
        directory_path (str): Path to the directory to index
        allowed_extensions (list, optional): List of file extensions to include
        
    Returns:
        list: List of indexed memories
    """
    if not os.path.exists(directory_path):
        return []
        
    if allowed_extensions is None:
        allowed_extensions = [
            # Documents
            '.txt', '.pdf', '.docx', '.doc', '.md', '.rtf',
            # Images
            '.jpg', '.jpeg', '.png', '.gif', '.bmp',
            # Audio
            '.mp3', '.wav', '.m4a', '.ogg', '.flac',
            # Other
            '.html', '.csv', '.json'
        ]
    
    memories = []
    
    # Walk through the directory
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            
            # Skip if not an allowed extension
            if file_ext not in allowed_extensions:
                continue
                
            # Get file modification time
            try:
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            except:
                mod_time = datetime.now()
                
            # Get file size
            try:
                file_size = os.path.getsize(file_path)
            except:
                file_size = 0
            
            # Generate a unique ID for the file
            file_id = hashlib.md5(file_path.encode()).hexdigest()
            
            # Determine file type and process accordingly
            if file_ext in ['.txt', '.pdf', '.docx', '.doc', '.md', '.rtf']:
                memory = parse_document(file_path)
                memory_type = 'document'
            elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                memory = analyze_image(file_path)
                memory_type = 'image'
            elif file_ext in ['.mp3', '.wav', '.m4a', '.ogg', '.flac']:
                # For now, just create a simple audio memory
                memory = {
                    'title': file,
                    'content': f"Audio file: {file}"
                }
                memory_type = 'audio'
            else:
                # For other files, just create a basic memory
                memory = {
                    'title': file,
                    'content': f"File: {file}"
                }
                memory_type = 'document'
            
            # Add common metadata
            memory.update({
                'id': file_id,
                'file_path': file_path,
                'file_name': file,
                'file_extension': file_ext,
                'file_size': file_size,
                'date': mod_time,
                'type': memory_type,
                'source': 'local_file'
            })
            
            memories.append(memory)
    
    # Save the memories to a sample file for demo purposes
    with open('data/sample_memories.json', 'w') as f:
        json.dump(memories, f)
    
    return memories