with open('/working_dir/nutri_igor_pinto_python/app/database.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_seed_patients = """            default_patients = [
                ("PAC-001", "Mariana Silva Souza", "", "123.456.789-00", "1994-05-14", "Feminino", "Cisgênero", "(71) 99123-4567", "5571991234567", "mariana.silva@email.com", "Advogada", "Casada", 0, 0, 0, 0, 0, "", "", "", 0, "[]", "Nenhum", 0, "", "Lactose", "", "", "", "Emagrecimento", "Moderado", "", "ativo", "2026-01-10T10:00:00", "2026-08-18T10:00:00"),
                ("PAC-002", "Carlos Eduardo Mendes", "", "234.567.890-11", "1988-11-22", "Masculino", "Cisgênero", "(71) 98234-5678", "5571982345678", "carlos.mendes@email.com", "Engenheiro de Software", "Solteiro", 0, 0, 0, 0, 0, "", "", "", 0, "[]", "Nenhum", 0, "", "", "", "", "", "Hipertrofia", "Intenso", "", "ativo", "2026-02-15T14:00:00", "2026-08-18T14:00:00"),
                ("PAC-003", "Beatriz Costa Oliveira", "", "345.678.901-22", "1997-03-08", "Feminino", "Cisgênero", "(71) 99345-6789", "5571993456789", "beatriz.costa@email.com", "Arquiteta", "Solteira", 0, 0, 0, 0, 0, "", "", "", 0, "[]", "Nenhum", 0, "", "Glúten", "", "", "", "Definição Muscular", "Moderado", "", "ativo", "2026-03-20T09:00:00", "2026-08-18T09:00:00"),
                ("PAC-004", "Roberto Alencar Santos", "", "456.789.012-33", "1975-09-30", "Masculino", "Cisgênero", "(71) 98456-7890", "5571984567890", "roberto.santos@email.com", "Empresário", "Casado", 0, 0, 0, 0, 0, "", "", "", 1, '["Hipertensão Arterial"]', "Losartana 50mg", 0, "", "", "", "", "", "Controle Metabólico e Longevidade", "Leve", "", "ativo", "2026-04-05T11:00:00", "2026-08-18T11:00:00"),
                ("PAC-005", "Juliana Nogueira Lima", "", "567.890.123-44", "1992-08-18", "Feminino", "Cisgênero", "(71) 99567-8901", "5571995678901", "juliana.lima@email.com", "Professora Universitária", "Casada", 1, 24, 6, 0, 0, "2026-12-08", "G1P0A0", "Sem intercorrências no 2º trimestre", 0, "[]", "Metilfolato + Sulfato Ferroso", 0, "", "", "", "", "", "Nutrição Pré-Natal e Saúde Materno-Fetal", "Leve", "", "ativo", "2026-05-12T16:00:00", "2026-08-18T16:00:00")
            ]"""

new_seed_patients = """            default_patients = [
                ("PAC-001", "Mariana Silva Souza", "", "123.456.789-00", "1994-05-14", "Feminino", "Cisgênero", "(71) 99123-4567", "5571991234567", "mariana.silva@email.com", "Advogada", "Casada", 0, 0, 0, 0, 0, "", "", "", 0, "[]", "Nenhum", 0, "", "Lactose", "", "", "", "Emagrecimento", "Moderado", "", "ativo", "PROJ-001", "Desafio 60 Dias — Emagrecimento Saudável & Definição", "2026-01-10T10:00:00", "2026-08-18T10:00:00"),
                ("PAC-002", "Carlos Eduardo Mendes", "", "234.567.890-11", "1988-11-22", "Masculino", "Cisgênero", "(71) 98234-5678", "5571982345678", "carlos.mendes@email.com", "Engenheiro de Software", "Solteiro", 0, 0, 0, 0, 0, "", "", "", 0, "[]", "Nenhum", 0, "", "", "", "", "", "Hipertrofia", "Intenso", "", "ativo", "PROJ-003", "Projeto Alta Performance & Hipertrofia para Atletas", "2026-02-15T14:00:00", "2026-08-18T14:00:00"),
                ("PAC-003", "Beatriz Costa Oliveira", "", "345.678.901-22", "1997-03-08", "Feminino", "Cisgênero", "(71) 99345-6789", "5571993456789", "beatriz.costa@email.com", "Arquiteta", "Solteira", 0, 0, 0, 0, 0, "", "", "", 0, "[]", "Nenhum", 0, "", "Glúten", "", "", "", "Definição Muscular", "Moderado", "", "ativo", "PROJ-005", "Consultório Particular / Atendimento Geral", "2026-03-20T09:00:00", "2026-08-18T09:00:00"),
                ("PAC-004", "Roberto Alencar Santos", "", "456.789.012-33", "1975-09-30", "Masculino", "Cisgênero", "(71) 98456-7890", "5571984567890", "roberto.santos@email.com", "Empresário", "Casado", 0, 0, 0, 0, 0, "", "", "", 1, '["Hipertensão Arterial"]', "Losartana 50mg", 0, "", "", "", "", "", "Controle Metabólico e Longevidade", "Leve", "", "ativo", "PROJ-004", "Programa Longevidade & Controle Cardiometabólico", "2026-04-05T11:00:00", "2026-08-18T11:00:00"),
                ("PAC-005", "Juliana Nogueira Lima", "", "567.890.123-44", "1992-08-18", "Feminino", "Cisgênero", "(71) 99567-8901", "5571995678901", "juliana.lima@email.com", "Professora Universitária", "Casada", 1, 24, 6, 0, 0, "2026-12-08", "G1P0A0", "Sem intercorrências no 2º trimestre", 0, "[]", "Metilfolato + Sulfato Ferroso", 0, "", "", "", "", "", "Nutrição Pré-Natal e Saúde Materno-Fetal", "Leve", "", "ativo", "PROJ-002", "Programa Nutrição Materno-Infantil & Gestação Saudável", "2026-05-12T16:00:00", "2026-08-18T16:00:00")
            ]"""

code = code.replace(old_seed_patients, new_seed_patients)

with open('/working_dir/nutri_igor_pinto_python/app/database.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Seed de pacientes atualizado.")
