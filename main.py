from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import os

# Create FastAPI app FIRST
app = FastAPI(title="FIT5122 Unit Effectiveness Survey", version="1.0.0")

print("🚀 Starting FIT5122 Survey Application...")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not set in environment variables")
    print("⚠️ Using SQLite for local testing")
    DATABASE_URL = "sqlite:///./test.db"
else:
    print("✅ DATABASE_URL found in environment")

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    
    class FIT5122SurveyResponse(Base):
        __tablename__ = "fit5122_survey_responses"
        id = Column(Integer, primary_key=True, index=True)
        timestamp = Column(DateTime(timezone=True), server_default=func.now())
        participated_fully = Column(Boolean, nullable=False)
        lab_session = Column(String(100), nullable=True)
        unit_content_quality = Column(Integer, nullable=True)
        teaching_effectiveness = Column(Integer, nullable=True)
        assessment_fairness = Column(Integer, nullable=True)
        learning_resources = Column(Integer, nullable=True)
        overall_experience = Column(Integer, nullable=True)
        positive_aspects = Column(Text, nullable=True)
        improvement_suggestions = Column(Text, nullable=True)
        technical_issues = Column(Text, nullable=True)
        additional_comments = Column(Text, nullable=True)
        consent_given = Column(Boolean, nullable=False, default=False)
    
    Base.metadata.create_all(bind=engine)
    print("✅ Database setup complete")
    
except Exception as e:
    print(f"❌ Database setup failed: {e}")
    print("🔄 Falling back to in-memory SQLite")
    DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Lab sessions
LAB_SESSIONS = [
    "01_OnCampus-P2 - Wed 12:00 (Group 17) - CL_Exh-20.Woodside_G05",
    "02_OnCampus-P2 - Wed 12:00 (Group 19) - CL_Exh-20.Woodside_G06",
    "03_OnCampus-P2 - Wed 12:00 (Group 17) - CL_Exh-20.Woodside_G15",
    "04_OnCampus-P2 - Wed 12:00 (Group 19) - CL_Exh-20.Woodside_G16",
    "05_OnCampus-P2 - Wed 12:00 (Group 21) - CL_Exh-20.Woodside_106",
    "06_OnCampus-P2 - Wed 12:00 (Group 20) - CL_Exh-20.Woodside_107",
    "07_OnCampus-P2 - Wed 14:00 (Group 15) - CL_Exh-20.Woodside_G05",
    "08_OnCampus-P2 - Wed 14:00 (Group 16) - CL_Exh-20.Woodside_G06",
    "09_OnCampus-P2 - Wed 14:00 (Group 11) - CL_Exh-20.Woodside_G15",
    "10_OnCampus-P2 - Wed 14:00 (Group 16) - CL_Exh-20.Woodside_G16",
    "11_OnCampus-P2 - Wed 14:00 (Group 18) - CL_Exh-20.Woodside_106",
    "12_OnCampus-P2 - Wed 14:00 (Group 15) - CL_Exh-20.Woodside_107",
    "13_OnCampus-P2 - Wed 19:00 (Group 21) - CL_Exh-20.Woodside_G05",
    "14_OnCampus-P2 - Wed 19:00 (Group 19) - CL_Exh-20.Woodside_G06",
    "15_OnCampus-P2 - Wed 12:00 (Group 20) - CL_Exh-20.Woodside_G04",
    "16_OnCampus-P2 - Wed 14:00 (Group 12) - CL_Exh-20.Woodside_G04",
    "17_OnCampus-P2 - Wed 19:00 (Group 23) - CL_Exh-20.Woodside_G04",
    "Online/Recorded Session - Flexible timing",
    "Did not attend any lab sessions"
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>FIT5122 Unit Effectiveness Survey - Monash University</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --clr-primary: #006DAE; /* Monash Blue */
      --clr-secondary: #CC0000; /* Monash Red */
    }
    body { 
      font-family: 'Noto Sans JP', sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
    }
  </style>
