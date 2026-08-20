import re
import os

# 1. Update app/models.py
with open('/working_dir/nutri_igor_pinto_python/app/models.py', 'r', encoding='utf-8') as f:
    models_code = f.read()

project_model_str = """
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
"""

if "class ProjectModel" not in models_code:
    models_code += "\n" + project_model_str
    # add projectId and projectName to PatientModel
    models_code = models_code.replace("status: str = \"ativo\"", "status: str = \"ativo\"\n    projectId: Optional[str] = \"\"\n    projectName: Optional[str] = \"\"")
    with open('/working_dir/nutri_igor_pinto_python/app/models.py', 'w', encoding='utf-8') as f:
        f.write(models_code)
    print("ProjectModel adicionado a app/models.py.")

# 2. Update app/database.py
with open('/working_dir/nutri_igor_pinto_python/app/database.py', 'r', encoding='utf-8') as f:
    db_code = f.read()

create_projects_table = """
        # 10. Tabela de Projetos & Programas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                description TEXT,
                start_date TEXT,
                end_date TEXT,
                target_goal TEXT,
                status TEXT DEFAULT 'Ativo',
                color TEXT
            )
        ''')
"""

if "CREATE TABLE IF NOT EXISTS projects" not in db_code:
    pos = db_code.find("conn.commit()")
    if pos != -1:
        db_code = db_code[:pos] + create_projects_table + "\n        " + db_code[pos:]
        print("Tabela projects adicionada ao SQLite schema.")

    # Add seed projects
    seed_projects_str = """
            # 9. Projetos Padrão
            default_projects = [
                ("PROJ-001", "Desafio 60 Dias — Emagrecimento Saudável & Definição", "Emagrecimento em Grupo", "Protocolo intensivo focado em redução de gordura visceral e preservação de massa magra.", "2026-07-01", "2026-09-01", "Redução média de 5% a 8% de gordura corporal", "Ativo", "#014338"),
                ("PROJ-002", "Programa Nutrição Materno-Infantil & Gestação Saudável", "Saúde Materno-Fetal", "Acompanhamento pré-natal individualizado com foco em micronutrientes, controle glicêmico e ganho de peso adequado.", "2026-05-01", "2026-12-31", "Controle glicêmico e ganho ponderal ótimo", "Ativo", "#FA7100"),
                ("PROJ-003", "Projeto Alta Performance & Hipertrofia para Atletas", "Nutrição Esportiva", "Superávit calórico limpo, timing de nutrientes pré/pós-treino e periodização dietoterápica.", "2026-06-01", "2026-11-30", "Ganho médio de 2.5kg a 4kg de massa magra", "Ativo", "#026353"),
                ("PROJ-004", "Programa Longevidade & Controle Cardiometabólico", "Saúde e Longevidade", "Dieta anti-inflamatória, controle de pressão arterial, lipídios e sensibilidade insulínica.", "2026-04-01", "2026-12-31", "Otimização de biomarcadores laboratoriais e redução de inflamação", "Ativo", "#334155"),
                ("PROJ-005", "Consultório Particular / Atendimento Geral", "Atendimento Individual Padrão", "Atendimento nutricional individualizado e personalizado do consultório clínico.", "2026-01-01", "2026-12-31", "Metas clínicas personalizadas", "Contínuo", "#64748B")
            ]

            cursor.executemany('''
                INSERT INTO projects (id, name, category, description, start_date, end_date, target_goal, status, color)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', default_projects)
    """
    pos_seed = db_code.find("conn.commit()\n            print(\"✓ Banco de Dados SQLite populado")
    if pos_seed != -1:
        db_code = db_code[:pos_seed] + seed_projects_str + "\n            " + db_code[pos_seed:]
        print("Seed de projetos adicionado ao SQLite.")

    with open('/working_dir/nutri_igor_pinto_python/app/database.py', 'w', encoding='utf-8') as f:
        f.write(db_code)

