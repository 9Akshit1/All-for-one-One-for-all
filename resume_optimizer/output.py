import nltk
nltk.download('wordnet')
nltk.download('brown')
nltk.download('averaged_perceptron_tagger_eng')
import os
import resume_optimizer.utils
import resume_optimizer.keyword_extractor
import resume_optimizer.resume_optimizer as r_o

def run(job_file, resume_file):
    """Analyzes a job description and resume and prints a report. Requires two command line arguments.

    Args:
        job_file_path (str): path to job description text file
        resume_path (str): path to resume text file
    """
    ro = r_o.ResumeOptimizer(job_file, resume_file)
    
    return ["Similarity Score: " + str(ro.similarity), ro.optimize_skills(), ro.list_similar_skills('design patterns', number_to_return=5), ro.optimize_acronyms(), ro.optimize_action_words()]

#run('resume_optimizer/data/jobs/web_and_db_developer.txt', 'resume_optimizer/data/resumes/pjb_resume.txt')