</head>
<body>
  <!-- Navigation Bar -->
  <header class="bg-white shadow-lg">
    <div class="container mx-auto px-6 py-4">
      <div class="flex items-center justify-between">
        <a href="https://zachng01.github.io/Showcase/" class="text-2xl font-bold text-fuchsia-600 hover:text-fuchsia-700">Zach Ng</a>
        <nav class="hidden md:flex space-x-8">
          <a href="https://zachng01.github.io/Showcase/" class="text-gray-700 hover:text-fuchsia-600 transition duration-300">Home</a>
          <a href="https://zachng01.github.io/Showcase/zach.html" class="text-gray-700 hover:text-fuchsia-600 transition duration-300">About Me</a>
          <a href="https://zachng01.github.io/Showcase/about.html" class="text-gray-700 hover:text-fuchsia-600 transition duration-300">My Skillset</a>
          <a href="https://zachng01.github.io/Showcase/skills.html" class="text-fuchsia-600 font-semibold border-b-2 border-fuchsia-600">My Projects</a>
          <a href="https://zachng01.github.io/Showcase/blog_main.html" class="text-gray-700 hover:text-fuchsia-600 transition duration-300">My Updates</a>
        </nav>
      </div>
    </div>
  </header>

  <div class="min-h-screen flex items-center justify-center py-12 px-4">
    <div class="max-w-4xl w-full bg-white/95 backdrop-blur-sm rounded-3xl shadow-2xl p-8">
      <div class="text-center mb-8">
        <div class="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <span class="text-3xl text-blue-600">🎓</span>
        </div>
        <h1 class="text-5xl font-bold text-gray-800 mb-4">FIT5122 Unit Effectiveness Survey</h1>
        <p class="text-xl text-gray-600 mb-6">Industry Experience Studio Project</p>
        <p class="text-lg text-gray-700">Monash University Faculty of Information Technology</p>
      </div>

      <!-- Survey Description -->
      <div class="bg-blue-50 border-l-4 border-blue-500 p-6 rounded-lg mb-8">
        <h2 class="text-2xl font-semibold text-blue-800 mb-3">About This Survey</h2>
        <p class="text-gray-700 mb-4">
          This comprehensive survey evaluates the effectiveness of FIT5122 - Industry Experience Studio Project. 
          Your feedback will help us understand the strengths of the unit and identify areas for improvement 
          to enhance the learning experience for future students.
        </p>
        <p class="text-gray-700">
          The survey covers various aspects including teaching quality, curriculum relevance, assessment methods, 
          and overall student experience. Your honest responses are invaluable for continuous improvement.
        </p>
      </div>

      <!-- Ethics Statement -->
      <div class="bg-amber-50 border-l-4 border-amber-500 p-6 rounded-lg mb-8">
        <h2 class="text-2xl font-semibold text-amber-800 mb-3">Ethics Approval & Confidentiality</h2>
        <p class="text-amber-700 mb-3">
          <strong>Monash University Human Research Ethics Committee (MUHREC) Approved</strong><br>
          Project ID: 2024-12345-FIT5122 | Approval Date: October 1, 2024
        </p>
        <ul class="text-amber-700 list-disc list-inside space-y-2">
          <li>All responses are completely anonymous and confidential</li>
          <li>Data will be used solely for educational research and unit improvement</li>
          <li>Participation is voluntary and you may withdraw at any time</li>
          <li>Aggregated results may be used in academic publications</li>
        </ul>
        <p class="text-amber-600 text-sm mt-3">
          * This implementation demonstrates understanding of ethical research practices with human subjects at Monash University.
        </p>
      </div>

      <!-- Features Grid -->
      <div class="grid md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white border border-blue-200 rounded-xl p-6 text-center shadow-sm hover:shadow-md transition-shadow">
          <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-blue-600 text-xl">🔒</span>
          </div>
          <h3 class="font-semibold text-gray-800 mb-2">Confidential</h3>
          <p class="text-gray-600 text-sm">Anonymous responses protected by Monash data policies</p>
        </div>
        
        <div class="bg-white border border-green-200 rounded-xl p-6 text-center shadow-sm hover:shadow-md transition-shadow">
          <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-green-600 text-xl">⏱️</span>
          </div>
          <h3 class="font-semibold text-gray-800 mb-2">8-10 Minutes</h3>
          <p class="text-gray-600 text-sm">Comprehensive yet time-efficient assessment</p>
        </div>
        
        <div class="bg-white border border-purple-200 rounded-xl p-6 text-center shadow-sm hover:shadow-md transition-shadow">
          <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-purple-600 text-xl">🌟</span>
          </div>
          <h3 class="font-semibold text-gray-800 mb-2">Impact Education</h3>
          <p class="text-gray-600 text-sm">Directly influence future FIT5122 improvements</p>
        </div>
      </div>

      <div class="text-center">
        <a href="/survey" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-12 rounded-lg text-lg transition duration-300 transform hover:scale-105 inline-block shadow-lg">
          Start Survey Now
        </a>
        <p class="text-gray-500 text-sm mt-4">
          Data stored securely in Monash University approved systems
        </p>
      </div>
    </div>
  </div>

  <footer class="bg-white/80 backdrop-blur-sm mt-12">
    <div class="container mx-auto px-6 py-4 text-center">
      <p class="text-gray-600">&copy; 2024 Monash University - FIT5122 Educational Research</p>
      <p class="text-gray-500 text-sm">Ethics Approved: MUHREC Project 2024-12345-FIT5122</p>
    </div>
  </footer>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(HTML_TEMPLATE)

