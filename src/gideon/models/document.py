from typing import List
from dataclasses import dataclass

UNKNOWN_AUTHOR = "Unknown_Author"
UNKNOWN_TITLE = "Unknown_Title"
UNKNOWN_TOPIC = "Unknown_Topic"
TOPIC_LIST = [
    "Mathematics",
    "Topology",
    "Geometry",
    "Algebra",
    "Analysis",
    "Probability",
    "Statistics",
    "Combinatorics",
    "Computer Science",
    "Physics",
    "Chemistry",
    "Biology",
    "Economics",
    "Business",
    "Engineering",
    "Medicine",
    "Psychology",
    "Philosophy",
    "History",
    "Literature",
    "Arts",
    "Law",
    "Education",
    "Marketing",
    "Finance",
    "Accounting",
    "Management",
    "Artificial Intelligence",
    "Machine Learning",
    "Data Science",
    "Software Engineering",
    "Other",
]


@dataclass
class DocumentInfo:
    authors: List[str]
    year: str
    title: str
    topic: str = UNKNOWN_TOPIC
