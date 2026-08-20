with open('/working_dir/nutri_igor_pinto_python/app/services/project_service.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('f"Projeto \\"{project.name}\\" ({project.id}) salvo com sucesso."', "f'Projeto {project.name} ({project.id}) salvo com sucesso.'")
code = code.replace('f"Projeto "{project.name}" ({project.id}) salvo com sucesso."', "f'Projeto {project.name} ({project.id}) salvo com sucesso.'")

with open('/working_dir/nutri_igor_pinto_python/app/services/project_service.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed quotes in project_service.py")
