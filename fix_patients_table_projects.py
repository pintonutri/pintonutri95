with open('/working_dir/nutri_igor_pinto_python/app/database.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Add project_id and project_name to patients table creation
if "project_id TEXT," not in code:
    code = code.replace("status TEXT DEFAULT 'ativo',", "status TEXT DEFAULT 'ativo',\n                project_id TEXT,\n                project_name TEXT,")

# Add project_id and project_name to insert statement
if "project_id, project_name" not in code:
    code = code.replace(
        "photo, status, created_at, updated_at)",
        "photo, status, project_id, project_name, created_at, updated_at)"
    )
    code = code.replace(
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )

with open('/working_dir/nutri_igor_pinto_python/app/database.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Tabela patients atualizada com project_id e project_name no database.py!")
