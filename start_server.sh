#!/bin/bash

# Script para iniciar el servidor de descarga de resultados
echo "🌐 INICIANDO SERVIDOR DE DESCARGA"
echo "================================="

# Activar entorno virtual
source venv/bin/activate

# Instalar Flask si no está instalado
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Instalando Flask..."
    pip install flask
fi

# Verificar que el archivo de resultados existe
if [ ! -f "call_analysis_results.csv" ]; then
    echo "⚠️  ADVERTENCIA: No se encontró el archivo call_analysis_results.csv"
    echo "💡 Ejecuta primero el análisis con: ./run_analysis.sh"
    echo ""
    echo "¿Quieres ejecutar el análisis ahora? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "🚀 Ejecutando análisis..."
        ./run_analysis.sh
    fi
fi

# Mostrar información del servidor
echo ""
echo "🌐 SERVIDOR DE DESCARGA"
echo "======================="
echo "📊 Dashboard: http://localhost:5000"
echo "📥 Descarga directa: http://localhost:5000/download"
echo "📈 API Status: http://localhost:5000/status"
echo ""
echo "🔧 Para detener el servidor: Ctrl+C"
echo ""

# Iniciar el servidor
echo "🚀 Iniciando servidor Flask..."
python3 download_server.py 