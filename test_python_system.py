import unittest
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.database import db
from app.models import PatientModel, EvaluationModel, DietModel, FoodModel, FinancialTransactionModel, ProjectModel
from app.services.patient_service import PatientService
from app.services.evaluation_service import EvaluationService
from app.services.diet_service import DietService
from app.services.nutrisense_ai_service import NutriSenseAIService
from app.services.pdf_service import PDFReportService
from app.services.financial_service import FinancialService
from app.services.calendar_service import CalendarService
from app.services.project_service import ProjectService
from fastapi.testclient import TestClient
from app.main import app

class TestNutriIgorPintoPythonSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_database_and_patients(self):
        patients = PatientService.get_all()
        self.assertGreaterEqual(len(patients), 5)
        p1 = PatientService.get_by_id("PAC-001")
        self.assertIsNotNone(p1)
        self.assertEqual(p1['name'], "Mariana Silva Souza")
        self.assertEqual(p1['gender'], "Feminino")

    def test_02_projects_and_patient_categorization(self):
        projects = ProjectService.get_all()
        self.assertGreaterEqual(len(projects), 5)
        proj1 = ProjectService.get_by_id("PROJ-001")
        self.assertIsNotNone(proj1)
        self.assertIn("Emagrecimento", proj1['name'])

        patients_proj1 = ProjectService.get_patients_by_project("PROJ-001")
        self.assertGreaterEqual(len(patients_proj1), 1)
        self.assertEqual(patients_proj1[0]['id'], "PAC-001")

        # Test project creation
        new_proj = ProjectService.create_or_update(ProjectModel(
            name="Projeto Saúde Corporativa Tech 2026",
            category="Saúde Corporativa",
            description="Intervenção nutricional para colaboradores de tecnologia.",
            startDate="2026-09-01",
            endDate="2026-12-31",
            targetGoal="Redução de estresse e melhora da disposição matinal",
            status="Ativo"
        ))
        self.assertIsNotNone(new_proj['id'])
        self.assertEqual(new_proj['name'], "Projeto Saúde Corporativa Tech 2026")
        ProjectService.delete(new_proj['id'])

    def test_03_evaluation_calculations(self):
        evals = EvaluationService.get_by_patient("PAC-001")
        self.assertGreaterEqual(len(evals), 1)
        ev = evals[0]
        self.assertIn("weight", ev)
        self.assertIn("bmi", ev)
        self.assertIn("body_fat_percent", ev)

        bmi_class = EvaluationService.get_bmi_classification(ev['bmi'])
        self.assertIsInstance(bmi_class, str)

        compare = EvaluationService.compare_evaluations("EV-002", "EV-001")
        self.assertIn("weight", compare)
        self.assertIn("diff", compare["weight"])

    def test_04_diet_prescription_and_auth_code(self):
        diet = DietService.get_by_patient("PAC-001")
        self.assertIsNotNone(diet)
        self.assertTrue(diet['auth_code'].startswith("PD-2026-"))
        
        val = DietService.validate_code(diet['auth_code'])
        self.assertTrue(val['valid'])
        self.assertEqual(val['patientName'], "Mariana Silva Souza")

    def test_05_nutrisense_ai_local_and_markdown(self):
        md = "### 📋 Parecer NutriSense\n* Paciente com **evolução positiva**."
        html = NutriSenseAIService.render_markdown(md)
        self.assertIn("<strong>evolução positiva</strong>", html)
        self.assertIn("<h4", html)

        res = NutriSenseAIService.chat("Prescrever plano para Mariana", patient_id="PAC-001")
        self.assertIn("text", res)
        self.assertIn("NutriSense", res["text"])

    def test_06_pdf_generation_reportlab(self):
        pdf_bio = PDFReportService.generate_bioimpedance_pdf("PAC-001")
        self.assertTrue(os.path.exists(pdf_bio))
        self.assertGreater(os.path.getsize(pdf_bio), 1000)

        pdf_diet = PDFReportService.generate_diet_pdf("PAC-001")
        self.assertTrue(os.path.exists(pdf_diet))
        self.assertGreater(os.path.getsize(pdf_diet), 1000)

    def test_07_financial_and_outro_payment_method(self):
        summary = FinancialService.get_summary()
        self.assertIn("totalRevenue", summary)
        self.assertIn("pendingAmount", summary)

        tx = FinancialTransactionModel(
            patientId="PAC-002",
            patientName="Carlos Eduardo Mendes",
            amount=400.0,
            category="Plano Trimestral",
            paymentMethod="Outro",
            paymentMethodOther="Vale Refeição Saúde",
            status="pago",
            date="2026-08-18T10:00:00"
        )
        saved = FinancialService.save_transaction(tx)
        self.assertEqual(saved['paymentMethodOther'], "Vale Refeição Saúde")
        FinancialService.delete_transaction(saved['id'])

    def test_08_fastapi_endpoints(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "healthy")

        resp_p = self.client.get("/api/v1/patients")
        self.assertEqual(resp_p.status_code, 200)
        self.assertIsInstance(resp_p.json(), list)

        resp_proj = self.client.get("/api/v1/projects")
        self.assertEqual(resp_proj.status_code, 200)
        self.assertIsInstance(resp_proj.json(), list)

        resp_d = self.client.get("/api/v1/diets/patient/PAC-001")
        self.assertEqual(resp_d.status_code, 200)

if __name__ == "__main__":
    unittest.main()
