import nltk
from textblob import TextBlob, Word
from textblob.wordnet import VERB
from nltk.corpus import wordnet
from sklearn.feature_extraction.text import TfidfVectorizer
import resume_optimizer.keyword_extractor as keyword_extract
from resume_optimizer.utils import *


class ResumeOptimizer:
    """"""
    def __init__(self, job_path, resume_path):
        self.job = read_job(job_path)
        self.resume = read_resume(resume_path)

    @property
    def similarity(self):
        return self._compute_similarity(self.job['description'], self.resume['content'])

    def _compute_similarity(self, textblob_1, textblob_2):
        documents = [str(textblob_1), str(textblob_2)]
        vector = TfidfVectorizer(min_df=1)
        similarity_vector = vector.fit_transform(documents)

        # Convert the sparse matrix to a dense format (array) and access the value
        similarity_matrix = similarity_vector * similarity_vector.T
        return similarity_matrix.toarray()[0, 1]


    def _find_similar_skills(self, target_skill, skills, threshold=0.5):
        list1 = target_skill.split(' ')
        syns1 = set(ss for word in list1 for ss in wordnet.synsets(word))
        scores = {}
        skill_list = []
        for skill in skills:
            scores[skill] = (0, None, None)
            list2 = skill.split(' ')
            syns2 = set(ss for word in list2 for ss in wordnet.synsets(word))
            for s1, s2 in product(syns1, syns2):
                if wordnet.wup_similarity(s1, s2) > scores[skill][0]:
                    scores[skill] = (wordnet.wup_similarity(s1, s2), s1, s2)

            if scores[skill][0] >= threshold:
                skill_list.append((skill, scores[skill][0]))

        return sorted(skill_list, key=lambda x: x[1], reverse=True)

    def _suggest_synonyms(self, target_words, words):
        suggestions = []
        word_synonyms = [(Word(w[0]).get_synsets(pos=VERB), w[1]) for w in target_words]
        for w in words:
            found = False
            synset = (Word(w[0]).get_synsets(pos=VERB), w[1])
            if len(synset[0]):
                for synonym in [s for s in word_synonyms if len(s[0])]:
                    similarity = synset[0][0].path_similarity(synonym[0][0])
                    if similarity == 1.0:
                        found = True
                    if 1.0 > similarity > 0.4 and not found:
                        suggestions.append((synset[0][0].name().split(".")[0], synonym[0][0].name().split(".")[0]))

        return suggestions

    def list_skills(self, job_skills, resume_skills):
        """Generate a skill report comparing job skills and resume skills."""
        output = []
        cell_length = max([len(s[0]) for s in job_skills]) + 2
        row_format = "{{:<{}}}".format(cell_length) * 4
        output.append('SKILL REPORT for {}'.format(self.job['title'].upper()))
        output.append('************\n')
        output.append(row_format.format('Job Ad Skills', 'Relevance', 'Your Skills', 'Relevance'))
        output.append('')
        for i, skill in enumerate(job_skills):
            if i < len(resume_skills):
                output.append(row_format.format(skill[0].upper(), skill[1], resume_skills[i][0].upper(), resume_skills[i][1]))
            else:
                output.append(row_format.format(skill[0].upper(), skill[1], '', ''))
        return "\n".join(output)

    def list_similar_skills(self, target_skill, number_to_return=3):
        """Generate suggestions for similar skills."""
        output = []
        similar_skills = self._find_similar_skills(target_skill, [rs[0] for rs in self.resume['skills']])
        for s in similar_skills[:min(number_to_return, len(similar_skills))]:
            output.append('Can you modify {} to use {}?'.format(s[0].upper(), target_skill.upper()))
        return "\n".join(output)

    def match_skills(self):
        """Generate a report of matching skills between the job and the resume."""
        output = []
        all_skills = get_all_skills()
        rake = keyword_extract.KeywordExtractor()
        resume_skills = [s for s in rake.extract(str(self.resume['content']), incl_scores=True) if s[0] in all_skills]
        job_skills = [s for s in rake.extract(str(self.job['description']), incl_scores=True) if s[0] in all_skills]
        matched_skills = [s for s in job_skills if s[0] in [rs[0] for rs in resume_skills]]
        cell_length = max([len(s[0]) for s in job_skills]) + 2
        row_format = "{{:<{}}}".format(cell_length) * 3
        output.append('\nMATCHING SKILLS')
        output.append('***************\n')
        output.append(row_format.format('Matching Skill', 'Job Relevance', 'Your Relevance'))
        for i, skill in enumerate(matched_skills):
            resume_importance = [rs[1] for rs in resume_skills if rs[0] == skill[0]][0]
            output.append(row_format.format(skill[0].upper(), skill[1], resume_importance))
        return "\n".join(output)

    def optimize_skills(self):
        """Optimize skills by generating reports and suggestions."""
        output = []
        # Add skill comparison
        output.append(self.list_skills(self.job['skills'], self.resume['skills']))
        # Add missing skill suggestions
        top_missing_skills = [s[0] for s in self.job['skills'] if s[0] not in [rs[0] for rs in self.resume['skills']]][:5]
        output.append('\nMISSING SKILL SUGGESTIONS')
        output.append('*************************\n')
        for skill in top_missing_skills:
            output.append(self.list_similar_skills(skill))
        return "\n".join(output)

    def optimize_acronyms(self):
        """Generate a list of acronyms to use."""
        output = []
        output.append('\nACRONYMS TO USE')
        output.append('****************\n')
        for a in [a[0] for a in self.job['acronyms']]:
            output.append(a)
        return "\n".join(output)

    def optimize_action_words(self):
        """Generate action word suggestions."""
        output = []
        output.append('\nACTION WORD SUGGESTIONS')
        output.append('***********************\n')
        suggestions = self._suggest_synonyms(self.job['actions'], self.resume['actions'])
        for suggestion in suggestions:
            output.append('Can you modify {} to use {}?'.format(suggestion[0].upper(), suggestion[1].upper()))
        return "\n".join(output)