# 3. Create app/services/project_service.py
project_service_code = """from typing import List, Optional, Dict, Any
from app.database import db
from app.models import ProjectModel

class ProjectService:
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects ORDER BY name ASC")
        rows = cursor.fetchall()
        conn.close()

        result = []
        for r in rows:
            p_dict = dict(r)
            # Count patients
            c_conn = db.get_connection()
            c_cursor = c_conn.cursor()
            c_cursor.execute("SELECT COUNT(*) as count FROM patients WHERE project_id = ?", (p_dict['id'],))
            p_dict['patientsCount'] = c_cursor.fetchone()['count']
            c_conn.close()
            result.append(p_dict)
        return result

    @staticmethod
    def get_by_id(project_id: str) -> Optional[Dict[str, Any]]:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None
        p_dict = dict(row)
        c_conn = db.get_connection()
        c_cursor = c_conn.cursor()
        c_cursor.execute("SELECT COUNT(*) as count FROM patients WHERE project_id = ?", (project_id,))
        p_dict['patientsCount'] = c_cursor.fetchone()['count']
        c_conn.close()
        return p_dict

    @staticmethod
    def create_or_update(project: ProjectModel) -> Dict[str, Any]:
        conn = db.get_connection()
        cursor = conn.cursor()

        if not project.id:
            cursor.execute("SELECT COUNT(*) as count FROM projects")
            count = cursor.fetchone()['count'] + 1
            project.id = f"PROJ-{str(count).zfill(3)}"

        cursor.execute('''
            INSERT INTO projects (id, name, category, description, start_date, end_date, target_goal, status, color)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name, category=excluded.category, description=excluded.description,
                start_date=excluded.start_date, end_date=excluded.end_date,
                target_goal=excluded.target_goal, status=excluded.status, color=excluded.color
        ''', (
            project.id, project.name, project.category, project.description,
            project.startDate, project.endDate, project.targetGoal,
            project.status, project.color
        ))

        conn.commit()
        conn.close()

        from app.services.audit_service import AuditService
        AuditService.log("PROJETO", "Projetos Nutricionais", f"Projeto \"{project.name}\" ({project.id}) salvo com sucesso.")
        return ProjectService.get_by_id(project.id)

    @staticmethod
    def delete(project_id: str) -> bool:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        conn.commit()
        conn.close()

        from app.services.audit_service import AuditService
        AuditService.log("PROJETO_DEL", "Projetos Nutricionais", f"Projeto {project_id} excluído.")
        return True

    @staticmethod
    def get_patients_by_project(project_id: str) -> List[Dict[str, Any]]:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE project_id = ? ORDER BY name ASC", (project_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
"""

with open('/working_dir/nutri_igor_pinto_python/app/services/project_service.py', 'w', encoding='utf-8') as f:
    f.write(project_service_code)
print("ProjectService criado com sucesso.")

# 4. Update app/api/routes.py with projects routes
with open('/working_dir/nutri_igor_pinto_python/app/api/routes.py', 'r', encoding='utf-8') as f:
    routes_code = f.read()

project_routes = """
# 8. Projetos & Programas Nutricionais
from app.models import ProjectModel
from app.services.project_service import ProjectService

@api_router.get("/projects")
def list_projects():
    return ProjectService.get_all()

@api_router.get("/projects/{project_id}")
def get_project(project_id: str):
    p = ProjectService.get_by_id(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return p

@api_router.post("/projects")
def save_project(proj: ProjectModel):
    return ProjectService.create_or_update(proj)

@api_router.delete("/projects/{project_id}")
def delete_project(project_id: str):
    ProjectService.delete(project_id)
    return {"status": "deleted", "id": project_id}

@api_router.get("/projects/{project_id}/patients")
def get_project_patients(project_id: str):
    return ProjectService.get_patients_by_project(project_id)
"""

if "/projects" not in routes_code:
    routes_code += "\n" + project_routes
    with open('/working_dir/nutri_igor_pinto_python/app/api/routes.py', 'w', encoding='utf-8') as f:
        f.write(routes_code)
    print("Rotas de Projetos adicionadas ao FastAPI routes.")

