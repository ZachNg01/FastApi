from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

app = FastAPI(title="Cooking School Survey", version="1.0.0")

# Mount templates
templates = Jinja2Templates(directory="templates")

# Survey questions (like pages in a book)
SURVEY_PAGES = [
    {
        "page": 1,
        "title": "Welcome to the Survey",
        "content": """
        <div class="max-w-4xl mx-auto bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl p-8">
            <h2 class="text-3xl font-bold text-gray-800 mb-6">Student Satisfaction Survey</h2>
            <p class="text-lg text-gray-600 mb-6">
                Thank you for participating in our cooking school satisfaction survey. 
                This survey follows Wallis Social Research methodology and will take about 5-10 minutes to complete.
            </p>
            <div class="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6">
                <p class="text-blue-700">
                    <strong>Confidentiality:</strong> Your responses are completely anonymous and will be used solely to improve our programs.
                </p>
            </div>
            <div class="text-center">
                <a href="/survey/1" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-8 rounded-lg transition duration-300 transform hover:scale-105">
                    Start Survey
                </a>
            </div>
        </div>
        """
    },
    {
        "page": 2,
        "title": "Student Information",
        "content": """
        <div class="max-w-4xl mx-auto bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl p-8">
            <h2 class="text-3xl font-bold text-gray-800 mb-6">Tell Us About Yourself</h2>
            <form method="post" action="/survey/2" class="space-y-6">
                <div class="grid md:grid-cols-2 gap-6">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Program</label>
                        <select name="program" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
                            <option value="">Select Program</option>
                            <option value="Culinary Arts">Culinary Arts</option>
                            <option value="Pastry & Baking">Pastry & Baking</option>
                            <option value="Hospitality Management">Hospitality Management</option>
                            <option value="Nutrition">Nutrition</option>
                            <option value="Wine Studies">Wine Studies</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Semester</label>
                        <select name="semester" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
                            <option value="">Select Semester</option>
                            <option value="1st">1st Semester</option>
                            <option value="2nd">2nd Semester</option>
                            <option value="3rd">3rd Semester</option>
                            <option value="4th">4th Semester</option>
                        </select>
                    </div>
                </div>
                <div class="flex justify-between mt-8">
                    <a href="/" class="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-6 rounded-lg transition duration-300">
                        Previous
                    </a>
                    <button type="submit" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-6 rounded-lg transition duration-300 transform hover:scale-105">
                        Next Page
                    </button>
                </div>
            </form>
        </div>
        """
    },
    {
        "page": 3,
        "title": "Instructor Evaluation",
        "content": """
        <div class="max-w-4xl mx-auto bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl p-8">
            <h2 class="text-3xl font-bold text-gray-800 mb-6">Instructor Effectiveness</h2>
            <p class="text-gray-600 mb-6">Please rate your instructors on the following aspects (1 = Poor, 5 = Excellent)</p>
            
            <form method="post" action="/survey/3" class="space-y-6">
                <!-- Knowledge -->
                <div class="bg-gray-50 p-6 rounded-lg">
                    <label class="block text-lg font-medium text-gray-800 mb-3">Subject Knowledge</label>
                    <div class="flex justify-between text-sm text-gray-600 mb-2">
                        <span>Poor</span>
                        <span>Excellent</span>
                    </div>
                    <div class="flex gap-4 justify-center">
                        {% for i in range(1, 6) %}
                        <label class="flex flex-col items-center cursor-pointer">
                            <input type="radio" name="knowledge" value="{{ i }}" required class="sr-only">
                            <div class="w-12 h-12 rounded-full border-2 border-indigo-300 flex items-center justify-center transition-all duration-300 hover:bg-indigo-100 radio-circle">
                                {{ i }}
                            </div>
                        </label>
                        {% endfor %}
                    </div>
                </div>

                <!-- Teaching Style -->
                <div class="bg-gray-50 p-6 rounded-lg">
                    <label class="block text-lg font-medium text-gray-800 mb-3">Teaching Style & Communication</label>
                    <div class="flex justify-between text-sm text-gray-600 mb-2">
                        <span>Poor</span>
                        <span>Excellent</span>
                    </div>
                    <div class="flex gap-4 justify-center">
                        {% for i in range(1, 6) %}
                        <label class="flex flex-col items-center cursor-pointer">
                            <input type="radio" name="teaching_style" value="{{ i }}" required class="sr-only">
                            <div class="w-12 h-12 rounded-full border-2 border-indigo-300 flex items-center justify-center transition-all duration-300 hover:bg-indigo-100 radio-circle">
                                {{ i }}
                            </div>
                        </label>
                        {% endfor %}
                    </div>
                </div>

                <!-- Support -->
                <div class="bg-gray-50 p-6 rounded-lg">
                    <label class="block text-lg font-medium text-gray-800 mb-3">Support & Availability</label>
                    <div class="flex justify-between text-sm text-gray-600 mb-2">
                        <span>Poor</span>
                        <span>Excellent</span>
                    </div>
                    <div class="flex gap-4 justify-center">
                        {% for i in range(1, 6) %}
                        <label class="flex flex-col items-center cursor-pointer">
                            <input type="radio" name="support" value="{{ i }}" required class="sr-only">
                            <div class="w-12 h-12 rounded-full border-2 border-indigo-300 flex items-center justify-center transition-all duration-300 hover:bg-indigo-100 radio-circle">
                                {{ i }}
                            </div>
                        </label>
                        {% endfor %}
                    </div>
                </div>

                <div class="flex justify-between mt-8">
                    <a href="/survey/2" class="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-6 rounded-lg transition duration-300">
                        Previous
                    </a>
                    <button type="submit" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-6 rounded-lg transition duration-300 transform hover:scale-105">
                        Next Page
                    </button>
                </div>
            </form>
        </div>
        """
    },
    {
        "page": 4,
        "title": "Facilities & Resources",
        "content": """
        <div class="max-w-4xl mx-auto bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl p-8">
            <h2 class="text-3xl font-bold text-gray-800 mb-6">Facilities & Resources</h2>
            <p class="text-gray-600 mb-6">How would you rate our facilities and learning resources?</p>
            
            <form method="post" action="/survey/4" class="space-y-6">
                <!-- Kitchen Facilities -->
                <div class="bg-gray-50 p-6 rounded-lg">
                    <label class="block text-lg font-medium text-gray-800 mb-3">Kitchen Facilities & Equipment</label>
                    <div class="flex justify-between text-sm text-gray-600 mb-2">
                        <span>Needs Improvement</span>
                        <span>Excellent</span>
                    </div>
                    <div class="flex gap-4 justify-center">
                        {% for i in range(1, 6) %}
                        <label class="flex flex-col items-center cursor-pointer">
                            <input type="radio" name="facilities" value="{{ i }}" required class="sr-only">
                            <div class="w-12 h-12 rounded-full border-2 border-green-300 flex items-center justify-center transition-all duration-300 hover:bg-green-100 radio-circle">
                                {{ i }}
                            </div>
                        </label>
                        {% endfor %}
                    </div>
                </div>

                <!-- Learning Resources -->
                <div class="bg-gray-50 p-6 rounded-lg">
                    <label class="block text-lg font-medium text-gray-800 mb-3">Learning Materials & Resources</label>
                    <div class="flex justify-between text-sm text-gray-600 mb-2">
                        <span>Inadequate</span>
                        <span>Comprehensive</span>
                    </div>
                    <div class="flex gap-4 justify-center">
                        {% for i in range(1, 6) %}
                        <label class="flex flex-col items-center cursor-pointer">
                            <input type="radio" name="resources" value="{{ i }}" required class="sr-only">
                            <div class="w-12 h-12 rounded-full border-2 border-green-300 flex items-center justify-center transition-all duration-300 hover:bg-green-100 radio-circle">
                                {{ i }}
                            </div>
                        </label>
                        {% endfor %}
                    </div>
                </div>

                <!-- Safety -->
                <div class="bg-gray-50 p-6 rounded-lg">
                    <label class="block text-lg font-medium text-gray-800 mb-3">Safety & Hygiene Standards</label>
                    <div class="flex justify-between text-sm text-gray-600 mb-2">
                        <span>Poor</span>
                        <span>Excellent</span>
                    </div>
                    <div class="flex gap-4 justify-center">
                        {% for i in range(1, 6) %}
                        <label class="flex flex-col items-center cursor-pointer">
                            <input type="radio" name="safety" value="{{ i }}" required class="sr-only">
                            <div class="w-12 h-12 rounded-full border-2 border-green-300 flex items-center justify-center transition-all duration-300 hover:bg-green-100 radio-circle">
                                {{ i }}
                            </div>
                        </label>
                        {% endfor %}
                    </div>
                </div>

                <div class="flex justify-between mt-8">
                    <a href="/survey/3" class="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-6 rounded-lg transition duration-300">
                        Previous
                    </a>
                    <button type="submit" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-6 rounded-lg transition duration-300 transform hover:scale-105">
                        Next Page
                    </button>
                </div>
            </form>
        </div>
        """
    },
    {
        "page": 5,
        "title": "Overall Experience",
        "content": """
        <div class="max-w-4xl mx-auto bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl p-8">
            <h2 class="text-3xl font-bold text-gray-800 mb-6">Overall Experience & Feedback</h2>
            
            <form method="post" action="/survey/5" class="space-y-6">
                <!-- Overall Satisfaction -->
                <div class="bg-yellow-50 border-l-4 border-yellow-500 p-6 rounded-lg">
                    <label class="block text-lg font-medium text-gray-800 mb-4">Overall Satisfaction with the Program</label>
                    <div class="flex justify-between text-sm text-gray-600 mb-2">
                        <span>Very Dissatisfied</span>
                        <span>Very Satisfied</span>
                    </div>
                    <div class="flex gap-4 justify-center">
                        {% for i in range(1, 6) %}
                        <label class="flex flex-col items-center cursor-pointer">
                            <input type="radio" name="overall_satisfaction" value="{{ i }}" required class="sr-only">
                            <div class="w-12 h-12 rounded-full border-2 border-yellow-300 flex items-center justify-center transition-all duration-300 hover:bg-yellow-100 radio-circle">
                                {{ i }}
                            </div>
                        </label>
                        {% endfor %}
                    </div>
                </div>

                <!-- Positive Feedback -->
                <div>
                    <label class="block text-lg font-medium text-gray-800 mb-3">What do you enjoy most about the program?</label>
                    <textarea name="positive_feedback" rows="4" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" placeholder="Share what you love about your experience..."></textarea>
                </div>

                <!-- Improvement Suggestions -->
                <div>
                    <label class="block text-lg font-medium text-gray-800 mb-3">Suggestions for improvement:</label>
                    <textarea name="improvements" rows="4" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" placeholder="How can we make the program better?"></textarea>
                </div>

                <!-- Additional Comments -->
                <div>
                    <label class="block text-lg font-medium text-gray-800 mb-3">Any additional comments?</label>
                    <textarea name="additional_comments" rows="3" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" placeholder="Other feedback or suggestions..."></textarea>
                </div>

                <div class="flex justify-between mt-8">
                    <a href="/survey/4" class="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-6 rounded-lg transition duration-300">
                        Previous
                    </a>
                    <button type="submit" class="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-8 rounded-lg transition duration-300 transform hover:scale-105">
                        Submit Survey
                    </button>
                </div>
            </form>
        </div>
        """
    }
]

