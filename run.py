#!/usr/bin/env python3
import uvicorn
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

if __name__ == "__main__":
    print("=" * 70)
    print(f"  🥦 INICIANDO {settings.PROJECT_NAME.upper()} (PYTHON FASTAPI)")
    print(f"  Profissional: {settings.PROFESSIONAL_NAME} • {settings.PROFESSIONAL_CRN}")
    print(f"  URL Local: http://127.0.0.1:8000")
    print(f"  Documentação Interativa Swagger: http://127.0.0.1:8000/docs")
    print("=" * 70)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
