class DocType: 
    ARTICLE = "Art"
    BOOK = "Book"
    THESIS = "Theses"
    COMMERCIAL_DOCUMENT = "CommDoc"
    LEGAL_DOCUMENT = "LegalDoc"
    NON_DISCLOSURE_AGREEMENT = "NDA"
    SCRIPT = "Scripts"

    DOCS = {
        ARTICLE: "articles",
        BOOK: "books",
        THESIS: "theses",
        COMMERCIAL_DOCUMENT: "commercial documents",
        LEGAL_DOCUMENT: "legal documents",
        SCRIPT: "scripts",
        NON_DISCLOSURE_AGREEMENT: "nda",
    }

    @staticmethod
    def get_all(cls):
        return list(cls.DOCS.values())
    
    @staticmethod
    def total_types(cls):
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

MONTHS = [
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
]
