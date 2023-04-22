import os
from flask import Flask, request
from flask_cors import CORS
from Services.ResumeExtraction import ResumeExtraction
from Services.JobExtraction import JobExtraction
from Services.Rules import Rules
import json

app = Flask(__name__)
CORS(app)

# Define the paths to the entity pattern files and resume file
resume_skills_patterns_path = 'D:/mahdi/Documents/Pinops/Resources/data/skills.jsonl'
resume_majors_patterns_path = 'D:/mahdi/Documents/Pinops/Resources/data/majors.jsonl'
resume_degrees_patterns_path = 'D:/mahdi/Documents/Pinops/Resources/data/degrees.jsonl'


@app.route('/extract_resume_entities', methods=['POST'])
def extract_entities_from_resume():
    # Get the uploaded file from the request
    uploaded_file = request.files['resume']
    # Save the uploaded file to a temporary location
    uploaded_file.save(os.path.join('D:/mahdi/Documents', uploaded_file.filename))
    # Get the path of the saved file
    resume_path = os.path.join('D:/mahdi/Documents', uploaded_file.filename)
    # Extract the resume entities using ResumeExtraction
    resume_extractor = ResumeExtraction(resume_skills_patterns_path, resume_majors_patterns_path,
                                        resume_degrees_patterns_path, resume_path)
    resume_entities = resume_extractor.extract_entities(resume_path)
    # Return the extracted entities as JSON
    return resume_entities



job_skills_patterns_path = 'D:/mahdi/Documents/Pinops/Resources/data/skills.jsonl'
job_majors_patterns_path = 'D:/mahdi/Documents/Pinops/Resources/data/majors.jsonl'
job_degrees_patterns_path = 'D:/mahdi/Documents/Pinops/Resources/data/degrees.jsonl'
@app.route('/score',methods=['POST'])
def SCORE():
    job_description = request.form['job_description']
    job_info_extractor = JobExtraction(job_skills_patterns_path, job_majors_patterns_path, job_degrees_patterns_path,
                                       job_description)

    job_entities = job_info_extractor.extract_entities(job_description)
    degrees=request.form['Degrees']
    skills=request.form['skills']
    Acceptable_Majors=request.form['Acceptable majors']
    ldegrees=degrees.split(',')
    lskills=skills.split(',')
    lmajors=Acceptable_Majors.split(',')
    resume_info = {'degrees': "", 'Acceptable majors': "", 'Skills': ""}
    resume_info['degrees']=ldegrees
    resume_info['Acceptable majors']=lmajors
    resume_info['Skills']=lskills
    with open('D:/mahdi/Documents/Pinops/Resources/data/labels.json') as fp:
        labels = json.load(fp)
    match = Rules(labels, job_entities, resume_info)
    score = match.matching_score(resume_info, job_entities)
    return str(score)


if __name__ == '__main__':
    app.run(port=3002)