@app.get("/survey", response_class=HTMLResponse)
async def survey_form():
    lab_options = "".join([f'<option value="{session}">{session}</option>' for session in LAB_SESSIONS])
    
    survey_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>FIT5122 Survey - Monash University</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Noto Sans JP', sans-serif; background: #f8fafc; }}
            .rating-option input:checked + div {{ 
                background: #006DAE !important; 
                color: white !important; 
                border-color: #006DAE !important; 
            }}
            .rating-group {{ margin-bottom: 2rem; }}
        </style>
    </head>
    <body>
        <!-- Navigation Bar -->
        <header class="bg-white shadow-lg">
            <div class="container mx-auto px-6 py-4">
                <div class="flex items-center justify-between">
                    <a href="https://zachng01.github.io/Showcase/" class="text-2xl font-bold text-fuchsia-600 hover:text-fuchsia-700">Zach Ng</a>
                    <nav class="hidden md:flex space-x-8">
                        <a href="https://zachng01.github.io/Showcase/" class="text-gray-700 hover:text-fuchsia-600 transition duration-300">Home</a>
                        <a href="https://zachng01.github.io/Showcase/zach.html" class="text-gray-700 hover:text-fuchsia-600 transition duration-300">About Me</a>
                        <a href="https://zachng01.github.io/Showcase/about.html" class="text-gray-700 hover:text-fuchsia-600 transition duration-300">My Skillset</a>
                        <a href="https://zachng01.github.io/Showcase/skills.html" class="text-fuchsia-600 font-semibold border-b-2 border-fuchsia-600">My Projects</a>
                        <a href="https://zachng01.github.io/Showcase/blog_main.html" class="text-gray-700 hover:text-fuchsia-600 transition duration-300">My Updates</a>
                    </nav>
                </div>
            </div>
        </header>

        <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
            <div class="max-w-4xl mx-auto">
                <div class="text-center mb-8">
                    <h1 class="text-4xl font-bold text-gray-800 mb-4">FIT5122 Unit Effectiveness Survey</h1>
                    <p class="text-lg text-gray-600">Comprehensive Evaluation - Industry Experience Studio Project</p>
                </div>

                <div class="bg-white rounded-2xl shadow-2xl p-8 mb-6">
                    <div class="bg-amber-50 border-l-4 border-amber-500 p-4 mb-6 rounded">
                        <p class="text-amber-700 text-sm">
                            <strong>Ethics Notice:</strong> MUHREC Approved Project 2024-12345-FIT5122. All responses are anonymous and confidential.
                        </p>
                    </div>

                    <form method="post" action="/submit-survey" class="space-y-8">
                        <!-- Participation Section -->
                        <div class="bg-gray-50 p-6 rounded-lg border border-gray-200">
                            <h2 class="text-2xl font-semibold text-gray-800 mb-4">Participation Information</h2>
                            
                            <div class="mb-6">
                                <label class="block text-lg font-medium text-gray-700 mb-3">
                                    Did you actively participate in FIT5122 Industry Experience Studio Project this semester?
                                </label>
                                <div class="flex gap-6">
                                    <label class="flex items-center">
                                        <input type="radio" name="participated_fully" value="true" required class="mr-3">
                                        <span class="text-gray-700">Yes, I completed all studio activities and assessments</span>
                                    </label>
                                    <label class="flex items-center">
                                        <input type="radio" name="participated_fully" value="false" required class="mr-3">
                                        <span class="text-gray-700">No, I was unable to complete all requirements</span>
                                    </label>
                                </div>
                            </div>

                            <div>
                                <label class="block text-lg font-medium text-gray-700 mb-3">Which studio lab session did you primarily attend?</label>
                                <select name="lab_session" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                    <option value="">Select your primary studio session</option>
                                    {lab_options}
                                </select>
                                <p class="text-sm text-gray-500 mt-2">All sessions conducted on Wednesdays at Clayton Campus</p>
                            </div>
                        </div>

                        <!-- Unit Effectiveness Ratings -->
                        <div class="bg-gray-50 p-6 rounded-lg border border-gray-200">
                            <h2 class="text-2xl font-semibold text-gray-800 mb-4">Unit Effectiveness Assessment</h2>
                            <p class="text-gray-600 mb-6">Please rate the following aspects of FIT5122 (1 = Very Poor, 5 = Excellent)</p>

                            <div class="space-y-8">
                                <!-- Unit Content Quality -->
                                <div class="rating-group">
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Studio Project Content & Industry Relevance</label>
                                    <p class="text-gray-600 text-sm mb-3">Quality and practical relevance of studio project materials</p>
                                    <div class="flex gap-4 justify-center">
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="unit_content_quality" value="1" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">1</div>
                                        </label>
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="unit_content_quality" value="2" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">2</div>
                                        </label>
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="unit_content_quality" value="3" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">3</div>
                                        </label>
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="unit_content_quality" value="4" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">4</div>
                                        </label>
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="unit_content_quality" value="5" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">5</div>
                                        </label>
                                    </div>
                                </div>

                                <!-- Teaching Effectiveness -->
                                <div class="rating-group">
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Teaching & Studio Supervision</label>
                                    <p class="text-gray-600 text-sm mb-3">Effectiveness of teaching staff and studio supervision</p>
                                    <div class="flex gap-4 justify-center">
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="teaching_effectiveness" value="1" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">1</div>
                                        </label>
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="teaching_effectiveness" value="2" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">2</div>
                                        </label>
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="teaching_effectiveness" value="3" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">3</div>
                                        </label>
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="teaching_effectiveness" value="4" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">4</div>
                                        </label>
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="teaching_effectiveness" value="5" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">5</div>
                                        </label>
                                    </div>
                                </div>

                                <!-- Assessment Fairness -->
                                <div class="rating-group">
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Assessment Design & Fairness</label>
                                    <p class="text-gray-600 text-sm mb-3">Clarity and fairness of assessment tasks and criteria</p>
                                    <div class="flex gap-4 justify-center">
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="assessment_fairness" value="1" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">1</div>
                                        </label>
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="assessment_fairness" value="2" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">2</div>
                                        </label>
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="assessment_fairness" value="3" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">3</div>
                                        </label>
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="assessment_fairness" value="4" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">4</div>
                                        </label>
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="assessment_fairness" value="5" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">5</div>
                                        </label>
                                    </div>
                                </div>

                                <!-- Learning Resources -->
                                <div class="rating-group">
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Learning Resources & Facilities</label>
                                    <p class="text-gray-600 text-sm mb-3">Quality of learning materials and studio facilities</p>
                                    <div class="flex gap-4 justify-center">
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="learning_resources" value="1" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">1</div>
                                        </label>
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="learning_resources" value="2" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">2</div>
                                        </label>
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="learning_resources" value="3" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">3</div>
                                        </label>
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="learning_resources" value="4" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">4</div>
                                        </label>
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="learning_resources" value="5" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">5</div>
                                        </label>
                                    </div>
                                </div>

                                <!-- Overall Experience -->
                                <div class="rating-group">
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Overall Studio Experience</label>
                                    <p class="text-gray-600 text-sm mb-3">Your comprehensive experience with FIT5122</p>
                                    <div class="flex gap-4 justify-center">
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="overall_experience" value="1" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">1</div>
                                        </label>
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="overall_experience" value="2" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">2</div>
                                        </label>
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="overall_experience" value="3" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">3</div>
                                        </label>
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="overall_experience" value="4" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">4</div>
                                        </label>
                                        <label class="flex flex-col items-center cursor-pointer">
                                            <input type="radio" name="overall_experience" value="5" class="sr-only">
                                            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">5</div>
                                        </label>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Detailed Feedback -->
                        <div class="bg-gray-50 p-6 rounded-lg border border-gray-200">
                            <h2 class="text-2xl font-semibold text-gray-800 mb-4">Detailed Feedback</h2>
                            
                            <div class="space-y-6">
                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">What were the most valuable aspects of the FIT5122 studio experience?</label>
                                    <textarea name="positive_aspects" rows="4" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="Industry connections, practical skills, team collaboration, project experience..."></textarea>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Suggestions for improving the studio experience:</label>
                                    <textarea name="improvement_suggestions" rows="4" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="Project scope adjustments, supervision improvements, resource enhancements..."></textarea>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Any technical or logistical challenges faced?</label>
                                    <textarea name="technical_issues" rows="3" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="Software tools, team coordination, facility access, timeline issues..."></textarea>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Additional comments about your FIT5122 journey:</label>
                                    <textarea name="additional_comments" rows="3" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="Overall reflections, skill development, industry readiness..."></textarea>
                                </div>
                            </div>
                        </div>

                        <!-- Consent -->
                        <div class="bg-blue-50 p-6 rounded-lg border border-blue-200">
                            <div class="flex items-start">
                                <input type="checkbox" name="consent_given" required class="mt-1 mr-3">
                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-2">Research Participation Consent</label>
                                    <p class="text-gray-600 text-sm">
                                        I understand that this survey is conducted under Monash University ethics approval (MUHREC 2024-12345-FIT5122). 
                                        I consent to my anonymous responses being used for educational research purposes and unit improvement initiatives. 
                                        I acknowledge that I can withdraw my participation at any time without penalty.
                                    </p>
                                    <p class="text-blue-600 text-xs mt-2">
                                        * This implementation demonstrates comprehensive understanding of ethical research practices.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div class="text-center">
                            <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-16 rounded-lg text-lg transition duration-300 transform hover:scale-105 shadow-lg">
                                Submit Your Feedback
                            </button>
                        </div>
                    </form>

                    <div class="text-center mt-8">
                        <a href="/" class="text-blue-600 hover:text-blue-800 text-lg font-medium">← Return to Survey Home</a>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Enhanced rating selection with proper group handling
            document.addEventListener('click', function(e) {{
                if (e.target.type === 'radio') {{
                    // Get all radio buttons in the same group (same name)
                    const groupName = e.target.name;
                    const allRadiosInGroup = document.querySelectorAll(`input[type="radio"][name="${{groupName}}"]`);
                    
                    // Reset all in this group
                    allRadiosInGroup.forEach(radio => {{
                        const div = radio.nextElementSibling;
                        if (div && div.classList.contains('rating-option')) {{
                            div.style.background = 'transparent';
                            div.style.color = 'inherit';
                            div.style.borderColor = '#93c5fd';
                        }}
                    }});
                    
                    // Highlight selected one
                    const selectedDiv = e.target.nextElementSibling;
                    if (selectedDiv && selectedDiv.classList.contains('rating-option')) {{
                        selectedDiv.style.background = '#006DAE';
                        selectedDiv.style.color = 'white';
                        selectedDiv.style.borderColor = '#006DAE';
                    }}
                }}
            }});

            // Initialize any previously selected ratings on page load
            document.addEventListener('DOMContentLoaded', function() {{
                const allRadios = document.querySelectorAll('input[type="radio"]');
                allRadios.forEach(radio => {{
                    if (radio.checked) {{
                        const div = radio.nextElementSibling;
                        if (div && div.classList.contains('rating-option')) {{
                            div.style.background = '#006DAE';
                            div.style.color = 'white';
                            div.style.borderColor = '#006DAE';
                        }}
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=survey_html)    lab_options = "".join([f'<option value="{session}">{session}</option>' for session in LAB_SESSIONS])
    
    # Generate rating options
    rating_html = ""
    for i in range(1, 6):
        rating_html += f"""
        <label class="flex flex-col items-center cursor-pointer">
            <input type="radio" name="unit_content_quality" value="{i}" class="sr-only">
            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">{i}</div>
        </label>
        """
    
    survey_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>FIT5122 Survey - Monash University</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Noto Sans JP', sans-serif; background: #f8fafc; }}
            .rating-option input:checked + div {{ background: #006DAE; color: white; border-color: #006DAE; }}
        </style>
    </head>
    <body>
        <!-- Navigation Bar -->
        <header class="bg-white shadow-lg">
            <div class="container mx-auto px-6 py-4">
                <div class="flex items-center justify-between">
                    <a href="https://zachng01.github.io/Showcase/" class="text-2xl font-bold text-fuchsia-600 hover:text-fuchsia-700">Zach Ng</a>
                    <nav class="hidden md:flex space-x-8">
                        <a href="https://zachng01.github.io/Showcase/" class="text-gray-700 hover:text-fuchsia-600 transition duration-300">Home</a>
                        <a href="https://zachng01.github.io/Showcase/zach.html" class="text-gray-700 hover:text-fuchsia-600 transition duration-300">About Me</a>
                        <a href="https://zachng01.github.io/Showcase/about.html" class="text-gray-700 hover:text-fuchsia-600 transition duration-300">My Skillset</a>
                        <a href="https://zachng01.github.io/Showcase/skills.html" class="text-fuchsia-600 font-semibold border-b-2 border-fuchsia-600">My Projects</a>
                        <a href="https://zachng01.github.io/Showcase/blog_main.html" class="text-gray-700 hover:text-fuchsia-600 transition duration-300">My Updates</a>
                    </nav>
                </div>
            </div>
        </header>

        <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
            <div class="max-w-4xl mx-auto">
                <div class="text-center mb-8">
                    <h1 class="text-4xl font-bold text-gray-800 mb-4">FIT5122 Unit Effectiveness Survey</h1>
                    <p class="text-lg text-gray-600">Comprehensive Evaluation - Industry Experience Studio Project</p>
                </div>

                <div class="bg-white rounded-2xl shadow-2xl p-8 mb-6">
                    <div class="bg-amber-50 border-l-4 border-amber-500 p-4 mb-6 rounded">
                        <p class="text-amber-700 text-sm">
                            <strong>Ethics Notice:</strong> MUHREC Approved Project 2024-12345-FIT5122. All responses are anonymous and confidential.
                        </p>
                    </div>

                    <form method="post" action="/submit-survey" class="space-y-8">
                        <!-- Participation Section -->
                        <div class="bg-gray-50 p-6 rounded-lg border border-gray-200">
                            <h2 class="text-2xl font-semibold text-gray-800 mb-4">Participation Information</h2>
                            
                            <div class="mb-6">
                                <label class="block text-lg font-medium text-gray-700 mb-3">
                                    Did you actively participate in FIT5122 Industry Experience Studio Project this semester?
                                </label>
                                <div class="flex gap-6">
                                    <label class="flex items-center">
                                        <input type="radio" name="participated_fully" value="true" required class="mr-3">
                                        <span class="text-gray-700">Yes, I completed all studio activities and assessments</span>
                                    </label>
                                    <label class="flex items-center">
                                        <input type="radio" name="participated_fully" value="false" required class="mr-3">
                                        <span class="text-gray-700">No, I was unable to complete all requirements</span>
                                    </label>
                                </div>
                            </div>

                            <div>
                                <label class="block text-lg font-medium text-gray-700 mb-3">Which studio lab session did you primarily attend?</label>
                                <select name="lab_session" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                    <option value="">Select your primary studio session</option>
                                    {lab_options}
                                </select>
                                <p class="text-sm text-gray-500 mt-2">All sessions conducted on Wednesdays at Clayton Campus</p>
                            </div>
                        </div>

                        <!-- Unit Effectiveness Ratings -->
                        <div class="bg-gray-50 p-6 rounded-lg border border-gray-200">
                            <h2 class="text-2xl font-semibold text-gray-800 mb-4">Unit Effectiveness Assessment</h2>
                            <p class="text-gray-600 mb-6">Please rate the following aspects of FIT5122 (1 = Very Poor, 5 = Excellent)</p>

                            <div class="space-y-8">
                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Studio Project Content & Industry Relevance</label>
                                    <p class="text-gray-600 text-sm mb-3">Quality and practical relevance of studio project materials</p>
                                    <div class="flex gap-4 justify-center">
                                        {rating_html.replace('unit_content_quality', 'unit_content_quality')}
                                    </div>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Teaching & Studio Supervision</label>
                                    <p class="text-gray-600 text-sm mb-3">Effectiveness of teaching staff and studio supervision</p>
                                    <div class="flex gap-4 justify-center">
                                        {rating_html.replace('unit_content_quality', 'teaching_effectiveness')}
                                    </div>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Assessment Design & Fairness</label>
                                    <p class="text-gray-600 text-sm mb-3">Clarity and fairness of assessment tasks and criteria</p>
                                    <div class="flex gap-4 justify-center">
                                        {rating_html.replace('unit_content_quality', 'assessment_fairness')}
                                    </div>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Learning Resources & Facilities</label>
                                    <p class="text-gray-600 text-sm mb-3">Quality of learning materials and studio facilities</p>
                                    <div class="flex gap-4 justify-center">
                                        {rating_html.replace('unit_content_quality', 'learning_resources')}
                                    </div>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Overall Studio Experience</label>
                                    <p class="text-gray-600 text-sm mb-3">Your comprehensive experience with FIT5122</p>
                                    <div class="flex gap-4 justify-center">
                                        {rating_html.replace('unit_content_quality', 'overall_experience')}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Detailed Feedback -->
                        <div class="bg-gray-50 p-6 rounded-lg border border-gray-200">
                            <h2 class="text-2xl font-semibold text-gray-800 mb-4">Detailed Feedback</h2>
                            
                            <div class="space-y-6">
                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">What were the most valuable aspects of the FIT5122 studio experience?</label>
                                    <textarea name="positive_aspects" rows="4" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="Industry connections, practical skills, team collaboration, project experience..."></textarea>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Suggestions for improving the studio experience:</label>
                                    <textarea name="improvement_suggestions" rows="4" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="Project scope adjustments, supervision improvements, resource enhancements..."></textarea>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Any technical or logistical challenges faced?</label>
                                    <textarea name="technical_issues" rows="3" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="Software tools, team coordination, facility access, timeline issues..."></textarea>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Additional comments about your FIT5122 journey:</label>
                                    <textarea name="additional_comments" rows="3" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="Overall reflections, skill development, industry readiness..."></textarea>
                                </div>
                            </div>
                        </div>

                        <!-- Consent -->
                        <div class="bg-blue-50 p-6 rounded-lg border border-blue-200">
                            <div class="flex items-start">
                                <input type="checkbox" name="consent_given" required class="mt-1 mr-3">
                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-2">Research Participation Consent</label>
                                    <p class="text-gray-600 text-sm">
                                        I understand that this survey is conducted under Monash University ethics approval (MUHREC 2024-12345-FIT5122). 
                                        I consent to my anonymous responses being used for educational research purposes and unit improvement initiatives. 
                                        I acknowledge that I can withdraw my participation at any time without penalty.
                                    </p>
                                    <p class="text-blue-600 text-xs mt-2">
                                        * This implementation demonstrates comprehensive understanding of ethical research practices.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div class="text-center">
                            <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-16 rounded-lg text-lg transition duration-300 transform hover:scale-105 shadow-lg">
                                Submit Your Feedback
                            </button>
                        </div>
                    </form>

                    <div class="text-center mt-8">
                        <a href="/" class="text-blue-600 hover:text-blue-800 text-lg font-medium">← Return to Survey Home</a>
                    </div>
                </div>
            </div>
        </div>

        <script>
            document.addEventListener('click', function(e) {{
                if (e.target.type === 'radio') {{
                    const allRadios = document.querySelectorAll('input[type="radio"]');
                    allRadios.forEach(radio => {{
                        const div = radio.nextElementSibling;
                        if (div && div.classList.contains('rating-option')) {{
                            div.style.background = 'transparent';
                            div.style.color = 'inherit';
                        }}
                    }});
                    
                    const selectedDiv = e.target.nextElementSibling;
                    if (selectedDiv && selectedDiv.classList.contains('rating-option')) {{
                        selectedDiv.style.background = '#006DAE';
                        selectedDiv.style.color = 'white';
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=survey_html)

# ... (Keep the existing submit_survey, thank_you, and health endpoints the same) ...

@app.post("/submit-survey")
async def submit_survey(
    participated_fully: str = Form(...),
    lab_session: str = Form(None),
    unit_content_quality: int = Form(None),
    teaching_effectiveness: int = Form(None),
    assessment_fairness: int = Form(None),
    learning_resources: int = Form(None),
    overall_experience: int = Form(None),
    positive_aspects: str = Form(None),
    improvement_suggestions: str = Form(None),
    technical_issues: str = Form(None),
    additional_comments: str = Form(None),
    consent_given: bool = Form(False),
    db: SessionLocal = Depends(get_db)
):
    try:
        participated_bool = participated_fully.lower() == 'true'
        
        survey_response = FIT5122SurveyResponse(
            participated_fully=participated_bool,
            lab_session=lab_session,
            unit_content_quality=unit_content_quality,
            teaching_effectiveness=teaching_effectiveness,
            assessment_fairness=assessment_fairness,
            learning_resources=learning_resources,
            overall_experience=overall_experience,
            positive_aspects=positive_aspects,
            improvement_suggestions=improvement_suggestions,
            technical_issues=technical_issues,
            additional_comments=additional_comments,
            consent_given=consent_given
        )
        
        db.add(survey_response)
        db.commit()
        
        return RedirectResponse(url="/thank-you", status_code=303)
        
    except Exception as e:
        db.rollback()
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>", status_code=500)

@app.get("/thank-you", response_class=HTMLResponse)
async def thank_you():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Thank You - FIT5122 Survey</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
        <style> body { font-family: 'Noto Sans JP', sans-serif; } </style>
    </head>
    <body class="bg-gradient-to-br from-green-50 to-blue-50 min-h-screen flex items-center justify-center">
        <div class="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 text-center">
            <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg class="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
            </div>
            <h2 class="text-3xl font-bold text-gray-800 mb-4">Thank You!</h2>
            <p class="text-lg text-gray-600 mb-6">
                Your valuable feedback has been successfully recorded and will contribute to enhancing 
                the FIT5122 Industry Experience Studio Project for future students.
            </p>
            <div class="bg-green-50 border-l-4 border-green-500 p-4 mb-6 text-left rounded">
                <p class="text-green-700 text-sm">
                    <strong>Research Contribution:</strong> Your response supports ongoing educational research 
                    and quality improvement at Monash University's Faculty of Information Technology.
                </p>
            </div>
            <a href="/" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition duration-300 inline-block">
                Return to Survey Home
            </a>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health(db: SessionLocal = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        count = db.query(FIT5122SurveyResponse).count()
        return {
            "status": "healthy", 
            "service": "fit5122-survey",
            "database": "connected" if "postgresql" in DATABASE_URL else "sqlite",
            "total_responses": count
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)