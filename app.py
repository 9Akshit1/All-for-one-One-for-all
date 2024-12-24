import sys
import os

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag, ne_chunk
import re
from difflib import SequenceMatcher
from collections import defaultdict
# Ensure the necessary NLTK resources are available
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('maxent_ne_chunker_tab')
nltk.download('words')

import shutil
import subprocess
import time
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, pyqtSignal, QEvent, QFile, QThread
from PyQt6.QtGui import QFont, QColor, QPalette, QKeySequence, QImageReader, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QWidget, QFileDialog, QLineEdit, QTextEdit, QComboBox, QScrollArea, QFormLayout, QProgressBar
)

from competition_finder.competition_finder import find_competitions
from resume_optimizer.output import run  

# Define a dark theme color palette
def apply_dark_theme(app):
    dark_palette = app.palette()
    dark_palette.setColor(dark_palette.ColorRole.Window, Qt.GlobalColor.black)
    dark_palette.setColor(dark_palette.ColorRole.WindowText, Qt.GlobalColor.white)
    dark_palette.setColor(dark_palette.ColorRole.Base, Qt.GlobalColor.darkGray)
    dark_palette.setColor(dark_palette.ColorRole.AlternateBase, Qt.GlobalColor.black)
    dark_palette.setColor(dark_palette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    dark_palette.setColor(dark_palette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    dark_palette.setColor(dark_palette.ColorRole.Text, Qt.GlobalColor.white)
    dark_palette.setColor(dark_palette.ColorRole.Button, Qt.GlobalColor.darkGray)
    dark_palette.setColor(dark_palette.ColorRole.ButtonText, Qt.GlobalColor.white)
    dark_palette.setColor(dark_palette.ColorRole.BrightText, Qt.GlobalColor.red)
    dark_palette.setColor(dark_palette.ColorRole.Highlight, Qt.GlobalColor.darkCyan)
    dark_palette.setColor(dark_palette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(dark_palette)

# Main Application Class
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Helper App")
        self.setGeometry(100, 100, 1200, 1000)  # Set the app size to be smaller
        self.setStyleSheet("background-color: #2E2E2E;")  # Set dark background color

        # Home Screen Setup
        self.home_widget = QWidget()
        self.setCentralWidget(self.home_widget)

        # Layout for Home Screen
        layout = QVBoxLayout()

        title_label = QLabel("Welcome to the Student Helper App")
        title_label.setFont(QFont("Arial", 20))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Buttons for each functionality with updated style
        profile_comparator_btn = QPushButton("Profile Comparator")
        profile_comparator_btn.setStyleSheet("""
            QPushButton {
                background-color: lightblue;
                color: white;
                border-radius: 15px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
            }
        """)
        profile_comparator_btn.clicked.connect(self.show_profile_comparator)
        layout.addWidget(profile_comparator_btn)

        competition_finder_btn = QPushButton("Competition Finder")
        competition_finder_btn.setStyleSheet("""
            QPushButton {
                background-color: lightblue;
                color: white;
                border-radius: 15px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
            }
        """)
        competition_finder_btn.clicked.connect(self.show_competition_finder)
        layout.addWidget(competition_finder_btn)

        resume_optimizer_btn = QPushButton("Resume Optimizer")
        resume_optimizer_btn.setStyleSheet("""
            QPushButton {
                background-color: lightblue;
                color: white;
                border-radius: 15px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
            }
        """)
        resume_optimizer_btn.clicked.connect(self.show_resume_optimizer)
        layout.addWidget(resume_optimizer_btn)

        application_writer_btn = QPushButton("Application Writer")
        application_writer_btn.setStyleSheet("""
            QPushButton {
                background-color: lightblue;
                color: white;
                border-radius: 15px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
            }
        """)
        application_writer_btn.clicked.connect(self.show_application_writer)
        layout.addWidget(application_writer_btn)

        # Add the result area within a scrollable widget
        self.result_area = QScrollArea()
        self.result_area.setWidgetResizable(True)  # Make it resizable
        layout.addWidget(self.result_area)

        # Set layout to home screen
        self.home_widget.setLayout(layout)

    # Functionality Windows
    def show_profile_comparator(self):
        self.profile_comparator_window = ProfileComparator(self.geometry().getRect())
        self.profile_comparator_window.show()

    def show_competition_finder(self):
        self.competition_finder_window = CompetitionFinder(self.geometry().getRect())
        self.competition_finder_window.show()

    def show_resume_optimizer(self):
        self.resume_optimizer_window = ResumeOptimizer(self.geometry().getRect())
        self.resume_optimizer_window.show()

    def show_application_writer(self):
        self.application_writer_window = ApplicationWriter(self.geometry().getRect())
        self.application_writer_window.show()

# Profile Comparator Window
class ProfileComparator(QWidget):
    def __init__(self, parent_size):
        super().__init__()
        self.setWindowTitle("Profile Comparator")
        self.setGeometry(*parent_size)
        self.setStyleSheet("background-color: #2E2E2E;")
        layout = QVBoxLayout()

        # Inputs for profile comparison
        layout.addWidget(QLabel("Enter School"))
        self.school_input = QLineEdit()
        layout.addWidget(self.school_input)

        layout.addWidget(QLabel("Enter Awards"))
        self.awards_input = QTextEdit()
        layout.addWidget(self.awards_input)

        layout.addWidget(QLabel("Enter Work/Volunteer Experience"))
        self.work_input = QTextEdit()
        layout.addWidget(self.work_input)

        # Additional Input Fields
        layout.addWidget(QLabel("Enter Licenses & Certifications"))
        self.certifications_input = QTextEdit()
        layout.addWidget(self.certifications_input)

        layout.addWidget(QLabel("Enter Projects"))
        self.projects_input = QTextEdit()
        layout.addWidget(self.projects_input)

        layout.addWidget(QLabel("Enter Skills"))
        self.skills_input = QTextEdit()
        layout.addWidget(self.skills_input)

        layout.addWidget(QLabel("Enter Interests"))
        self.interests_input = QTextEdit()
        layout.addWidget(self.interests_input)

        layout.addWidget(QLabel("Enter University Applying To"))
        self.university_input = QLineEdit()
        layout.addWidget(self.university_input)

        layout.addWidget(QLabel("Enter Major Applying To"))
        self.major_input = QLineEdit()
        layout.addWidget(self.major_input)

        submit_btn = QPushButton("Compare")
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: lightblue;
                color: white;
                border-radius: 15px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
            }
        """)
        submit_btn.clicked.connect(self.display_results)
        layout.addWidget(submit_btn)

        # Scrollable result area
        self.result_area = QScrollArea()
        layout.addWidget(self.result_area)

        self.setLayout(layout)

        # Example dataset of profiles
        self.dataset = [
            {
                "school": "XYZ High School",
                "age": "17",
                "awards": "National Merit Scholar, State Science Fair Runner-Up",
                "work_experience": "Web developer, Fresh Future Foundation                                                                                 August 2024  - PRESENT\nLeveraged React.js, Node.js, HTML, and CSS, to revamp the frontend of organization’s website\nIncreased social media presence by regularly updating Instagram and posting. Made connections.\nSet up events and ideas for the organization. From hackathons to coding/robotics projects.\nReference: Arya Vaidhya  | aryav663@gmail.com\n\nEmbedded C & Arduino Assistant Teacher, OBotz Robotics 			        June 2023 - March 2024\nLead lessons at OBotz Robotics, teaching students about microcontrollers, mechanical and electronic components, Arduino programming, and embedded C through interactive methods\nIncorporated real-world examples and hands-on projects into the curriculum, enabling students to apply theoretical knowledge to practical tasks and problem-solving scenarios\nReference: Cyrilkumar Jithuri  | cyril@ucmasottawa.ca  | (613) 404-5572",
                "certifications": "AP Scholar with Distinction, Certified Lifeguard",
                "projects": "Developed a Mobile App for Homework Tracking \n\nResearch on Renewable Energy Sources",
                "skills": "C++ Programming, Public Speaking, Team Leadership",
                "interests": "Environmental Science, Software Development",
                "university": "University of Waterloo",
                "major": "Environmental Engineering"
            },
            {
                "school": "Lincoln High School",
                "age": "18",
                "awards": "Regional Debate Champion, School Valedictorian",
                "work_experience": "Intern at Local Newspaper, Volunteer at Animal Shelter",
                "certifications": "Journalism Workshop Certificate, Advanced Spanish Language Certification",
                "projects": "Editor of School Newspaper, Organized Charity Drive for Homeless Shelter",
                "skills": "Writing, Critical Thinking, Bilingual in English and Spanish",
                "interests": "Journalism, Animal Welfare",
                "university": "University of Waterloo",
                "major": "Journalism"
            },
            {
                "school": "Central High School",
                "age": "19",
                "awards": "State Track and Field Champion, National Honor Society Member",
                "work_experience": "Assistant Coach for Middle School Track Team, Volunteer at Senior Care Center",
                "certifications": "First Aid and CPR Certified, Coaching Certification Level 1",
                "projects": "Organized Community Fitness Program, Research on Sports Nutrition",
                "skills": "Leadership, Time Management, Athletic Training",
                "interests": "Sports Medicine, Community Health",
                "university": "University of Waterloo",
                "major": "Kinesiology"
            },
            {
                "school": "Eastside High School",
                "age": "18",
                "awards": "Art Competition Winner, Scholarship for Creative Writing",
                "work_experience": "Freelance Graphic Designer, Volunteer at Art Museum",
                "certifications": "Adobe Creative Suite Certified, Creative Writing Workshop Certificate",
                "projects": "Illustrated Children's Book, Curated School Art Exhibition",
                "skills": "Digital Illustration, Creative Writing, Event Planning",
                "interests": "Visual Arts, Literature",
                "university": "University of Waterloo",
                "major": "Illustration"
            },
            {
                "school": "Westview High School",
                "age": "17",
                "awards": "Robotics Competition National Finalist, Math League Champion",
                "work_experience": "Intern at Engineering Firm, Volunteer at STEM Camp for Kids",
                "certifications": "Robotics Programming Certification, Advanced Calculus Course",
                "projects": "Built Autonomous Drone, Developed Algorithm for Optimizing Traffic Flow",
                "skills": "Robotics, Python Programming, Analytical Thinking",
                "interests": "Artificial Intelligence, Mechanical Engineering",
                "university": "University of Waterloo",
                "major": "Robotics Engineering"
            },
            {
                "school": "Southridge High School",
                "age": "18",
                "awards": "National History Day Winner, Model United Nations Best Delegate",
                "work_experience": "Intern at Historical Society, Volunteer at Local Library",
                "certifications": "Advanced Placement Scholar, Historical Research Methods Certificate",
                "projects": "Documentary on Civil Rights Movement, Organized School History Bee",
                "skills": "Research, Public Speaking, Leadership",
                "interests": "History, International Relations",
                "university": "Georgetown University",
                "major": "International Relations"
            },
            {
                "school": "Northgate High School",
                "age": "19",
                "awards": "State Music Competition Winner, Orchestra Concertmaster",
                "work_experience": "Music Tutor, Volunteer at Community Theater",
                "certifications": "Grade 8 Violin Certification, Music Theory Advanced Level",
                "projects": "Composed Original Symphony, Led School Orchestra Tour",
                "skills": "Violin Performance, Composition, Team Collaboration",
                "interests": "Classical Music, Music Education",
                "university": "Juilliard School",
                "major": "Violin Performance"
            },
            {
                "school": "Brookfield High School",
                "age": "17",
                "awards": "National Coding Competition Winner, Science Olympiad Medalist",
                "work_experience": "Intern at Software Startup, Volunteer at Coding Bootcamp for Youth",
                "certifications": "Java Programming Certification, Data Structures and Algorithms Course",
                "projects": "Developed Educational Game App, Research on Machine Learning Models",
                "skills": "Java, Machine Learning, Problem-Solving",
                "interests": "Computer Science, Educational Technology",
                "university": "Carnegie Mellon University",
                "major": "Computer Science"
            },
            {
                "school": "Riverside High School",
                "age": "18",
                "awards": "Young Entrepreneurs Award, Business Plan Competition Winner",
                "work_experience": "Founder of Online Retail Store, Volunteer at Business Incubator",
                "certifications": "Entrepreneurship Course Certificate, Digital Marketing Certification",
                "projects": "Launched E-commerce Platform, Organized Startup Weekend at School",
                "skills": "Entrepreneurship, Marketing, Team Leadership",
                "interests": "Business Development, E-commerce",
                "university": "University of Pennsylvania",
                "major": "Entrepreneurship"
            },
            {
                "school": "Merivale High School",
                "age": "18",
                "awards": "Math Olympiad State Champion, Physics Bowl Winner",
                "work_experience": "Engineer, Sparkling H20 Youth Robotics 					                       July 2024  - PRESENT\nPart of the software team. Used Java to develop subsystems and commands to control the FIRST competition robots. Participated in competitions for testing and calibrating robots.\nWorked with the mechanical and outreach team to develop strategies, plan, and build the robot\nReference: Spark Youth Robotics Club  | spark.youthrc@gmail.com",
                "certifications": "Advanced Physics Certification, Machine Learning Basics",
                "projects": "Simulated Astrophysics Model, Built Custom 3D Printer",
                "skills": "Physics, Data Analysis, CAD Design",
                "interests": "Astrophysics, Robotics",
                "university": "University of Waterloo",
                "major": "Engineering"
            }
        ]
    
    def clean_text(self, text):
        text = re.sub(r"[\t•-]+", "\n", text)  # Replace newlines, tabs, and bullets with a newline
        return text

    def calculate_similarity(self, user_keywords, dataset_keywords):
        matches = sum(1 for word in user_keywords if word in dataset_keywords)    
        total = len(user_keywords) + len(dataset_keywords)
        return (2 * matches) / total if total > 0 else 0     #weird calcualtion but it works i guess

    def extract_keywords(self, text):
        stop_words = set(stopwords.words("english"))
        words = word_tokenize(text.lower())  # Tokenize the text and make it lowercase
        
        # POS tagging
        tagged_words = pos_tag(words)
        
        # Named Entity Recognition (NER)
        named_entities = ne_chunk(tagged_words)
        
        # List to store the keywords
        keywords = []

        # Extract named entities (proper nouns, organizations, etc.)
        for entity in named_entities:
            if isinstance(entity, nltk.Tree):  # If it's a named entity (e.g., a company or location)
                keywords.append(' '.join(c[0] for c in entity))

        # Further extraction for detailed words (like technologies, verbs related to work, etc.)
        for word, pos in tagged_words:
            # Extract specific nouns (e.g., job titles, technologies) and verbs related to work
            if pos in ['NN', 'NNS', 'NNP', 'NNPS']:  # Nouns (singular and plural, proper nouns)
                keywords.append(word)
            elif pos in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:  # Verbs
                keywords.append(word)

        # Remove stopwords and duplicates
        keywords = [word for word in keywords if word not in stop_words]
        keywords = list(set(keywords))  # Remove duplicates

        # Optional: Filter out unnecessary characters (e.g., punctuation, numbers)
        keywords = [word for word in keywords if word.isalnum()]

        return keywords

    def split_experiences(self, text):
        return re.split(r"\n\n", text.strip())    #seaprates sections when there is a newline

    def display_results(self):
        user_profile = {
            "school": self.clean_text(self.school_input.text()),
            "awards": self.clean_text(self.awards_input.toPlainText()),
            "work_experience": self.clean_text(self.work_input.toPlainText()),
            "certifications": self.clean_text(self.certifications_input.toPlainText()),
            "projects": self.clean_text(self.projects_input.toPlainText()),
            "skills": self.clean_text(self.skills_input.toPlainText()),
            "interests": self.clean_text(self.interests_input.toPlainText()),
            "university": self.clean_text(self.university_input.text()),
            "major": self.clean_text(self.major_input.text()),
        }

        weights = {
            "school": 0.05,
            "awards": 0.25,
            "work_experience": 0.25,
            "certifications": 0.1,
            "projects": 0.2,
            "skills": 0.05,
            "interests": 0.05,
            "major": 0.05
        }

        target_university = user_profile["university"].lower()

        # Filter dataset by university
        filtered_profiles = [p for p in self.dataset if p["university"].lower() == target_university]

        results = []
        for profile in filtered_profiles:
            user_keywords = defaultdict(list)
            dataset_keywords = defaultdict(list)

            for category in user_profile:
                if category != "university":
                    if category in ["work_experience", "projects"]:
                        user_sections = self.split_experiences(user_profile[category])
                        dataset_sections = self.split_experiences(profile[category])

                        for user_section in user_sections:
                            user_keywords[category].append(self.extract_keywords(user_section))
                        for dataset_section in dataset_sections:
                            dataset_keywords[category].append(self.extract_keywords(dataset_section))
                    else:
                        user_keywords[category] = self.extract_keywords(user_profile[category])
                        dataset_keywords[category] = self.extract_keywords(profile[category])

            total_score = 0
            similar_items = []
            different_items = []
            for category in user_keywords:
                if isinstance(user_keywords[category][0], list):
                    category_scores = []
                    highest_scores = []
                    for u_section_kw in user_keywords[category]:
                        for d_section_kw in dataset_keywords[category]:
                            category_scores.append(self.calculate_similarity(u_section_kw, d_section_kw))    
                        highest_scores.append(max(category_scores))
                    avg_score = sum(category_scores) / len(category_scores)
                    total_score += avg_score * weights[category] if category_scores else 0
                else:
                    avg_score = self.calculate_similarity(user_keywords[category], dataset_keywords[category])
                    total_score += avg_score * weights[category]
                if avg_score >= 0.5:
                        similar_items.append([user_profile[category], profile[category]])
                else:
                    different_items.append([user_profile[category], profile[category]])
            results.append((profile, total_score, similar_items, different_items))

        # Sort by highest similarity and display results
        results.sort(key=lambda x: x[1], reverse=True)
        self.show_results(results)

    def show_results(self, results):
        result_text = ""
        for profile, score, similar_items, different_items in results:
            result_text += f"Profile: {profile['school']} - Score: {score:.2%}\n"
            # LATER ADD: SEE THE SIMILAR AND DIFFERENT ITEMS IN LIKE A TABLE FORMAT AFTER USER CLICKS

        result_label = QLabel(result_text)
        result_label.setStyleSheet("color: white;")
        self.result_area.setWidget(result_label)

# Competition Finder Window
class CompetitionFinder(QWidget):
    def __init__(self, parent_size):
        super().__init__()
        self.setWindowTitle("Competition Finder")
        self.setGeometry(*parent_size)
        self.setStyleSheet("background-color: #2E2E2E;")
        layout = QVBoxLayout()

        # Inputs for competition finder
        layout.addWidget(QLabel("Enter City"))
        self.city_input = QLineEdit()
        layout.addWidget(self.city_input)

        layout.addWidget(QLabel("Enter State/Province"))
        self.state_province_input = QLineEdit()
        layout.addWidget(self.state_province_input)

        layout.addWidget(QLabel("Enter Country"))
        self.country_input = QLineEdit()
        layout.addWidget(self.country_input)

        layout.addWidget(QLabel("Enter Age"))
        self.age_input = QLineEdit()
        layout.addWidget(self.age_input)

        layout.addWidget(QLabel("Enter Interests"))
        self.interests_input = QTextEdit()
        layout.addWidget(self.interests_input)

        # Added education status input
        layout.addWidget(QLabel("Enter Current Education Status"))
        self.education_status_input = QComboBox()
        self.education_status_input.addItems(["High School", "Middle School", "University/College"])
        layout.addWidget(self.education_status_input)

        submit_btn = QPushButton("Find Competitions")
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: lightblue;
                color: white;
                border-radius: 15px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
            }
        """)
        submit_btn.clicked.connect(self.display_results)
        layout.addWidget(submit_btn)

        # Scrollable result area
        self.result_area = QScrollArea()
        layout.addWidget(self.result_area)

        self.setLayout(layout)

    def display_results(self):
        # Collect user inputs
        city = self.city_input.text()
        state_province = self.state_province_input.text()
        country = self.country_input.text()
        age = self.age_input.text()
        interests = self.interests_input.toPlainText()
        education_status = self.education_status_input.currentText()

        results = find_competitions(city, state_province, country, age, interests, education_status)
        
        # Display results
        results_widget = QWidget()
        results_layout = QVBoxLayout()

        for result in results:
            if "error" in result:
                box = QLabel(result["error"])
            else:
                box = QLabel(f"Title: {result['title']}\nLink: {result['link']}\nSnippet: {result['snippet']}\n")
            box.setWordWrap(True)
            results_layout.addWidget(box)

        results_widget.setLayout(results_layout)
        self.result_area.setWidget(results_widget)

# Resume Optimizer Window
class ResumeOptimizer(QWidget):
    def __init__(self, parent_size):
        super().__init__()
        self.setWindowTitle("Resume Optimizer")
        self.setGeometry(*parent_size)
        self.setStyleSheet("background-color: #2E2E2E; color: white;")

        # Main layout with scroll area
        main_layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QFormLayout(scroll_content)

        # Add User's Info title
        user_info_title = QLabel("User's Information")
        user_info_title.setStyleSheet("font-size: 18px; font-weight: bold; color: lightblue;")
        self.scroll_layout.addRow(user_info_title)

        # Input fields for User's Info
        self.inputs = {}
        self.add_input_field("Education", is_multiline=True)
        self.add_input_field("Skills", is_multiline=True)
        self.add_input_field("Awards & Accomplishments", is_multiline=True)
        self.add_input_field("Certifications & Licenses", is_multiline=True)
        self.add_input_field("Volunteer & Work Experience", is_multiline=True)

        # Add Job Info title
        job_info_title = QLabel("Job Information")
        job_info_title.setStyleSheet("font-size: 18px; font-weight: bold; color: lightblue;")
        self.scroll_layout.addRow(job_info_title)

        # Input fields for Job Info
        self.add_input_field("Job Title", is_multiline=False)
        self.add_input_field("Job Description (including company)", is_multiline=True)
        self.add_input_field("Essential Duties & Responsibilities", is_multiline=True)
        self.add_input_field("Requirements & Qualifications", is_multiline=True)

        # Submit button
        submit_btn = QPushButton("Optimize Resume")
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: lightblue;
                color: black;
                border-radius: 15px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
            }
        """)
        submit_btn.clicked.connect(self.handle_submission)
        self.scroll_layout.addWidget(submit_btn)

        # Add form to scroll area
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # Scrollable result area
        self.result_area = QScrollArea()
        self.result_area.setWidgetResizable(True)
        self.result_label = QLabel()
        self.result_label.setStyleSheet("color: white; padding: 10px;")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.result_area.setWidget(self.result_label)
        main_layout.addWidget(self.result_area)

        self.setLayout(main_layout)

    def add_input_field(self, label_text, is_multiline=False):
        """Add an input field with a label to the form layout."""
        label = QLabel(label_text + ":")
        label.setStyleSheet("font-weight: bold;")
        self.scroll_layout.addRow(label)
        if is_multiline:
            input_field = QTextEdit()
        else:
            input_field = QLineEdit()
        input_field.setStyleSheet("background-color: #404040; color: white;")
        self.inputs[label_text] = input_field
        self.scroll_layout.addRow(input_field)

    def handle_submission(self):
        """Handle the submission process: save files and call `run` function."""
        try:
            resume_folder_path = "resume_optimizer/data/resumes"  
            os.makedirs(resume_folder_path, exist_ok=True)

            # Create resume.txt
            resume_file_path = os.path.join(resume_folder_path, "resume.txt")
            with open(resume_file_path, "w", encoding="utf-8") as resume_file:  # Specify UTF-8 encoding
                resume_file.write("Education:\n" + self.inputs["Education"].toPlainText() + "\n")
                resume_file.write("\nSkills:\n" + self.inputs["Skills"].toPlainText() + "\n")
                resume_file.write("\nAwards & Accomplishments:\n" + self.inputs["Awards & Accomplishments"].toPlainText() + "\n")
                resume_file.write("\nCertifications & Licenses:\n" + self.inputs["Certifications & Licenses"].toPlainText() + "\n")
                resume_file.write("\nVolunteer & Work Experience:\n" + self.inputs["Volunteer & Work Experience"].toPlainText() + "\n")

            job_folder_path = "resume_optimizer/data/jobs"  
            os.makedirs(job_folder_path, exist_ok=True)
            job_file_path = os.path.join(job_folder_path, "job.txt")
            with open(job_file_path, "w", encoding="utf-8") as job_file:  # Specify UTF-8 encoding
                job_file.write("Job Title:\n" + self.inputs["Job Title"].text() + "\n")
                job_file.write("\nJob Description:\n" + self.inputs["Job Description (including company)"].toPlainText() + "\n")
                job_file.write("\nEssential Duties & Responsibilities:\n" + self.inputs["Essential Duties & Responsibilities"].toPlainText() + "\n")
                job_file.write("\nRequirements & Qualifications:\n" + self.inputs["Requirements & Qualifications"].toPlainText() + "\n")

            # Call the `run` function
            result = "\n".join(run(job_file_path, resume_file_path))
            print("Done!")
            self.result_label.setText(result)
        except Exception as e:
            self.result_label.setText(f"An error occurred: {e}")

# Application Writer Window
class ApplicationWriter(QWidget):
    def __init__(self, parent_size):
        super().__init__()
        self.setWindowTitle("Application Writer")
        self.setGeometry(*parent_size)
        self.setStyleSheet("background-color: #2E2E2E;")
        
        # Header
        self.header = QLabel("Application Writer")
        self.header.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.subheader = QLabel("Applications for the lazy")
        self.subheader.setStyleSheet("font-size: 14px; font-style: italic; color: #bbbbbb;")
        
        header_layout = QVBoxLayout()
        header_layout.addWidget(self.header)
        header_layout.addWidget(self.subheader)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Upload Documents Section
        doc_section = QVBoxLayout()
        doc_title = QLabel("Provide Relevant Documents (max 4)")
        doc_title.setStyleSheet("font-size: 18px;")

        self.file_preview = QLabel()
        self.file_preview.setFixedSize(150, 150)
        self.file_preview.setStyleSheet(
            "background-color: #333333; border-radius: 10px; border: 1px dashed #444444;"
        )
        self.file_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_preview.setText("No File Selected")

        self.doc_button = QPushButton("Choose File")
        self.doc_button.setStyleSheet(
            "background-color: #1e90ff; color: white; border-radius: 10px; padding: 10px;"
        )
        self.doc_button.clicked.connect(self.load_file_preview)

        self.doc_error_label = QLabel("")
        self.doc_error_label.setStyleSheet("color: red; font-size: 12px;")

        doc_section.addWidget(doc_title)
        doc_section.addWidget(self.file_preview, alignment=Qt.AlignmentFlag.AlignLeft)
        doc_section.addWidget(self.doc_button, alignment=Qt.AlignmentFlag.AlignLeft)
        doc_section.addWidget(self.doc_error_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # Provide Questions Section
        question_section = QVBoxLayout()
        question_title = QLabel("Provide Questions")
        question_title.setStyleSheet("font-size: 18px;")

        self.question_text_box = QTextEdit()
        self.question_text_box.setPlaceholderText("Enter each question on a new line")
        self.question_text_box.setFixedHeight(90)
        self.question_text_box.setStyleSheet(
            "background-color: #333333; color: white; border-radius: 10px; padding: 5px; "
        )
        self.question_text_box.textChanged.connect(self.adjust_question_box_height)

        self.question_error_label = QLabel("")
        self.question_error_label.setStyleSheet("color: red; font-size: 12px;")
        
        question_section.addWidget(question_title)
        question_section.addWidget(self.question_text_box)
        question_section.addWidget(self.question_error_label)

        # Style Section
        style_section = QVBoxLayout()
        style_title = QLabel("Style (optional)")
        style_title.setStyleSheet("font-size: 18px;")

        self.style_dropdown = QComboBox()
        self.style_dropdown.addItems(["Formal", "Casual"])
        self.style_dropdown.setStyleSheet(
            "background-color: #333333; color: white; border: none; padding: 5px; border-radius: 10px;"
        )

        style_note = QLabel("Choose how you want the response to sound.")
        style_note.setStyleSheet("font-size: 12px; color: #bbbbbb;")

        style_section.addWidget(style_title)
        style_section.addWidget(self.style_dropdown)
        style_section.addWidget(style_note)

        # Footer
        next_button = QPushButton("Next")
        next_button.setStyleSheet(
            "background-color: #1e90ff; color: white; font-size: 16px; padding: 10px; border-radius: 10px;"
        )
        next_button.setFixedSize(100, 40)
        next_button.clicked.connect(self.on_next_button_click)

        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        footer_layout.addWidget(next_button)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(doc_section)
        main_layout.addSpacing(20)
        main_layout.addLayout(question_section)
        main_layout.addSpacing(20)
        main_layout.addLayout(style_section)
        main_layout.addStretch()
        main_layout.addLayout(footer_layout)

        self.setLayout(main_layout)

        self.style = "Formal"   #default

    def load_file_preview(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose File")
        if file_name:
            image_reader = QImageReader(file_name)
            pixmap = QPixmap.fromImageReader(image_reader)
            scaled_pixmap = pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.file_preview.setPixmap(scaled_pixmap)
            self.upload_file(file_name)  
        else:
            self.file_preview.setText("No File Selected")

    def upload_file(self, file_path):
        os.makedirs('user_files', exist_ok=True)

        file_name = os.path.basename(file_path)
        destination = os.path.join('user_files', file_name)

        shutil.copy(file_path, destination)  

    def adjust_question_box_height(self):
        document = self.question_text_box.document()
        line_count = document.blockCount()
        self.question_text_box.setFixedHeight(min(90 + (line_count - 3) * 20, 300))

    def on_next_button_click(self):
        is_valid = True
        
        if not self.file_preview.pixmap():
            self.doc_error_label.setText("This field must be completed.")
            is_valid = False
        else:
            self.doc_error_label.clear()

        questions = self.question_text_box.toPlainText().strip()
        if not questions:
            self.question_error_label.setText("This field must be completed.")
            is_valid = False
        else:
            self.question_error_label.clear()

        self.style = self.style_dropdown.currentText() if self.style_dropdown.currentText() else "Formal"

        if is_valid:
            uploaded_files = [os.path.join('user_files', f) for f in os.listdir('user_files')]
            data = {
                "uploaded_files": uploaded_files,
                "questions": questions,
                "style": self.style
            }
            subprocess.run(["python", "application_writer/extract.py"], input=str(data), text=True)
        else:
            print("Please complete all fields.")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    apply_dark_theme(app)

    main_window = MainApp()
    main_window.show()

    sys.exit(app.exec())