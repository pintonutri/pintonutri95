with open('/working_dir/nutri_igor_pinto_python/app/services/pdf_service.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace("<br>", "<br/>")

with open('/working_dir/nutri_igor_pinto_python/app/services/pdf_service.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed br in pdf_service.py")
