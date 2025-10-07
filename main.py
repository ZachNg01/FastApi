from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import os
from dotenv import load_dotenv

load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")

# Fix connection string format
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    # Already correct format
    pass
elif DATABASE_URL and DATABASE_URL.startswith("psql '"):
    # Extract the actual connection URL from the psql command
    DATABASE_URL = DATABASE_URL.split("'")[1]

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FIT5122SurveyResponse(Base):
    __tablename__ = "fit5122_survey_responses"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Participation information
    participated_fully = Column(Boolean, nullable=False)
    lab_session = Column(String(50), nullable=True)
    
    # Unit effectiveness ratings (1-5 scale)
    unit_content_quality = Column(Integer, nullable=True)
    teaching_effectiveness = Column(Integer, nullable=True)
    assessment_fairness = Column(Integer, nullable=True)
    learning_resources = Column(Integer, nullable=True)
    overall_experience = Column(Integer, nullable=True)
    
    # Detailed feedback
    positive_aspects = Column(Text, nullable=True)
    improvement_suggestions = Column(Text, nullable=True)
    technical_issues = Column(Text, nullable=True)
    
    # Additional comments
    additional_comments = Column(Text, nullable=True)
    
    # Consent and ethics
    consent_given = Column(Boolean, nullable=False, default=False)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="FIT5122 Unit Effectiveness Survey", version="1.0.0")