# Store survey responses temporarily (in production, use a database)
survey_responses = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Homepage with your beautiful HTML design"""
    return templates.TemplateResponse("base.html", {"request": request})

@app.get("/survey/{page_number}")
async def get_survey_page(request: Request, page_number: int):
    """Get a specific survey page"""
    if page_number < 1 or page_number > len(SURVEY_PAGES):
        return RedirectResponse("/")
    
    page_data = SURVEY_PAGES[page_number - 1]
    return templates.TemplateResponse("base.html", {
        "request": request,
        "survey_content": page_data["content"],
        "current_page": page_number,
        "total_pages": len(SURVEY_PAGES)
    })

@app.post("/survey/{page_number}")
async def post_survey_page(request: Request, page_number: int):
    """Handle survey form submission"""
    form_data = await request.form()
    
    # Store the responses (in production, save to database)
    session_id = request.client.host  # Simple session identifier
    if session_id not in survey_responses:
        survey_responses[session_id] = {}
    
    # Add form data to responses
    for key, value in form_data.items():
        survey_responses[session_id][key] = value
    
    # Move to next page or complete survey
    if page_number < len(SURVEY_PAGES):
        return RedirectResponse(f"/survey/{page_number + 1}")
    else:
        # Survey complete - show thank you page
        return RedirectResponse("/thank-you")

@app.get("/thank-you", response_class=HTMLResponse)
async def thank_you(request: Request):
    """Thank you page after survey completion"""
    thank_you_content = """
    <div class="max-w-2xl mx-auto bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl p-12 text-center">
        <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg class="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
        </div>
        <h2 class="text-3xl font-bold text-gray-800 mb-4">Thank You!</h2>
        <p class="text-lg text-gray-600 mb-6">
            Your feedback has been successfully submitted. Your responses will help us improve our cooking school programs and provide better experiences for future students.
        </p>
        <div class="bg-green-50 border-l-4 border-green-500 p-4 mb-6 text-left">
            <p class="text-green-700">
                <strong>Wallis Social Research Methodology:</strong> Your responses contribute to meaningful educational research that drives positive change in culinary education.
            </p>
        </div>
        <a href="/" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-8 rounded-lg transition duration-300 inline-block">
            Return to Home
        </a>
    </div>
    """
    return templates.TemplateResponse("base.html", {
        "request": request,
        "survey_content": thank_you_content
    })

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cooking-school-survey"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)