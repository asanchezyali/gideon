import re
from pathlib import Path
from typing import Optional, Tuple
from ..models.document import TOPIC_LIST


class FilenameValidator:
    @staticmethod
    def is_valid_format(filename: str) -> bool:
        """
        Check if filename follows the expected format:
        Author.Year.Title.Topic.Timestamp.pdf
        
        Returns True if the filename matches the expected pattern.
        """
        if not filename.endswith('.pdf'):
            return False
            
        # Remove .pdf extension
        name_without_ext = filename[:-4]
        
        # Split by dots
        parts = name_without_ext.split('.')
        
        # Should have exactly 5 parts: Author, Year, Title, Topic, Timestamp
        if len(parts) != 5:
            return False
        
        author, year, title, topic, timestamp = parts
        
        # Validate each part
        if not FilenameValidator._is_valid_author(author):
            return False
            
        if not FilenameValidator._is_valid_year(year):
            return False
            
        if not FilenameValidator._is_valid_title(title):
            return False
            
        if not FilenameValidator._is_valid_topic(topic):
            return False
            
        if not FilenameValidator._is_valid_timestamp(timestamp):
            return False
            
        return True
    
    @staticmethod
    def _is_valid_author(author: str) -> bool:
        """
        Valid author formats:
        - FirstName_LastName
        - FirstName_MiddleName_LastName
        - FirstName_LastName_And_Others
        - Unknown_Author
        """
        if author == "Unknown_Author":
            return True
            
        # Check if it ends with "_And_Others"
        if author.endswith("_And_Others"):
            author = author[:-11]  # Remove "_And_Others"
            
        # Check if all parts are capitalized and separated by underscores
        parts = author.split('_')
        if len(parts) < 2:
            return False
            
        for part in parts:
            if not part or not part[0].isupper() or not part[1:].islower():
                return False
                
        return True
    
    @staticmethod
    def _is_valid_year(year: str) -> bool:
        """Valid year is 4 digits"""
        return len(year) == 4 and year.isdigit()
    
    @staticmethod
    def _is_valid_title(title: str) -> bool:
        """
        Valid title format:
        - First word capitalized, rest lowercase
        - Words separated by underscores
        - Unknown_Title is also valid
        """
        if title == "Unknown_Title":
            return True
            
        parts = title.split('_')
        if not parts:
            return False
            
        # First word should be capitalized
        if not parts[0] or not parts[0][0].isupper():
            return False
            
        # Rest should be lowercase
        for i, part in enumerate(parts):
            if i == 0:
                if not part[0].isupper() or not part[1:].islower():
                    return False
            else:
                if not part.islower():
                    return False
                    
        return True
    
    @staticmethod
    def _is_valid_topic(topic: str) -> bool:
        """
        Valid topic should be from the predefined list or Unknown_Topic
        Format: Words separated by underscores, each word capitalized
        """
        if topic == "Unknown_Topic":
            return True
            
        # Convert underscore format back to space format for comparison
        topic_with_spaces = topic.replace('_', ' ')
        
        # Check if it matches any topic in the list
        return topic_with_spaces in TOPIC_LIST
    
    @staticmethod
    def _is_valid_timestamp(timestamp: str) -> bool:
        """
        Valid timestamp format: YYYYMMDD_HHMMSS
        """
        if len(timestamp) != 15:
            return False
            
        if timestamp[8] != '_':
            return False
            
        date_part = timestamp[:8]
        time_part = timestamp[9:]
        
        # Check if all digits
        if not date_part.isdigit() or not time_part.isdigit():
            return False
            
        # Basic validation of date/time values
        year = int(date_part[:4])
        month = int(date_part[4:6])
        day = int(date_part[6:8])
        hour = int(time_part[:2])
        minute = int(time_part[2:4])
        second = int(time_part[4:6])
        
        if year < 1900 or year > 2100:
            return False
        if month < 1 or month > 12:
            return False
        if day < 1 or day > 31:
            return False
        if hour > 23:
            return False
        if minute > 59:
            return False
        if second > 59:
            return False
            
        return True
    
    @staticmethod
    def extract_info_from_filename(filename: str) -> Optional[Tuple[str, str, str, str, str]]:
        """
        Extract information from a properly formatted filename.
        Returns (author, year, title, topic, timestamp) or None if invalid format.
        """
        if not FilenameValidator.is_valid_format(filename):
            return None
            
        name_without_ext = filename[:-4]
        parts = name_without_ext.split('.')
        
        return tuple(parts)