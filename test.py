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
    QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QMessageBox,
    QPushButton, QWidget, QFileDialog, QLineEdit, QTextEdit, QComboBox, QScrollArea, QFormLayout, QGridLayout, QStackedLayout, QProgressBar, QStackedWidget, QHBoxLayout, QSpacerItem, QSizePolicy
)

from competition_finder.competition_finder import find_competitions
from resume_optimizer.output import run  

# Assuming QuestionSlider is in the same file or imported from another file
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
                "questions": questions,
                "style": style
            }
        #return subprocess.run(["python", "application_writer/extract.py"], input=str(data), text=True)

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
            margin-top: -75px;
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
            answer_label = QLabel(f"A: {answer}")
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

# Entry point for the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ApplicationWriter((100, 100, 600, 400))  # Example window size
    window.show()
    sys.exit(app.exec())
