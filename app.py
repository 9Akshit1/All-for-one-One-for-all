import sys
import os

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag, ne_chunk
import re
from difflib import SequenceMatcher
from collections import defaultdict

#nltk.download('punkt')
#nltk.download('stopwords')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('maxent_ne_chunker')
#nltk.download('maxent_ne_chunker_tab')
#nltk.download('words')

import shutil
import subprocess
import time
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, pyqtSignal, QEvent, QFile, QThread
from PyQt6.QtGui import QFont, QColor, QPalette, QKeySequence, QImageReader, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QWidget, QFileDialog, QLineEdit, QTextEdit, QComboBox, QScrollArea, QFormLayout, QGridLayout, QStackedLayout, QProgressBar, QStackedWidget, QHBoxLayout, QSpacerItem, QSizePolicy
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
        self.setWindowTitle("student helper app")
        self.setGeometry(100, 100, 1200, 1000)  # Window size

        # Background Color
        self.setStyleSheet("background-color: #ECE0E0;")

        # Home Screen Setup
        self.home_widget = QWidget()
        self.setCentralWidget(self.home_widget)

        # Layout for Home Screen
        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)  # Increased vertical spacing

        # Layered Title
        self.title_container = QWidget()  # Container for the titles
        self.title_container.setFixedWidth(400)  # Set the width of the container
        self.title_container.setFixedHeight(100)  # Adjust as necessary
        self.title_container.setStyleSheet("background-color: transparent;")  # Ensure the container is transparent

        # Shared font settings
        self.title_font = QFont("Coming Soon")
        self.title_font.setPointSize(50)
        self.title_font.setBold(True)

        # Yellow shadow (slightly shifted left)
        self.title_label_shadow = QLabel("afoofa", self.title_container)
        self.title_label_shadow.setFont(self.title_font)
        self.title_label_shadow.setStyleSheet("color: #FED82D;")  # Yellow color
        self.title_label_shadow.move(95, 20)  # Slightly shift to the left and upward

        # Orange main title (centered on top)
        self.title_label = QLabel("afoofa", self.title_container)
        self.title_label.setFont(self.title_font)
        self.title_label.setStyleSheet("color: #FF532B;")  # Deep orange color
        self.title_label.move(100, 25)  # Center-aligned relative to the shadow

        # Use a horizontal layout to center the title container
        self.center_layout = QHBoxLayout()
        self.center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align content to the center
        self.center_layout.addWidget(self.title_container)

        # Subtitle Label
        subtitle_label = QLabel("an app all for one, and one for all students")
        subtitle_font = QFont("Arial")
        subtitle_font.setPointSize(12)
        subtitle_font.setBold(True)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        subtitle_label.setStyleSheet("color: gray;")

        self.center_layout.addWidget(subtitle_label)

        # Add the centered title layout to the main layout
        self.layout.addLayout(self.center_layout)

        # Buttons with Rounded Corners
        button_style = """
            QPushButton {
                background-color: #FF532B;  /* Deep orange color */
                color: #FEDB37;  /* Yellow text */
                font-size: 11pt;
                font-weight: bold;
                padding: 15px;
                border-radius: 25px;
                width: 300px;
            }
            QPushButton:hover {
                background-color: #FFA500;  /* Lighter orange on hover */
            }
        """

        # Create Buttons
        button_labels = ["profile comparator", "competition finder", "resume optimizer", "application writer"]
        button_callbacks = [
            self.show_profile_comparator,
            self.show_competition_finder,
            self.show_resume_optimizer,
            self.show_application_writer,
        ]

        # Adding Title and Buttons
        self.layout.addWidget(self.title_container)
        self.layout.addWidget(subtitle_label)
        self.layout.addStretch(1)

        for label, callback in zip(button_labels, button_callbacks):
            button = QPushButton(label)
            button.setStyleSheet(button_style)
            button.clicked.connect(callback)
            button.setMaximumWidth(300)
            self.layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.layout.addStretch(2)

        # Footer Text
        footer_label = QLabel("9akshit1")
        footer_font = QFont("Arial")
        footer_font.setPointSize(12)
        footer_font.setBold(True)
        footer_label.setFont(footer_font)
        footer_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        footer_label.setStyleSheet("color: #FF6D4C; margin-bottom: 10px;")
        self.layout.addWidget(footer_label)

        # Set layout to home screen
        self.home_widget.setLayout(self.layout)

    def resizeEvent(self, event):
        # Recalculate the position of the title container when the window is resized
        window_width = self.width()
        title_width = self.title_container.width()

        # Calculate the horizontal position to center the title container
        x_position = (window_width - title_width) // 2
        self.title_container.move(x_position, 100)  

        super().resizeEvent(event)

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

