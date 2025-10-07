from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.database import get_db
from app.models import SurveyResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def view_results(request: Request, db: Session = Depends(get_db)):
    # Calculate average ratings
    avg_ratings = db.query(
        func.avg(SurveyResponse.instructor_effectiveness).label('avg_instructor'),
        func.avg(SurveyResponse.curriculum_quality).label('avg_curriculum'),
        func.avg(SurveyResponse.facility_rating).label('avg_facility'),
        func.avg(SurveyResponse.equipment_quality).label('avg_equipment'),
        func.avg(SurveyResponse.support_services).label('avg_support'),
        func.avg(SurveyResponse.overall_satisfaction).label('avg_overall'),
        func.count(SurveyResponse.id).label('total_responses')
    ).first()
    
    # Program breakdown
    program_stats = db.query(
        SurveyResponse.program,
        func.count(SurveyResponse.id).label('count'),
        func.avg(SurveyResponse.overall_satisfaction).label('avg_satisfaction')
    ).group_by(SurveyResponse.program).all()
    
    # Recent responses
    recent_responses = db.query(SurveyResponse).order_by(SurveyResponse.timestamp.desc()).limit(10).all()
    
    return templates.TemplateResponse("results.html", {
        "request": request,
        "avg_ratings": avg_ratings,
        "program_stats": program_stats,
        "recent_responses": recent_responses
    })

@router.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """API endpoint for survey statistics"""
    avg_ratings = db.query(
        func.avg(SurveyResponse.instructor_effectiveness).label('instructor'),
        func.avg(SurveyResponse.curriculum_quality).label('curriculum'),
        func.avg(SurveyResponse.facility_rating).label('facility'),
        func.avg(SurveyResponse.equipment_quality).label('equipment'),
        func.avg(SurveyResponse.support_services).label('support'),
        func.avg(SurveyResponse.overall_satisfaction).label('overall'),
        func.count(SurveyResponse.id).label('total_responses')
    ).first()
    
    return {
        "average_ratings": {
            "instructor": round(avg_ratings.instructor or 0, 2),
            "curriculum": round(avg_ratings.curriculum or 0, 2),
            "facility": round(avg_ratings.facility or 0, 2),
            "equipment": round(avg_ratings.equipment or 0, 2),
            "support": round(avg_ratings.support or 0, 2),
            "overall": round(avg_ratings.overall or 0, 2)
        },
        "total_responses": avg_ratings.total_responses
    }