templates = Jinja2Templates(directory="templates")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>FIT5122 Unit Effectiveness Survey - Monash University</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/tsparticles@2.11.1/tsparticles.bundle.min.js"></script>
  
  <style>
    :root {
      --clr-primary: #006DAE; /* Monash Blue */
      --clr-secondary: #CC0000; /* Monash Red */
    }
    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0; padding: 0;
    }
    body, html {
      height: 100%; overflow-x: hidden;
      font-family: 'Noto Sans JP', sans-serif;
      position: relative;
      background: url('https://images.unsplash.com/photo-1522163182402-3bff2d4a46bc?auto=format&fit=crop&w=1950&q=80') center/cover no-repeat fixed;
    }

    /* tsParticles */
    #tsparticles {
      position: absolute; top: 0; left: 0;
      width: 100%; height: 100%;
      z-index: -10;
    }
    .gradient-overlay {
      position: absolute; inset: 0;
      background: linear-gradient(45deg,
        rgba(0,109,174,0.15) 0%,
        rgba(204,0,0,0.15) 25%,
        rgba(0,109,174,0.15) 50%,
        rgba(204,0,0,0.15) 75%,
        rgba(0,109,174,0.15) 100%);
      animation: overlayRotate 30s linear infinite;
      pointer-events: none; z-index: -5;
    }
    @keyframes overlayRotate {
      from { transform: rotate(0deg) scale(1.2); }
      to   { transform: rotate(360deg) scale(1.2); }
    }

    /* Navbar */
    header {
      background: rgba(255,255,255,0.9);
      backdrop-filter: blur(10px);
      position: fixed; top: 0; width: 100%; z-index: 50;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .container { max-width: 1280px; margin: 0 auto; }
    nav a {
      color: #000000; font-weight: 500;
      transition: color 0.3s;
    }
    nav a:hover, nav a.active {
      color: var(--clr-primary);
    }

    /* Main Content */
    .main-content {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 100px 20px 20px;
    }

    .info-card {
      max-width: 800px;
      background: rgba(255,255,255,0.95);
      backdrop-filter: blur(8px);
      padding: 2rem; border-radius: 0.5rem;
      box-shadow: 0 8px 24px rgba(0,0,0,0.7);
      text-align: center;
    }

    .ethics-notice {
      background: #fff3cd;
      border: 1px solid #ffeaa7;
      border-radius: 0.375rem;
      padding: 1rem;
      margin: 1rem 0;
      text-align: left;
    }

    .rating-option input:checked + div {
      background: var(--clr-primary);
      color: white;
      border-color: var(--clr-primary);
    }
  </style>
</head>
<body>
  <!-- Animated background -->
  <div id="tsparticles"></div>
  <div class="gradient-overlay"></div>

  <!-- Navbar -->
  <header>
    <div class="container px-6 py-4 flex items-center justify-between">
      <a href="/" class="text-2xl font-bold" style="color: var(--clr-primary);">FIT5122 Survey</a>
      <nav class="hidden md:flex space-x-8" id="nav-links">
        <a href="/" class="active">Home</a>
        <a href="/survey">Take Survey</a>
        <a href="/health">Health</a>
      </nav>
    </div>
  </header>

  <!-- Main Content -->
  <div class="main-content">
    <div class="info-card">
      <div class="flex items-center justify-center mb-6">
        <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mr-4">
          <span class="text-2xl" style="color: var(--clr-primary);">🎓</span>
        </div>
        <h1 class="text-4xl font-bold" style="color: var(--clr-primary);">FIT5122 Unit Effectiveness Survey</h1>
      </div>
      
      <p class="text-lg text-gray-600 mb-6">
        Monash University Faculty of Information Technology
      </p>

      <div class="ethics-notice">
        <h3 class="font-bold text-amber-800 mb-2">Ethics Approval Notice</h3>
        <p class="text-amber-700 text-sm">
          This survey has obtained approval from the Monash University Human Research Ethics Committee (MUHREC). 
          All data collection follows ethical guidelines for research involving human subjects.
        </p>
        <p class="text-amber-600 text-xs mt-2">
          * This survey is for demonstration purposes to showcase understanding of ethics in human subject research at Monash University.
        </p>
      </div>
      
      <div class="grid md:grid-cols-3 gap-6 mb-8">
        <div class="bg-blue-50 p-6 rounded-lg border border-blue-200">
          <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-blue-600 text-xl">🔒</span>
          </div>
          <h3 class="font-semibold text-gray-800 mb-2">Confidential</h3>
          <p class="text-gray-600 text-sm">Your responses are anonymous and secure</p>
        </div>
        
        <div class="bg-green-50 p-6 rounded-lg border border-green-200">
          <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-green-600 text-xl">⏱️</span>
          </div>
          <h3 class="font-semibold text-gray-800 mb-2">5-7 Minutes</h3>
          <p class="text-gray-600 text-sm">Quick and easy to complete</p>
        </div>
        
        <div class="bg-purple-50 p-6 rounded-lg border border-purple-200">
          <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-purple-600 text-xl">🌟</span>
          </div>
          <h3 class="font-semibold text-gray-800 mb-2">Improve Education</h3>
          <p class="text-gray-600 text-sm">Help enhance FIT5122 for future students</p>
        </div>
      </div>
      
      <a href="/survey" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-12 rounded-lg text-lg transition duration-300 transform hover:scale-105 inline-block" style="background-color: var(--clr-primary);">
        Start Survey
      </a>

      <div class="mt-6 text-sm text-gray-500">
        <p>Data stored securely in Monash University approved database systems</p>
      </div>
    </div>
  </div>

  <footer class="text-center text-gray-300 p-6 bg-white/5 w-full">
    <span>&copy; 2024 Monash University - FIT5122 Unit Effectiveness Research</span>
  </footer>

  <script>
    tsParticles.load('tsparticles', {
      fpsLimit: 60,
      background: { color: 'transparent' },
      particles: {
        number: { value: 60, density: { enable: true, area: 800 } },
        color: { value: ['#006DAE', '#CC0000'] },
        shape: { type: ['circle'] },
        opacity: { value: 0.3 },
        size: { value: { min: 1, max: 4 } },
        move: { enable: true, speed: 1, random: true, straight: false }
      },
      detectRetina: true
    });
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE

@app.get("/survey", response_class=HTMLResponse)
async def survey_form(request: Request):
    survey_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>FIT5122 Survey - Monash University</title>
      <script src="https://cdn.tailwindcss.com"></script>
      <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
      <style>
        :root { --clr-primary: #006DAE; --clr-secondary: #CC0000; }
        body { font-family: 'Noto Sans JP', sans-serif; background: #f5f5f5; min-height: 100vh; padding: 20px; }
        .rating-option input:checked + div { background: #006DAE; color: white; border-color: #006DAE; }
      </style>
    </head>
    <body>
      <header class="bg-white shadow-sm fixed top-0 left-0 right-0 z-50">
        <div class="container mx-auto px-6 py-4 flex items-center justify-between">
          <a href="/" class="text-2xl font-bold text-blue-800">FIT5122 Survey</a>
          <nav class="hidden md:flex space-x-8">
            <a href="/" class="text-gray-600 hover:text-blue-800">Home</a>
            <a href="/survey" class="text-blue-800 font-semibold">Take Survey</a>
          </nav>
        </div>
      </header>

      <div class="min-h-screen flex items-center justify-center pt-20">
        <div class="max-w-4xl w-full bg-white rounded-2xl shadow-2xl p-8">
          <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-blue-800 mb-4">FIT5122 Unit Effectiveness Survey</h1>
            <p class="text-lg text-gray-600">Monash University Faculty of Information Technology</p>
          </div>

          <div class="bg-amber-50 border-l-4 border-amber-400 p-4 mb-6">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-amber-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm text-amber-700">
                  <strong>Ethics Approval:</strong> This research has MUHREC approval. *Demo for ethics compliance understanding.
                </p>
              </div>
            </div>
          </div>

          <form method="post" action="/submit-survey" class="space-y-8">
            <!-- Participation Section -->
            <div class="bg-gray-50 p-6 rounded-lg">
              <h2 class="text-2xl font-semibold text-gray-800 mb-4">Participation Information</h2>
              
              <div class="mb-6">
                <label class="block text-lg font-medium text-gray-700 mb-3">
                  Did you fully participate in FIT5122 this semester?
                </label>
                <div class="flex gap-6">
                  <label class="flex items-center">
                    <input type="radio" name="participated_fully" value="true" required class="mr-2">
                    <span>Yes</span>
                  </label>
                  <label class="flex items-center">
                    <input type="radio" name="participated_fully" value="false" required class="mr-2">
                    <span>No</span>
                  </label>
                </div>
              </div>

              <div>
                <label class="block text-lg font-medium text-gray-700 mb-3">Which lab session did you attend?</label>
                <select name="lab_session" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                  <option value="">Select lab session</option>
                  <option value="Monday 9am">Monday 9am</option>
                  <option value="Monday 2pm">Monday 2pm</option>
                  <option value="Tuesday 10am">Tuesday 10am</option>
                  <option value="Tuesday 3pm">Tuesday 3pm</option>
                  <option value="Wednesday 11am">Wednesday 11am</option>
                  <option value="Wednesday 4pm">Wednesday 4pm</option>
                  <option value="Thursday 1pm">Thursday 1pm</option>
                  <option value="Friday 9am">Friday 9am</option>
                  <option value="Online">Online/Recorded</option>
                </select>
              </div>
            </div>

            <!-- Unit Effectiveness Ratings -->
            <div class="bg-gray-50 p-6 rounded-lg">
              <h2 class="text-2xl font-semibold text-gray-800 mb-4">Unit Effectiveness Ratings</h2>
              <p class="text-gray-600 mb-6">Please rate the following aspects (1 = Very Poor, 5 = Excellent)</p>

              <!-- Unit Content Quality -->
              <div class="mb-6">
                <label class="block text-lg font-medium text-gray-800 mb-3">Unit Content Quality & Relevance</label>
                <div class="flex gap-4 justify-center">
                  {% for i in range(1, 6) %}
                  <label class="flex flex-col items-center cursor-pointer">
                    <input type="radio" name="unit_content_quality" value="{{ i }}" class="sr-only">
                    <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">
                      {{ i }}
                    </div>
                  </label>
                  {% endfor %}
                </div>
              </div>

              <!-- Teaching Effectiveness -->
              <div class="mb-6">
                <label class="block text-lg font-medium text-gray-800 mb-3">Teaching & Instruction Effectiveness</label>
                <div class="flex gap-4 justify-center">
                  {% for i in range(1, 6) %}
                  <label class="flex flex-col items-center cursor-pointer">
                    <input type="radio" name="teaching_effectiveness" value="{{ i }}" class="sr-only">
                    <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">
                      {{ i }}
                    </div>
                  </label>
                  {% endfor %}
                </div>
              </div>

              <!-- Assessment Fairness -->
              <div class="mb-6">
                <label class="block text-lg font-medium text-gray-800 mb-3">Assessment Fairness & Clarity</label>
                <div class="flex gap-4 justify-center">
                  {% for i in range(1, 6) %}
                  <label class="flex flex-col items-center cursor-pointer">
                    <input type="radio" name="assessment_fairness" value="{{ i }}" class="sr-only">
                    <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">
                      {{ i }}
                    </div>
                  </label>
                  {% endfor %}
                </div>
              </div>

              <!-- Learning Resources -->
              <div class="mb-6">
                <label class="block text-lg font-medium text-gray-800 mb-3">Learning Resources & Materials</label>
                <div class="flex gap-4 justify-center">
                  {% for i in range(1, 6) %}
                  <label class="flex flex-col items-center cursor-pointer">
                    <input type="radio" name="learning_resources" value="{{ i }}" class="sr-only">
                    <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">
                      {{ i }}
                    </div>
                  </label>
                  {% endfor %}
                </div>
              </div>

              <!-- Overall Experience -->
              <div class="mb-6">
                <label class="block text-lg font-medium text-gray-800 mb-3">Overall Unit Experience</label>
                <div class="flex gap-4 justify-center">
                  {% for i in range(1, 6) %}
                  <label class="flex flex-col items-center cursor-pointer">
                    <input type="radio" name="overall_experience" value="{{ i }}" class="sr-only">
                    <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center transition-all duration-300 hover:bg-blue-100 rating-option">
                      {{ i }}
                    </div>
                  </label>
                  {% endfor %}
                </div>
              </div>
            </div>

            <!-- Detailed Feedback -->
            <div class="bg-gray-50 p-6 rounded-lg">
              <h2 class="text-2xl font-semibold text-gray-800 mb-4">Detailed Feedback</h2>
              
              <div class="mb-6">
                <label class="block text-lg font-medium text-gray-800 mb-3">What were the most positive aspects of FIT5122?</label>
                <textarea name="positive_aspects" rows="3" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="Share what worked well in the unit..."></textarea>
              </div>

              <div class="mb-6">
                <label class="block text-lg font-medium text-gray-800 mb-3">Suggestions for improvement:</label>
                <textarea name="improvement_suggestions" rows="3" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="How can we improve FIT5122 for future students?"></textarea>
              </div>

              <div class="mb-6">
                <label class="block text-lg font-medium text-gray-800 mb-3">Any technical issues or challenges faced?</label>
                <textarea name="technical_issues" rows="2" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="Moodle, software, or other technical issues..."></textarea>
              </div>

              <div>
                <label class="block text-lg font-medium text-gray-800 mb-3">Additional comments:</label>
                <textarea name="additional_comments" rows="2" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="Any other feedback..."></textarea>
              </div>
            </div>

            <!-- Consent -->
            <div class="bg-blue-50 p-6 rounded-lg border border-blue-200">
              <div class="flex items-start">
                <input type="checkbox" name="consent_given" required class="mt-1 mr-3">
                <div>
                  <label class="block text-lg font-medium text-gray-800 mb-2">Ethics Consent</label>
                  <p class="text-gray-600 text-sm">
                    I understand that this survey is for research purposes and has Monash University ethics approval. 
                    I consent to my anonymous responses being used for educational research and unit improvement. 
                    *This is a demonstration of ethics compliance understanding.
                  </p>
                </div>
              </div>
            </div>

            <div class="text-center">
              <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg text-lg transition duration-300">
                Submit Survey
              </button>
            </div>
          </form>

          <div class="text-center mt-6">
            <a href="/" class="text-blue-600 hover:text-blue-800">← Back to Home</a>
          </div>
        </div>
      </div>

      <script>
        // Rating button interaction
        document.addEventListener('click', function(e) {
          if (e.target.type === 'radio') {
            const allRadios = document.querySelectorAll('input[type="radio"]');
            allRadios.forEach(radio => {
              const div = radio.nextElementSibling;
              if (div && div.classList.contains('rating-option')) {
                div.style.background = 'transparent';
                div.style.color = 'inherit';
              }
            });
            
            const selectedDiv = e.target.nextElementSibling;
            if (selectedDiv && selectedDiv.classList.contains('rating-option')) {
              selectedDiv.style.background = '#006DAE';
              selectedDiv.style.color = 'white';
            }
          }
        });
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
        
        return RedirectResponse(url="/thank-you", status_code=303)
        
    except Exception as e:
        db.rollback()
        return HTMLResponse(content=f"<h1>Error submitting survey: {str(e)}</h1>", status_code=500)

@app.get("/thank-you", response_class=HTMLResponse)
async def thank_you():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Thank You - FIT5122 Survey</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 min-h-screen flex items-center justify-center">
        <div class="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 text-center">
            <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg class="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
            </div>
            <h2 class="text-3xl font-bold text-gray-800 mb-4">Thank You!</h2>
            <p class="text-lg text-gray-600 mb-6">
                Your feedback has been successfully submitted and will help improve FIT5122 for future students.
            </p>
            <div class="bg-green-50 border-l-4 border-green-500 p-4 mb-6 text-left">
                <p class="text-green-700 text-sm">
                    <strong>Research Contribution:</strong> Your response contributes to educational research at Monash University.
                </p>
            </div>
            <a href="/" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition duration-300 inline-block">
                Return to Home
            </a>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health(db: SessionLocal = Depends(get_db)):
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {
            "status": "healthy", 
            "service": "fit5122-survey",
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)