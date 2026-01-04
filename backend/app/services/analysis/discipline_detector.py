"""
Multi-Discipline Detector

Detects multiple relevant academic disciplines from an abstract.
Uses keyword matching with weighted scoring and OpenAlex field mappings.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import re


@dataclass
class DetectedDiscipline:
    """A detected academic discipline with confidence score."""
    name: str
    confidence: float  # 0.0 to 1.0
    evidence: List[str]  # Keywords/phrases that led to detection
    openalex_field_id: Optional[str] = None
    openalex_subfield_id: Optional[str] = None  # Subfield name (e.g., "Obstetrics and Gynecology")
    openalex_subfield_numeric_id: Optional[int] = None  # Numeric ID for API filtering (e.g., 2729)


# Discipline keyword mappings with primary (high weight) and secondary (lower weight) terms
DISCIPLINE_KEYWORDS: Dict[str, Dict[str, List[str]]] = {
    "Urology": {
        "primary": [
            "urinary", "bladder", "urology", "urological", "urodynamic", "voiding",
            "incontinence", "overactive bladder", "oab", "prostate", "kidney stone",
            "ureter", "urethra", "cystitis", "micturition", "detrusor", "uroflowmetry"
        ],
        "secondary": [
            "pelvic floor", "nocturia", "benign prostatic", "bph", "urgency"
        ],
    },
    "Gynecology": {
        "primary": [
            "gynecology", "gynecological", "obstetric", "obstetrics", "female reproductive",
            "uterus", "uterine", "ovarian", "ovary", "cervical", "cervix", "menstrual",
            "pregnancy", "pregnant", "labor", "delivery", "prenatal", "maternal",
            "endometriosis", "pcos", "polycystic ovary"
        ],
        "secondary": [
            "pelvic", "reproductive", "fertility", "menopause", "postmenopausal",
            "women's health", "female", "hormonal"
        ],
    },
    "Rheumatology": {
        "primary": [
            "rheumatology", "rheumatological", "fibromyalgia", "arthritis", "rheumatoid",
            "lupus", "sle", "systemic lupus", "autoimmune", "spondylitis", "gout",
            "osteoarthritis", "scleroderma", "vasculitis", "myositis"
        ],
        "secondary": [
            "joint pain", "inflammatory", "rheumatic", "connective tissue",
            "musculoskeletal", "synovitis", "articular"
        ],
    },
    "Pain Medicine": {
        "primary": [
            "chronic pain", "pain management", "analgesic", "nociceptive",
            "neuropathic pain", "pain syndrome", "pain medicine", "algology",
            "central sensitization", "pain clinic", "pain therapy"
        ],
        "secondary": [
            "opioid", "pain relief", "pain assessment", "hyperalgesia",
            "allodynia", "widespread pain", "pain intensity"
        ],
    },
    "Cardiology": {
        "primary": [
            "cardiac", "cardiovascular", "heart", "coronary", "arrhythmia",
            "myocardial", "atrial", "ventricular", "cardiomyopathy", "cardiology",
            "heart failure", "angina", "pericardial", "aortic", "mitral"
        ],
        "secondary": [
            "hypertension", "blood pressure", "ecg", "echocardiography",
            "ejection fraction", "atherosclerosis", "stent", "cabg"
        ],
    },
    "Neurology": {
        "primary": [
            "neurological", "neurology", "brain", "stroke", "cerebral", "epilepsy",
            "seizure", "dementia", "alzheimer", "parkinson", "multiple sclerosis",
            "neuropathy", "encephalitis", "meningitis", "headache", "migraine"
        ],
        "secondary": [
            "cognitive", "motor", "sensory", "spinal cord", "nerve",
            "neurodegenerative", "tremor", "ataxia"
        ],
    },
    "Oncology": {
        "primary": [
            "cancer", "tumor", "tumour", "oncology", "malignant", "carcinoma",
            "lymphoma", "leukemia", "leukaemia", "metastasis", "metastatic",
            "chemotherapy", "radiotherapy", "neoplasm", "sarcoma", "melanoma"
        ],
        "secondary": [
            "biopsy", "staging", "survival rate", "remission", "relapse",
            "immunotherapy", "targeted therapy", "tumor marker"
        ],
    },
    "Endocrinology": {
        "primary": [
            "diabetes", "diabetic", "endocrine", "endocrinology", "thyroid",
            "insulin", "glucose", "metabolic", "hormone", "hormonal",
            "pituitary", "adrenal", "hyperthyroid", "hypothyroid"
        ],
        "secondary": [
            "hba1c", "glycemic", "obesity", "lipid", "cholesterol",
            "testosterone", "estrogen", "cortisol"
        ],
    },
    "Psychiatry": {
        "primary": [
            "psychiatric", "psychiatry", "mental health", "depression", "anxiety",
            "schizophrenia", "bipolar", "psychosis", "psychotic", "ptsd",
            "obsessive compulsive", "ocd", "mood disorder", "antidepressant"
        ],
        "secondary": [
            "psychological", "mood", "cognitive behavioral", "cbt",
            "suicidal", "self-harm", "antipsychotic"
        ],
    },
    "Pulmonology": {
        "primary": [
            "pulmonary", "respiratory", "lung", "bronchial", "asthma", "copd",
            "pneumonia", "pulmonology", "thoracic", "pleural", "bronchitis",
            "emphysema", "fibrosis", "ventilation"
        ],
        "secondary": [
            "oxygen", "spirometry", "dyspnea", "cough", "sputum",
            "bronchoscopy", "chest"
        ],
    },
    "Gastroenterology": {
        "primary": [
            "gastroenterology", "gastrointestinal", "hepatic", "liver", "bowel",
            "colon", "intestinal", "stomach", "esophageal", "pancreatic",
            "cirrhosis", "hepatitis", "ibd", "crohn", "colitis", "celiac"
        ],
        "secondary": [
            "endoscopy", "colonoscopy", "gi", "digestive", "abdominal",
            "constipation", "diarrhea"
        ],
    },
    "Nephrology": {
        "primary": [
            "renal", "kidney", "nephrology", "nephrotic", "dialysis",
            "hemodialysis", "glomerular", "ckd", "acute kidney", "gfr",
            "proteinuria", "nephritis", "transplant kidney"
        ],
        "secondary": [
            "creatinine", "urea", "electrolyte", "uremic"
        ],
    },
    "Infectious Disease": {
        "primary": [
            "infectious disease", "infection", "bacterial", "viral", "fungal",
            "hiv", "aids", "tuberculosis", "sepsis", "antibiotic", "antimicrobial",
            "covid", "coronavirus", "influenza", "hepatitis b", "hepatitis c"
        ],
        "secondary": [
            "pathogen", "microbiome", "resistance", "transmission",
            "epidemic", "pandemic", "outbreak"
        ],
    },
    "Immunology": {
        "primary": [
            "immunology", "immune", "immunological", "autoimmune", "antibody",
            "immunotherapy", "immunodeficiency", "cytokine", "t-cell", "b-cell",
            "allergy", "allergic", "hypersensitivity", "immunosuppression"
        ],
        "secondary": [
            "inflammation", "inflammatory", "interleukin", "interferon",
            "innate immunity", "adaptive immunity"
        ],
    },
    "Pediatrics": {
        "primary": [
            "pediatric", "paediatric", "pediatrics", "child", "children",
            "infant", "neonate", "neonatal", "adolescent", "developmental",
            "childhood", "newborn", "preterm", "premature"
        ],
        "secondary": [
            "growth", "puberty", "vaccination", "congenital", "pediatrician"
        ],
    },
    "Geriatrics": {
        "primary": [
            "geriatric", "elderly", "older adults", "aging", "ageing",
            "frailty", "geriatrics", "gerontology", "dementia", "falls"
        ],
        "secondary": [
            "polypharmacy", "sarcopenia", "longevity", "centenarian"
        ],
    },
    "Pharmacology": {
        "primary": [
            "pharmacology", "pharmacological", "drug", "medication", "therapeutic",
            "pharmacokinetic", "pharmacodynamic", "dosing", "adverse effect",
            "drug interaction", "clinical trial", "phase i", "phase ii", "phase iii"
        ],
        "secondary": [
            "efficacy", "safety", "tolerability", "bioavailability"
        ],
    },
    "Emergency Medicine": {
        "primary": [
            "emergency", "acute", "trauma", "critical care", "icu",
            "intensive care", "resuscitation", "triage", "emergency department"
        ],
        "secondary": [
            "stabilization", "urgent", "life-threatening"
        ],
    },
    "Dermatology": {
        "primary": [
            "dermatology", "dermatological", "skin", "cutaneous", "psoriasis",
            "eczema", "dermatitis", "melanoma", "acne", "alopecia"
        ],
        "secondary": [
            "rash", "pruritus", "topical", "phototherapy"
        ],
    },
    "Ophthalmology": {
        "primary": [
            "ophthalmology", "ophthalmic", "eye", "ocular", "retinal", "retina",
            "glaucoma", "cataract", "macular", "corneal", "vision", "blindness"
        ],
        "secondary": [
            "intraocular", "visual acuity", "fundus", "vitreous"
        ],
    },
    "Orthopedics": {
        "primary": [
            "orthopedic", "orthopaedic", "bone", "fracture", "joint replacement",
            "spine", "spinal", "musculoskeletal", "tendon", "ligament",
            "arthroplasty", "osteotomy", "scoliosis"
        ],
        "secondary": [
            "mobility", "rehabilitation", "prosthesis", "implant"
        ],
    },
    "Surgery": {
        "primary": [
            "surgery", "surgical", "operative", "laparoscopic", "endoscopic",
            "minimally invasive", "robotic surgery", "resection", "excision",
            "transplant", "bypass"
        ],
        "secondary": [
            "postoperative", "perioperative", "anesthesia", "wound"
        ],
    },
    "Radiology": {
        "primary": [
            "radiology", "radiological", "imaging", "ct scan", "mri", "pet",
            "ultrasound", "x-ray", "mammography", "fluoroscopy"
        ],
        "secondary": [
            "contrast", "diagnostic imaging", "interventional radiology"
        ],
    },
    "Epidemiology": {
        "primary": [
            "epidemiology", "epidemiological", "prevalence", "incidence",
            "population-based", "cohort", "case-control", "risk factor",
            "odds ratio", "relative risk", "hazard ratio"
        ],
        "secondary": [
            "surveillance", "outbreak", "mortality", "morbidity"
        ],
    },
    "Public Health": {
        "primary": [
            "public health", "health policy", "prevention", "screening",
            "health promotion", "community health", "health disparities",
            "social determinants", "vaccination program"
        ],
        "secondary": [
            "health education", "intervention", "health outcomes"
        ],
    },
}


# OpenAlex field/subfield mappings with numeric IDs
# Numeric IDs are required for accurate filtering in OpenAlex API
OPENALEX_FIELD_MAPPING: Dict[str, Dict[str, str]] = {
    "Urology": {"field": "Medicine", "subfield": "Urology", "subfield_id": 2746},
    "Gynecology": {"field": "Medicine", "subfield": "Obstetrics and Gynecology", "subfield_id": 2729},
    "Rheumatology": {"field": "Medicine", "subfield": "Rheumatology", "subfield_id": 2745},
    "Pain Medicine": {"field": "Medicine", "subfield": "Anesthesiology and Pain Medicine", "subfield_id": 2700},
    "Cardiology": {"field": "Medicine", "subfield": "Cardiology and Cardiovascular Medicine", "subfield_id": 2705},
    "Neurology": {"field": "Medicine", "subfield": "Neurology", "subfield_id": 2728},
    "Oncology": {"field": "Medicine", "subfield": "Oncology", "subfield_id": 2730},
    "Endocrinology": {"field": "Medicine", "subfield": "Endocrinology, Diabetes and Metabolism", "subfield_id": 2712},
    "Psychiatry": {"field": "Medicine", "subfield": "Psychiatry and Mental Health", "subfield_id": 2738},
    "Pulmonology": {"field": "Medicine", "subfield": "Pulmonary and Respiratory Medicine", "subfield_id": 2740},
    "Gastroenterology": {"field": "Medicine", "subfield": "Gastroenterology", "subfield_id": 2715},
    "Nephrology": {"field": "Medicine", "subfield": "Nephrology", "subfield_id": 2727},
    "Infectious Disease": {"field": "Medicine", "subfield": "Infectious Diseases", "subfield_id": 2725},
    "Immunology": {"field": "Medicine", "subfield": "Immunology", "subfield_id": 2723},
    "Pediatrics": {"field": "Medicine", "subfield": "Pediatrics, Perinatology and Child Health", "subfield_id": 2735},
    "Geriatrics": {"field": "Medicine", "subfield": "Geriatrics and Gerontology", "subfield_id": 2718},
    "Pharmacology": {"field": "Medicine", "subfield": "Pharmacology", "subfield_id": 2736},
    "Emergency Medicine": {"field": "Medicine", "subfield": "Emergency Medicine", "subfield_id": 2711},
    "Dermatology": {"field": "Medicine", "subfield": "Dermatology", "subfield_id": 2708},
    "Ophthalmology": {"field": "Medicine", "subfield": "Ophthalmology", "subfield_id": 2731},
    "Orthopedics": {"field": "Medicine", "subfield": "Orthopedics and Sports Medicine", "subfield_id": 2732},
    "Surgery": {"field": "Medicine", "subfield": "Surgery", "subfield_id": 2746},
    "Radiology": {"field": "Medicine", "subfield": "Radiology, Nuclear Medicine and Imaging", "subfield_id": 2741},
    "Epidemiology": {"field": "Medicine", "subfield": "Epidemiology", "subfield_id": 2713},
    "Public Health": {"field": "Medicine", "subfield": "Public Health, Environmental and Occupational Health", "subfield_id": 2739},
}


class MultiDisciplineDetector:
    """Detects multiple academic disciplines from text."""

    def __init__(self, min_confidence: float = 0.15):
        """
        Initialize the detector.

        Args:
            min_confidence: Minimum confidence threshold for including a discipline.
        """
        self.min_confidence = min_confidence

    def detect(
        self,
        title: str,
        abstract: str,
        keywords: Optional[List[str]] = None
    ) -> List[DetectedDiscipline]:
        """
        Detect all relevant disciplines from the input.

        Args:
            title: Article title.
            abstract: Article abstract.
            keywords: Optional list of author-provided keywords.

        Returns:
            List of detected disciplines, sorted by confidence (descending).
        """
        # Combine all text for analysis
        keywords_text = " ".join(keywords or [])
        text = f"{title} {abstract} {keywords_text}".lower()

        disciplines: List[DetectedDiscipline] = []

        for discipline_name, keyword_sets in DISCIPLINE_KEYWORDS.items():
            confidence, evidence = self._calculate_confidence(text, keyword_sets)

            if confidence >= self.min_confidence:
                openalex_info = OPENALEX_FIELD_MAPPING.get(discipline_name, {})
                disciplines.append(DetectedDiscipline(
                    name=discipline_name,
                    confidence=confidence,
                    evidence=evidence,
                    openalex_field_id=openalex_info.get("field"),
                    openalex_subfield_id=openalex_info.get("subfield"),
                    openalex_subfield_numeric_id=openalex_info.get("subfield_id"),
                ))

        # Sort by confidence descending
        disciplines.sort(key=lambda x: x.confidence, reverse=True)

        # Normalize confidence scores relative to top discipline
        if disciplines:
            max_conf = disciplines[0].confidence
            for d in disciplines:
                d.confidence = round(d.confidence / max_conf, 2)

        return disciplines

    def _calculate_confidence(
        self,
        text: str,
        keyword_sets: Dict[str, List[str]]
    ) -> tuple:
        """
        Calculate confidence score based on keyword matches.

        Args:
            text: Lowercase text to search.
            keyword_sets: Dictionary with 'primary' and 'secondary' keyword lists.

        Returns:
            Tuple of (confidence score, list of matched keywords).
        """
        score = 0.0
        evidence: List[str] = []

        # Primary keywords (high weight)
        for keyword in keyword_sets.get("primary", []):
            if self._keyword_in_text(keyword, text):
                score += 0.3
                evidence.append(keyword)

        # Secondary keywords (lower weight)
        for keyword in keyword_sets.get("secondary", []):
            if self._keyword_in_text(keyword, text):
                score += 0.15
                evidence.append(keyword)

        # Cap at 1.0 before normalization
        return min(score, 1.0), evidence

    def _keyword_in_text(self, keyword: str, text: str) -> bool:
        """
        Check if keyword appears in text with word boundary handling.

        For multi-word phrases, do simple contains check.
        For single words, use word boundary to avoid partial matches.
        """
        keyword_lower = keyword.lower()
        if " " in keyword_lower:
            # Multi-word phrase: simple contains
            return keyword_lower in text
        else:
            # Single word: use word boundary pattern
            pattern = rf"\b{re.escape(keyword_lower)}\b"
            return bool(re.search(pattern, text))

    def get_primary_discipline(
        self,
        disciplines: List[DetectedDiscipline]
    ) -> Optional[DetectedDiscipline]:
        """Get the highest-confidence discipline."""
        return disciplines[0] if disciplines else None

    def get_cross_discipline_fields(
        self,
        disciplines: List[DetectedDiscipline],
        max_fields: int = 3
    ) -> List[str]:
        """
        Get OpenAlex subfields for cross-discipline search.

        Args:
            disciplines: List of detected disciplines.
            max_fields: Maximum number of fields to return.

        Returns:
            List of OpenAlex subfield names.
        """
        fields: List[str] = []
        for d in disciplines[:max_fields]:
            if d.openalex_subfield_id:
                fields.append(d.openalex_subfield_id)
        return fields

    def to_dict_list(self, disciplines: List[DetectedDiscipline]) -> List[Dict]:
        """
        Convert detected disciplines to dictionary format for API response.

        Args:
            disciplines: List of detected disciplines.

        Returns:
            List of dictionaries suitable for JSON serialization.
        """
        return [
            {
                "name": d.name,
                "confidence": d.confidence,
                "evidence": d.evidence,
                "openalex_field_id": d.openalex_field_id,
                "openalex_subfield_id": d.openalex_subfield_id,
                "openalex_subfield_numeric_id": d.openalex_subfield_numeric_id,
            }
            for d in disciplines
        ]


# Convenience function for quick detection
def detect_disciplines(
    title: str,
    abstract: str,
    keywords: Optional[List[str]] = None,
    min_confidence: float = 0.15
) -> List[DetectedDiscipline]:
    """
    Quick function to detect disciplines from article text.

    Args:
        title: Article title.
        abstract: Article abstract.
        keywords: Optional list of keywords.
        min_confidence: Minimum confidence threshold.

    Returns:
        List of detected disciplines sorted by confidence.
    """
    detector = MultiDisciplineDetector(min_confidence=min_confidence)
    return detector.detect(title, abstract, keywords)