# Question Slider Window Class for Input Taking
class QuestionSlider(QWidget):
    def __init__(self, input_questions, submit_callback, parent=None):
        super().__init__(parent)
        self.input_questions = input_questions
        self.current_index = 0
        self.submit_callback = submit_callback  # Callback to send the answers back to the caller

        # Set the background color for the whole screen
        self.setStyleSheet("background-color: #ECE0E0;")

        # Layout for the screen
        self.layout = QVBoxLayout()

        # Layered Title
        self.title_container = QWidget()  # Container for the titles
        self.title_container.setFixedWidth(800)  # Set the width of the container
        self.title_container.setFixedHeight(60)  # Adjust as necessary
        self.title_container.setStyleSheet("background-color: transparent;")  

        # Shared font settings
        self.title_font = QFont("Coming Soon")
        self.title_font.setPointSize(50)
        self.title_font.setBold(True)

        # Yellow shadow (slightly shifted left)
        self.title_label_shadow = QLabel("afoofa", self.title_container)
        self.title_label_shadow.setFont(self.title_font)
        self.title_label_shadow.setStyleSheet("""
            font-family: 'Coming Soon', sans-serif;
            font-size: 40px;
            color: #FED82D;
            padding: 10px;
        """)
        self.title_label_shadow.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.title_label_shadow.move(-10, 0)  # Slightly shift to the left and upward

        # Orange main title (centered on top)
        self.title_label = QLabel("afoofa", self.title_container)
        self.title_label.setFont(self.title_font)
        self.title_label.setStyleSheet("""
            font-family: 'Coming Soon', sans-serif;
            font-size: 40px;
            color: #FF532B;
            padding: 10px;
        """)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.title_label.move(-5, 5)  # Center-aligned relative to the shadow

        # Use a horizontal layout to center the title container
        self.center_layout = QHBoxLayout()
        self.center_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align content to the center
        self.center_layout.addWidget(self.title_container)

        # Add the centered title layout to the main layout
        self.layout.addLayout(self.center_layout)

        # Subtitle Label
        subtitle_label = QLabel("an app all for one, and one for all students")
        subtitle_font = QFont("Arial")
        subtitle_font.setPointSize(12)
        subtitle_font.setBold(True)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        subtitle_label.setStyleSheet("""
            color: gray;
            padding-left: 10px;  /* Adds 10px padding to the left */
        """)

        self.layout.addWidget(subtitle_label)

        # Stacked widget for questions
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Iterate through the input questions to create individual pages
        self.input_fields = []
        for question, input_type in self.input_questions:
            question_page = QWidget()
            question_layout = QVBoxLayout()
            question_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center-align the layout

            # Display question
            question_label = QLabel(question)
            question_label.setStyleSheet("""
                font-family: 'Coming Soon', sans-serif;
                font-size: 25px;
                font-weight: bold;
                color: #FF532B;
                padding: 0px;
                margin-bottom: 5px; /* Reduce spacing to 5px */
            """)
            question_layout.addWidget(question_label)

            # Add input field based on input type
            input_field = None
            if input_type == "text":
                input_field = QLineEdit()
                input_field.setFixedHeight(30)  # Set fixed height for the input box
                input_field.setStyleSheet("""
                    border: none;
                    border-bottom: 2px solid #FF532B;
                    background: transparent;
                    color: #FF532B;
                    padding: 5px;
                """)
            elif input_type == "textarea":
                input_field = QTextEdit()
                input_field.setFixedHeight(30)  # Match height with other input types
                input_field.setStyleSheet("""
                    border: none;
                    border-bottom: 2px solid #FF532B;
                    background: transparent;
                    color: #FF532B;
                    padding: 5px;
                """)
                input_field.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
            elif input_type == "combobox":
                input_field = QComboBox()
                input_field.addItems(["High School", "Middle School", "University/College"])
                input_field.setFixedHeight(30)  # Match height with other input types
                input_field.setStyleSheet("""
                    border: none;
                    border-bottom: 2px solid #FF532B;
                    background: transparent;
                    color: #FF532B;
                    padding: 5px;
                """)

            self.input_fields.append(input_field)
            question_layout.addWidget(input_field, alignment=Qt.AlignmentFlag.AlignVCenter)

            # Add navigation buttons (left/right)
            nav_layout = QHBoxLayout()
            nav_layout.setSpacing(5)  
            self.left_button = QPushButton("<")
            self.right_button = QPushButton(">")
            nav_layout.addWidget(self.left_button)
            nav_layout.addWidget(self.right_button)

            # Style the buttons
            nav_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.left_button.setStyleSheet("""
                background-color: #FF532B;
                color: #FED82D;
                border-radius: 10px;
                padding: 10px;
                margin-top: 15px;
            """)

            self.right_button.setStyleSheet("""
                background-color: #FF532B;
                color: #FED82D;
                border-radius: 10px;
                padding: 10px;
                margin-top: 15px;
            """)

            # Add the buttons to the layout
            question_layout.addLayout(nav_layout)

            self.left_button.clicked.connect(self.show_previous_question)
            self.right_button.clicked.connect(self.show_next_question)

            # Add vertical space between nav buttons and submit button
            vertical_spacer = QSpacerItem(0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            question_layout.addSpacerItem(vertical_spacer)

            # Submit Button at the right side of the screen
            submit_button = QPushButton("Submit")
            submit_button.setStyleSheet("""
                QPushButton {
                    background-color: #FF532B;
                    color: #FED82D;
                    border-radius: 15px;
                    font-family: 'Coming Soon', sans-serif;
                    font-size: 18px;
                    font-weight: bold;
                    width: 120px;  /* Set fixed width */
                    height: 40px;  /* Set fixed height */
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #FF5A3C;
                }
            """)
            submit_button.setFixedSize(120, 40)  # Explicitly set button size

            # Add a container to position the submit button at the right
            submit_button_container = QHBoxLayout()
            submit_button_container.addWidget(submit_button)
            question_layout.addLayout(submit_button_container)

            submit_button.clicked.connect(self.submit_answers)

            # Add question page to stacked widget
            question_page.setLayout(question_layout)
            self.stacked_widget.addWidget(question_page)

        # Name label styling
        name_label = QLabel("9akshit1")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("""
            font-family: 'Coming Soon', sans-serif;
            font-size: 15px;
            font-weight: bold;
            color: #FF532B;
            padding: 10px;
        """)

        # Add the text directly to the main layout at the bottom
        self.layout.addWidget(name_label, alignment=Qt.AlignmentFlag.AlignBottom)

        # Set the layout for the main widget
        self.setLayout(self.layout)

    def show_previous_question(self):
        self.current_index = (self.current_index - 1) % len(self.input_questions)
        self.stacked_widget.setCurrentIndex(self.current_index)

    def show_next_question(self):
        self.current_index = (self.current_index + 1) % len(self.input_questions)
        self.stacked_widget.setCurrentIndex(self.current_index)

    def submit_answers(self):
        # Collect all answers
        answers = {}
        for idx, (question, input_type) in enumerate(self.input_questions):
            if input_type == "text":
                answers[question] = self.input_fields[idx].text()
            elif input_type == "textarea":
                answers[question] = self.input_fields[idx].toPlainText()
            elif input_type == "combobox":
                answers[question] = self.input_fields[idx].currentText()

        # Call the provided callback function with the answers
        self.submit_callback(answers)

# Class for each profile widget
class ProfileWidget(QWidget):
    def __init__(self, rank, profile, score, similar_items, different_items, expand_callback, collapse_callback):
        super().__init__()
        self.rank = rank
        self.profile = profile
        self.score = score
        self.similar_items = similar_items
        self.different_items = different_items
        self.expand_callback = expand_callback
        self.collapse_callback = collapse_callback

        self.is_expanded = False  # Tracks the expanded state

        # Outer container layout
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)  # No margins around the container
        outer_layout.setSpacing(0)

        # Container widget for the profile content
        container = QWidget(self)
        container.setStyleSheet("""
            background-color: #FF532B;
            border-radius: 20px;
            padding: 15px;
            font-weight: bold;
            font-size: 14px;
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)  # Padding inside the container
        container_layout.setSpacing(10)

        # Profile information
        self.rank_label = QLabel(f"#{rank} Profile")
        self.score_label = QLabel(f"Score: {score:.2%}")
        self.school_label = QLabel(f"School: {profile['school']}")

        # Style for text (12px font size)
        text_style = "color: #FED82D; font-size: 12px;"
        self.rank_label.setStyleSheet(text_style)
        self.score_label.setStyleSheet(text_style)
        self.school_label.setStyleSheet(text_style)

        # Add labels to the container layout
        container_layout.addWidget(self.rank_label, alignment=Qt.AlignmentFlag.AlignTop)
        container_layout.addWidget(self.score_label, alignment=Qt.AlignmentFlag.AlignTop)
        container_layout.addWidget(self.school_label, alignment=Qt.AlignmentFlag.AlignTop)

        # Expand button
        self.expand_button = QPushButton("Click for More Info")
        self.expand_button.setStyleSheet("""
            background-color: #FED82D;
            color: #FF532B;
            border-radius: 5px;
            padding: 5px;
            font-weight: bold;
            font-size: 12px;
        """)
        self.expand_button.clicked.connect(self.expand)
        container_layout.addWidget(self.expand_button, alignment=Qt.AlignmentFlag.AlignBottom)

        # Expanded view content (hidden by default)
        self.details_label = QLabel()
        self.details_label.setStyleSheet("color: #FED82D; font-size: 12px;")
        self.details_label.setWordWrap(True)
        self.details_label.hide()

        # Go Back button (hidden by default)
        self.go_back_button = QPushButton("Go Back to Profiles")
        self.go_back_button.setStyleSheet("""
            background-color: #FED82D;
            color: #FF532B;
            border-radius: 5px;
            padding: 5px;
            font-weight: bold;
            font-size: 12px;
        """)
        self.go_back_button.clicked.connect(self.collapse)
        self.go_back_button.hide()

        # Add the details and go-back button to the container layout
        container_layout.addWidget(self.details_label, alignment=Qt.AlignmentFlag.AlignTop)
        container_layout.addWidget(self.go_back_button, alignment=Qt.AlignmentFlag.AlignBottom)

        # Add the container to the outer layout
        outer_layout.addWidget(container)

    def expand(self):
        """Expand the profile widget to show detailed information."""
        if not self.is_expanded:
            self.is_expanded = True
            self.details_label.setText(
                f"School: {self.profile['school']}\n"
                f"Score: {self.score:.2%}\n\n"
                f"Similar Items:\n{self.similar_items}\n\n"
                f"Different Items:\n{self.different_items}"
            )
            self.details_label.show()
            self.expand_button.hide()
            self.go_back_button.show()
            self.expand_callback(self)

    def collapse(self):
        """Collapse the profile widget to return to grid view."""
        if self.is_expanded:
            self.is_expanded = False
            self.details_label.hide()
            self.expand_button.show()
            self.go_back_button.hide()
            self.collapse_callback(self)

# Profile Comparator Window
class ProfileComparator(QWidget):
    def __init__(self, parent_size):
        super().__init__()
        self.setWindowTitle("Profile Comparator")
        self.setGeometry(*parent_size)
        self.setStyleSheet("background-color: #ECE0E0;")

        layout = QVBoxLayout()

        # Stacked widget to switch between screens
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Input questions for profile comparison
        input_fields = [
            ("Enter School:", "text"),
            ("Enter Awards:", "textarea"),
            ("Enter Work/Volunteer Experience:", "textarea"),
            ("Enter Licenses & Certifications:", "textarea"),
            ("Enter Projects:", "textarea"),
            ("Enter Skills:", "textarea"),
            ("Enter Interests:", "textarea"),
            ("Enter University Applying To:", "text"),
            ("Enter Major Applying To:", "text"),
        ]

        self.input_widget = QuestionSlider(input_fields, self.handle_inputs, self)
        self.stacked_widget.addWidget(self.input_widget)

        self.result_area = QScrollArea()
        #layout.addWidget(self.result_area)

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

        # Predefined Answers only used for testing
        self.predefined_answers = {
            'Enter School': 'Merivale High School',
            'Enter Awards': 'Hack 49 Hackathon 3rd Place Winner using Surge Stitch Project (2024)\nGIA Hacks 2 Hackathon 4th Place Winner using EduPiano Project (2024)\nOntario Silver Medal for Exemplary Academic Display of Achieving a +90% Average (2024)\nOttawa Regional Science Fair Curiosity & Ingenuity Category Winner (2024)\nFryer UWaterloo Competition National Rank 104 (2024)\nCanadian Computing Competition Junior Distinction (2024)\nCanadian Intermediate Mathematics Canada UWaterloo National Rank 142 (2023)\nOttawa Regional Science Fair ASHRAE Special Award Winner (2023)\nObotz Olympiad National 1st Rank (2020)',
            'Enter Work/Volunteer Experience': 'Founder & President, Ottawa ACES Business Chapter                                                              August 2024  - PRESENT\nIncreased social media presence by regularly updating Instagram and posting. Set up events & lessons. \nBrought in guest speakers & teachers. Working on bringing sponsors and developing a startup business.\nReference: ACES  | advancedcurriculums.official@gmail.com  \n\n\nWeb developer, Fresh Future Foundation                                                                                 August 2024  - PRESENT\nLeveraged React.js, Node.js, HTML, and CSS, to revamp the frontend of organization’s website\nIncreased social media presence by regularly updating Instagram and posting. Made connections.\nSet up events and ideas for the organization. From hackathons to coding/robotics projects. \nReference: Arya Vaidhya  | aryav663@gmail.com \n\n\nEngineer, Sparkling H20 Youth Robotics \t\t\t\t\t                       July 2024  - PRESENT\nPart of the software team. Used Java to develop subsystems and commands to control the FIRST competition robots. Participated in competitions for testing and calibrating robots. \nWorked with the mechanical and outreach team to develop strategies, plan, and build the robot\nReference: Spark Youth Robotics Club  | spark.youthrc@gmail.com \n\n\nEmbedded C & Arduino Assistant Teacher, OBotz Robotics \t\t\t        June 2023 - March 2024\nLead lessons at OBotz Robotics, teaching students about microcontrollers, mechanical and electronic components, Arduino programming, and embedded C through interactive methods\nIncorporated real-world examples and hands-on projects into the curriculum, enabling students to apply theoretical knowledge to practical tasks and problem-solving scenarios\nReference: Cyrilkumar Jithuri  | cyril@ucmasottawa.ca  | (613) 404-5572',
            'Enter Licenses & Certifications': 'Graduated all 7 levels of Obotz Barrhaven Robotics with Honour Roll and as Competition Winner\nEarned Drone license; C (Intermediate), Python (Intermediate), JavaScript (Intermediate) certificates',
            'Enter Projects': "MediSuit | An Advanced Medical Suit Leveraging Non-Invasive Ultrasound Technology and Biochemical Sensing for Predictive Disease and Injury Detection + Targeted Drug Delivery Mechanisms              -  PRESENT\nUtilizes AI and machine learning, including CNNs, for high-accuracy ultrasound data analysis (98%).\nAnalyzes extensive datasets to recommend optimal treatments for injuries and diseases.\nFeatures an autonomous medicine pack and micro-seams for precise, localized medication transport.\n\n\nSurge Stitch\t\t\t\t\t\t\t         \t\t\t          October 2024\nCreated a medical stitching robot by utilizing computer vision (Python) and Embedded C\nDeveloped a new stitching method through 3D simulations and CAD modelling\nGenerated different prototype models and demonstrated a working example to an audience\n\n\nTraffic Analyzer & Carjacking Camera          \t\t\t\t\t\t   September 2024\nUtilized TensorFlow and video framing modules to analyze traffic videos. Identified traffic hotspots, and root causes of traffic based on detailed and lengthy input videos.\nGiven a dataset of stolen vehicles or a specific car, tracks & predicts vehicle's movements through surveillance cameras and driving pattern analysis in cases of theft. Leveraged Googlemaps API\n\n\nEduPiano\t\t\t\t          \t\t\t\t\t\t        August 2024\nLeveraged Python and complex algorithms to calculate the most comfortable finger positions of a piano music song from sheet music. Developed a 2D piano and friendly UI using Pygame.\nDesigned an IRL projection piano prototype and a posture corrector to teach users step by step. \n\n\nExoplanet Habitability Predictor\t\t\t\t\t\t\t                     Feburary 2024\nAnalyzed trends & correlations in the NASA Exoplanet Archive using Python Matplotlib library.\nDeveloped a novel method for calculating the relative habitability of exoplanets based on planetary and stellar characteristics using Python, Pandas, NumPy, and SciPy.\nVisualized data through an interactive public website application featuring simulations and an interactive front-end, utilizing JavaScript, HTML, and CSS.\nImplemented techniques like memoization to enhance user experience by reducing wait times and improving computational speed.\n\n\nBasFinance: The Easy to use Financial Knowledge Teacher                                                  February 2024\nDeveloped a suite of Python scripts capable of currency conversion, investment and loan tracking, stock market simulation, and displaying moving averages of stocks using math libraries.\nTransformed these applications into a modern finance website designed to educate users about various financial concepts and tools.\n\n\nTriGames\t\t\t\t\t\t\t\t\t\t    December 2022\nDesigned and developed multiple games using Pygame, C#, and JavaScript, showcasing proficiency in class-object-oriented programming, error handling, and server control.\nLeveraged web development languages like JavaScript, HTML, and CSS to ensure seamless game accessibility without interruptions.\nDemonstrated expertise in 3D modelling to enhance the gaming experience for specific projects.\n\n\nAutonomous Stair Climbing Wheelchair\t\t\t\t\t\t                           June 2020\nLed an embedded C project focused on designing and implementing an autonomous stair-climbing wheelchair equipped with sensors.\nDeveloped the wheelchair's fully autonomous feature capable of following pre-inputted routes while avoiding obstacles and ensuring user safety.\nDesigned a futuristic, protective, and ergonomic wheelchair to provide support and assistance during emergencies, including built-in mechanisms for contacting health support.",
            'Enter Skills': 'Main Coding Languages: Python, Arduino C, HTML, CSS, JS, and currently learning Java\nExperience in AI/ML, Arduino, Game Development, Web Development, Data Analytics\nSoft Skills: Leadership, Time Management, Communication, Debugging, Analytical skills',
            'Enter Interests': 'Robotics, Coding, Math, Science',
            'Enter University Applying To': 'University of Waterloo',
            'Enter Major Applying To': 'Engineering'
        }

        # Add a skip button for testing
        skip_button = QPushButton("Skip", self)
        skip_button.clicked.connect(self.skip_answers)
        layout.addWidget(skip_button)

        self.setLayout(layout)

    def skip_answers(self):     # A function that is used for faster testing
        # Use the predefined answers when the submit button is clicked
        self.handle_inputs(self.predefined_answers)

    def handle_inputs(self, inputs):
        #print(inputs)
        self.process_comparison(inputs)

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

    def process_comparison(self, user_original_profile):
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

        # Mapping of old keys to new keys
        key_mapping = {
            'Enter School': 'school',
            'Enter Awards': 'awards',
            'Enter Work/Volunteer Experience': 'work_experience',
            'Enter Licenses & Certifications': 'certifications',
            'Enter Projects': 'projects',
            'Enter Skills': 'skills',
            'Enter Interests': 'interests',
            'Enter University Applying To': 'university',
            'Enter Major Applying To': 'major'
        }

        # Create a new dictionary with updated keys
        user_profile = {key_mapping[old_key]: value for old_key, value in user_original_profile.items()}

        target_university = user_profile["university"].lower()

        filtered_profiles = [p for p in self.dataset if p["university"].lower() == target_university]
        results = []

        for profile in filtered_profiles:
            user_keywords = defaultdict(list)
            dataset_keywords = defaultdict(list)
            for category, weight in weights.items():
                user_text = self.clean_text(user_profile[category])
                dataset_text = self.clean_text(profile[category])
                if category in ["work_experience", "projects"]:
                    user_sections = self.split_experiences(user_text)
                    dataset_sections = self.split_experiences(dataset_text)

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
        self.display_results(results)

    def display_results(self, results):
        # Clear the current content by removing the current widget
        if self.stacked_widget.count() > 0:
            self.stacked_widget.removeWidget(self.stacked_widget.currentWidget())

        # Header Section - Layered Title
        self.title_container = QWidget()  # Container for the titles
        self.title_container.setFixedWidth(800)  # Set the width of the container
        self.title_container.setFixedHeight(40)  # Adjust as necessary
        self.title_container.setStyleSheet("background-color: transparent; margin-top: -20px;")  

        # Shared font settings
        title_font = QFont("Coming Soon")
        title_font.setPointSize(50)
        title_font.setBold(True)

        # Yellow shadow (slightly shifted left)
        title_label_shadow = QLabel("afoofa", self.title_container)
        title_label_shadow.setFont(title_font)
        title_label_shadow.setStyleSheet("""
            font-family: 'Coming Soon', sans-serif;
            font-size: 40px;
            color: #FED82D;
            padding: 10px;
        """)
        title_label_shadow.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_label_shadow.move(0, 0)  # Slightly shift to the left

        # Orange main title (centered on top)
        title_label = QLabel("afoofa", self.title_container)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            font-family: 'Coming Soon', sans-serif;
            font-size: 40px;
            color: #FF532B;
            padding: 10px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_label.move(-5, 5)  # Center-aligned relative to the shadow

        # Layout for the title container (centered)
        title_layout = QHBoxLayout()
        title_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align content to the left
        title_layout.addWidget(self.title_container)

        # Add the centered title layout to the main layout
        header_widget = QWidget()
        header_widget.setLayout(title_layout)

        # Subtitle Section
        subtitle_label = QLabel("an app all for one, and one for all students")
        subtitle_font = QFont("Arial")
        subtitle_font.setPointSize(12)
        subtitle_font.setBold(True)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        subtitle_label.setStyleSheet("""
            color: gray;
            margin-top: 0px;
            padding-left: 10px;  /* Adds padding to the left */
        """)

        # Create a main layout and add the title container and subtitle
        main_layout = QVBoxLayout()
        main_layout.addWidget(header_widget)
        main_layout.addWidget(subtitle_label)

        # Create a widget for the header section
        header_section = QWidget()
        header_section.setLayout(main_layout)

        self.results = results

        # Scrollable area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        # Set the fixed width and height of the scroll area
        scroll_area.setFixedWidth(1200)
        scroll_area.setFixedHeight(350)

        # Hide the scrollbars (both vertical and horizontal)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Style to hide the scrollbars but keep the left and right borders colored orange
        scroll_area.setStyleSheet("""
            border-left: 3px solid #FF532B;  
            border-right: 3px solid #FF532B;  
            border-top: none;  
            border-bottom: none;  
            border-radius: 20px;  
        """)

        # Main container widget
        container = QWidget()
        self.grid_layout = QGridLayout()
        container.setLayout(self.grid_layout)
        scroll_area.setWidget(container)

        # Add profiles to grid
        self.profile_widgets = []
        for idx, (profile, score, similar_items, different_items) in enumerate(results):
            profile_widget = ProfileWidget(
                rank=idx + 1,
                profile=profile,
                score=score,
                similar_items=similar_items,
                different_items=different_items,
                expand_callback=self.expand_profile,
                collapse_callback=self.collapse_profile,
            )
            self.profile_widgets.append(profile_widget)
            row, col = divmod(idx, 4)  # 4 profiles per row
            self.grid_layout.addWidget(profile_widget, row, col)

        # Create a central layout and center the scroll area
        central_layout = QVBoxLayout()
        central_layout.addWidget(scroll_area, alignment=Qt.AlignmentFlag.AlignCenter)  # Center the scroll area

        # Create a central widget to hold the layout
        central_widget = QWidget()
        central_widget.setLayout(central_layout)

        # Add the header section above the scroll area
        main_layout = QVBoxLayout()
        main_layout.addWidget(header_section)
        main_layout.addWidget(central_widget)

        # Name Label Section (bottom of the screen)
        name_label = QLabel("9akshit1")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("""
            font-family: 'Coming Soon', sans-serif;
            font-size: 15px;
            font-weight: bold;
            color: #FF532B;
            padding: 10px;
        """)

        # Add the name label at the bottom of the main layout
        main_layout.addWidget(name_label, alignment=Qt.AlignmentFlag.AlignBottom)

        # Create a main widget for the display results and set its layout
        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        # Add the main widget to the stacked widget
        self.stacked_widget.addWidget(main_widget)

    def expand_profile(self, expanded_widget):
        # Hide all other profile widgets
        for widget in self.profile_widgets:
            if widget != expanded_widget:
                widget.hide()

    def collapse_profile(self, collapsed_widget):
        # Show all other profile widgets
        for widget in self.profile_widgets:
            widget.show()

# Competition Finder Window
class CompetitionFinder(QWidget):
    def __init__(self, parent_size):
        super().__init__()
        self.setWindowTitle("Competition Finder")
        self.setGeometry(*parent_size)
        self.setStyleSheet("background-color: #ECE0E0;")  
        
        layout = QVBoxLayout()
        
        # Stacked widget to switch between screens
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Set up the input questions and pass the reference to the QuestionSlider
        input_questions = [
            ("Enter City:", "text"),
            ("Enter State/Province:", "text"),
            ("Enter Country:", "text"),
            ("Enter Age:", "text"),
            ("Enter Interests:", "textarea"),
            ("Enter Current Education Status:", "combobox", ["High School", "Middle School", "University/College"])
        ]
        
        self.question_slider = QuestionSlider(input_questions, self.handle_answers, self)
        self.stacked_widget.addWidget(self.question_slider)

        # Set the layout for the competition finder window
        self.setLayout(layout)

    def handle_answers(self, answers):
        # Process the answers and find the results
        print("Collected Answers:", answers)
        
        # Now use the collected answers to call your competition finding function
        results = find_competitions(answers["Enter City:"], answers["Enter State/Province:"], answers["Enter Country:"], answers["Enter Age:"], answers["Enter Interests:"], answers["Enter Current Education Status:"])
        
        # Display results on the same window after questions are completed
        self.display_results(results)

    def display_results(self, results):
        # Clear the current content by removing the current widget
        if self.stacked_widget.count() > 0:
            self.stacked_widget.removeWidget(self.stacked_widget.currentWidget())

        # Header Section - Layered Title
        self.title_container = QWidget()  # Container for the titles
        self.title_container.setFixedWidth(800)  # Set the width of the container
        self.title_container.setFixedHeight(40)  # Adjust as necessary
        self.title_container.setStyleSheet("background-color: transparent; margin-top: -20px;")  

        # Shared font settings
        title_font = QFont("Coming Soon")
        title_font.setPointSize(50)
        title_font.setBold(True)

        # Yellow shadow (slightly shifted left)
        title_label_shadow = QLabel("afoofa", self.title_container)
        title_label_shadow.setFont(title_font)
        title_label_shadow.setStyleSheet("""
            font-family: 'Coming Soon', sans-serif;
            font-size: 40px;
            color: #FED82D;
            padding: 10px;
        """)
        title_label_shadow.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_label_shadow.move(0, 0)  # Slightly shift to the left

        # Orange main title (centered on top)
        title_label = QLabel("afoofa", self.title_container)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            font-family: 'Coming Soon', sans-serif;
            font-size: 40px;
            color: #FF532B;
            padding: 10px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_label.move(-5, 5)  # Center-aligned relative to the shadow

        # Layout for the title container (centered)
        title_layout = QHBoxLayout()
        title_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align content to the left
        title_layout.addWidget(self.title_container)

        # Add the centered title layout to the main layout
        header_widget = QWidget()
        header_widget.setLayout(title_layout)

        # Subtitle Section
        subtitle_label = QLabel("an app all for one, and one for all students")
        subtitle_font = QFont("Arial")
        subtitle_font.setPointSize(12)
        subtitle_font.setBold(True)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        subtitle_label.setStyleSheet("""
            color: gray;
            margin-top: 0px;
            padding-left: 10px;  /* Adds padding to the left */
        """)

        # Create a main layout and add the title container and subtitle
        main_layout = QVBoxLayout()
        main_layout.addWidget(header_widget)
        main_layout.addWidget(subtitle_label)

        # Create a widget for the header section
        header_section = QWidget()
        header_section.setLayout(main_layout)

        # Create the scrollable container for results
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        # Set the fixed width and height of the scroll area
        scroll_area.setFixedWidth(900)
        scroll_area.setFixedHeight(350)

        # Hide the scrollbars (both vertical and horizontal)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Style to hide the scrollbars but keep the left and right borders colored orange
        scroll_area.setStyleSheet("""
            border-left: 3px solid #FF532B;  
            border-right: 3px solid #FF532B;  
            border-top: none;  
            border-bottom: none;  
            background-color: transparent;  
        """)

        # Create the result widget and layout
        results_widget = QWidget()
        results_layout = QVBoxLayout()
        results_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Center the results layout

        # Style for each result item
        item_style = """
            background-color: #FF532B;  
            border: none;
            padding: 10px;
            margin-bottom: 5px;
            border-radius: 10px;  
        """

        # Set up the font for the title/category labels (yellow, bold, font: "Coming Soon")
        title_font = QFont("Coming Soon")
        title_font.setPointSize(11)
        title_font.setBold(True)

        # Iterate through the results and add them to the layout
        for result in results:
            # Title
            title_label = QLabel(f"Title: {result['title']}")
            title_label.setFont(title_font)
            title_label.setStyleSheet("color: #FED82D;")  # Yellow-ish color

            # Link
            link_label = QLabel(f"Link: <a href='{result['link']}'>{result['link']}</a>")
            link_label.setFont(title_font)
            link_label.setStyleSheet("color: #FED82D;")  # Yellow-ish color
            link_label.setOpenExternalLinks(True)

            # Snippet
            snippet_label = QLabel(f"Snippet: {result['snippet']}")
            snippet_label.setFont(title_font)
            snippet_label.setStyleSheet("color: #FED82D;")  # Yellow-ish color

            # Container for the result item
            result_item = QWidget()
            result_item_layout = QVBoxLayout()
            result_item_layout.addWidget(title_label)
            result_item_layout.addWidget(link_label)
            result_item_layout.addWidget(snippet_label)
            result_item.setLayout(result_item_layout)
            result_item.setStyleSheet(item_style)  # Apply the orange background style

            # Make sure the result item stretches to the full width of the scroll area
            result_item.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


            # Add the result item to the results layout
            results_layout.addWidget(result_item)

        # Set up the final layout for the results widget
        results_widget.setLayout(results_layout)

        # Set the widget for the scroll area
        scroll_area.setWidget(results_widget)

        # Create a central layout and center the scroll area
        central_layout = QVBoxLayout()
        central_layout.addWidget(scroll_area, alignment=Qt.AlignmentFlag.AlignCenter)  # Center the scroll area

        # Create a central widget to hold the layout
        central_widget = QWidget()
        central_widget.setLayout(central_layout)

        # Add the header section above the scroll area
        main_layout = QVBoxLayout()
        main_layout.addWidget(header_section)
        main_layout.addWidget(central_widget)

        # Name Label Section (bottom of the screen)
        name_label = QLabel("9akshit1")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("""
            font-family: 'Coming Soon', sans-serif;
            font-size: 15px;
            font-weight: bold;
            color: #FF532B;
            padding: 10px;
        """)

        # Add the name label at the bottom of the main layout
        main_layout.addWidget(name_label, alignment=Qt.AlignmentFlag.AlignBottom)

        # Create a main widget for the display results and set its layout
        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        # Add the main widget to the stacked widget
        self.stacked_widget.addWidget(main_widget)

# Resume Optimizer Window
class ResumeOptimizer(QWidget):
    def __init__(self, parent_size):
        super().__init__()
        self.setWindowTitle("Resume Optimizer")
        self.setGeometry(*parent_size)
        self.setStyleSheet("background-color: #ECE0E0;")  
        
        layout = QVBoxLayout()

        # Stacked widget to switch between screens
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Set up the input questions and pass the reference to the QuestionSlider
        input_questions = [
            ("Education:", "textarea"),
            ("Skills:", "textarea"),
            ("Awards & Accomplishments:", "textarea"),
            ("Certifications & Licenses:", "textarea"),
            ("Volunteer & Work Experience:", "textarea"),
            ("Job Title:", "text"),
            ("Job Description (including company):", "textarea"),
            ("Essential Duties & Responsibilities:", "textarea"),
            ("Requirements & Qualifications:", "textarea")
        ]

        self.question_slider = QuestionSlider(input_questions, self.handle_answers, self)
        self.stacked_widget.addWidget(self.question_slider)

        # Predefined answers for testing
        self.predefined_answers = {
            'Education:': 'Merivale High School',
            'Skills:': 'Main Coding Languages: Python, Arduino C, HTML, CSS, JS, and currently learning Java\nExperience in AI/ML, Arduino, Game Development, Web Development, Data Analytics\nSoft Skills: Leadership, Time Management, Communication, Debugging, Analytical skills',
            'Awards & Accomplishments:': 'Hack 49 Hackathon 3rd Place Winner using Surge Stitch Project (2024)\nGIA Hacks 2 Hackathon 4th Place Winner using EduPiano Project (2024)\nOntario Silver Medal for Exemplary Academic Display of Achieving a +90% Average (2024)\nOttawa Regional Science Fair Curiosity & Ingenuity Category Winner (2024)\nFryer UWaterloo Competition National Rank 104 (2024)\nCanadian Computing Competition Junior Distinction (2024)\nCanadian Intermediate Mathematics Canada UWaterloo National Rank 142 (2023)\nOttawa Regional Science Fair ASHRAE Special Award Winner (2023)\nObotz Olympiad National 1st Rank (2020)',
            'Certifications & Licenses:': 'Graduated all 7 levels of Obotz Barrhaven Robotics with Honour Roll and as Competition Winner\nEarned Drone license; C (Intermediate), Python (Intermediate), JavaScript (Intermediate) certificates',
            'Volunteer & Work Experience:': '''Founder & President, Ottawa ACES Business Chapter - August 2024  - PRESENT
        Increased social media presence by regularly updating Instagram and posting. Set up events & lessons. 
        Brought in guest speakers & teachers. Working on bringing sponsors and developing a startup business.
        Reference: ACES | advancedcurriculums.official@gmail.com  

        Web developer, Fresh Future Foundation - August 2024  - PRESENT
        Leveraged React.js, Node.js, HTML, and CSS, to revamp the frontend of organization’s website
        Increased social media presence by regularly updating Instagram and posting. Made connections.
        Set up events and ideas for the organization. From hackathons to coding/robotics projects. 
        Reference: Arya Vaidhya  | aryav663@gmail.com  

        Engineer, Sparkling H20 Youth Robotics - July 2024  - PRESENT
        Part of the software team. Used Java to develop subsystems and commands to control the FIRST competition robots. Participated in competitions for testing and calibrating robots. 
        Worked with the mechanical and outreach team to develop strategies, plan, and build the robot.
        Reference: Spark Youth Robotics Club  | spark.youthrc@gmail.com  

        Embedded C & Arduino Assistant Teacher, OBotz Robotics - June 2023 - March 2024
        Lead lessons at OBotz Robotics, teaching students about microcontrollers, mechanical and electronic components, Arduino programming, and embedded C through interactive methods.
        Incorporated real-world examples and hands-on projects into the curriculum, enabling students to apply theoretical knowledge to practical tasks and problem-solving scenarios.
        Reference: Cyrilkumar Jithuri  | cyril@ucmasottawa.ca | (613) 404-5572''',
            'Job Title:': 'Web and Database Developer',
            'Job Description (including company):': '''Denali Advanced Integration is one of the nation’s leading technology integrators by 
        volume and capacity with experience in Data Center, Unified Communications, 
        Mobility and Virtualization. Denali has more than 400 dedicated employees focused 
        on design, architecture, implementation, and operations. From Client End Devices to 
        the Cloud, Denali provides service to retail, healthcare, industrial, and government 
        environments both domestically and abroad. 

        We are seeking a Senior .Net Developer who can independently build a web-based 
        application and the BI reports around it. This includes front, middle, and back-end 
        development, SSRS, and SSIS. This is an ongoing contract engagement.''',
            'Essential Duties & Responsibilities:': '''Requirements gathering and analysis, system design and specification, build, 
        prototype, unit testing, integrated testing, validation and verification, installing, 
        configuration, customization, troubleshooting, training of users and new 
        applications, modification and support across the enterprise. 
        Design new solutions or fixes to enhance existing applications using web-enabled 
        development programs using .Net 4.5, C#, ASP.Net, HTML, CSHTML, JavaScript, and 
        similar or other web services and service-oriented tools. 
        Design and build relational databases using Microsoft SQL Server including 
        performance tuning and database backup/recovery. 
        Develop web site and web plug-in tools, databases, queries, and SSRS reports. 
        Maintain and evolve the External and Internal Portals, and similar applications. 
        Support users on existing applications.''',
            'Requirements & Qualifications:': '''Proficiency in .NET Framework version 4.5, Web Technologies, and IIS 
        Proficiency in OOP, Design Patterns, main Data Structures, Enterprise level Web and 
        Windows applications using SQL Server, Oracle, or other high-performance DBMS. 
        SQL Technologies: Transactional level SQL (including stored procedures, views and 
        indexes, and performance optimization). 
        Demonstrated knowledge of creating reports using SSRS. 
        Experience with SSIS is a plus. 
        Strong skills in database application development including working knowledge of 
        data design and development with Microsoft SQL Server DBMS system. 
        Development and SDLC tools: Visual Studio, TFS, SQL Server Management Studio, 
        SVN, YouTrack, or similar tools or Proven technical leadership skills. 
        Proven experience developing appropriate systems and metrics for measuring 
        progress, backlogs, workloads, staffing, and other project resources. 
        Knowledge of how to architect and design a new application and integrate multiple 
        applications and databases for consumption by internal and external customers. 
        Extensive experience building Enterprise level Web/Windows applications, 
        testing, and integration. 
        Knowledge of Windows-based web server administration is a plus. 
        Must be able to work independently with minimum supervision. 
        Must be able to communicate in writing and verbally all projects' progress. 
        Experience in the mortgage, banking, or finance industries is a plus. 
        This is an onsite role - local candidates are highly desired and will be given first 
        preference.''',
        }

        # Add a skip button for testing
        #skip_button = QPushButton("Skip", self)
        #skip_button.clicked.connect(self.skip_answers)
        #layout.addWidget(skip_button)

        self.setLayout(layout)

    def skip_answers(self):     # A function that is used for faster testing
        # Use the predefined answers when the submit button is clicked
        self.handle_answers(self.predefined_answers)

    def handle_answers(self, answers):
        # Process the answers and generate the optimized resume
        print("Collected Answers:", answers)

        # Save the answers to files and process them
        try:
            resume_folder_path = "resume_optimizer/data/resumes"  
            os.makedirs(resume_folder_path, exist_ok=True)

            # Create resume.txt
            resume_file_path = os.path.join(resume_folder_path, "resume.txt")
            with open(resume_file_path, "w", encoding="utf-8") as resume_file:  # Specify UTF-8 encoding
                resume_file.write("Education:\n" + answers["Education:"] + "\n")
                resume_file.write("\nSkills:\n" + answers["Skills:"] + "\n")
                resume_file.write("\nAwards & Accomplishments:\n" + answers["Awards & Accomplishments:"] + "\n")
                resume_file.write("\nCertifications & Licenses:\n" + answers["Certifications & Licenses:"] + "\n")
                resume_file.write("\nVolunteer & Work Experience:\n" + answers["Volunteer & Work Experience:"] + "\n")

            job_folder_path = "resume_optimizer/data/jobs"  
            os.makedirs(job_folder_path, exist_ok=True)
            job_file_path = os.path.join(job_folder_path, "job.txt")
            with open(job_file_path, "w", encoding="utf-8") as job_file:  # Specify UTF-8 encoding
                job_file.write("Job Title:\n" + answers["Job Title:"] + "\n")
                job_file.write("\nJob Description:\n" + answers["Job Description (including company):"] + "\n")
                job_file.write("\nEssential Duties & Responsibilities:\n" + answers["Essential Duties & Responsibilities:"] + "\n")
                job_file.write("\nRequirements & Qualifications:\n" + answers["Requirements & Qualifications:"] + "\n")

            # Call the `run` function
            result = "\n".join(run(job_file_path, resume_file_path))
            print("Done!")
            self.display_results(result)
        except Exception as e:
            self.display_results(f"An error occurred: {e}")

    def display_results(self, results):
        # Clear the current content by removing the current widget
        if self.stacked_widget.count() > 0:
            self.stacked_widget.removeWidget(self.stacked_widget.currentWidget())

        # Header Section - Layered Title
        self.title_container = QWidget()  # Container for the titles
        self.title_container.setFixedWidth(800)  # Set the width of the container
        self.title_container.setFixedHeight(40)  # Adjust as necessary
        self.title_container.setStyleSheet("background-color: transparent; margin-top: -20px;")  

        # Shared font settings
        title_font = QFont("Coming Soon")
        title_font.setPointSize(50)
        title_font.setBold(True)

        # Yellow shadow (slightly shifted left)
        title_label_shadow = QLabel("afoofa", self.title_container)
        title_label_shadow.setFont(title_font)
        title_label_shadow.setStyleSheet("""
            font-family: 'Coming Soon', sans-serif;
            font-size: 40px;
            color: #FED82D;
            padding: 10px;
        """)
        title_label_shadow.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_label_shadow.move(0, 0)  # Slightly shift to the left

        # Orange main title (centered on top)
        title_label = QLabel("afoofa", self.title_container)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            font-family: 'Coming Soon', sans-serif;
            font-size: 40px;
            color: #FF532B;
            padding: 10px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_label.move(-5, 5)  # Center-aligned relative to the shadow

        # Layout for the title container (centered)
        title_layout = QHBoxLayout()
        title_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align content to the left
        title_layout.addWidget(self.title_container)

        # Add the centered title layout to the main layout
        header_widget = QWidget()
        header_widget.setLayout(title_layout)

        # Subtitle Section
        subtitle_label = QLabel("an app all for one, and one for all students")
        subtitle_font = QFont("Arial")
        subtitle_font.setPointSize(12)
        subtitle_font.setBold(True)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        subtitle_label.setStyleSheet("""
            color: gray;
            margin-top: 0px;
            padding-left: 10px;  /* Adds padding to the left */
        """)

        # Create a main layout and add the title container and subtitle
        main_layout = QVBoxLayout()
        main_layout.addWidget(header_widget)
        main_layout.addWidget(subtitle_label)

        # Create a widget for the header section
        header_section = QWidget()
        header_section.setLayout(main_layout)

        # Create the scrollable container for results
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        # Set the fixed width and height of the scroll area
        scroll_area.setFixedWidth(900)
        scroll_area.setFixedHeight(350)

        # Hide the scrollbars (both vertical and horizontal)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Style to hide the scrollbars but keep the left and right borders colored orange
        scroll_area.setStyleSheet("""
            border-left: 3px solid #FF532B;  
            border-right: 3px solid #FF532B;  
            border-top: none;  
            border-bottom: none;  
            background-color: transparent;  
        """)

        # Display the results
        results_widget = QWidget()
        results_layout = QVBoxLayout()

        results_label = QLabel(results)
        results_label.setStyleSheet("color: #FED82D; padding: 10px; font-weight: bold; background-color: #FF532B;")
        results_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        results_label.setWordWrap(True)

        results_layout.addWidget(results_label)
        # Set up the final layout for the results widget
        results_widget.setLayout(results_layout)

        # Set the widget for the scroll area
        scroll_area.setWidget(results_widget)

        # Create a central layout and center the scroll area
        central_layout = QVBoxLayout()
        central_layout.addWidget(scroll_area, alignment=Qt.AlignmentFlag.AlignCenter)  # Center the scroll area

        # Create a central widget to hold the layout
        central_widget = QWidget()
        central_widget.setLayout(central_layout)

        # Add the header section above the scroll area
        main_layout = QVBoxLayout()
        main_layout.addWidget(header_section)
        main_layout.addWidget(central_widget)

        # Name Label Section (bottom of the screen)
        name_label = QLabel("9akshit1")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("""
            font-family: 'Coming Soon', sans-serif;
            font-size: 15px;
            font-weight: bold;
            color: #FF532B;
            padding: 10px;
        """)

        # Add the name label at the bottom of the main layout
        main_layout.addWidget(name_label, alignment=Qt.AlignmentFlag.AlignBottom)

        # Create a main widget for the display results and set its layout
        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        # Add the main widget to the stacked widget
        self.stacked_widget.addWidget(main_widget)

# Application Writer Window
class ApplicationWriter(QWidget):
    def __init__(self, parent_size):
        super().__init__()
        self.setWindowTitle("Application Writer")
        self.setGeometry(*parent_size)
        self.setStyleSheet("background-color: #ECE0E0;") 
        
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