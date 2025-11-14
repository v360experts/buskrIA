"""
Script principal para ejecutar todos los tests de integración
"""
import os
import sys
import subprocess
from pathlib import Path

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Imprimir encabezado"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def run_test(test_file, test_name):
    """Ejecutar un test y retornar el resultado"""
    print_header(f"EJECUTANDO: {test_name}")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        # Imprimir salida
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"{Colors.WARNING}{result.stderr}{Colors.ENDC}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ ERROR ejecutando test: {str(e)}{Colors.ENDC}")
        return False


def main():
    """Ejecutar todos los tests"""
    print_header("🧪 TESTS DE INTEGRACIÓN COMPLETOS")
    
    print(f"{Colors.OKCYAN}Este script ejecutará todos los tests de integración para verificar:")
    print("  - Conexión a MongoDB")
    print("  - Integración con Vertex AI (Embeddings)")
    print("  - Vector Search")
    print("  - Servicios principales{Colors.ENDC}\n")
    
    # Obtener directorio de tests
    tests_dir = Path(__file__).parent
    
    # Lista de tests a ejecutar
    tests = [
        ("test_mongodb.py", "MongoDB Connection"),
        ("test_vertex_ai.py", "Vertex AI Integration"),
        ("test_services.py", "Services Integration"),
    ]
    
    results = []
    
    for test_file, test_name in tests:
        test_path = tests_dir / test_file
        
        if not test_path.exists():
            print(f"{Colors.WARNING}⚠️  Test no encontrado: {test_file}{Colors.ENDC}")
            continue
        
        success = run_test(str(test_path), test_name)
        results.append((test_name, success))
    
    # Resumen final
    print_header("📊 RESUMEN FINAL")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    failed = total - passed
    
    for test_name, success in results:
        if success:
            status = f"{Colors.OKGREEN}✅ PASS{Colors.ENDC}"
        else:
            status = f"{Colors.FAIL}❌ FAIL{Colors.ENDC}"
        print(f"{status} - {test_name}")
    
    print(f"\n{Colors.BOLD}Total: {total} | Pasados: {Colors.OKGREEN}{passed}{Colors.ENDC}{Colors.BOLD} | Fallidos: {Colors.FAIL}{failed}{Colors.ENDC}{Colors.BOLD}{Colors.ENDC}")
    
    if failed == 0:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 ¡Todos los tests pasaron exitosamente!{Colors.ENDC}\n")
        return 0
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}⚠️  Algunos tests fallaron. Revisa los detalles arriba.{Colors.ENDC}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

