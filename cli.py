#!/usr/bin/env python3
import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.services.patient_service import PatientService
from app.services.evaluation_service import EvaluationService
from app.services.diet_service import DietService
from app.services.nutrisense_ai_service import NutriSenseAIService
from app.services.pdf_service import PDFReportService
from app.services.financial_service import FinancialService
from app.services.calendar_service import CalendarService
from app.services.project_service import ProjectService
from app.models import PatientModel, EvaluationModel, DietModel, FoodModel, ProjectModel

def print_header():
    print("=" * 75)
    print(f"  🥦 {settings.PROJECT_NAME.upper()}")
    print(f"  Profissional: {settings.PROFESSIONAL_NAME} • {settings.PROFESSIONAL_CRN}")
    print("=" * 75)

def menu_patients():
    while True:
        print_header()
        print("\n--- GESTÃO DE PACIENTES & PRONTUÁRIOS ---")
        print("1. Listar Todos os Pacientes")
        print("2. Buscar Paciente por Nome / CPF")
        print("3. Cadastrar Novo Paciente (com Projeto)")
        print("4. Ver Prontuário de Paciente")
        print("5. Aniversariantes do Mês")
        print("0. Voltar ao Menu Principal")

        op = input("\nEscolha uma opção: ").strip()
        if op == "1":
            pts = PatientService.get_all()
            print(f"\nTotal: {len(pts)} pacientes cadastrados:")
            for p in pts:
                proj_name = p.get('project_name') or 'Consultório Padrão'
                print(f"  [{p['id']}] {p['name']} | CPF: {p.get('cpf') or '-'} | Sexo: {p['gender']} | Projeto: {proj_name}")
            input("\nPressione ENTER para continuar...")
        elif op == "2":
            q = input("Digite o nome ou CPF para buscar: ").strip()
            pts = PatientService.get_all(search=q)
            print(f"\nResultados ({len(pts)}):")
            for p in pts:
                print(f"  [{p['id']}] {p['name']} | Tel: {p.get('phone')} | Projeto: {p.get('project_name') or '-'}")
            input("\nPressione ENTER para continuar...")
        elif op == "3":
            name = input("Nome Completo *: ").strip()
            if not name:
                print("Nome é obrigatório.")
                continue
            gender = input("Sexo (Feminino/Masculino) [Feminino]: ").strip() or "Feminino"
            phone = input("Telefone / WhatsApp: ").strip()
            bdate = input("Data de Nascimento (AAAA-MM-DD): ").strip()
            obj = input("Objetivo Nutricional: ").strip() or "Emagrecimento e Saúde"

            # Projetos disponíveis
            projs = ProjectService.get_all()
            print("\nProjetos / Programas Disponíveis:")
            for i, pr in enumerate(projs):
                print(f"  {i+1}. {pr['name']} ({pr['category']})")
            p_choice = input(f"Escolha o projeto (1-{len(projs)}) [1]: ").strip() or "1"
            chosen_proj = projs[int(p_choice)-1] if p_choice.isdigit() and 1 <= int(p_choice) <= len(projs) else projs[0]

            p = PatientModel(
                name=name,
                gender=gender,
                phone=phone,
                whatsapp=phone,
                birthDate=bdate,
                objective=obj,
                projectId=chosen_proj['id'],
                projectName=chosen_proj['name']
            )
            saved = PatientService.create_or_update(p)
            print(f"\n✓ Paciente {saved['name']} cadastrado e vinculado ao projeto \"{chosen_proj['name']}\" com sucesso! ID: {saved['id']}")
            input("\nPressione ENTER para continuar...")
        elif op == "4":
            pid = input("Digite o ID do paciente (ex: PAC-001): ").strip().upper()
            p = PatientService.get_by_id(pid)
            if not p:
                print("Paciente não encontrado.")
            else:
                print(f"\n--- PRONTUÁRIO DE {p['name'].upper()} ({p['id']}) ---")
                print(f"CPF: {p.get('cpf')} | Nascimento: {p.get('birth_date')} ({p.get('age')} anos)")
                print(f"Projeto Vinculado: {p.get('project_name') or 'Consultório Padrão'}")
                print(f"Sexo: {p['gender']} | Objetivo: {p.get('objective')}")
                if p.get('is_pregnant'):
                    print(f"🤰 Gestante: {p.get('gestational_weeks')}ª semana | DPP: {p.get('probable_due_date')}")
                
                evals = EvaluationService.get_by_patient(pid)
                print(f"\nAvaliações de Bioimpedância ({len(evals)}):")
                for e in evals:
                    print(f"  • {e['date'][:10]} -> Peso: {e['weight']}kg | %Gordura: {e['body_fat_percent']}% | Músculo: {e['muscle_mass']}kg | IMC: {e['bmi']}")
            input("\nPressione ENTER para continuar...")
        elif op == "5":
            b_pts = PatientService.get_all(filter_type="birthdays")
            print(f"\n🎉 Aniversariantes do Mês ({len(b_pts)}):")
            for p in b_pts:
                print(f"  • {p['name']} - Data: {p.get('birth_date')} | Tel: {p.get('phone')}")
            input("\nPressione ENTER para continuar...")
        elif op == "0":
            break

