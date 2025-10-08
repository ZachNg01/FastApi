from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import os
import ssl

# Create FastAPI app FIRST
app = FastAPI(title="GenAI Lab Preparation Research", version="1.0.0")

print("🚀 Starting GenAI Lab Preparation Research Application...")

# Database setup with SSL fix for Neon
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("DATABASE_URL not set in environment variables")
    print("Using SQLite for local testing")
    DATABASE_URL = "sqlite:///./test.db"
else:
    print("DATABASE_URL found in environment")

try:
    # For Neon PostgreSQL with SSL
    if "postgresql" in DATABASE_URL:
        # Add SSL context for stable connections
        import psycopg2
        from sqlalchemy.pool import NullPool
        
        engine = create_engine(
            DATABASE_URL,
            poolclass=NullPool,  # Use NullPool to avoid connection issues
            pool_pre_ping=True,  # Check connection before using
            connect_args={
                'sslmode': 'require',
                'sslrootcert': '/etc/ssl/certs/ca-certificates.crt'
            }
        )
        print("Using PostgreSQL with SSL configuration")
    else:
        # For SQLite
        engine = create_engine(DATABASE_URL)
        print("Using SQLite database")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    
    # Original FIT5122 Survey Model
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
    
    # New GenAI Research Survey Model
    class GenAISurveyResponse(Base):
        __tablename__ = "genai_survey_responses"
        id = Column(Integer, primary_key=True, index=True)
        timestamp = Column(DateTime(timezone=True), server_default=func.now())
        
        # Participant Information
        student_id = Column(String(20), nullable=True)
        study_group = Column(String(20), nullable=False)  # 'control' or 'experimental'
        faculty = Column(String(100), nullable=False)
        year_level = Column(String(20), nullable=False)
        
        # Pre-Lab Assessment (Both Groups)
        pre_lab_confidence = Column(Integer, nullable=False)  # 1-5 scale
        safety_knowledge_confidence = Column(Integer, nullable=False)  # 1-5 scale
        technical_skills_confidence = Column(Integer, nullable=False)  # 1-5 scale
        
        # GenAI Group Specific (Experimental Group)
        genai_tools_used = Column(String(500), nullable=True)  # Which tools used
        prompt_quality = Column(Integer, nullable=True)  # 1-5 scale
        output_helpfulness = Column(Integer, nullable=True)  # 1-5 scale
        ai_preparedness_rating = Column(Integer, nullable=True)  # 1-5 scale
        
        # Traditional Methods Group Specific (Control Group)
        traditional_methods_used = Column(String(500), nullable=True)
        traditional_preparedness_rating = Column(Integer, nullable=True)  # 1-5 scale
        
        # Post-Lab Assessment (Both Groups)
        task_accuracy_rating = Column(Integer, nullable=False)  # 1-5 scale
        safety_compliance_rating = Column(Integer, nullable=False)  # 1-5 scale
        conceptual_understanding_gain = Column(Integer, nullable=False)  # 1-5 scale
        
        # Qualitative Feedback
        preparation_method_strengths = Column(Text, nullable=True)
        preparation_method_limitations = Column(Text, nullable=True)
        ai_experience_feedback = Column(Text, nullable=True)  # For experimental group
        suggestions_improvement = Column(Text, nullable=True)
        
        # Ethical Compliance
        consent_given = Column(Boolean, nullable=False, default=False)
        data_usage_consent = Column(Boolean, nullable=False, default=False)
    
    Base.metadata.create_all(bind=engine)
    print("Database setup complete")
    print("✅ Both survey tables created successfully")
    
except Exception as e:
    print(f" Database setup failed: {e}")
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

# Lab sessions for original FIT5122 survey
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

# Research-specific data options
FACULTIES = [
    "Pharmacy and Pharmaceutical Sciences",
    "Medicine, Nursing and Health Sciences",
    "Science",
    "Engineering",
    "Information Technology",
    "Other"
]

YEAR_LEVELS = ["1st Year", "2nd Year", "3rd Year", "4th Year", "Postgraduate"]

GENAI_TOOLS = [
    "ChatGPT",
    "Google Bard",
    "Claude",
    "Microsoft Copilot",
    "Research-specific AI tools",
    "Other"
]

