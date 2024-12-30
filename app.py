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

from sklearn.metrics.pairwise import cosine_similarity
import spacy
import numpy as np

from competition_finder.competition_finder import find_competitions
from resume_optimizer.output import run  
from application_writer.extract import extract_and_generate 

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

# Question Slider Window Class for Input Taking Windows
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
        for question, input_type, *options in self.input_questions:
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
                input_field.addItems(options[0])
                input_field.setFixedHeight(30)  # Match height with other input types
                input_field.setStyleSheet("""
                    border: none;
                    border-bottom: 2px solid #FF532B;
                    background: transparent;
                    color: #FF532B;
                    padding: 5px;
                """)
            elif input_type == "file":
                # Create a widget for the file upload field
                file_upload_container = QWidget()
                file_upload_layout = QVBoxLayout()
                file_upload_container.setLayout(file_upload_layout)

                # File name label (to display the selected file's name)
                file_name_label = QLabel("No file selected")
                file_name_label.setStyleSheet("""
                    font-family: 'Arial';
                    font-size: 14px;
                    color: #555555;
                    padding: 5px;
                """)
                file_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                # File upload button
                file_upload_button = QPushButton("Upload File")
                file_upload_button.setStyleSheet("""
                    QPushButton {
                        background-color: #008CBA;
                        color: white;
                        border-radius: 10px;
                        padding: 10px;
                    }
                    QPushButton:hover {
                        background-color: #005F75;
                    }
                """)

                # Preview label for the uploaded file
                file_preview_label = QLabel()
                file_preview_label.setFixedHeight(100)
                file_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                # Store file path
                file_path = ""

                # Ensure 'user_files' directory exists
                if not os.path.exists("user_files"):
                    os.makedirs("user_files")

                def handle_file_upload():
                    nonlocal file_path
                    file_path, _ = QFileDialog.getOpenFileName(self, "Upload File", "", "All Files (*.*);;PDF Files (*.pdf);;Images (*.png *.jpg)")
                    if file_path:
                        # Update file name label
                        file_name_label.setText(os.path.basename(file_path))

                        # Attempt to preview the file if it's an image
                        image_reader = QImageReader(file_path)
                        if image_reader.canRead():
                            image = image_reader.read()
                            pixmap = QPixmap.fromImage(image)
                            file_preview_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))

                        # Save the file to the user_files directory
                        try:
                            destination_path = os.path.join("user_files", os.path.basename(file_path))
                            with open(file_path, "rb") as source_file:
                                with open(destination_path, "wb") as dest_file:
                                    dest_file.write(source_file.read())
                            print(f"File successfully uploaded to: {destination_path}")
                        except Exception as e:
                            print(f"Error saving file: {e}")

                # Connect button click to the file upload handler
                file_upload_button.clicked.connect(handle_file_upload)

                # Add components to layout
                file_upload_layout.addWidget(file_name_label)
                file_upload_layout.addWidget(file_upload_button)
                file_upload_layout.addWidget(file_preview_label)

                # Add file upload container to the input fields
                input_field = file_upload_container


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
        for idx, (question, input_type, *options) in enumerate(self.input_questions):
            if input_type == "text":
                answers[question] = self.input_fields[idx].text()
            elif input_type == "textarea":
                answers[question] = self.input_fields[idx].toPlainText()
            elif input_type == "combobox":
                answers[question] = self.input_fields[idx].currentText()
            elif input_type == "file":
                # Get the file path or file name
                file_upload_container = self.input_fields[idx]
                file_name_label = file_upload_container.findChild(QLabel)
                answers[question] = "user_files/" + file_name_label.text()  # File name text stored in the label

        # Call the provided callback function with the answers
        self.submit_callback(answers)

