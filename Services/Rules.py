import ast
from Resources import DEGREES_IMPORTANCE
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class Rules:

    def __init__(self, labels, resumes, jobs):
        self.labels = labels
        self.resumes = resumes
        self.jobs = jobs
        self.degrees_importance = DEGREES_IMPORTANCE

    def modifying_type_resume(self, resumes):
        resumes["Minimum degree level"] = ast.literal_eval(resumes["Minimum degree level"])
        for i in range(len(resumes["Skills"])):
            resumes["Skills"][i] = ast.literal_eval(resumes["Skills"][i])
        return resumes

    def modifying_type_job(self, jobs):
        for i in range(len(jobs["Skills"])):
            jobs["Skills"][i] = ast.literal_eval(jobs["Skills"][i])
        return jobs

    # degree matching
    @staticmethod
    def assign_degree_match(match_scores):
        """calculate a degree matching score"""
        match_score = 0
        if len(match_scores) != 0:
            if max(match_scores) >= 2:
                match_score = 0.5
            elif (max(match_scores) >= 0) and (max(match_scores) < 2):
                match_score = 1
        return match_score

    def degree_matching(self, resumes, jobs):
        """calculate the final degree matching scores between resumes and job description"""
        job_min_degree = self.degrees_importance[jobs['Minimum degree level']]
        match_scores = []
        for j in resumes['degrees']:
             score = self.degrees_importance[j] - job_min_degree
             match_scores.append(score)
        return self.assign_degree_match(match_scores)

    # majors matching
    def get_major_category(self, major):
        """get a major's category"""
        categories = self.labels["MAJOR"].keys()
        for c in categories:
            if major in self.labels["MAJOR"][c]:
                return c

    def get_job_acceptable_majors(self, jobs):
        """get acceptable job majors"""
        job_majors = jobs['Acceptable majors']
        job_majors_categories = []
        for i in job_majors:
            job_majors_categories.append(self.get_major_category(i))
        return job_majors, job_majors_categories

    def get_major_score(self, resumes, jobs):
        """calculate major matching score for one resume"""
        resume_majors = resumes['Acceptable majors']
        job_majors, job_majors_categories = self.get_job_acceptable_majors(jobs)
        major_score = 0
        for r in resume_majors:
            if r in job_majors:
                major_score = 1
                break
            elif self.get_major_category(r) in job_majors_categories:
                major_score = 0.5
        return major_score

    # skills matching
    @staticmethod
    def unique_job_skills(jobs):
        """calculate number of unique skills in the job description"""
        unique_job_skills = []
        for i in jobs['Skills']:
            if i not in unique_job_skills:
                unique_job_skills.append(i)
        num_unique_job_skills = len(unique_job_skills)
        return num_unique_job_skills, unique_job_skills

    def semantic_similarity(self, job, resume):
        model = SentenceTransformer('bert-base-nli-mean-tokens')
        # Encoding:
        score = 0
        sen = job + resume
        sen_embeddings = model.encode(sen)
        for i in range(len(job)):
            if job[i] in resume:
                score += 1
            else:
                if max(cosine_similarity([sen_embeddings[i]], sen_embeddings[len(job):])[0]) >= 0.4:
                    score += max(cosine_similarity([sen_embeddings[i]], sen_embeddings[len(job):])[0])
                    # print(job[i],max(cosine_similarity([sen_embeddings[i]],sen_embeddings[len(job):])[0]),cosine_similarity([sen_embeddings[i]],sen_embeddings[len(job):])[0])
        score = score / len(job)
        return round(score, 2)

    def skills_semantic_matching(self, resumes,job_skills):
        """calculate the skills semantic matching scores between resumes and job description"""
        return self.semantic_similarity(job_skills, resumes['Skills'])

    # calculate matching scores
    def matching_score(self, resumes, jobs):
        # matching degrees
        degree_score = self.degree_matching(resumes, jobs)

        # matching majors
        major_score = self.get_major_score(resumes, jobs)

        # matching skills
        num_unique_job_skills, job_skills = self.unique_job_skills(jobs)
        # matching skills semantically
        skills_score = self.skills_semantic_matching(resumes, job_skills)
        print(degree_score)
        print(major_score)
        print(skills_score)
        final_score = (skills_score + degree_score + major_score) / 3
        return round(final_score, 3)