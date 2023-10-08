EXCLUDE_PROJECT_DIR = [".owner", ".vscode", ".git", ".gitignore", ".DS_Store", ".job"]
FORMAT_NORMAL_DOC = "<author>.<year>.<title>.<topic>.<doc_type>.<ext>"
FORMAT_COMMERCIAL_DOC = "<date>.<company>.<name>.<doc_type>.<ext>"
FORMAT_RESEARCH_PROJECT = "<ProjectName>.<Topic>.Owner"
FORMAT_COMMERCIAL_PROJECT = "<ProjectName>.<Company>.Job"

class DocType:
    ARTICLE = "Art"
    BOOK = "Book"
    THESIS = "Theses"
    COMMERCIAL_DOCUMENT = "CommDoc"
    LEGAL_DOCUMENT = "LegalDoc"
    NON_DISCLOSURE_AGREEMENT = "NDA"
    PERSONAL_DOCUMENT = "PersonalDoc"

    @staticmethod
    def get_type_docs():
        docs = {
            DocType.ARTICLE: "Articles",
            DocType.BOOK: "Books",
            DocType.THESIS: "Theses",
            DocType.COMMERCIAL_DOCUMENT: "Commercial documents",
            DocType.LEGAL_DOCUMENT: "Legal documents",
            DocType.NON_DISCLOSURE_AGREEMENT: "Non-disclosure agreements",
            DocType.PERSONAL_DOCUMENT: "Personal documents",
        }
        return docs

    def get_type_ext_docs():
        return [
            DocType.ARTICLE,
            DocType.BOOK,
            DocType.THESIS,
            DocType.COMMERCIAL_DOCUMENT,
            DocType.LEGAL_DOCUMENT,
            DocType.NON_DISCLOSURE_AGREEMENT,
            DocType.PERSONAL_DOCUMENT,
        ]

    @staticmethod
    def total_types():
        return len(DocType.get_type_ext_docs())


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
    "Prog": "Programming",
    "Bus": "business",
    "Heal": "Health",
    "Block": "Blockchain",
    "Othr": "Other",
    "Own": "Own",
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
