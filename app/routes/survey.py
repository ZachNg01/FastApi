from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.models import SurveyResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def survey_form(request: Request):
    return templates.TemplateResponse("survey.html", {"request": request})

@router.post("/submit")
async def submit_survey(
    request: Request,
    student_id: str = Form(None),
    program: str = Form(...),
    semester: str = Form(...),
    instructor_effectiveness: int = Form(...),
    curriculum_quality: int = Form(...),
    facility_rating: int = Form(...),
    equipment_quality: int = Form(...),
    support_services: int = Form(...),
    overall_satisfaction: int = Form(...),
    positive_comments: str = Form(None),
    improvement_suggestions: str = Form(None),
    additional_comments: str = Form(None),
    age_group: str = Form(None),
    prior_experience: str = Form(None),
    follow_up_permission: bool = Form(False),
    db: Session = Depends(get_db)
):
    try:
        # Validate ratings are within 1-5 range
        ratings = [
            instructor_effectiveness, curriculum_quality, facility_rating,
            equipment_quality, support_services, overall_satisfaction
        ]
        
        for rating in ratings:
            if not 1 <= rating <= 5:
                raise HTTPException(status_code=400, detail="Ratings must be between 1 and 5")
        
        survey_response = SurveyResponse(
            student_id=student_id,
            program=program,
            semester=semester,
            instructor_effectiveness=instructor_effectiveness,
            curriculum_quality=curriculum_quality,
            facility_rating=facility_rating,
            equipment_quality=equipment_quality,
            support_services=support_services,
            overall_satisfaction=overall_satisfaction,
            positive_comments=positive_comments,
            improvement_suggestions=improvement_suggestions,
            additional_comments=additional_comments,
            age_group=age_group,
            prior_experience=prior_experience,
            follow_up_permission=follow_up_permission
        )
        
        db.add(survey_response)
        db.commit()
        db.refresh(survey_response)
        
        return RedirectResponse(url="/survey/thank-you", status_code=303)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error submitting survey: {str(e)}")

@router.get("/thank-you", response_class=HTMLResponse)
async def thank_you(request: Request):
    return templates.TemplateResponse("thank_you.html", {"request": request})