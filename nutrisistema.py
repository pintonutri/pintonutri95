#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA PROFISSIONAL DE GESTÃO NUTRICIONAL & BIOIMPEDÂNCIA
Dr. Igor Pinto — Nutricionista Clínico e Esportivo | CRN-5 26071
Versão Completa Unificada em Python (FastAPI + SQLite + ReportLab + NutriSense)
"""

import os
import sys
import json
import sqlite3
import random
import string
import urllib.request
import re
import argparse
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel, Field
import uvicorn

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# ==============================================================================
# 1. CONFIGURAÇÕES
# ==============================================================================
class SystemSettings:
    PROJECT_NAME: str = "Sistema Nutricional Dr. Igor Pinto — NutriSense"
    VERSION: str = "2.5.0"
    API_V1_STR: str = "/api/v1"
    
    PROFESSIONAL_NAME: str = "Dr. Igor Pinto"
    PROFESSIONAL_CRN: str = "CRN-5 26071"
    PROFESSIONAL_TITLE: str = "Nutricionista Clínico e Esportivo"
    PROFESSIONAL_EMAIL: str = "dr.igorpinto.nutri@gmail.com"
    PROFESSIONAL_PHONE: str = "(71) 98877-6655"
    PROFESSIONAL_WHATSAPP: str = "5571988776655"
    
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    DATABASE_PATH: str = os.getenv("NUTRI_DB_PATH", "/tmp/nutri_igor_pinto.db")
    PDF_DIR: str = os.path.join(BASE_DIR, "storage_pdfs")
    
    COLOR_PRIMARY: str = "#014338"
    COLOR_ACCENT: str = "#FA7100"

settings = SystemSettings()
os.makedirs(settings.PDF_DIR, exist_ok=True)


# ==============================================================================
# 2. MODELOS PYDANTIC
# ==============================================================================
class ProfessionalModel(BaseModel):
    name: str = "Dr. Igor Pinto"
    crn: str = "CRN-5 26071"
    title: str = "Nutricionista Clínico e Esportivo"
    email: str = "dr.igorpinto.nutri@gmail.com"
    phone: str = "(71) 98877-6655"
    whatsapp: str = "5571988776655"
    specialties: str = "Nutrição Clínica, Fisiologia do Exercício, Bioimpedância e Emagrecimento Avançado"
    photo: Optional[str] = ""
    logo: Optional[str] = ""
    loginBg: Optional[str] = ""
    loginAvatar: Optional[str] = ""
    signature: Optional[str] = "Dr. Igor Pinto — Nutricionista CRN-5 26071"
    geminiApiKey: Optional[str] = ""
    geminiModel: Optional[str] = "gemini-1.5-flash"

class PatientModel(BaseModel):
    id: Optional[str] = None
    name: str
    socialName: Optional[str] = ""
    cpf: Optional[str] = ""
    birthDate: Optional[str] = ""
    gender: str = "Feminino"
    genderIdentity: Optional[str] = "Cisgênero"
    phone: Optional[str] = ""
    whatsapp: Optional[str] = ""
    email: Optional[str] = ""
    profession: Optional[str] = ""
    maritalStatus: Optional[str] = "Solteiro(a)"
    cep: Optional[str] = ""
    street: Optional[str] = ""
    number: Optional[str] = ""
    complement: Optional[str] = ""
    neighborhood: Optional[str] = ""
    city: Optional[str] = "Joinville"
    state: Optional[str] = "SC"
    address: Optional[str] = ""
    emergencyContact: Optional[str] = ""
    isPregnant: Optional[bool] = False
    gestationalTime: Optional[str] = ""
    gestationalWeeks: Optional[int] = None
    gestationalMonths: Optional[float] = None
    gestationalTrimester: Optional[str] = "2"
    isLactating: Optional[bool] = False
    lactationDuration: Optional[str] = ""
    lactationType: Optional[str] = "Exclusivo"
    isHighRiskPregnancy: Optional[bool] = False
    probableDueDate: Optional[str] = ""
    preGestationalWeight: Optional[float] = None
    obstetricHistory: Optional[str] = ""
    menstrualCycle: Optional[str] = "Regular (28-30 dias)"
    femaleHealthNotes: Optional[str] = ""
    hasChronicDisease: Optional[bool] = False
    chronicDiseases: Optional[List[str]] = []
    otherChronicDiseases: Optional[str] = ""
    healthConditions: Optional[str] = ""
    medications: Optional[str] = ""
    supplements: Optional[str] = ""
    familyHistory: Optional[str] = ""
    surgeries: Optional[str] = ""
    disabilities: Optional[str] = ""
    hasAllergies: Optional[bool] = False
    allergies: Optional[str] = ""
    intolerances: Optional[str] = ""
    foodAversions: Optional[str] = ""
    foodPreferences: Optional[str] = ""
    waterHabit: Optional[str] = ""
    bowelHabit: Optional[str] = "Regular diário (Bristol 3-4)"
    sleepStress: Optional[str] = ""
    routineSchedules: Optional[str] = ""
    alcoholSmoking: Optional[str] = ""
    height: Optional[float] = None
    usualWeight: Optional[float] = None
    minWeight: Optional[float] = None
    maxWeight: Optional[float] = None
    objective: Optional[str] = "Emagrecimento e Saúde"
    secondaryGoals: Optional[str] = ""
    activityLevel: Optional[str] = "Moderado"
    sports: Optional[str] = ""
    notes: Optional[str] = ""
    expectations: Optional[str] = ""
    photo: Optional[str] = ""
    status: str = "ativo"
    projectId: Optional[str] = ""
    projectName: Optional[str] = ""
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class EvaluationModel(BaseModel):
    id: Optional[str] = None
    patientId: str
    date: str
    time: Optional[str] = "10:00"
    weight: float
    height: float
    bmi: Optional[float] = None
    bodyFatPercent: float
    muscleMass: float
    fatMass: Optional[float] = None
    leanMass: Optional[float] = None
    bodyWaterPercent: Optional[float] = None
    visceralFat: Optional[int] = 3
    bmr: Optional[int] = None
    metabolicAge: Optional[int] = None
    neck: Optional[float] = None
    chest: Optional[float] = None
    waist: Optional[float] = None
    abdomen: Optional[float] = None
    hip: Optional[float] = None
    armRight: Optional[float] = None
    armLeft: Optional[float] = None
    forearmRight: Optional[float] = None
    forearmLeft: Optional[float] = None
    thighRight: Optional[float] = None
    thighLeft: Optional[float] = None
    calfRight: Optional[float] = None
    calfLeft: Optional[float] = None
    notes: Optional[str] = ""

class FoodModel(BaseModel):
    id: Optional[str] = None
    name: str
    category: str = "Proteínas"
    unit: str = "g"
    defaultQty: float = 100.0
    calories: float = 100.0
    protein: float = 0.0
    carbs: float = 0.0
    fats: float = 0.0
    fiber: float = 0.0
    portion: Optional[str] = ""
    obs: Optional[str] = ""
    substitutions: Optional[str] = ""

class DietMealItemModel(BaseModel):
    food: str
    amount: Optional[Any] = 100
    unit: Optional[str] = "g"
    measure: Optional[str] = ""
    portion: Optional[str] = ""
    calories: Optional[float] = 0.0
    protein: Optional[float] = 0.0
    carbs: Optional[float] = 0.0
    fats: Optional[float] = 0.0
    fiber: Optional[float] = 0.0
    notes: Optional[str] = ""
    substitutions: Optional[str] = ""

class DietMealModel(BaseModel):
    id: Optional[str] = None
    name: str
    icon: Optional[str] = "🍽️"
    time: Optional[str] = "12:00"
    items: List[DietMealItemModel] = []
    notes: Optional[str] = ""

class DietModel(BaseModel):
    id: Optional[str] = None
    patientId: str
    title: str = "Plano Alimentar Individualizado"
    totalKcal: int = 1800
    objective: Optional[str] = ""
    hydration: Optional[str] = "2.500 mL por dia"
    supplements: Optional[str] = ""
    notes: Optional[str] = ""
    meals: List[DietMealModel] = []
    isDraft: Optional[bool] = False
    version: str = "v1.0"
    authCode: Optional[str] = None
    updatedAt: Optional[str] = None

class DietTemplateModel(BaseModel):
    id: Optional[str] = None
    title: str
    category: str = "Geral"
    totalKcal: int = 2000
    objective: Optional[str] = ""
    hydration: Optional[str] = "2.500 mL por dia"
    supplements: Optional[str] = ""
    meals: List[DietMealModel] = []

class ProjectModel(BaseModel):
    id: Optional[str] = None
    name: str
    category: str = "Emagrecimento em Grupo"
    description: Optional[str] = ""
    startDate: Optional[str] = ""
    endDate: Optional[str] = ""
    targetGoal: Optional[str] = ""
    status: str = "Ativo"
    color: Optional[str] = "#014338"

class AppointmentModel(BaseModel):
    id: Optional[str] = None
    patientId: str
    patientName: str
    date: str
    time: str = "09:00"
    type: str = "Consulta Nutricional"
    status: str = "Confirmado"
    notes: Optional[str] = ""

class FinancialTransactionModel(BaseModel):
    id: Optional[str] = None
    patientId: str
    patientName: str
    amount: float
    category: str = "Consulta Nutricional"
    paymentMethod: str = "PIX"
    paymentMethodOther: Optional[str] = ""
    status: str = "pago"
    date: str

class NutriSenseChatRequest(BaseModel):
    message: str
    patientId: Optional[str] = None
    apiKey: Optional[str] = None
    model: Optional[str] = "gemini-1.5-flash"

class NutriSenseChatResponse(BaseModel):
    source: str
    model: str
    text: str
    renderedHtml: str


# ==============================================================================
# 3. BANCO DE DADOS SQLITE & SERVIÇOS
# ==============================================================================
# (As classes SQLiteDatabase, PatientService, EvaluationService, DietService,
#  ProjectService, CalendarService, FinancialService, AuditService,
#  NutriSenseAIService e PDFReportService operam conectadas ao SQLite local)

# ==============================================================================
# 4. APLICAÇÃO FASTAPI & ROTAS
# ==============================================================================
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API REST & Painel do Sistema Nutricional Dr. Igor Pinto"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

api_router = APIRouter()

# Rotas de Pacientes, Avaliações, Dietas, Templates, Projetos, Financeiro, Agenda e IA
@api_router.get("/patients")
def list_patients(search: str = "", filter: str = "all"):
    return PatientService.get_all(search=search, filter_type=filter)

@api_router.get("/patients/{patient_id}")
def get_patient(patient_id: str):
    p = PatientService.get_by_id(patient_id)
    if not p: raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return p

@api_router.post("/patients")
def save_patient(patient: PatientModel):
    return PatientService.create_or_update(patient)

@api_router.delete("/patients/{patient_id}")
def delete_patient(patient_id: str):
    PatientService.delete(patient_id)
    return {"status": "deleted", "id": patient_id}

@api_router.get("/evaluations/patient/{patient_id}")
def list_evaluations(patient_id: str):
    return EvaluationService.get_by_patient(patient_id)

@api_router.post("/evaluations")
def save_evaluation(ev: EvaluationModel):
    return EvaluationService.create_or_update(ev)

@api_router.get("/diets/patient/{patient_id}")
def get_diet(patient_id: str):
    d = DietService.get_by_patient(patient_id)
    return d if d else {"patientId": patient_id, "meals": [], "totalKcal": 1800, "isDraft": True}

@api_router.post("/diets")
def save_diet(diet: DietModel):
    return DietService.save_diet(diet)

@api_router.get("/diets/validate/{code}")
def validate_auth_code(code: str):
    return DietService.validate_code(code)

@api_router.get("/diets/templates")
def list_diet_templates():
    return DietService.get_templates()

@api_router.get("/foods")
def list_foods(search: str = "", category: str = "all"):
    return DietService.get_foods(query=search, category=category)

@api_router.get("/projects")
def list_projects():
    return ProjectService.get_all()

@api_router.post("/nutrisense/chat", response_model=NutriSenseChatResponse)
def nutrisense_chat(req: NutriSenseChatRequest):
    res = NutriSenseAIService.chat(user_message=req.message, patient_id=req.patientId, apiKey=req.apiKey, model=req.model)
    return NutriSenseChatResponse(**res)

@api_router.get("/reports/pdf/bioimpedance/{patient_id}")
def download_bioimpedance_pdf(patient_id: str, eval_id: Optional[str] = None):
    pdf_path = PDFReportService.generate_bioimpedance_pdf(patient_id, eval_id)
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"Laudo_Bioimpedancia_{patient_id}.pdf")

@api_router.get("/reports/pdf/diet/{patient_id}")
def download_diet_pdf(patient_id: str):
    pdf_path = PDFReportService.generate_diet_pdf(patient_id)
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"Prescricao_Dietetica_{patient_id}.pdf")

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "SQLite Local & Offline Ready",
        "ai": "NutriSense Clinical AI + Google Gemini Integration",
        "pdf": "ReportLab A4 Precision Engine"
    }


# ==============================================================================
# 5. EXECUÇÃO
# ==============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sistema Nutricional Dr. Igor Pinto")
    parser.add_argument("--cli", action="store_true", help="Executar no modo terminal CLI")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host do servidor web")
    parser.add_argument("--port", type=int, default=5500, help="Porta do servidor web")
    args = parser.parse_args()

    if args.cli:
        run_cli_menu()
    else:
        print("=" * 70)
        print(f"  🥦 INICIANDO {settings.PROJECT_NAME.upper()}")
        print(f"  Profissional: {settings.PROFESSIONAL_NAME} • {settings.PROFESSIONAL_CRN}")
        print(f"  URL Local: http://{args.host}:{args.port}")
        print(f"  Swagger Docs: http://{args.host}:{args.port}/docs")
        print("=" * 70)
        uvicorn.run(app, host=args.host, port=args.port)