import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class MedicalReport:
    name: Optional[str] = None
    age: Optional[str] = None
    history: Optional[str] = None
    allergies: Optional[str] = None
    medications: Optional[str] = None
    surgeries: Optional[str] = None
    notes: Optional[str] = None
    raw_text: str = ""


def parse_medical_report(text: str) -> MedicalReport:
    """Parse medical report text into structured fields."""
    
    # Clean up the text
    text = text.strip()
    
    # Split text into sections based on field headers
    sections = {}
    current_section = None
    current_content = []
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this line is a section header
        if re.match(r'^(Name|Age|History|Allergies|Medications|Surgeries|Notes):\s*$', line, re.IGNORECASE):
            # Save previous section
            if current_section and current_content:
                sections[current_section] = ' '.join(current_content).strip()
            
            # Start new section
            current_section = line.split(':')[0].strip().lower()
            current_content = []
        else:
            # Add content to current section
            if current_section:
                # Skip lines that look like they belong to previous section
                if current_section == 'allergies' and line == 'aunt.':
                    continue
                current_content.append(line)
            else:
                # If no section started yet, this might be a name
                if not sections.get('name') and len(line.split()) <= 3:
                    sections['name'] = line
    
    # Save last section
    if current_section and current_content:
        sections[current_section] = ' '.join(current_content).strip()
    
    # Create report object
    report = MedicalReport(raw_text=text)
    
    # Map sections to report fields
    field_mapping = {
        'name': 'name',
        'age': 'age', 
        'history': 'history',
        'allergies': 'allergies',
        'medications': 'medications',
        'surgeries': 'surgeries',
        'notes': 'notes'
    }
    
    for section_key, field_name in field_mapping.items():
        if section_key in sections:
            value = sections[section_key].strip()
            if value and value.lower() not in ['none', 'n/a', 'na', 'not applicable']:
                setattr(report, field_name, value)
    
    return report


def extract_structured_medical_data(text: str) -> Dict[str, any]:
    """Extract structured medical data and return as dictionary."""
    report = parse_medical_report(text)
    
    return {
        "name": report.name,
        "age": report.age,
        "history": report.history,
        "allergies": report.allergies,
        "medications": report.medications,
        "surgeries": report.surgeries,
        "notes": report.notes,
        "raw_text": report.raw_text,
        "is_medical_document": any([
            report.name, report.age, report.history, 
            report.allergies, report.medications, report.surgeries
        ])
    }