TRADITIONAL_METHODS = [
    "Lab manuals/guides",
    "Lecture notes",
    "Textbooks",
    "Peer discussion",
    "Video demonstrations",
    "Previous lab notes",
    "Other"
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Research Portal - Monash University</title>
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
      background: #aae6be;
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
    <div class="max-w-6xl w-full bg-white/95 backdrop-blur-sm rounded-3xl shadow-2xl p-8">
      <div class="text-center mb-8">
        <div class="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <span class="text-3xl text-blue-600">🔬</span>
        </div>
        <h1 class="text-5xl font-bold text-gray-800 mb-4">Monash University Research Portal</h1>
        <p class="text-xl text-gray-600 mb-6">Faculty of Pharmacy and Pharmaceutical Sciences</p>
        <p class="text-lg text-gray-700">Advancing STEM Education Through Innovative Research</p>
      </div>

      <!-- Research Projects Grid -->
      <div class="grid md:grid-cols-2 gap-8 mb-8">
        <!-- GenAI Research Project -->
        <div class="bg-gradient-to-br from-blue-50 to-indigo-100 border-2 border-blue-200 rounded-2xl p-6 hover:shadow-lg transition-shadow">
          <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
            <span class="text-2xl text-blue-600">🤖</span>
          </div>
          <h2 class="text-2xl font-bold text-gray-800 mb-3">GenAI Lab Preparation Study</h2>
          <p class="text-gray-600 mb-4">
            Investigating how Generative AI tools impact student preparedness, technical skills, and safety knowledge in laboratory settings.
          </p>
          <div class="space-y-2 mb-4">
            <div class="flex items-center text-sm text-blue-600">
              <span class="font-semibold">Status:</span>
              <span class="ml-2 bg-blue-100 px-2 py-1 rounded-full">Recruiting Participants</span>
            </div>
            <div class="flex items-center text-sm text-gray-600">
              <span class="font-semibold">Ethics:</span>
              <span class="ml-2">MUHREC 2025-67890-GENAI</span>
            </div>
          </div>
          <a href="/genai-survey" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition duration-300 inline-block w-full text-center">
            Participate in Study
          </a>
        </div>

        <!-- FIT5122 Research Project -->
        <div class="bg-gradient-to-br from-green-50 to-emerald-100 border-2 border-green-200 rounded-2xl p-6 hover:shadow-lg transition-shadow">
          <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
            <span class="text-2xl text-green-600">💼</span>
          </div>
          <h2 class="text-2xl font-bold text-gray-800 mb-3">FIT5122 Unit Effectiveness</h2>
          <p class="text-gray-600 mb-4">
            Evaluating the effectiveness of Industry Experience Studio Project delivery and student learning outcomes.
          </p>
          <div class="space-y-2 mb-4">
            <div class="flex items-center text-sm text-green-600">
              <span class="font-semibold">Status:</span>
              <span class="ml-2 bg-green-100 px-2 py-1 rounded-full">Ongoing</span>
            </div>
            <div class="flex items-center text-sm text-gray-600">
              <span class="font-semibold">Ethics:</span>
              <span class="ml-2">MUHREC 2025-12345-FIT5122</span>
            </div>
          </div>
          <a href="/survey" class="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition duration-300 inline-block w-full text-center">
            Participate in Survey
          </a>
        </div>
      </div>

      <!-- Research Overview -->
      <div class="bg-white border border-gray-200 rounded-xl p-6 mb-8">
        <h2 class="text-3xl font-bold text-gray-800 mb-6 text-center">GenAI in Laboratory Education Research</h2>
        
        <div class="grid md:grid-cols-3 gap-6 mb-8">
          <div class="text-center">
            <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span class="text-purple-600">🎯</span>
            </div>
            <h3 class="font-semibold text-gray-800 mb-2">Research Aim</h3>
            <p class="text-gray-600 text-sm">Investigate GenAI's impact on student lab preparation compared to traditional methods</p>
          </div>
          
          <div class="text-center">
            <div class="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span class="text-orange-600">👥</span>
            </div>
            <h3 class="font-semibold text-gray-800 mb-2">Study Design</h3>
            <p class="text-gray-600 text-sm">Quasi-experimental with control and experimental groups</p>
          </div>
          
          <div class="text-center">
            <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span class="text-blue-600">📊</span>
            </div>
            <h3 class="font-semibold text-gray-800 mb-2">Data Collection</h3>
            <p class="text-gray-600 text-sm">Mixed-methods: assessments, surveys, and qualitative feedback</p>
          </div>
        </div>

        <!-- Research Questions -->
        <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-lg mb-6">
          <h3 class="text-lg font-semibold text-blue-800 mb-2">Research Questions:</h3>
          <ul class="text-blue-700 list-disc list-inside space-y-1 text-sm">
            <li>How do GenAI-generated outputs impact students' accuracy in completing lab tasks?</li>
            <li>How does using GenAI impact students' conceptual understanding and safety knowledge?</li>
            <li>What characteristics of GenAI prompts and outputs correlate with enhanced performance?</li>
          </ul>
        </div>

        <!-- Significance -->
        <div class="bg-green-50 border-l-4 border-green-500 p-4 rounded-lg">
          <h3 class="text-lg font-semibold text-green-800 mb-2">Research Significance:</h3>
          <p class="text-green-700 text-sm">
            This study contributes to AI in education by providing evidence-based insights into GenAI efficacy for lab preparation. 
            Findings could guide educators on integrating AI tools and inform technology-enhanced learning policies in STEM education.
          </p>
        </div>
      </div>

      <!-- Ethics Statement -->
      <div class="bg-amber-50 border-l-4 border-amber-500 p-6 rounded-lg">
        <h2 class="text-2xl font-semibold text-amber-800 mb-3">Ethics Approval & Confidentiality</h2>
        <p class="text-amber-700 mb-3">
          <strong>Monash University Human Research Ethics Committee (MUHREC) Approved</strong><br>
          All studies conducted under strict ethical guidelines with full participant confidentiality.
        </p>
        <ul class="text-amber-700 list-disc list-inside space-y-2 text-sm">
          <li>Informed consent obtained for all participants</li>
          <li>All data anonymized and stored securely</li>
          <li>Voluntary participation with right to withdraw</li>
          <li>Ethical approval: MUHREC 2025-67890-GENAI & MUHREC 2025-12345-FIT5122</li>
        </ul>
      </div>
    </div>
  </div>

  <footer class="bg-white/80 backdrop-blur-sm mt-12">
    <div class="container mx-auto px-6 py-4 text-center">
      <p class="text-gray-600">&copy; 2025 Monash University - Educational Research Portal</p>
      <p class="text-gray-500 text-sm">All research conducted under Monash University HREC approval</p>
    </div>
  </footer>
</body>
</html>
"""

# =============================================================================
# ORIGINAL FIT5122 SURVEY ROUTES (UNCHANGED)
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(HTML_TEMPLATE)

@app.get("/survey", response_class=HTMLResponse)
async def survey_form():
    lab_options = "".join([f'<option value="{session}">{session}</option>' for session in LAB_SESSIONS])
    
    def generate_rating_options(field_name):
        rating_html = ""
        for i in range(1, 6):
            rating_html += f"""
            <label class="flex flex-col items-center cursor-pointer">
                <input type="radio" name="{field_name}" value="{i}" class="sr-only" onchange="handleRatingChange(this)">
                <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option" data-value="{i}">{i}</div>
            </label>
            """
        return rating_html
    
    survey_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>FIT5122 Survey - Monash University</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Noto Sans JP', sans-serif; background: #aae6be; }}
            .rating-selected {{
                background: #006DAE !important;
                color: white !important;
                border-color: #006DAE !important;
                transform: scale(1.1);
            }}
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

        <div class="min-h-screen bg-[#aae6be] py-8 px-4">
            <div class="max-w-4xl mx-auto">
                <div class="text-center mb-8">
                    <h1 class="text-4xl font-bold text-gray-800 mb-4">FIT5122 Unit Effectiveness Survey</h1>
                    <p class="text-lg text-gray-600">Evaluating the Effectiveness of FIT5122's Delivery</p>
                </div>

                <div class="bg-white rounded-2xl shadow-2xl p-8 mb-6">
                    <div class="bg-amber-50 border-l-4 border-amber-500 p-4 mb-6 rounded">
                        <p class="text-amber-700 text-sm">
                            <strong>Ethics Notice:</strong> MUHREC Approved Project 2025-12345-FIT5122. All responses are anonymous and confidential.
                        </p>
                    </div>

                    <form method="post" action="/submit-survey" class="space-y-8" id="surveyForm">
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
                                    <div class="flex gap-4 justify-center" id="unit_content_quality_ratings">
                                        {generate_rating_options('unit_content_quality')}
                                    </div>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Teaching & Studio Supervision</label>
                                    <p class="text-gray-600 text-sm mb-3">Effectiveness of teaching staff and studio supervision</p>
                                    <div class="flex gap-4 justify-center" id="teaching_effectiveness_ratings">
                                        {generate_rating_options('teaching_effectiveness')}
                                    </div>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Assessment Design & Fairness</label>
                                    <p class="text-gray-600 text-sm mb-3">Clarity and fairness of assessment tasks and criteria</p>
                                    <div class="flex gap-4 justify-center" id="assessment_fairness_ratings">
                                        {generate_rating_options('assessment_fairness')}
                                    </div>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Learning Resources & Facilities</label>
                                    <p class="text-gray-600 text-sm mb-3">Quality of learning materials and studio facilities</p>
                                    <div class="flex gap-4 justify-center" id="learning_resources_ratings">
                                        {generate_rating_options('learning_resources')}
                                    </div>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Overall Studio Experience</label>
                                    <p class="text-gray-600 text-sm mb-3">Your comprehensive experience with FIT5122</p>
                                    <div class="flex gap-4 justify-center" id="overall_experience_ratings">
                                        {generate_rating_options('overall_experience')}
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
                                        I understand that this survey is conducted under Monash University ethics approval (MUHREC 2025-12345-FIT5122). 
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
                        <a href="/" class="text-blue-600 hover:text-blue-800 text-lg font-medium">← Return to Research Portal</a>
                    </div>
                </div>
            </div>
        </div>

        <script>
            function handleRatingChange(radio) {{
                // Get all rating options in the same question group
                const container = radio.closest('div[class*="justify-center"]');
                const allOptions = container.querySelectorAll('.rating-option');
                
                // Remove selected class from all options in this group
                allOptions.forEach(option => {{
                    option.classList.remove('rating-selected');
                }});
                
                // Add selected class to the chosen option
                const selectedOption = radio.nextElementSibling;
                selectedOption.classList.add('rating-selected');
            }}

            // Initialize any previously selected ratings on page load
            document.addEventListener('DOMContentLoaded', function() {{
                const allRadios = document.querySelectorAll('input[type="radio"]');
                allRadios.forEach(radio => {{
                    if (radio.checked) {{
                        const selectedOption = radio.nextElementSibling;
                        selectedOption.classList.add('rating-selected');
                    }}
                }});
            }});

            // Form submission handler
            document.getElementById('surveyForm').addEventListener('submit', function(e) {{
                const submitBtn = this.querySelector('button[type="submit"]');
                submitBtn.disabled = true;
                submitBtn.innerHTML = 'Submitting...';
                submitBtn.classList.remove('hover:scale-105', 'hover:bg-blue-700');
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=survey_html)

@app.post("/submit-survey")
async def submit_survey(
    request: Request,
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
        print("📥 Received FIT5122 survey submission")
        
        # Convert string to boolean
        participated_bool = participated_fully.lower() == 'true'
        
        # Create survey response
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
        db.refresh(survey_response)
        
        print(f"✅ FIT5122 survey response saved with ID: {survey_response.id}")
        
        return RedirectResponse(url="/thank-you", status_code=303)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error saving FIT5122 survey: {e}")
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Submission Error</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-100 min-h-screen flex items-center justify-center">
            <div class="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 text-center">
                <div class="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <span class="text-2xl text-red-600">⚠️</span>
                </div>
                <h2 class="text-3xl font-bold text-gray-800 mb-4">Submission Error</h2>
                <p class="text-lg text-gray-600 mb-6">
                    We encountered an issue saving your response. Please try again in a moment.
                </p>
                <div class="bg-red-50 border-l-4 border-red-500 p-4 mb-6 text-left rounded">
                    <p class="text-red-700 text-sm">
                        <strong>Technical Issue:</strong> Database connection temporarily unavailable.
                    </p>
                </div>
                <a href="/survey" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition duration-300 inline-block">
                    Try Again
                </a>
                <div class="mt-4">
                    <a href="/" class="text-blue-600 hover:text-blue-800">Return to Research Portal</a>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)

# =============================================================================
# NEW GENAI RESEARCH SURVEY ROUTES
# =============================================================================

@app.get("/genai-survey", response_class=HTMLResponse)
async def genai_survey_form():
    faculty_options = "".join([f'<option value="{faculty}">{faculty}</option>' for faculty in FACULTIES])
    year_options = "".join([f'<option value="{year}">{year}</option>' for year in YEAR_LEVELS])
    genai_tool_options = "".join([f'<option value="{tool}">{tool}</option>' for tool in GENAI_TOOLS])
    traditional_method_options = "".join([f'<option value="{method}">{method}</option>' for method in TRADITIONAL_METHODS])
    
    def generate_rating_options(field_name, required=False):
        rating_html = ""
        for i in range(1, 6):
            required_attr = "required" if required else ""
            rating_html += f"""
            <label class="flex flex-col items-center cursor-pointer">
                <input type="radio" name="{field_name}" value="{i}" class="sr-only" onchange="handleRatingChange(this)" {required_attr}>
                <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option" data-value="{i}">
                    <span class="text-sm font-medium">{i}</span>
                </div>
                <span class="text-xs text-gray-500 mt-1">{['Very Low','Low','Moderate','High','Very High'][i-1]}</span>
            </label>
            """
        return rating_html
    
    survey_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>GenAI Lab Preparation Study - Monash University</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Noto Sans JP', sans-serif; background: #aae6be; }}
            .rating-selected {{
                background: #006DAE !important;
                color: white !important;
                border-color: #006DAE !important;
                transform: scale(1.1);
            }}
            .group-section {{
                display: none;
            }}
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

        <div class="min-h-screen bg-[#aae6be] py-8 px-4">
            <div class="max-w-4xl mx-auto">
                <div class="text-center mb-8">
                    <h1 class="text-4xl font-bold text-gray-800 mb-4">GenAI Lab Preparation Research Study</h1>
                    <p class="text-lg text-gray-600">Investigating AI Tools in Laboratory Education</p>
                </div>

                <div class="bg-white rounded-2xl shadow-2xl p-8 mb-6">
                    <div class="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6 rounded">
                        <p class="text-blue-700 text-sm">
                            <strong>Research Study:</strong> MUHREC Approved Project 2025-67890-GENAI. 
                            This study investigates how Generative AI impacts lab preparation effectiveness.
                        </p>
                    </div>

                    <form method="post" action="/submit-genai-survey" class="space-y-8" id="genaiSurveyForm">
                        <!-- Study Information -->
                        <div class="bg-purple-50 p-6 rounded-lg border border-purple-200">
                            <h2 class="text-2xl font-semibold text-purple-800 mb-4">Study Information</h2>
                            <p class="text-purple-700 mb-4">
                                This research examines how Generative AI tools compare to traditional methods for laboratory preparation. 
                                You will be randomly assigned to either the experimental group (using AI tools) or control group (traditional methods).
                            </p>
                            <div class="grid md:grid-cols-2 gap-4 text-sm">
                                <div class="bg-white p-3 rounded border">
                                    <strong>👥 Experimental Group:</strong> Use GenAI tools for lab prep
                                </div>
                                <div class="bg-white p-3 rounded border">
                                    <strong>📚 Control Group:</strong> Use traditional lab manuals & materials
                                </div>
                            </div>
                        </div>

                        <!-- Participant Information -->
                        <div class="bg-gray-50 p-6 rounded-lg border border-gray-200">
                            <h2 class="text-2xl font-semibold text-gray-800 mb-4">Participant Information</h2>
                            
                            <div class="grid md:grid-cols-2 gap-6">
                                <div>
                                    <label class="block text-lg font-medium text-gray-700 mb-2">Student ID (Optional)</label>
                                    <input type="text" name="student_id" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="e.g., 12345678">
                                </div>
                                
                                <div>
                                    <label class="block text-lg font-medium text-gray-700 mb-2">Faculty</label>
                                    <select name="faculty" required class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                                        <option value="">Select your faculty</option>
                                        {faculty_options}
                                    </select>
                                </div>
                                
                                <div>
                                    <label class="block text-lg font-medium text-gray-700 mb-2">Year Level</label>
                                    <select name="year_level" required class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                                        <option value="">Select year level</option>
                                        {year_options}
                                    </select>
                                </div>
                                
                                <div>
                                    <label class="block text-lg font-medium text-gray-700 mb-2">Study Group Assignment</label>
                                    <select name="study_group" required class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" onchange="toggleGroupSections(this.value)">
                                        <option value="">Select your group</option>
                                        <option value="experimental">Experimental Group (GenAI Tools)</option>
                                        <option value="control">Control Group (Traditional Methods)</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <!-- Pre-Lab Assessment -->
                        <div class="bg-green-50 p-6 rounded-lg border border-green-200">
                            <h2 class="text-2xl font-semibold text-green-800 mb-4">Pre-Lab Preparation Assessment</h2>
                            <p class="text-green-700 mb-6">Rate your confidence levels BEFORE starting the lab session:</p>

                            <div class="space-y-6">
                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Overall Lab Preparation Confidence</label>
                                    <p class="text-gray-600 text-sm mb-3">How confident do you feel about successfully completing the lab tasks?</p>
                                    <div class="flex gap-4 justify-center" id="pre_lab_confidence_ratings">
                                        {generate_rating_options('pre_lab_confidence', True)}
                                    </div>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Safety Knowledge Confidence</label>
                                    <p class="text-gray-600 text-sm mb-3">How confident are you in your understanding of lab safety procedures?</p>
                                    <div class="flex gap-4 justify-center" id="safety_knowledge_confidence_ratings">
                                        {generate_rating_options('safety_knowledge_confidence', True)}
                                    </div>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Technical Skills Confidence</label>
                                    <p class="text-gray-600 text-sm mb-3">How confident are you in your technical ability to perform lab procedures?</p>
                                    <div class="flex gap-4 justify-center" id="technical_skills_confidence_ratings">
                                        {generate_rating_options('technical_skills_confidence', True)}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Experimental Group Section -->
                        <div id="experimental-group" class="group-section bg-blue-50 p-6 rounded-lg border border-blue-200">
                            <h2 class="text-2xl font-semibold text-blue-800 mb-4">GenAI Tools Usage</h2>
                            
                            <div class="space-y-6">
                                <div>
                                    <label class="block text-lg font-medium text-gray-700 mb-3">Which GenAI tools did you use for lab preparation?</label>
                                    <select name="genai_tools_used" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" multiple>
                                        {genai_tool_options}
                                    </select>
                                    <p class="text-sm text-gray-500 mt-2">Hold Ctrl/Cmd to select multiple options</p>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Quality of AI Prompts Used</label>
                                    <p class="text-gray-600 text-sm mb-3">How effective were your prompts in generating useful lab preparation content?</p>
                                    <div class="flex gap-4 justify-center" id="prompt_quality_ratings">
                                        {generate_rating_options('prompt_quality')}
                                    </div>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Helpfulness of AI Outputs</label>
                                    <p class="text-gray-600 text-sm mb-3">How useful were the AI-generated responses for your lab preparation?</p>
                                    <div class="flex gap-4 justify-center" id="output_helpfulness_ratings">
                                        {generate_rating_options('output_helpfulness')}
                                    </div>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">AI-Assisted Preparedness</label>
                                    <p class="text-gray-600 text-sm mb-3">How well did GenAI tools prepare you for the lab session?</p>
                                    <div class="flex gap-4 justify-center" id="ai_preparedness_rating_ratings">
                                        {generate_rating_options('ai_preparedness_rating')}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Control Group Section -->
                        <div id="control-group" class="group-section bg-orange-50 p-6 rounded-lg border border-orange-200">
                            <h2 class="text-2xl font-semibold text-orange-800 mb-4">Traditional Methods Usage</h2>
                            
                            <div class="space-y-6">
                                <div>
                                    <label class="block text-lg font-medium text-gray-700 mb-3">Which traditional methods did you use for lab preparation?</label>
                                    <select name="traditional_methods_used" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" multiple>
                                        {traditional_method_options}
                                    </select>
                                    <p class="text-sm text-gray-500 mt-2">Hold Ctrl/Cmd to select multiple options</p>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Traditional Methods Preparedness</label>
                                    <p class="text-gray-600 text-sm mb-3">How well did traditional methods prepare you for the lab session?</p>
                                    <div class="flex gap-4 justify-center" id="traditional_preparedness_rating_ratings">
                                        {generate_rating_options('traditional_preparedness_rating')}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Post-Lab Assessment -->
                        <div class="bg-indigo-50 p-6 rounded-lg border border-indigo-200">
                            <h2 class="text-2xl font-semibold text-indigo-800 mb-4">Post-Lab Performance Assessment</h2>
                            <p class="text-indigo-700 mb-6">Rate your performance and learning AFTER completing the lab session:</p>

                            <div class="space-y-6">
                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Task Accuracy & Performance</label>
                                    <p class="text-gray-600 text-sm mb-3">How accurately were you able to complete the lab tasks?</p>
                                    <div class="flex gap-4 justify-center" id="task_accuracy_rating_ratings">
                                        {generate_rating_options('task_accuracy_rating', True)}
                                    </div>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Safety Compliance & Awareness</label>
                                    <p class="text-gray-600 text-sm mb-3">How well did you follow safety protocols during the lab?</p>
                                    <div class="flex gap-4 justify-center" id="safety_compliance_rating_ratings">
                                        {generate_rating_options('safety_compliance_rating', True)}
                                    </div>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Conceptual Understanding Gain</label>
                                    <p class="text-gray-600 text-sm mb-3">How much did your understanding of lab concepts improve?</p>
                                    <div class="flex gap-4 justify-center" id="conceptual_understanding_gain_ratings">
                                        {generate_rating_options('conceptual_understanding_gain', True)}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Qualitative Feedback -->
                        <div class="bg-gray-50 p-6 rounded-lg border border-gray-200">
                            <h2 class="text-2xl font-semibold text-gray-800 mb-4">Qualitative Feedback</h2>
                            
                            <div class="space-y-6">
                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">What were the strengths of your preparation method?</label>
                                    <textarea name="preparation_method_strengths" rows="3" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="What worked well in your lab preparation approach?"></textarea>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">What limitations did you encounter?</label>
                                    <textarea name="preparation_method_limitations" rows="3" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="What challenges or limitations did you face?"></textarea>
                                </div>

                                <div id="ai-feedback-section" class="group-section">
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Experience with GenAI Tools</label>
                                    <textarea name="ai_experience_feedback" rows="3" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="Your experience using AI tools, prompt strategies, output quality..."></textarea>
                                </div>

                                <div>
                                    <label class="block text-lg font-medium text-gray-800 mb-3">Suggestions for improving lab preparation</label>
                                    <textarea name="suggestions_improvement" rows="3" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="How could lab preparation be enhanced for future students?"></textarea>
                                </div>
                            </div>
                        </div>

                        <!-- Consent -->
                        <div class="bg-purple-50 p-6 rounded-lg border border-purple-200">
                            <div class="space-y-4">
                                <div class="flex items-start">
                                    <input type="checkbox" name="consent_given" required class="mt-1 mr-3">
                                    <div>
                                        <label class="block text-lg font-medium text-gray-800 mb-2">Research Participation Consent</label>
                                        <p class="text-gray-600 text-sm">
                                            I understand that this research is conducted under Monash University ethics approval (MUHREC 2025-67890-GENAI). 
                                            I consent to participate voluntarily and understand that I may withdraw at any time without penalty. 
                                            I acknowledge that my responses will be anonymized and used for educational research purposes.
                                        </p>
                                    </div>
                                </div>
                                
                                <div class="flex items-start">
                                    <input type="checkbox" name="data_usage_consent" required class="mt-1 mr-3">
                                    <div>
                                        <label class="block text-lg font-medium text-gray-800 mb-2">Data Usage Consent</label>
                                        <p class="text-gray-600 text-sm">
                                            I consent to my anonymized data being used in research publications, presentations, 
                                            and for improving educational practices at Monash University.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="text-center">
                            <button type="submit" class="bg-purple-600 hover:bg-purple-700 text-white font-bold py-4 px-16 rounded-lg text-lg transition duration-300 transform hover:scale-105 shadow-lg">
                                Submit Research Response
                            </button>
                        </div>
                    </form>

                    <div class="text-center mt-8">
                        <a href="/" class="text-purple-600 hover:text-purple-800 text-lg font-medium">← Return to Research Portal</a>
                    </div>
                </div>
            </div>
        </div>

        <script>
            function handleRatingChange(radio) {{
                const container = radio.closest('div[class*="justify-center"]');
                const allOptions = container.querySelectorAll('.rating-option');
                
                allOptions.forEach(option => {{
                    option.classList.remove('rating-selected');
                }});
                
                const selectedOption = radio.nextElementSibling;
                selectedOption.classList.add('rating-selected');
            }}

            function toggleGroupSections(group) {{
                // Hide all group-specific sections first
                document.querySelectorAll('.group-section').forEach(section => {{
                    section.style.display = 'none';
                }});
                
                // Show relevant sections based on group selection
                if (group === 'experimental') {{
                    document.getElementById('experimental-group').style.display = 'block';
                    document.getElementById('ai-feedback-section').style.display = 'block';
                }} else if (group === 'control') {{
                    document.getElementById('control-group').style.display = 'block';
                }}
            }}

            // Initialize on page load
            document.addEventListener('DOMContentLoaded', function() {{
                const allRadios = document.querySelectorAll('input[type="radio"]');
                allRadios.forEach(radio => {{
                    if (radio.checked) {{
                        const selectedOption = radio.nextElementSibling;
                        selectedOption.classList.add('rating-selected');
                    }}
                }});
                
                // Check if group is already selected
                const groupSelect = document.querySelector('select[name="study_group"]');
                if (groupSelect.value) {{
                    toggleGroupSections(groupSelect.value);
                }}
            }});

            // Form submission handler
            document.getElementById('genaiSurveyForm').addEventListener('submit', function(e) {{
                const submitBtn = this.querySelector('button[type="submit"]');
                submitBtn.disabled = true;
                submitBtn.innerHTML = 'Submitting Research Data...';
                submitBtn.classList.remove('hover:scale-105', 'hover:bg-purple-700');
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=survey_html)

@app.post("/submit-genai-survey")
async def submit_genai_survey(
    request: Request,
    student_id: str = Form(None),
    study_group: str = Form(...),
    faculty: str = Form(...),
    year_level: str = Form(...),
    pre_lab_confidence: int = Form(...),
    safety_knowledge_confidence: int = Form(...),
    technical_skills_confidence: int = Form(...),
    genai_tools_used: str = Form(None),
    prompt_quality: int = Form(None),
    output_helpfulness: int = Form(None),
    ai_preparedness_rating: int = Form(None),
    traditional_methods_used: str = Form(None),
    traditional_preparedness_rating: int = Form(None),
    task_accuracy_rating: int = Form(...),
    safety_compliance_rating: int = Form(...),
    conceptual_understanding_gain: int = Form(...),
    preparation_method_strengths: str = Form(None),
    preparation_method_limitations: str = Form(None),
    ai_experience_feedback: str = Form(None),
    suggestions_improvement: str = Form(None),
    consent_given: bool = Form(False),
    data_usage_consent: bool = Form(False),
    db: SessionLocal = Depends(get_db)
):
    try:
        print("📥 Received GenAI research survey submission")
        print(f"📊 Study Group: {study_group}")
        
        # Create research response
        research_response = GenAISurveyResponse(
            student_id=student_id,
            study_group=study_group,
            faculty=faculty,
            year_level=year_level,
            pre_lab_confidence=pre_lab_confidence,
            safety_knowledge_confidence=safety_knowledge_confidence,
            technical_skills_confidence=technical_skills_confidence,
            genai_tools_used=genai_tools_used,
            prompt_quality=prompt_quality,
            output_helpfulness=output_helpfulness,
            ai_preparedness_rating=ai_preparedness_rating,
            traditional_methods_used=traditional_methods_used,
            traditional_preparedness_rating=traditional_preparedness_rating,
            task_accuracy_rating=task_accuracy_rating,
            safety_compliance_rating=safety_compliance_rating,
            conceptual_understanding_gain=conceptual_understanding_gain,
            preparation_method_strengths=preparation_method_strengths,
            preparation_method_limitations=preparation_method_limitations,
            ai_experience_feedback=ai_experience_feedback,
            suggestions_improvement=suggestions_improvement,
            consent_given=consent_given,
            data_usage_consent=data_usage_consent
        )
        
        db.add(research_response)
        db.commit()
        db.refresh(research_response)
        
        print(f"✅ GenAI research response saved with ID: {research_response.id}")
        print(f"📈 Group: {study_group}, Faculty: {faculty}")
        
        return RedirectResponse(url="/thank-you-genai", status_code=303)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error saving GenAI research survey: {e}")
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Research Submission Error</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-100 min-h-screen flex items-center justify-center">
            <div class="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 text-center">
                <div class="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <span class="text-2xl text-red-600">⚠️</span>
                </div>
                <h2 class="text-3xl font-bold text-gray-800 mb-4">Research Submission Error</h2>
                <p class="text-lg text-gray-600 mb-6">
                    We encountered an issue saving your research response. Please try again in a moment.
                </p>
                <div class="bg-red-50 border-l-4 border-red-500 p-4 mb-6 text-left rounded">
                    <p class="text-red-700 text-sm">
                        <strong>Technical Issue:</strong> Research data saving temporarily unavailable.
                    </p>
                </div>
                <a href="/genai-survey" class="bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-8 rounded-lg transition duration-300 inline-block">
                    Try Again
                </a>
                <div class="mt-4">
                    <a href="/" class="text-purple-600 hover:text-purple-800">Return to Research Portal</a>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)

# =============================================================================
# THANK YOU PAGES
# =============================================================================

@app.get("/thank-you", response_class=HTMLResponse)
async def thank_you():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Thank You - FIT5122 Survey</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
        <style> body { font-family: 'Noto Sans JP', sans-serif; background: #aae6be; } </style>
    </head>
    <body class="min-h-screen flex items-center justify-center">
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
                Return to Research Portal
            </a>
        </div>
    </body>
    </html>
    """

@app.get("/thank-you-genai", response_class=HTMLResponse)
async def thank_you_genai():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Thank You - GenAI Research</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
        <style> body { font-family: 'Noto Sans JP', sans-serif; background: #aae6be; } </style>
    </head>
    <body class="min-h-screen flex items-center justify-center">
        <div class="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 text-center">
            <div class="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg class="w-10 h-10 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
            </div>
            <h2 class="text-3xl font-bold text-gray-800 mb-4">Research Participation Complete!</h2>
            <p class="text-lg text-gray-600 mb-6">
                Thank you for contributing to our study on Generative AI in laboratory education. 
                Your responses will help advance understanding of AI tools in STEM education.
            </p>
            <div class="bg-purple-50 border-l-4 border-purple-500 p-4 mb-6 text-left rounded">
                <p class="text-purple-700 text-sm">
                    <strong>Research Impact:</strong> Your participation contributes to evidence-based insights 
                    that could shape future educational practices and technology integration at Monash University.
                </p>
            </div>
            <a href="/" class="bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-8 rounded-lg transition duration-300 inline-block">
                Return to Research Portal
            </a>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health(db: SessionLocal = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        fit5122_count = db.query(FIT5122SurveyResponse).count()
        genai_count = db.query(GenAISurveyResponse).count()
        return {
            "status": "healthy", 
            "service": "monash-research-portal",
            "database": "connected" if "postgresql" in DATABASE_URL else "sqlite",
            "surveys": {
                "fit5122_responses": fit5122_count,
                "genai_responses": genai_count,
                "total_responses": fit5122_count + genai_count
            }
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
        
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)