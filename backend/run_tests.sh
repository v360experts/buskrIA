#!/bin/bash

# Script para ejecutar todos los tests de integración
# Uso: ./run_tests.sh

set -e

echo "🧪 Ejecutando Tests de Integración..."
echo ""

# Cambiar al directorio del backend
cd "$(dirname "$0")"

# Verificar que existe .env
if [ ! -f .env ]; then
    echo "⚠️  Archivo .env no encontrado"
    echo "   Copia env.example a .env y configura las variables"
    echo ""
    read -p "¿Continuar de todos modos? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Ejecutar tests
python -m tests.test_all

