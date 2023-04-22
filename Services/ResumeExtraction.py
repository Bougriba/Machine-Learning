import spacy

from Resources import DEGREES_IMPORTANCE
from spacy.lang.en import English
from spacy.lang.fr import French
import PyPDF2
from langdetect import detect


class ResumeExtraction:

    def __init__(self, skills_patterns_path, majors_patterns_path, degrees_patterns_path, resume_path):
        self.resume = resume_path
        self.skills_patterns_path = skills_patterns_path
        self.majors_patterns_path = majors_patterns_path
        self.degrees_patterns_path = degrees_patterns_path
        self.degrees_importance = DEGREES_IMPORTANCE


    @staticmethod
    def match_majors_by_spacy(self, resume):
        language = detect(resume)
        if language == "en":
            nlp = English()
        else:
            nlp = French()
        # Add the pattern to the matcher
        patterns_path = self.majors_patterns_path
        ruler = nlp.add_pipe("entity_ruler")
        ruler.from_disk(patterns_path)
        # Process some text
        doc1 = nlp(resume)
        acceptable_majors = []
        for ent in doc1.ents:
            labels_parts = ent.label_.split('|')
            if labels_parts[0] == 'MAJOR':
                if labels_parts[2].replace('-', ' ') not in acceptable_majors:
                    acceptable_majors.append(labels_parts[2].replace('-', ' '))
                if labels_parts[2].replace('-', ' ') not in acceptable_majors:
                    acceptable_majors.append(labels_parts[2].replace('-', ' '))
        return acceptable_majors

    @staticmethod
    def match_degrees_by_spacy(self, resume):
        language = detect(resume)
        if language == "en":
            nlp = English()
        else:
            nlp = French()
        # Add the pattern to the matcher
        patterns_path = self.degrees_patterns_path
        ruler = nlp.add_pipe("entity_ruler")
        ruler.from_disk(patterns_path)
        # Process some text
        doc1 = nlp(resume)
        degree_levels = []
        for ent in doc1.ents:
            labels_parts = ent.label_.split('|')
            if labels_parts[0] == 'DEGREE':
                print((ent.text, ent.label_))
                if labels_parts[1] not in degree_levels:
                    degree_levels.append(labels_parts[1])
        return degree_levels

    @staticmethod
    def match_skills_by_spacy(self, resume):
        language = detect(resume)
        if language == "en":
            nlp = English()
        else:
            nlp = French()
        patterns_path = self.skills_patterns_path
        ruler = nlp.add_pipe("entity_ruler")
        ruler.from_disk(patterns_path)
        # Process some text
        doc1 = nlp(resume)
        resume_skills = []
        for ent in doc1.ents:
            labels_parts = ent.label_.split('|')
            if labels_parts[0] == 'SKILL':
                print((ent.text, ent.label_))
                if labels_parts[1].replace('-', ' ') not in resume_skills:
                    resume_skills.append(labels_parts[1].replace('-', ' '))
        return resume_skills

    @staticmethod
    def get_minimum_degree(self, degrees):
        """get the minimum degree that the candidate has"""
        d = {degree: self.degrees_importance[degree] for degree in degrees}
        return min(d, key=d.get)


    def extract_entities(self, resume_path):
        # read resume text from pdf
        with open(resume_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            resume = ''
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                resume += page.extract_text()
        lang = detect(resume)
        # recognize and extract entities
        resume_info = {'degrees': "", 'Acceptable majors': "", 'Skills': ""}
        resume = resume.replace('. ', ' ')
        degrees = self.match_degrees_by_spacy(self, resume)
        resume_info['degrees']=degrees
        resume_info['Acceptable majors'] = self.match_majors_by_spacy(self, resume)
        resume_info['Skills'] = self.match_skills_by_spacy(self, resume)
        return resume_info
