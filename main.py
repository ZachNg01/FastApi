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
    print("⚠️ DATABASE_URL not set - using SQLite")
    DATABASE_URL = "sqlite:///./test.db"

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
  <title>FIT5122 Survey - Monash University</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen flex items-center justify-center">
  <div class="max-w-2xl w-full bg-white rounded-2xl shadow-2xl p-8 text-center">
    <h1 class="text-4xl font-bold text-blue-800 mb-4">FIT5122 Unit Effectiveness Survey</h1>
    <p class="text-lg text-gray-600 mb-6">Monash University Faculty of Information Technology</p>
    <div class="bg-blue-50 p-4 rounded-lg mb-6">
      <p class="text-blue-700">Ethics Approved - MUHREC</p>
    </div>
    <a href="/survey" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg inline-block">
      Start Survey
    </a>
    <div class="mt-4">
      <a href="/health" class="text-blue-600 hover:text-blue-800">Health Check</a>
    </div>
  </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(HTML_TEMPLATE)

@app.get("/survey", response_class=HTMLResponse)
async def survey_form():
    lab_options = "".join([f'<option value="{session}">{session}</option>' for session in LAB_SESSIONS])
    
    # Generate rating options
    rating_html = ""
    for i in range(1, 6):
        rating_html += f"""
        <label class="flex flex-col items-center cursor-pointer">
            <input type="radio" name="rating" value="{i}" class="sr-only">
            <div class="w-12 h-12 rounded-full border-2 border-blue-300 flex items-center justify-center hover:bg-blue-100 rating-option">{i}</div>
        </label>
        """
    
    survey_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FIT5122 Survey</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 min-h-screen flex items-center justify-center">
        <div class="max-w-2xl w-full bg-white rounded-2xl shadow-2xl p-8">
            <h1 class="text-3xl font-bold text-blue-800 mb-6 text-center">FIT5122 Survey</h1>
            
            <form method="post" action="/submit-survey" class="space-y-6">
                <div>
                    <label class="block text-lg font-medium text-gray-700 mb-3">Did you participate in FIT5122?</label>
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
                    <label class="block text-lg font-medium text-gray-700 mb-3">Lab Session</label>
                    <select name="lab_session" class="w-full px-4 py-2 border border-gray-300 rounded-lg">
                        <option value="">Select session</option>
                        {lab_options}
                    </select>
                </div>

                <div>
                    <label class="block text-lg font-medium text-gray-700 mb-3">Rate your experience (1-5)</label>
                    <div class="flex gap-4 justify-center">
                        {rating_html}
                    </div>
                </div>

                <div>
                    <label class="block text-lg font-medium text-gray-700 mb-3">Comments</label>
                    <textarea name="comments" rows="3" class="w-full px-4 py-3 border border-gray-300 rounded-lg" placeholder="Your feedback..."></textarea>
                </div>

                <div class="flex items-start">
                    <input type="checkbox" name="consent_given" required class="mt-1 mr-3">
                    <label class="text-gray-700">I consent to participate in this research</label>
                </div>

                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg">
                    Submit Survey
                </button>
            </form>

            <div class="text-center mt-6">
                <a href="/" class="text-blue-600 hover:text-blue-800">← Back to Home</a>
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

@app.post("/submit-survey")
async def submit_survey(
    participated_fully: str = Form(...),
    lab_session: str = Form(None),
    comments: str = Form(None),
    consent_given: bool = Form(False),
    db: SessionLocal = Depends(get_db)
):
    try:
        participated_bool = participated_fully.lower() == 'true'
        
        survey_response = FIT5122SurveyResponse(
            participated_fully=participated_bool,
            lab_session=lab_session,
            positive_aspects=comments,
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
        <title>Thank You</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 min-h-screen flex items-center justify-center">
        <div class="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 text-center">
            <h2 class="text-3xl font-bold text-gray-800 mb-4">Thank You!</h2>
            <p class="text-lg text-gray-600 mb-6">Your response has been recorded.</p>
            <a href="/" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg inline-block">
                Return to Home
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
            "database": "connected",
            "total_responses": count
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)