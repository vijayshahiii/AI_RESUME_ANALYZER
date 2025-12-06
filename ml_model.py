import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

JOB_ROLES_DATABASE = {
    'Full Stack Developer': {
        'keywords': ['PYTHON','JAVASCRIPT','REACT','NODE','SQL','API','FRONTEND','BACKEND','HTML','CSS','DJANGO','FLASK','EXPRESS','MONGODB','POSTGRESQL'],
        'weight': 1.2
    },
    'Data Scientist': {
        'keywords': ['PYTHON','MACHINE LEARNING','DEEP LEARNING','TENSORFLOW','PYTORCH','PANDAS','NUMPY','STATISTICS','SQL','VISUALIZATION','R','JUPYTER'],
        'weight': 1.3
    },
    'Backend Engineer': {
        'keywords': ['PYTHON','JAVA','API','REST','DATABASE','SQL','SERVER','MICROSERVICES','SPRING','NODE','GOLANG','REDIS','KAFKA'],
        'weight': 1.1
    },
    'Frontend Developer': {
        'keywords': ['JAVASCRIPT','REACT','VUE','ANGULAR','CSS','HTML','UI','UX','TYPESCRIPT','WEBPACK','SASS','RESPONSIVE'],
        'weight': 1.0
    },
    'DevOps Engineer': {
        'keywords': ['DOCKER','KUBERNETES','CI/CD','AWS','AZURE','LINUX','JENKINS','TERRAFORM','ANSIBLE','MONITORING','GIT','BASH'],
        'weight': 1.4
    },
    'Mobile Developer': {
        'keywords': ['REACT NATIVE','FLUTTER','IOS','ANDROID','SWIFT','KOTLIN','MOBILE','APP','FIREBASE','XCODE'],
        'weight': 1.1
    },
    'Machine Learning Engineer': {
        'keywords': ['MACHINE LEARNING','DEEP LEARNING','TENSORFLOW','PYTORCH','PYTHON','NEURAL NETWORKS','NLP','COMPUTER VISION','AWS','DOCKER'],
        'weight': 1.5
    },
    'Cloud Architect': {
        'keywords': ['AWS','AZURE','GCP','CLOUD','INFRASTRUCTURE','SERVERLESS','LAMBDA','KUBERNETES','TERRAFORM','ARCHITECTURE'],
        'weight': 1.3
    }
}

ACTION_VERBS = [
    'ACHIEVED','IMPROVED','INCREASED','DECREASED','REDUCED','LED','MANAGED','DEVELOPED','CREATED',
    'IMPLEMENTED','DESIGNED','OPTIMIZED','LAUNCHED','BUILT','DELIVERED','ENHANCED','STREAMLINED',
    'AUTOMATED','COLLABORATED'
]

RESUME_SECTIONS = ['EXPERIENCE','EDUCATION','SKILLS','PROJECTS','CERTIFICATIONS']