def menu_projects():
    while True:
        print_header()
        projs = ProjectService.get_all()
        print("\n--- ÁREA DE PROJETOS & PROGRAMAS NUTRICIONAIS ---")
        print(f"Total de Projetos Ativos: {len(projs)}")
        print("-" * 50)
        for p in projs:
            print(f"  [{p['id']}] {p['name']}")
            print(f"      Categoria: {p['category']} | Status: {p['status']} | Pacientes: {p.get('patientsCount', 0)}")
            print(f"      Meta: {p.get('target_goal') or 'Acompanhamento contínuo'}")
            print()

        print("1. Criar Novo Projeto")
        print("2. Ver Pacientes de um Projeto")
        print("3. Cadastrar Paciente em um Projeto")
        print("4. Excluir Projeto")
        print("0. Voltar ao Menu Principal")

        op = input("\nEscolha uma opção: ").strip()
        if op == "1":
            name = input("Nome do Projeto / Desafio *: ").strip()
            if not name:
                print("Nome é obrigatório.")
                continue
            cat = input("Categoria (Emagrecimento em Grupo, Nutrição Esportiva, Saúde Materno-Fetal, etc.): ").strip() or "Emagrecimento em Grupo"
            desc = input("Descrição / Metodologia: ").strip()
            sdate = input("Data Início (AAAA-MM-DD): ").strip() or datetime.today().strftime("%Y-%m-%d")
            edate = input("Data Término (AAAA-MM-DD): ").strip()
            goal = input("Meta Principal do Grupo: ").strip()

            new_proj = ProjectService.create_or_update(ProjectModel(
                name=name,
                category=cat,
                description=desc,
                startDate=sdate,
                endDate=edate,
                targetGoal=goal,
                status="Ativo"
            ))
            print(f"\n✓ Projeto \"{new_proj['name']}\" ({new_proj['id']}) criado com sucesso!")
            input("\nPressione ENTER para continuar...")
        elif op == "2":
            proj_id = input("Digite o ID do projeto (ex: PROJ-001): ").strip().upper()
            pts = ProjectService.get_patients_by_project(proj_id)
            proj = ProjectService.get_by_id(proj_id)
            print(f"\nPacientes do Projeto \"{proj['name'] if proj else proj_id}\" ({len(pts)}):")
            for p in pts:
                print(f"  • [{p['id']}] {p['name']} ({p['gender']}) | CPF: {p.get('cpf')} | Objetivo: {p.get('objective')}")
            input("\nPressione ENTER para continuar...")
        elif op == "3":
            proj_id = input("Digite o ID do projeto de destino (ex: PROJ-001): ").strip().upper()
            proj = ProjectService.get_by_id(proj_id)
            if not proj:
                print("Projeto não encontrado.")
                continue
            name = input("Nome Completo do Paciente *: ").strip()
            gender = input("Sexo [Feminino]: ").strip() or "Feminino"
            phone = input("WhatsApp: ").strip()
            p = PatientModel(name=name, gender=gender, phone=phone, whatsapp=phone, projectId=proj['id'], projectName=proj['name'])
            saved = PatientService.create_or_update(p)
            print(f"✓ Paciente {saved['name']} cadastrado e vinculado ao projeto \"{proj['name']}\"!")
            input("\nPressione ENTER para continuar...")
        elif op == "4":
            proj_id = input("Digite o ID do projeto para excluir: ").strip().upper()
            ProjectService.delete(proj_id)
            print("✓ Projeto excluído com sucesso.")
            input("\nPressione ENTER para continuar...")
        elif op == "0":
            break

def menu_nutrisense_ai():
    print_header()
    print("\n--- NUTRISENSE IA — CONSULTORIA CLÍNICA INTEGRADA ---")
    pid = input("Deseja contextualizar com um paciente? Digite o ID (ou ENTER para geral): ").strip().upper()
    patient_id = pid if pid else None

    while True:
        msg = input("\n[Dr. Igor Pinto] > ").strip()
        if not msg or msg.lower() in ["sair", "voltar", "exit"]:
            break

        print("\n✨ NutriSense processando evidências clínicas...")
        res = NutriSenseAIService.chat(msg, patient_id=patient_id)
        print(f"\n[NutriSense IA ({res['source']})]:\n")
        print(res['text'])
        print("-" * 60)

