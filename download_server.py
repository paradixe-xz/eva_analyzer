from flask import Flask, send_file, render_template_string
import os
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# HTML template para mostrar estadísticas
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Análisis de Llamadas - Resultados</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }
        .stat-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }
        .stat-number { font-size: 2em; font-weight: bold; color: #007bff; }
        .stat-label { color: #666; margin-top: 5px; }
        .download-btn { display: inline-block; background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .download-btn:hover { background: #218838; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }
        .status-item { background: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; }
        .status-count { font-size: 1.5em; font-weight: bold; color: #495057; }
        .status-name { color: #6c757d; font-size: 0.9em; }
        .error { color: #dc3545; }
        .success { color: #28a745; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Análisis de Llamadas - Resultados</h1>
        
        {% if file_exists %}
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{{ total_calls }}</div>
                    <div class="stat-label">Total de Llamadas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ processed_calls }}</div>
                    <div class="stat-label">Procesadas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ unique_statuses }}</div>
                    <div class="stat-label">Estados Únicos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ last_updated }}</div>
                    <div class="stat-label">Última Actualización</div>
                </div>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="/download" class="download-btn">📥 Descargar CSV Completo</a>
            </div>
            
            <h3>📈 Distribución por Estado:</h3>
            <div class="status-grid">
                {% for status, count in status_distribution.items() %}
                <div class="status-item">
                    <div class="status-count">{{ count }}</div>
                    <div class="status-name">{{ status }}</div>
                </div>
                {% endfor %}
            </div>
            
            <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                <h4>📋 Primeras 10 Llamadas:</h4>
                <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                    <thead>
                        <tr style="background: #e9ecef;">
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">ID</th>
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">Estado</th>
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">Justificación</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for call in sample_calls %}
                        <tr style="border-bottom: 1px solid #dee2e6;">
                            <td style="padding: 10px;">{{ call.conversation_id }}</td>
                            <td style="padding: 10px;">{{ call.call_status }}</td>
                            <td style="padding: 10px;">{{ call.justification[:50] }}{% if call.justification|length > 50 %}...{% endif %}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        {% else %}
            <div style="text-align: center; padding: 50px;">
                <h2 class="error">❌ Archivo de resultados no encontrado</h2>
                <p>El archivo 'call_analysis_results.csv' no existe aún.</p>
                <p>Ejecuta primero el análisis con: <code>python3 analyzer.py</code></p>
            </div>
        {% endif %}
        
        <div style="margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
            <h4>🔧 Comandos Útiles:</h4>
            <ul>
                <li><strong>Ejecutar análisis:</strong> <code>python3 analyzer.py</code></li>
                <li><strong>Ver resultados:</strong> <code>head -10 call_analysis_results.csv</code></li>
                <li><strong>Contar líneas:</strong> <code>wc -l call_analysis_results.csv</code></li>
                <li><strong>Filtrar por estado:</strong> <code>grep "sin_contestaron" call_analysis_results.csv | wc -l</code></li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    file_path = '/eva_analyzer/call_analysis_results.csv'
    
    if os.path.exists(file_path):
        try:
            # Leer el CSV para obtener estadísticas
            df = pd.read_csv(file_path)
            
            # Estadísticas básicas
            total_calls = len(df)
            processed_calls = len(df[df['call_status'].notna()])
            unique_statuses = df['call_status'].nunique()
            
            # Obtener fecha de modificación
            mod_time = os.path.getmtime(file_path)
            last_updated = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
            
            # Distribución por estado
            status_distribution = df['call_status'].value_counts().to_dict()
            
            # Primeras 10 llamadas para mostrar
            sample_calls = df.head(10)[['conversation_id', 'call_status', 'justification']].to_dict('records')
            
            return render_template_string(HTML_TEMPLATE, 
                                       file_exists=True,
                                       total_calls=total_calls,
                                       processed_calls=processed_calls,
                                       unique_statuses=unique_statuses,
                                       last_updated=last_updated,
                                       status_distribution=status_distribution,
                                       sample_calls=sample_calls)
        except Exception as e:
            return f"Error al leer el archivo: {str(e)}", 500
    else:
        return render_template_string(HTML_TEMPLATE, file_exists=False)

@app.route('/download')
def download_file():
    file_path = '/eva_analyzer/call_analysis_results.csv'
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name='call_analysis_results.csv')
    else:
        return "Archivo no encontrado. Ejecuta primero el análisis.", 404

@app.route('/status')
def status():
    file_path = '/eva_analyzer/call_analysis_results.csv'
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            return {
                'file_exists': True,
                'total_calls': len(df),
                'processed_calls': len(df[df['call_status'].notna()]),
                'status_distribution': df['call_status'].value_counts().to_dict()
            }
        except Exception as e:
            return {'error': str(e)}
    else:
        return {'file_exists': False}

if __name__ == '__main__':
    print("🌐 Iniciando servidor de descarga en http://0.0.0.0:4000")
    print("📊 Visita http://localhost:4000 para ver los resultados")
    print("📥 Descarga directa: http://localhost:4000/download")
    app.run(host='0.0.0.0', port=4000, debug=False) 