class ResumeAnalyzerML:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')

    def calculate_resume_score(self, text):
        t = text.lower()
        score = 0

        sections = sum(10 if s in t else 0 for s in RESUME_SECTIONS)
        score += min(sections, 30)

        numbers = len(re.findall(r'\d+%|\d+\+|\d+k|\d+m|\d+x|increased.*\d+|improved.*\d+|reduced.*\d+', t))
        score += min(numbers * 4, 20)

        action_count = sum(1 for v in ACTION_VERBS if v.lower() in t)
        score += min(action_count * 1.5, 15)

        wc = len(text.split())
        if 400 <= wc <= 800:
            score += 10
        elif 300 <= wc < 400 or 800 < wc <= 1000:
            score += 7
        elif wc > 200:
            score += 4

        contact = ['email','@','phone','linkedin','github','portfolio']
        contact_score = sum(2 if c in t else 0 for c in contact[:3])
        score += min(contact_score, 5)

        all_skills = set()
        for r in JOB_ROLES_DATABASE.values():
            all_skills.update(r['keywords'])

        skill_match = sum(1 for s in all_skills if s.lower() in t)
        score += min(skill_match * 1.5, 20)

        return min(int(score), 100)

    def match_job_roles(self, text):
        t = text.lower()
        roles = []
        for name, data in JOB_ROLES_DATABASE.items():
            k = data['keywords']
            w = data['weight']
            m = sum(1 for skill in k if skill.lower() in t)
            base = (m / len(k)) * 100
            final = min(base * w, 100)
            if final > 15:
                roles.append({
                    'role': name,
                    'match': round(final, 1),
                    'matched_skills': m,
                    'total_skills': len(k)
                })
        roles.sort(key=lambda x: x['match'], reverse=True)
        return roles

    def extract_skills(self, text):
        t = text.lower()
        all_skills = set()
        for r in JOB_ROLES_DATABASE.values():
            all_skills.update(r['keywords'])

        found = sorted([s for s in all_skills if s.lower() in t])
        missing = sorted([s for s in all_skills if s.lower() not in t])

        important = []
        for r in JOB_ROLES_DATABASE.values():
            for s in r['keywords'][:5]:
                if s in missing and s not in important:
                    important.append(s)

        return {
            'found': found[:15],
            'missing': important[:10]
        }

    def generate_strengths(self, text, score):
        t = text.lower()
        strengths = []

        if sum(1 for s in RESUME_SECTIONS if s.lower() in t) >= 4:
            strengths.append('✓ Well-structured resume')

        achievements = len(re.findall(r'\d+%|\d+\+', text))
        if achievements >= 3:
            strengths.append(f'✓ Strong achievements ({achievements})')

        acts = sum(1 for v in ACTION_VERBS if v.lower() in t)
        if acts >= 8:
            strengths.append(f'✓ Good action word usage ({acts})')

        wc = len(text.split())
        if 400 <= wc <= 800:
            strengths.append(f'✓ Good resume length ({wc} words)')

        all_skills = set()
        for r in JOB_ROLES_DATABASE.values():
            all_skills.update(r['keywords'])
        skill_count = sum(1 for s in all_skills if s.lower() in t)
        if skill_count >= 10:
            strengths.append(f'✓ Strong technical skills ({skill_count})')

        if 'linkedin' in t or 'github' in t:
            strengths.append('✓ Professional links included')

        return strengths if strengths else ['Resume needs improvement']

    def generate_improvements(self, text, score):
        t = text.lower()
        imp = []

        achievements = len(re.findall(r'\d+%|\d+\+', text))
        if achievements < 3:
            imp.append('Add measurable achievements')

        acts = sum(1 for v in ACTION_VERBS if v.lower() in t)
        if acts < 6:
            imp.append('Use more action words')

        wc = len(text.split())
        if wc < 300:
            imp.append('Increase resume size')
        elif wc > 1000:
            imp.append('Reduce resume size')

        if 'certification' not in t and 'certified' not in t:
            imp.append('Add certifications')

        all_skills = set()
        for r in JOB_ROLES_DATABASE.values():
            all_skills.update(r['keywords'])
        sc = sum(1 for s in all_skills if s.lower() in t)
        if sc < 8:
            imp.append('Add more skills')

        if 'linkedin' not in t and 'github' not in t:
            imp.append('Add LinkedIn or GitHub')

        if 'project' not in t:
            imp.append('Add projects')

        if not any(x in t for x in ['led','managed','mentored','collaborated']):
            imp.append('Add teamwork/leadership experience')

        return imp[:6]

    def analyze_complete(self, text):
        score = self.calculate_resume_score(text)
        roles = self.match_job_roles(text)
        skills = self.extract_skills(text)
        strengths = self.generate_strengths(text, score)
        improvements = self.generate_improvements(text, score)
        return {
            'score': score,
            'matched_roles': roles,
            'skills': skills,
            'strengths': strengths,
            'improvements': improvements
        }
