import re
import PyPDF2
import pandas as pd


class ResumeInfoExtraction:

    def __init__(self, skills_patterns_path, majors_patterns_path, degrees_patterns_path):
        self.skills_patterns_path = skills_patterns_path
        self.majors_patterns_path = majors_patterns_path
        self.degrees_patterns_path = degrees_patterns_path

    @staticmethod
    def match_majors_by_regex(text, majors_patterns):
        majors = []
        for pattern in majors_patterns:
            match = re.findall(pattern, text, re.IGNORECASE)
            if match:
                majors.extend(match)
        majors = list(set(majors))
        return majors

    @staticmethod
    def match_degrees_by_regex(text, degrees_patterns):
        degrees = []
        for pattern in degrees_patterns:
            match = re.findall(pattern, text, re.IGNORECASE)
            if match:
                degrees.extend(match)
        degrees = list(set(degrees))
        return degrees

    @staticmethod
    def match_skills_by_regex(text, skills_patterns):
        skills = []
        for pattern in skills_patterns:
            match = re.findall(pattern, text, re.IGNORECASE)
            if match:
                skills.extend(match)
        skills = list(set(skills))
        return skills

    def extract_entities(self, resume_path):
        # read resume text from pdf
        with open(resume_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            resume_text = ''
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                resume_text += page.extract_text()
        # recognize and extract entities
        degrees_patterns = open(self.degrees_patterns_path).read().splitlines()
        majors_patterns = open(self.majors_patterns_path).read().splitlines()
        skills_patterns = open(self.skills_patterns_path).read().splitlines()
        degrees = self.match_degrees_by_regex(resume_text, degrees_patterns)
        majors = self.match_majors_by_regex(resume_text, majors_patterns)
        skills = self.match_skills_by_regex(resume_text, skills_patterns)
        print(resume_text)
        # store extracted information in a DataFrame
        resume_info = pd.DataFrame(columns=['Degree level', 'Major', 'Skill'])
        resume_info = resume_info.append({
            'Degree level': ' '.join(degrees),
            'Major': ', '.join(majors),
            'Skill': ', '.join(skills)
        }, ignore_index=True)
        return resume_info
