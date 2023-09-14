class DocType: 
    ARTICLE = "articles"
    BOOK = "books"
    THESIS = "theses"
    COMMERCIAL_DOCUMENT = "commercial_documents"
    LEGAL_DOCUMENT = "legal_documents"
    SCRIPT = "scripts"
    NON_DISCLOSURE_AGREEMENT = "nda"

    @staticmethod
    def get_all():
        return [
            DocType.ARTICLE,
            DocType.BOOK,
            DocType.THESIS,
            DocType.COMMERCIAL_DOCUMENT,
            DocType.LEGAL_DOCUMENT,
            DocType.SCRIPT,
            DocType.NON_DISCLOSURE_AGREEMENT,
        ]
    
    @staticmethod
    def total_types():
        return len(DocType.get_all())

TOPICS = {
    "Math": "Mathematics",
    "TopoGeo": "Topology Geometry",
    "AlgNum": "Algebra and Number Theory",
    "Anal": "Analysis",
    "SetLog": "Set Theory and Logic",
    "ProbStat": "Probability and Statistics",
    "CompSci": "Computer Science",
    "MLAI": "Machine Learning and AI",
    "Phys": "Physical Sciences",
    "Bio": "Biological Sciences",
    "SocSc": "Social Sciences",
    "EcoFin": "Economics and finance",
    "PsySoc": "Psychology and Sociology",
    "Hum": "Humanities",
    "Arts": "Arts",
    "Eng": "Engineering",
    "Bus": "business",
    "Heal": "Health",
    "Block": "Blockchain",
    "Othr": "Other",
}

