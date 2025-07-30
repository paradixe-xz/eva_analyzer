#!/bin/bash

# Script completo: Análisis + Servidor de descarga
echo "🚀 EJECUCIÓN COMPLETA: ANÁLISIS + SERVIDOR"
echo "============================================"

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Función para imprimir con colores
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "analyzer.py" ]; then
    echo "❌ Error: No se encontró analyzer.py"
    echo "💡 Asegúrate de estar en el directorio correcto"
    exit 1
fi

# Activar entorno virtual
print_status "Activando entorno virtual..."
source venv/bin/activate

# Verificar que Ollama esté corriendo
print_status "Verificando Ollama..."
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    print_warning "Ollama no está corriendo. Iniciando..."
    ollama serve &
    sleep 5
fi

# Verificar que el modelo existe
print_status "Verificando modelo call_analyzer..."
if ! ollama list | grep -q "call_analyzer"; then
    print_warning "Modelo call_analyzer no encontrado. Creando..."
    ollama create call_analyzer -f Modelfile
fi

# Ejecutar análisis
echo ""
echo "📊 EJECUTANDO ANÁLISIS DE LLAMADAS"
echo "=================================="
python3 analyzer.py

# Verificar si el análisis se completó
if [ -f "call_analysis_results.csv" ]; then
    print_success "Análisis completado exitosamente!"
    
    # Mostrar estadísticas básicas
    if command -v wc &> /dev/null; then
        TOTAL_LINES=$(wc -l < "call_analysis_results.csv")
        print_status "Total de filas procesadas: $((TOTAL_LINES - 1))"
    fi
    
    echo ""
    echo "🌐 INICIANDO SERVIDOR DE DESCARGA"
    echo "================================="
    
    # Instalar Flask si no está instalado
    if ! python3 -c "import flask" 2>/dev/null; then
        print_status "Instalando Flask..."
        pip install flask
    fi
    
    echo ""
    echo "🌐 SERVIDOR DE DESCARGA"
    echo "======================="
    echo "📊 Dashboard: http://localhost:4000"
    echo "📥 Descarga directa: http://localhost:4000/download"
    echo "📈 API Status: http://localhost:5000/status"
    echo ""
    echo "🔧 Para detener el servidor: Ctrl+C"
    echo ""
    
    # Iniciar servidor
    print_status "Iniciando servidor Flask..."
    python3 download_server.py
    
else
    print_warning "El análisis no se completó correctamente"
    echo "💡 Revisa los errores arriba"
    exit 1
fi 