#!/bin/bash

# Script de instalación y ejecución para RunPod
# Análisis de llamadas telefónicas con Ollama

set -e  # Salir si hay algún error

echo "🚀 INICIANDO CONFIGURACIÓN DEL PROYECTO DE ANÁLISIS DE LLAMADAS"
echo "================================================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si estamos en un sistema Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_error "Este script está diseñado para sistemas Linux"
    exit 1
fi

# Actualizar sistema
print_status "Actualizando sistema..."
sudo apt update -y
sudo apt upgrade -y

# Instalar dependencias del sistema
print_status "Instalando dependencias del sistema..."
sudo apt install -y curl wget git python3 python3-pip python3-venv

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    print_error "Python3 no está instalado"
    exit 1
fi

print_success "Python3 encontrado: $(python3 --version)"

# Crear entorno virtual
print_status "Creando entorno virtual Python..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias de Python
print_status "Instalando dependencias de Python..."
pip install --upgrade pip
pip install pandas requests ollama flask

# Verificar si Ollama está instalado
if ! command -v ollama &> /dev/null; then
    print_status "Ollama no está instalado. Instalando..."
    
    # Descargar e instalar Ollama
    curl -fsSL https://ollama.ai/install.sh | sh
    
    # Agregar Ollama al PATH
    export PATH=$PATH:$HOME/.local/bin
    
    # Verificar instalación
    if ! command -v ollama &> /dev/null; then
        print_error "No se pudo instalar Ollama"
        exit 1
    fi
fi

print_success "Ollama encontrado: $(ollama --version)"

# Iniciar Ollama en segundo plano
print_status "Iniciando Ollama..."
ollama serve &
OLLAMA_PID=$!

# Esperar a que Ollama esté listo
print_status "Esperando a que Ollama esté listo..."
sleep 10

# Verificar que Ollama esté corriendo
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    print_error "Ollama no está respondiendo en el puerto 11434"
    exit 1
fi

print_success "Ollama está corriendo correctamente"

# Descargar modelo base si no existe
print_status "Verificando modelo base..."
if ! ollama list | grep -q "llama3.2"; then
    print_status "Descargando modelo llama3.2..."
    ollama pull llama3.2
fi

# Crear modelo personalizado
print_status "Creando modelo personalizado 'call_analyzer'..."
if ollama list | grep -q "call_analyzer"; then
    print_warning "Modelo call_analyzer ya existe. Eliminando versión anterior..."
    ollama rm call_analyzer
fi

ollama create call_analyzer -f Modelfile
print_success "Modelo call_analyzer creado exitosamente"

# Verificar que el CSV existe
if [ ! -f "all_leads_ana (1).csv" ]; then
    print_error "No se encontró el archivo 'all_leads_ana (1).csv'"
    exit 1
fi

print_success "Archivo CSV encontrado"

# Verificar que analyzer.py existe
if [ ! -f "analyzer.py" ]; then
    print_error "No se encontró el archivo 'analyzer.py'"
    exit 1
fi

print_success "Archivo analyzer.py encontrado"

# Ejecutar análisis
print_status "Iniciando análisis de llamadas..."
echo "================================================================"
echo "📊 PROCESANDO ANÁLISIS DE LLAMADAS"
echo "================================================================"

python3 analyzer.py

# Verificar si el análisis se completó exitosamente
if [ -f "call_analysis_results.csv" ]; then
    print_success "Análisis completado exitosamente!"
    print_status "Resultados guardados en: call_analysis_results.csv"
    
    # Mostrar estadísticas básicas
    if command -v wc &> /dev/null; then
        TOTAL_LINES=$(wc -l < "call_analysis_results.csv")
        print_status "Total de filas procesadas: $((TOTAL_LINES - 1))"  # Restar 1 por el header
    fi
else
    print_error "El análisis no se completó correctamente"
    exit 1
fi

# Limpiar proceso de Ollama
print_status "Deteniendo Ollama..."
kill $OLLAMA_PID 2>/dev/null || true

echo "================================================================"
print_success "¡PROCESO COMPLETADO EXITOSAMENTE!"
echo "================================================================"
echo ""
echo "📁 Archivos generados:"
echo "   - call_analysis_results.csv (resultados del análisis)"
echo ""
echo "🔧 Para ejecutar solo el análisis sin reinstalar:"
echo "   source venv/bin/activate"
echo "   ollama serve &"
echo "   python3 analyzer.py"
echo ""
echo "📊 Para ver los resultados:"
echo "   head -10 call_analysis_results.csv" 