# Class for each profile widget for ProfileComparator
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
            font-size: 15px;
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)  # Padding inside the container
        container_layout.setSpacing(10)

        # Profile information
        self.rank_label = QLabel(f"#{rank} Profile")
        self.score_label = QLabel(f"Score: {score:.2%}")
        self.school_label = QLabel(f"School: {profile['school']}")

        # Style for text (12px font size)
        text_style = "color: #FED82D; font-size: 15px;"
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
            font-size: 15px;
        """)
        self.expand_button.clicked.connect(self.expand)
        container_layout.addWidget(self.expand_button, alignment=Qt.AlignmentFlag.AlignBottom)

        # Expanded view content (hidden by default)
        self.details_label = QLabel()
        self.details_label.setStyleSheet("color: #FED82D; font-size: 15px; font-weight: bold;")
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
            font-size: 15px;
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
                f"Similar Items:\n{"\n - ".join(self.similar_items)}\n\n"
                f"Different Items:\n{"\n - ".join(self.different_items)}"
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
                "school": "Ridgemont High School",
                "awards": "Silver Medal, National Chemistry Olympiad (2024)\nFinalist, AI for Social Good Challenge (2024)\nRecipient, Mayor's Civic Award for STEM Outreach (2023)",
                "work_experience": "Machine Learning Intern, AI Future Lab (July 2024 - PRESENT)\nWorked on developing a convolutional neural network (CNN) for medical imaging. Collaborated with a team to preprocess datasets and optimize models for greater prediction accuracy. Reference: Dr. Elena Moore | elena.moore@aifuturelab.org\n\nSTEM Outreach Coordinator, TechEd Society (May 2023 - June 2024)\nDesigned and conducted workshops on coding and AI for underprivileged youth. Secured partnerships with local schools to expand the program reach. Reference: James Watson | james.watson@techedsociety.ca",
                "certifications": "TensorFlow Developer Certificate\nGoogle Data Analytics Professional Certificate",
                "projects": "EcoDrone (July 2024)\nDesigned a drone capable of detecting illegal logging activities using satellite imaging and AI. Achieved 92% accuracy in identifying deforestation patterns through TensorFlow models.\n\nAutoCrop (March 2024)\nDeveloped a Python-based system to automate crop health monitoring using drone imagery. Integrated NDVI analysis for precision agriculture insights.",
                "skills": "Python, TensorFlow, Data Analytics, Public Speaking, Team Collaboration",
                "interests": "Environmental Sustainability, AI for Social Good, STEM Outreach",
                "university": "University of Waterloo",
                "major": "Computer Science"
            },
            {
                "school": "Brookfield High School",
                "awards": "Gold Medal, International Physics Olympiad (2024)\nTop 5 Finalist, International Astronomy & Astrophysics Competition (2023)\nExcellence in Research, Ottawa Science Fair (2023)",
                "work_experience": "Research Assistant, Astrophysics Lab, Carleton University (June 2024 - PRESENT)\nAssisted in data analysis for a study on exoplanet atmospheric conditions. Created Python scripts to process spectral data and visualize results. Reference: Dr. Richard Kent | richard.kent@carleton.ca\n\nPhysics Tutor, Ottawa Youth Tutoring Initiative (September 2023 - May 2024)\nProvided weekly one-on-one tutoring sessions for high school students struggling with physics concepts. Reference: Sarah Lin | sarah.lin@oyti.ca",
                "certifications": "Advanced Python Programming Certificate\nIntroduction to Astrophysics by edX",
                "projects": "Stellar Spectroscopy Analyzer (April 2024)\nDeveloped a Python-based tool to analyze and classify star types using spectral data. Presented findings at the Regional Science Fair.\n\nPlanetarium VR (October 2023)\nDesigned an immersive VR application that simulates star-gazing experiences based on real-time celestial data. Integrated Unity and C# for the project.",
                "skills": "Python, Data Visualization, C#, Public Speaking, Research Methodologies",
                "interests": "Astronomy, Physics, Data Science, VR Development",
                "university": "Carleton University",
                "major": "Astrophysics"
            },
            {
                "school": "Lisgar Collegiate Institute",
                "awards": "Bronze Medal, Canadian Biology Olympiad (2024)\nBest Project Award, National Youth Innovation Challenge (2023)\nDean’s List, Honor Roll for Academic Excellence (2023)",
                "work_experience": "Lab Intern, Ottawa General Hospital (July 2024 - PRESENT)\nConducted PCR and ELISA tests in a clinical lab setting. Assisted with patient data entry and analysis. Reference: Dr. Elena Roberts | elena.roberts@ogh.ca\n\nVolunteer Coordinator, Green Earth Organization (May 2023 - June 2024)\nOrganized tree-planting drives and community clean-up events. Managed over 50 volunteers per event. Reference: James Howard | james.howard@greenearth.org",
                "certifications": "Medical Laboratory Assistant Certification\nBiology Essentials for Healthcare Professionals by Coursera",
                "projects": "Gene Editing Simulation (June 2024)\nCreated an educational tool to simulate CRISPR gene-editing processes. Used Python and Flask for backend development.\n\nUrban Ecology Mapping (January 2024)\nCollaborated with local NGOs to map biodiversity in urban parks. Developed an interactive web-based visualization using JavaScript and Leaflet.js.",
                "skills": "Python, Biology Lab Techniques, Flask, Leadership, Communication",
                "interests": "Genetics, Ecology, Community Service, Data Visualization",
                "university": "University of Waterloo",
                "major": "Biology and Environmental Science"
            },
                {
                "school": "Canterbury High School",
                "awards": "National Young Composers Award (2024)\n1st Place, Provincial Robotics Competition (2023)\nArtistic Excellence Award, Ottawa Arts Festival (2023)",
                "work_experience": "Composer Intern, Ottawa Symphony Orchestra (June 2024 - PRESENT)\nWorked with senior composers to develop modern orchestral pieces. Coordinated live rehearsals and provided feedback for musicians. Reference: Anna Tchaikovsky | anna.t@ottawasymphony.ca\n\nRobotics Club Mentor, Canterbury High Robotics (September 2023 - June 2024)\nGuided junior members in programming and mechanical design. Helped the team secure first place in the provincial competition. Reference: Mark Stevenson | mark.stevenson@canterburyrobotics.ca",
                "certifications": "Music Theory and Composition Certificate\nArduino Robotics Certification",
                "projects": "Symphonic AI (August 2024)\nDeveloped an AI-driven software that generates orchestral compositions based on input parameters. Used Python and TensorFlow for AI training.\n\nSmart Plant System (February 2024)\nDesigned an Arduino-based automated watering system for houseplants. Created a companion mobile app using Flutter for real-time monitoring.",
                "skills": "Python, TensorFlow, Music Composition, Arduino, Leadership",
                "interests": "Music, Robotics, AI, Sustainability",
                "university": "University of Waterloo",
                "major": "Engineering and Music Technology"
            },
            {
                "school": "Gloucester High School",
                "awards": "Top Innovator Award, National Business Challenge (2024)\n1st Place, Local Hackathon for Sustainable Solutions (2023)\nRecipient, Entrepreneurial Leadership Award (2023)",
                "work_experience": "Startup Founder, GreenSolutions (March 2024 - PRESENT)\nLaunched a startup focused on creating sustainable packaging solutions. Secured seed funding and partnerships with local businesses. Reference: John Edwards | john.edwards@greensolutions.com\n\nIntern, Ottawa Economic Development Agency (May 2023 - February 2024)\nAssisted in drafting proposals for local business grants. Conducted market research to support policy recommendations. Reference: Sarah Wright | sarah.wright@ottawaeda.ca",
                "certifications": "Sustainable Business Practices by LinkedIn Learning\nIntermediate Java Programming Certificate",
                "projects": "EcoPack (June 2024)\nDeveloped biodegradable packaging material using plant-based polymers. Created prototypes and performed market testing.\n\nBizPlan App (October 2023)\nBuilt a web app to help small businesses generate business plans. Used JavaScript for front-end development and Node.js for the backend.",
                "skills": "JavaScript, Node.js, Entrepreneurship, Market Analysis, Leadership",
                "interests": "Business Development, Sustainability, Programming",
                "university": "University of Waterloo",
                "major": "Commerce"
            },
                {
                "school": "Nepean High School",
                "awards": "Gold Medal, National Math Olympiad (2024)\nBest Research Paper, Youth AI Conference (2023)\nHonor Roll, Academic Excellence Award (2023)",
                "work_experience": "Data Science Intern, AnalyticsLab (July 2024 - PRESENT)\nDeveloped predictive models using Python and R to analyze market trends. Presented insights to stakeholders to guide business strategies. Reference: Dr. Emily Tran | emily.tran@analyticslab.com\n\nTeaching Assistant, MathEnrichment Academy (September 2023 - June 2024)\nProvided group tutoring for advanced calculus and linear algebra. Assisted in curriculum development for summer programs. Reference: Michael Lee | michael.lee@mathenrichment.ca",
                "certifications": "Data Science Professional Certificate by IBM\nAdvanced R Programming Certification",
                "projects": "Stock Market Predictor (May 2024)\nBuilt a machine learning model to predict stock price movements using historical data. Utilized Python libraries like scikit-learn and pandas.\n\nAI Tutor (December 2023)\nCreated an AI chatbot for math tutoring. Integrated natural language processing techniques to provide real-time explanations.",
                "skills": "Python, R, Data Analysis, Machine Learning, Public Speaking",
                "interests": "Data Science, Mathematics, AI Development",
                "university": "University of Waterloo",
                "major": "Data Science"
            },
            {
                "school": "St. Patrick's High School",
                "awards": "1st Place, National Debating Championships (2024)\nOutstanding Achievement Award, Model UN (2023)\nPublic Speaking Champion, Regional Toastmasters Competition (2023)",
                "work_experience": "Policy Research Intern, Ottawa City Hall (June 2024 - PRESENT)\nAnalyzed local housing policies and drafted reports to propose improvements. Collaborated with teams on urban planning projects. Reference: Maria Sanchez | maria.sanchez@ottawacityhall.ca\n\nDebate Coach, St. Patrick’s Debate Club (September 2023 - June 2024)\nTrained junior debaters in argumentation techniques. Organized and judged regional debate tournaments. Reference: Rachel Cooper | rachel.cooper@stpatricks.ca",
                "certifications": "Public Policy Essentials by edX\nAdvanced Communication Skills by Coursera",
                "projects": "Affordable Housing Plan (April 2024)\nCollaborated with peers to draft a comprehensive housing plan for Ottawa, focusing on low-income families. Presented to city officials.\n\nDebate Strategy Guide (October 2023)\nAuthored a guide on effective debating techniques, distributed as a resource in provincial debate clubs.",
                "skills": "Public Speaking, Research, Policy Analysis, Leadership, Collaboration",
                "interests": "Public Policy, Debate, Urban Planning, Community Development",
                "university": "University of Waterloo",
                "major": "Political Science"
            },
            {
                "school": "Sir Wilfrid Laurier Secondary School",
                "awards": "Regional Winner, Canadian Young Innovators Challenge (2024)\nExcellence in Coding, National Hackathon (2023)\nTop 3 Finalist, Regional Science Fair (2023)",
                "work_experience": "Software Developer Intern, CodeSpark Inc. (July 2024 - PRESENT)\nDeveloped mobile app features using React Native. Enhanced user experience by optimizing app loading times. Reference: Alex Johnson | alex.johnson@codespark.com\n\nCamp Counselor, STEM Summer Camp (June 2023 - August 2023)\nTaught coding and robotics to children aged 8-14. Designed engaging STEM-related activities and competitions. Reference: Lisa Martin | lisa.martin@stemcamp.ca",
                "certifications": "Full-Stack Web Development by Udemy\nReact Native Advanced Training Certificate",
                "projects": "EcoTracker App (May 2024)\nCreated a mobile app to help users track and reduce their carbon footprint. Implemented APIs for real-time environmental data.\n\nHealthMonitor (November 2023)\nDeveloped a smartwatch app to monitor heart rate and alert users of irregularities. Used Swift for development.",
                "skills": "React Native, Swift, App Development, Team Collaboration, Creativity",
                "interests": "Mobile Development, Robotics, Environmental Technology",
                "university": "University of Waterloo",
                "major": "Software Engineering"
            },
            {
                "school": "Colonel By Secondary School",
                "awards": "Bronze Medal, International Biology Olympiad (2024)\nBest Poster Presentation, National Science Fair (2023)\nRecipient, STEM Excellence Scholarship (2023)",
                "work_experience": "Research Assistant, Ottawa Molecular Biology Lab (July 2024 - PRESENT)\nAssisted in conducting experiments on gene editing using CRISPR technology. Analyzed and documented research findings for publication. Reference: Dr. Claire Bernard | claire.bernard@molecularlab.ca\n\nTutor, BioGenius Academy (September 2023 - June 2024)\nTutored high school students in advanced biology and chemistry. Designed interactive lessons to simplify complex topics. Reference: Jenna Tan | jenna.tan@biogenius.com",
                "certifications": "Genomics and Biotechnology Certificate by edX\nAdvanced Biostatistics by Coursera",
                "projects": "CRISPR-Driven Gene Therapy (March 2024)\nCollaborated on a project to study the application of CRISPR in treating genetic disorders. Used bioinformatics tools to analyze DNA sequences.\n\nSustainable Farming Solutions (December 2023)\nDeveloped an experiment to optimize crop yield using organic fertilizers. Results presented at the National Science Fair.",
                "skills": "Molecular Biology, Bioinformatics, Data Analysis, Teaching, Presentation Skills",
                "interests": "Genetic Engineering, Environmental Sustainability, Public Health",
                "university": "University of Waterloo",
                "major": "Molecular Biology and Genetics"
            },
            {
                "school": "Earl of March Secondary School",
                "awards": "1st Place, National Robotics Championship (2024)\nInnovation Award, Regional Coding Competition (2023)\nRecipient, Governor General’s Academic Medal (2023)",
                "work_experience": "Robotics Engineer Intern, TechNova Robotics (June 2024 - PRESENT)\nDeveloped autonomous systems for industrial robots. Improved navigation algorithms for efficiency in warehouse settings. Reference: Paul Jenkins | paul.jenkins@technova.com\n\nFreelance Web Developer (January 2023 - May 2024)\nBuilt custom websites for small businesses. Focused on responsive design and e-commerce integrations. Reference: Olivia Harper | olivia.harper@webworks.ca",
                "certifications": "Advanced Robotics Programming by Udacity\nCertified Web Developer by FreeCodeCamp",
                "projects": "Drone Delivery System (April 2024)\nDesigned and programmed an autonomous drone for small package deliveries. Implemented GPS and computer vision for navigation.\n\nE-Commerce Website Template (July 2023)\nCreated a customizable website template for small businesses. Features included payment gateway integration and analytics.",
                "skills": "C++, Python, Computer Vision, Web Development, Problem-Solving",
                "interests": "Robotics, AI, Web Development, Entrepreneurship",
                "university": "University of Waterloo",
                "major": "Mechatronics Engineering"
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
        #skip_button = QPushButton("Skip", self)
        #skip_button.clicked.connect(self.skip_answers)
        #layout.addWidget(skip_button)

        self.setLayout(layout)

    def skip_answers(self):     # A function that is used for faster testing
        # Use the predefined answers when the submit button is clicked
        self.handle_inputs(self.predefined_answers)

    def handle_inputs(self, inputs):
        print(inputs)
        self.process_comparison(inputs)

    def clean_text(self, text):
        text = re.sub(r"[\t•-]+", "\n", text)  # Replace newlines, tabs, and bullets with a newline
        return text

    def midlevel_calculate_similarity(self, user_keywords, dataset_keywords):
        matches = sum(1 for word in user_keywords if word in dataset_keywords)    
        total = len(user_keywords) + len(dataset_keywords)
        return (2 * matches) / total if total > 0 else 0     #weird calcualtion but it works i guess

    def calculate_similarity(self, user_keywords, dataset_keywords):
        # Check if either list is empty
        if not user_keywords or not dataset_keywords:
            return 0.0  # Return 0 similarity if either list is empty

        # Load a lightweight spaCy model
        nlp = spacy.load('en_core_web_sm')  # You can use "en_core_web_md" for better accuracy
        
        # Embed each keyword list into a combined vector
        def embed_list(keywords):
            embeddings = [nlp(keyword).vector for keyword in keywords if nlp(keyword).vector.any()]
            return np.mean(embeddings, axis=0) if embeddings else np.zeros((nlp.vocab.vectors_length,))
        
        embedding1 = embed_list(user_keywords)
        embedding2 = embed_list(dataset_keywords)
        
        # Compute cosine similarity
        similarity = cosine_similarity([embedding1], [embedding2])[0][0]
        
        # Scale similarity to range [0, 1] (optional)
        similarity_scaled = (similarity + 1) / 2
        
        return similarity_scaled

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

    def split_experiences(self, text, category):
        if category in ["work_experience", "projects"]:
            return re.split(r"\n\n", text.strip())    #seaprates sections when there is a full line space
        elif category in ["awards", "certifications"]:
            return re.split(r"\n", text.strip())    #seaprates sections when there is a just a next line

    def process_comparison(self, user_original_profile):
        weights = {
            "school": 0.01,
            "awards": 0.25,
            "work_experience": 0.25,
            "certifications": 0.1,
            "projects": 0.2,
            "skills": 0.1,
            "interests": 0.01,
            "major": 0.03
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
            
                if category in ["awards", "work_experience", "certifications", "projects"]:
                    user_sections = self.split_experiences(user_text, category)
                    dataset_sections = self.split_experiences(dataset_text, category)
                    for user_section in user_sections:
                        u_section_kw = self.extract_keywords(user_section)
                        user_keywords[category].append([u_section_kw, user_section])
                    for dataset_section in dataset_sections:
                        d_section_kw = self.extract_keywords(dataset_section)
                        dataset_keywords[category].append([d_section_kw, dataset_section])
                else:
                    user_keywords[category] = self.extract_keywords(user_profile[category])
                    dataset_keywords[category] = self.extract_keywords(profile[category])

            total_score = 0
            similar_items = []
            different_items = []
            for category in user_keywords:
                print(f"-----------------{category}-----------------")
                if isinstance(user_keywords[category][0], list):
                    category_scores = []
                    highest_scores = []
                    for i in range(0, len(user_keywords[category])):
                        u_section_kw = user_keywords[category][i][0]
                        u_section = user_keywords[category][i][1]
                        print("\nUser section:", u_section)
                        print("KEYWORDS:", u_section_kw)
                        for i in range(0, len(dataset_keywords[category])):
                            d_section_kw = dataset_keywords[category][i][0]
                            d_section = dataset_keywords[category][i][1]
                            print("\nDataset section:", d_section)
                            print("KEYWORDS:", d_section_kw)
                            similarity = self.calculate_similarity(u_section_kw, d_section_kw)
                            print("Similarity:", similarity)
                            category_scores.append(similarity)    
                        highest_score = max(category_scores)
                        print("Highest score:", highest_score)
                        highest_scores.append(highest_score)
                        if highest_score >= 0.5:
                            similar_items.append(u_section)
                        else:
                            different_items.append(u_section)
                    avg_score = sum(highest_scores) / len(highest_scores)
                    print("Average Score:", avg_score)
                    total_score += avg_score * weights[category] if category_scores else 0
                else:
                    avg_score = self.calculate_similarity(user_keywords[category], dataset_keywords[category])
                    total_score += avg_score * weights[category]
                    if avg_score >= 0.5:
                        similar_items.append(user_profile[category])
                    else:
                        different_items.append(user_profile[category])
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
            ("Enter Interests (if multiple, separate with comma + space):", "textarea"),
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
        results = find_competitions(answers["Enter City:"], answers["Enter State/Province:"], answers["Enter Country:"], answers["Enter Age:"], answers["Enter Interests (if multiple, separate with comma + space):"], answers["Enter Current Education Status:"])
        
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
            result = run(job_file_path, resume_file_path)
            self.display_results(result)
        except Exception as e:
            self.display_results(f"An error occurred: {e}")

    def display_results(self, results):
        # Clear the current content by removing the current widget
        if self.stacked_widget.count() > 0:
            self.stacked_widget.removeWidget(self.stacked_widget.currentWidget())

        self.results = results

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

        # Content Section
        central_layout = QVBoxLayout()

        # Title Label
        result_title_label = QLabel(results[0] if results else "No Results")
        result_title_label.setStyleSheet("""
            font-size: 20px; font-weight: bold; color: #FF532B; 
            background-color: #FED82D; border-radius: 20px;
            padding: 10px;
        """)
        result_title_label.setFixedSize(430, 45)
        result_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        central_layout.addWidget(result_title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Scrollable content area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedSize(850, 300)
        scroll_area.setStyleSheet("""
            border: 3px solid #FF532B;
            background-color: #FF532B;
            border-radius: 20px 20px 20px 20px;
        """)

        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        scroll_area.setWidget(self.results_widget)

        # Buttons for navigating results
        buttons_widget_left = QWidget()  # Left buttons
        buttons_layout_left = QVBoxLayout(buttons_widget_left)

        buttons_widget_right = QWidget()  # Right buttons
        buttons_layout_right = QVBoxLayout(buttons_widget_right)

        button_labels = ["Skill Report", "Similar Skills", "Acronyms", "Action Words"]

        for i in range(1, len(results)):
            button = QPushButton(button_labels[i - 1])
            button.setStyleSheet("""
                background-color: #FF532B; color: #FED82D;
                font-size: 14px; font-weight: bold; border-radius: 20px;
                height: 40px;
            """)
            button.clicked.connect(lambda _, idx=i: self.display_result(idx))

            if i % 2 == 1:  # Alternate buttons to left and right
                buttons_layout_left.addWidget(button)
            else:
                buttons_layout_right.addWidget(button)

        buttons_widget_left.setFixedWidth(150)  # Limit width of left button container
        buttons_widget_right.setFixedWidth(150)  # Limit width of right button container

        # Horizontal Layout for Buttons and Scroll Area
        horizontal_layout = QHBoxLayout()

        # Add left buttons, scroll area, and right buttons in a horizontal layout
        horizontal_layout.addWidget(buttons_widget_left)
        horizontal_layout.addWidget(scroll_area)
        horizontal_layout.addWidget(buttons_widget_right)

        # Set stretching for central layout
        horizontal_layout.setStretch(0, 1)  # Allow left buttons to take some space
        horizontal_layout.setStretch(1, 3)  # Allow scroll area to take more space
        horizontal_layout.setStretch(2, 1)  # Allow right buttons to take some space

        # Central Layout
        central_layout.addWidget(result_title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        central_layout.addLayout(horizontal_layout)
        central_layout.setAlignment(horizontal_layout, Qt.AlignmentFlag.AlignCenter)


        central_widget = QWidget()
        central_widget.setLayout(central_layout)

        main_layout.addWidget(central_widget)

        # Footer Section
        footer_label = QLabel("9akshit1")
        footer_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #FF532B;")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(footer_label, alignment=Qt.AlignmentFlag.AlignBottom)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.stacked_widget.addWidget(main_widget)

    def display_result(self, idx):
        # Clear existing widgets in results layout
        for i in reversed(range(self.results_layout.count())):
            self.results_layout.itemAt(i).widget().deleteLater()

        # Add selected result content
        result_label = QLabel(self.results[idx])
        result_label.setStyleSheet("""
            color: #FED82D; font-size: 14px; font-weight: bold; padding: 10px;
        """)
        result_label.setWordWrap(True)
        self.results_layout.addWidget(result_label)

# Application Writer Window
class ApplicationWriter(QWidget):
    def __init__(self, parent_size):
        super().__init__()
        self.setWindowTitle("Application Writer")
        self.setGeometry(*parent_size)
        self.setStyleSheet("background-color: #ECE0E0;")  

        layout = QVBoxLayout()

        # Stacked widget to switch between screens
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Input questions setup
        input_questions = [
            ("Provide Resume Document:", "file"),
            ("Provide Questions:", "textarea"),
            ("Choose Style (optional):", "combobox", ["Formal", "Casual"])
        ]

        self.question_slider = QuestionSlider(input_questions, self.handle_answers, self)
        self.stacked_widget.addWidget(self.question_slider)

        # Set the layout for the application writer window
        self.setLayout(layout)

    def handle_answers(self, answers):
        # Process the answers and create application responses
        print("Collected Answers:", answers)

        # Call a function to generate the application based on inputs
        documents = answers.get("Provide Resume Document:")
        questions = answers.get("Provide Questions:")
        style = answers.get("Choose Style (optional):")

        results = self.generate_application(documents, questions, style)

        # Display results on the same window after questions are completed
        self.display_results(results)

    def generate_application(self, documents, questions, style):
        data = {
                "uploaded_files": documents,
                "questions": questions.split("?"),
                "style": style
            }
        return extract_and_generate(data)

        # Placeholder for application generation logic
        return {"Question 1" : "Generated response for question 1.", 
                "Question 2" : "Generated response for question 2."}

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
            background-color: transparent;  
        """)

        # Create the result widget and layout
        results_widget = QWidget()
        results_layout = QVBoxLayout()
        results_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align the results layout

        # Style for each question container (orange background)
        question_style = """
            background-color: #FF532B;  
            border: none;
            padding: 10px;
            margin: 0;  
            border-radius: 50px 50px 50px 50px;  
            font-family: 'Arial';
            font-size: 16px;
            font-weight: bold;
            color: #FFDD00; 
            width: 850px;
        """

        # Style for each answer container (darker orange background)
        answer_style = """
            background-color: #E34B22;  
            border: none;
            padding: 10px;
            margin: 0;  
            margin-top: -50px;
            margin-left: 15px;  
            border-radius: 20px 20px 0 0;  
            font-family: 'Arial';
            font-size: 13px;
            font-weight: bold;
            color: #FFDD00; 
            width: 800px;  
        """

        for idx, (question, answer) in enumerate(results.items()):  # Assuming `results` is a dictionary with questions as keys and answers as values
            # Create a container for both the question and answer (no space in between)
            container_widget = QWidget()

            # Create a layout to hold the question and answer labels inside the container
            container_layout = QVBoxLayout()
            container_layout.setSpacing(0)  # No space between the question and answer
            container_layout.setContentsMargins(0, 0, 0, 0)  # Remove all margins

            # Create a label for the question with the appropriate style
            question_label = QLabel(f"Q{idx+1}: {question}")
            question_label.setStyleSheet(question_style)
            question_label.setWordWrap(True)  # Allow multiline text
            question_label.setFixedWidth(1175)  # Set the width of the question rectangle
            question_label.setFixedHeight(35)  # Set the height of the question rectangle

            # Create a label for the answer with the appropriate style
            answer_label = QLabel(f"{answer}")
            answer_label.setStyleSheet(answer_style)
            answer_label.setWordWrap(True)  # Allow multiline text
            answer_label.setFixedWidth(1160)  # Set the width of the answer rectangle

            # Add the question and answer labels to the layout (tightly packed with no space between)
            container_layout.addWidget(question_label)
            container_layout.addWidget(answer_label)

            # Set the layout to the container widget
            container_widget.setLayout(container_layout)

            # Add the container widget to the results layout
            results_layout.addWidget(container_widget)

        # Remove borders or padding from the main container to avoid any outer edges
        results_widget.setStyleSheet("border: none; padding: 0;")

        results_widget.setLayout(results_layout)
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

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainApp()
    main_window.show()

    sys.exit(app.exec())
