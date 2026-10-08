from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from twinpay_tr.api import deps
from twinpay_tr.models.settings import Settings
from twinpay_tr.models.scenario import Scenario
from twinpay_tr.schemas.settings import SettingsUpdate, SettingsResponse, ScenarioCreate, ScenarioResponse
from typing import List

router = APIRouter()

def get_or_create_settings(db: Session, user_id: int) -> Settings:
    settings = db.query(Settings).filter(Settings.user_id == user_id).first()
    if not settings:
        settings = Settings(user_id=user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.get("/", response_model=SettingsResponse)
def get_settings(db: Session = Depends(deps.get_db), user_id: int = Depends(deps.get_user_id)):
    return get_or_create_settings(db, user_id)

@router.put("/", response_model=SettingsResponse)
def update_settings(
    settings_in: SettingsUpdate,
    db: Session = Depends(deps.get_db),
    user_id: int = Depends(deps.get_user_id)
):
    settings = get_or_create_settings(db, user_id)
    if settings_in.language is not None:
        settings.language = settings_in.language
    if settings_in.chaos_mode_enabled is not None:
        settings.chaos_mode_enabled = settings_in.chaos_mode_enabled
    if settings_in.error_rate is not None:
        if 0 <= settings_in.error_rate <= 100:
            settings.error_rate = settings_in.error_rate
    if settings_in.delay_ms is not None:
        if settings_in.delay_ms >= 0:
            settings.delay_ms = settings_in.delay_ms
    if settings_in.seed is not None:
        settings.seed = settings_in.seed
            
    db.commit()
    db.refresh(settings)
    return settings

@router.post("/scenarios", response_model=ScenarioResponse, status_code=201)
def create_scenario(
    scenario_in: ScenarioCreate,
    db: Session = Depends(deps.get_db),
    user_id: int = Depends(deps.get_user_id)
):
    scenario = Scenario(
        user_id=user_id,
        name=scenario_in.name,
        chaos_mode_enabled=scenario_in.chaos_mode_enabled,
        error_rate=scenario_in.error_rate,
        delay_ms=scenario_in.delay_ms,
        seed=scenario_in.seed
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    return scenario

@router.get("/scenarios", response_model=List[ScenarioResponse])
def get_scenarios(db: Session = Depends(deps.get_db), user_id: int = Depends(deps.get_user_id)):
    return db.query(Scenario).filter(Scenario.user_id == user_id).all()

@router.post("/scenarios/{scenario_id}/apply", response_model=SettingsResponse)
def apply_scenario(
    scenario_id: int,
    db: Session = Depends(deps.get_db),
    user_id: int = Depends(deps.get_user_id)
):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id, Scenario.user_id == user_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Senaryo bulunamadı")
        
    settings = get_or_create_settings(db, user_id)
    settings.chaos_mode_enabled = scenario.chaos_mode_enabled
    settings.error_rate = scenario.error_rate
    settings.delay_ms = scenario.delay_ms
    settings.seed = scenario.seed
    db.commit()
    db.refresh(settings)
    return settings