def menu_pdf_generator():
    print_header()
    print("\n--- GERADOR OFICIAL DE LAUDOS E PRESCRIÇÕES EM PDF (A4) ---")
    pid = input("Digite o ID do paciente (ex: PAC-001): ").strip().upper()
    p = PatientService.get_by_id(pid)
    if not p:
        print("Paciente não encontrado.")
        input("\nPressione ENTER para continuar...")
        return

    print("\n1. Gerar Laudo de Bioimpedância em PDF")
    print("2. Gerar Prescrição Dietética Autenticada em PDF")
    op = input("Escolha o documento: ").strip()

    if op == "1":
        pdf_path = PDFReportService.generate_bioimpedance_pdf(pid)
        print(f"\n✓ Laudo de Bioimpedância gerado com sucesso!")
        print(f"📄 Arquivo salvo em: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
    elif op == "2":
        pdf_path = PDFReportService.generate_diet_pdf(pid)
        print(f"\n✓ Prescrição Dietética gerada com sucesso!")
        print(f"📄 Arquivo salvo em: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
    input("\nPressione ENTER para continuar...")

def menu_financial():
    while True:
        print_header()
        summary = FinancialService.get_summary()
        print("\n--- CONTROLE FINANCEIRO INTERNO ---")
        print(f"Faturamento Recebido: R$ {summary['totalRevenue']:.2f}")
        print(f"Valores Pendentes:    R$ {summary['pendingAmount']:.2f}")
        print(f"Total de Lançamentos: {summary['transactionsCount']}")
        print("-" * 40)
        print("1. Listar Lançamentos")
        print("2. Novo Recebimento")
        print("3. Alternar Status (Pago/Pendente)")
        print("0. Voltar ao Menu Principal")

        op = input("\nEscolha uma opção: ").strip()
        if op == "1":
            txs = FinancialService.get_transactions()
            print("\nExtrato Financeiro:")
            for t in txs:
                st = "✓ PAGO" if t['status'] == "pago" else "⏳ PENDENTE"
                meth = f"Outro ({t.get('payment_method_other')})" if t['payment_method'] == "Outro" else t['payment_method']
                print(f"  [{t['id']}] {t['date'][:10]} | {t['patient_name']} | R$ {t['amount']:.2f} | {meth} | {st}")
            input("\nPressione ENTER para continuar...")
        elif op == "2":
            pid = input("ID do Paciente: ").strip().upper()
            p = PatientService.get_by_id(pid)
            if not p:
                print("Paciente não encontrado.")
                continue
            amt = float(input("Valor (R$): ").strip() or "350")
            cat = input("Categoria [Consulta Nutricional]: ").strip() or "Consulta Nutricional"
            method = input("Forma (PIX, Cartão de Crédito, Cartão de Débito, Dinheiro, Outro) [PIX]: ").strip() or "PIX"
            other = ""
            if method.lower() == "outro":
                other = input("Especifique a forma de pagamento: ").strip()
            st = input("Status (pago/pendente) [pago]: ").strip() or "pago"

            from app.models import FinancialTransactionModel
            tx = FinancialTransactionModel(
                patientId=p['id'],
                patientName=p['name'],
                amount=amt,
                category=cat,
                paymentMethod=method,
                paymentMethodOther=other,
                status=st,
                date=datetime.now().isoformat()
            )
            FinancialService.save_transaction(tx)
            print("✓ Lançamento financeiro registrado com sucesso!")
            input("\nPressione ENTER para continuar...")
        elif op == "3":
            tx_id = input("Digite o ID do lançamento (ex: TX-001): ").strip().upper()
            res = FinancialService.toggle_status(tx_id)
            print(f"Status atualizado: {res}")
            input("\nPressione ENTER para continuar...")
        elif op == "0":
            break

def main():
    while True:
        print_header()
        print("\nMENU PRINCIPAL:")
        print("1. Gestão de Pacientes & Prontuários")
        print("2. 📁 Área de Projetos & Categorização de Pacientes")
        print("3. NutriSense IA (Assistente Clínico & Gemini)")
        print("4. Emissão de Laudos & Prescrições em PDF A4")
        print("5. Controle Financeiro Interno")
        print("6. Validar Código de Autenticação (PD-2026-XXXXXX)")
        print("7. Iniciar Servidor Web FastAPI (http://127.0.0.1:8000)")
        print("0. Sair")

        op = input("\nEscolha uma opção: ").strip()
        if op == "1":
            menu_patients()
        elif op == "2":
            menu_projects()
        elif op == "3":
            menu_nutrisense_ai()
        elif op == "4":
            menu_pdf_generator()
        elif op == "5":
            menu_financial()
        elif op == "6":
            code = input("\nDigite o código da prescrição (ex: PD-2026-MR7890): ").strip()
            res = DietService.validate_code(code)
            print("\nResultado da Validação:")
            print(json.dumps(res, indent=2, ensure_ascii=False))
            input("\nPressione ENTER para continuar...")
        elif op == "7":
            print("\nIniciando Servidor Web FastAPI em http://127.0.0.1:8000 ...")
            import uvicorn
            from app.main import app
            uvicorn.run(app, host="127.0.0.1", port=8000)
        elif op == "0":
            print("\nEncerrando sistema. Até logo, Dr. Igor Pinto!")
            break

if __name__ == "__main__":
    main()
