class DocType:
    ARTICLE = "Art"
    BOOK = "Book"
    THESIS = "Theses"
    COMMERCIAL_DOCUMENT = "CommDoc"
    LEGAL_DOCUMENT = "LegalDoc"
    NON_DISCLOSURE_AGREEMENT = "NDA"
    SCRIPT = "Scripts"

    @staticmethod
    def get_type_docs():
        docs = {
            DocType.ARTICLE: "articles",
            DocType.BOOK: "books",
            DocType.THESIS: "theses",
            DocType.COMMERCIAL_DOCUMENT: "commercial documents",
            DocType.LEGAL_DOCUMENT: "legal documents",
            DocType.SCRIPT: "scripts",
            DocType.NON_DISCLOSURE_AGREEMENT: "nda",
        }
        return list(docs.values())

    def get_type_ext_docs():
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
        return len(DocType.get_type_docs())


TOPICS = {
    "Math": "Mathematics",
    "TopoGeo": "Topology Geometry",
    "AlgNum": "Algebra and Number Theory",
    "Anal": "Analysis",
    "SetLog": "Set Theory and Logic",
    "ProbStat": "Probability and Statistics",
    "Graph": "Graph Theory",
    "DiffEq": "Differential Equations",
    "LinAlg": "Linear Algebra",
    "Crypto": "Cryptography",
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
