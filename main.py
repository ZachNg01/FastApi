from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import os

app = FastAPI()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Cooking School Survey – Wallis Social Research</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/tsparticles@2.11.1/tsparticles.bundle.min.js"></script>
  
  <style>
    :root {
      --clr-bg: #111;
      --clr-fg: #eee;
      --clr-primary: #4F46E5;
      --clr-secondary: #10B981;
    }
    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0; padding: 0;
    }
    body, html {
      height: 100%; overflow-x: hidden;
      font-family: 'Noto Sans JP', sans-serif;
      color: var(--clr-fg);
      position: relative;
      /* Sakura tree background */
      background: url('https://images.unsplash.com/photo-1522163182402-3bff2d4a46bc?auto=format&fit=crop&w=1950&q=80') center/cover no-repeat fixed;
    }
    a { text-decoration: none; }

    /* tsParticles */
    #tsparticles {
      position: absolute; top: 0; left: 0;
      width: 100%; height: 100%;
      z-index: -10;
    }
    /* Animated gradient overlay */
    .gradient-overlay {
      position: absolute; inset: 0;
      background: linear-gradient(45deg,
        rgba(79,70,229,0.15) 0%,
        rgba(16,185,129,0.15) 25%,
        rgba(139,92,246,0.15) 50%,
        rgba(224,170,255,0.15) 75%,
        rgba(79,70,229,0.15) 100%);
      animation: overlayRotate 30s linear infinite;
      pointer-events: none; z-index: -5;
    }
    @keyframes overlayRotate {
      from { transform: rotate(0deg) scale(1.2); }
      to   { transform: rotate(360deg) scale(1.2); }
    }

    /* Navbar */
    header {
      background: rgba(255,255,255,0.2);
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
      color: #3111e7;
    }
    #mobile-menu {
      background: rgba(31,41,55,0.9);
      backdrop-filter: blur(8px);
    }

    /* About Me Card */
    .info-card {
      margin: 100px auto 2rem;
      max-width: 800px;
      background: rgba(31,41,55,0.8);
      backdrop-filter: blur(8px);
      padding: 2rem; border-radius: 0.5rem;
      box-shadow: 0 8px 24px rgba(0,0,0,0.7);
      text-align: center;
    }
    .info-card h1 {
      font-size: 2.5rem; color: var(--clr-primary); margin-bottom: 1rem;
    }
    .info-card p {
      font-size: 1.125rem; line-height: 1.6; opacity: 0.9;
    }

    /* Map container */
    #map {
      width: 100%; height: 400px;
      max-width: 1200px;
      margin: 2rem auto;
      border-radius: 0.5rem;
      box-shadow: 0 4px 16px rgba(0,0,0,0.6);
    }

    /* Skillset Section */
    .skills {
      display: flex; flex-wrap: wrap; gap: 1rem;
      padding: 1rem; max-width: 1200px; margin: 0 auto 4rem;
    }
    .skill-card {
      flex: 1 1 280px;
      background: rgba(31,41,55,0.9);
      border-radius: 0.5rem; overflow: hidden;
      box-shadow: 0 4px 16px rgba(0,0,0,0.6);
      transition: transform 0.3s, box-shadow 0.3s;
      display: flex; flex-direction: column;
    }
    .skill-card:hover {
      transform: translateY(-6px);
      box-shadow: 0 8px 32px rgba(0,0,0,0.8);
    }
    .skill-header {
      background: #1f2937; padding: 1rem;
      display: flex; align-items: center; gap: 1rem;
    }
    .skill-header svg {
      width: 2rem; height: 2rem; fill: var(--clr-secondary);
    }
    .skill-header h3 {
      color: var(--clr-secondary); font-size: 1.25rem; margin: 0;
    }
    .skill-body {
      padding: 1.5rem; flex: 1;
      color: #d1d5db; line-height: 1.5;
    }

    /* Interests Section */
    .interests {
      max-width: 1200px; margin: 0 auto 4rem;
      padding: 2rem; display: grid;
      grid-template-columns: repeat(auto-fit,minmax(240px,1fr));
      gap: 2rem;
    }
    .interest-card {
      background: rgba(31,41,55,0.9);
      border-radius: 0.5rem; padding: 2rem 1rem;
      text-align: center; box-shadow: 0 4px 16px rgba(0,0,0,0.6);
      transition: transform 0.3s, box-shadow 0.3s;
      position: relative; overflow: hidden;
    }
    .interest-card:hover {
      transform: translateY(-6px);
      box-shadow: 0 8px 32px rgba(0,0,0,0.8);
    }
    .interest-card h3 {
      font-size: 1.5rem;
      color: yellow;
      margin-bottom: 0.5rem;
    }

    .interest-card p {
      color: #d1d5db; line-height: 1.5;
    }

    footer {
      text-align: center; padding: 1rem;
      background: rgba(255,255,255,0.1); color: #e5e7eb;
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
      <a href="index.html" class="text-2xl font-bold text-fuchsia-400 hover:text-fuchsia-300">Zach Ng</a>

      <nav class="hidden md:flex space-x-8" id="nav-links">
        <a href="index.html">Home</a>
        <a href="zach.html" class="active">About Me</a>
        <a href="about.html">My Skillset</a>
        <a href="skills.html">My Projects</a>
        <a href="blog_main.html">My Updates</a>
      </nav>
      <button id="burger" class="md:hidden text-gray-200 focus:outline-none">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"/>
        </svg>
      </button>
    </div>
  </header>

  <!-- Mobile Menu -->
  <div id="mobile-menu" class="hidden md:hidden fixed top-16 inset-x-0 z-40">
    <ul class="bg-gray-800 bg-opacity-90 backdrop-blur p-4 space-y-2 text-gray-200">
      <li><a href="index.html">Home</a></li>
      <li><a href="zach.html">About Me</a></li>
      <li><a href="about.html">My Skillset</a></li>
      <li><a href="skills.html">My Projects</a></li>
      <li><a href="blog_main.html">My Updates</a></li>

    </ul>
  </div>

  <!-- Main Content -->
  <div class="main-content">
    <div class="info-card">
      <h1 class="text-4xl font-bold text-white mb-6">Cooking School Student Satisfaction Survey</h1>
      <p class="text-xl text-gray-300 mb-8">
        Wallis Social Research Methodology
      </p>
      
      <div class="grid md:grid-cols-3 gap-6 mb-8">
        <div class="bg-indigo-500/20 p-6 rounded-lg border border-indigo-400/30">
          <div class="w-12 h-12 bg-indigo-400/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-indigo-300 text-xl">🔒</span>
          </div>
          <h3 class="font-semibold text-white mb-2">Confidential</h3>
          <p class="text-gray-300 text-sm">Your responses are anonymous and secure</p>
        </div>
        
        <div class="bg-green-500/20 p-6 rounded-lg border border-green-400/30">
          <div class="w-12 h-12 bg-green-400/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-green-300 text-xl">⏱️</span>
          </div>
          <h3 class="font-semibold text-white mb-2">5-10 Minutes</h3>
          <p class="text-gray-300 text-sm">Quick and easy to complete</p>
        </div>
        
        <div class="bg-purple-500/20 p-6 rounded-lg border border-purple-400/30">
          <div class="w-12 h-12 bg-purple-400/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-purple-300 text-xl">🌟</span>
          </div>
          <h3 class="font-semibold text-white mb-2">Make a Difference</h3>
          <p class="text-gray-300 text-sm">Help improve our programs</p>
        </div>
      </div>
      
      <a href="/survey" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 px-12 rounded-lg text-lg transition duration-300 transform hover:scale-105 inline-block">
        Start Survey
      </a>
    </div>
  </div>

  <footer class="text-center text-gray-300 p-6 bg-white/5 w-full flex flex-col md:flex-row items-center justify-center gap-4 text-sm">
    <span>&copy; 2024 Cooking School Survey - Wallis Social Research</span>
    <span>Confidential Educational Research</span>
  </footer>

  <script>
    // tsParticles init
    tsParticles.load('tsparticles', {
      fpsLimit: 60,
      background: { color: 'transparent' },
      particles: {
        number: { value: 80, density: { enable: true, area: 800 } },
        color: { value: ['#4F46E5', '#10b981', '#8B5CF6'] },
        shape: { type: ['circle'] },
        opacity: { value: 0.3 },
        size: { value: { min: 1, max: 4 } },
        move: {
          enable: true,
          speed: 1,
          random: true,
          straight: false,
        }
      },
      detectRetina: true
    });

    // Mobile menu toggle
    document.getElementById('burger').addEventListener('click', () => {
      document.getElementById('mobile-menu').classList.toggle('hidden');
    });
  </script>
</body>
</html>
"""

SURVEY_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Survey - Cooking School</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
  <style>
    body { 
      font-family: 'Noto Sans JP', sans-serif;
      background: url('https://images.unsplash.com/photo-1522163182402-3bff2d4a46bc?auto=format&fit=crop&w=1950&q=80') center/cover no-repeat fixed;
      min-height: 100vh;
      padding: 20px;
    }
  </style>
</head>
<body>
  <div class="min-h-screen flex items-center justify-center">
    <div class="max-w-4xl w-full bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl p-8">
      <h1 class="text-4xl font-bold text-gray-800 mb-6 text-center">Student Satisfaction Survey</h1>
      
      <form class="space-y-6">
        <!-- Student Info -->
        <div class="grid md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Program</label>
            <select class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500">
              <option>Culinary Arts</option>
              <option>Pastry & Baking</option>
              <option>Hospitality Management</option>
              <option>Nutrition</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Semester</label>
            <select class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500">
              <option>1st Semester</option>
              <option>2nd Semester</option>
              <option>3rd Semester</option>
              <option>4th Semester</option>
            </select>
          </div>
        </div>

        <!-- Ratings -->
        <div class="space-y-4">
          <div class="bg-gray-50 p-4 rounded-lg">
            <label class="block text-lg font-medium text-gray-800 mb-3">Instructor Effectiveness</label>
            <div class="flex gap-4 justify-center">
              <label class="flex flex-col items-center cursor-pointer">
                <input type="radio" name="instructor" value="1" class="sr-only">
                <div class="w-12 h-12 rounded-full border-2 border-indigo-300 flex items-center justify-center hover:bg-indigo-100">1</div>
              </label>
              <label class="flex flex-col items-center cursor-pointer">
                <input type="radio" name="instructor" value="2" class="sr-only">
                <div class="w-12 h-12 rounded-full border-2 border-indigo-300 flex items-center justify-center hover:bg-indigo-100">2</div>
              </label>
              <label class="flex flex-col items-center cursor-pointer">
                <input type="radio" name="instructor" value="3" class="sr-only">
                <div class="w-12 h-12 rounded-full border-2 border-indigo-300 flex items-center justify-center hover:bg-indigo-100">3</div>
              </label>
              <label class="flex flex-col items-center cursor-pointer">
                <input type="radio" name="instructor" value="4" class="sr-only">
                <div class="w-12 h-12 rounded-full border-2 border-indigo-300 flex items-center justify-center hover:bg-indigo-100">4</div>
              </label>
              <label class="flex flex-col items-center cursor-pointer">
                <input type="radio" name="instructor" value="5" class="sr-only">
                <div class="w-12 h-12 rounded-full border-2 border-indigo-300 flex items-center justify-center hover:bg-indigo-100">5</div>
              </label>
            </div>
          </div>
        </div>

        <!-- Feedback -->
        <div>
          <label class="block text-lg font-medium text-gray-800 mb-3">What do you enjoy most?</label>
          <textarea rows="3" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="Share your positive experiences..."></textarea>
        </div>

        <div class="text-center">
          <button type="button" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-8 rounded-lg transition duration-300">
            Submit Survey
          </button>
        </div>
      </form>

      <div class="text-center mt-6">
        <a href="/" class="text-indigo-600 hover:text-indigo-800">← Back to Home</a>
      </div>
    </div>
  </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE

@app.get("/survey", response_class=HTMLResponse)
async def survey():
    return SURVEY_HTML

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "cooking-school-survey", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)