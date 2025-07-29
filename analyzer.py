import pandas as pd
import ollama
from ollama import Client
import json
import os
import sys

def check_ollama_connection():
    """Verificar si Ollama está corriendo"""
    try:
        client = Client(host='http://localhost:11434')
        client.list()
        return True
    except Exception as e:
        print(f"❌ Error: Ollama no está corriendo. Inicia Ollama primero.")
        print(f"Error: {str(e)}")
        return False

def analyze_transcription(transcription):
    try:
        # Verificar si la transcripción está vacía
        if not transcription or transcription == '[]' or transcription == 'NULL':
            return json.dumps({
                "category": "sin_contestaron",
                "justification": "Transcripción vacía - no contestaron la llamada"
            })
        
        # Conectar con Ollama y enviar la transcripción
        client = Client(host='http://localhost:11434')
        response = client.chat(
            model='call_analyzer',
            messages=[
                {
                    'role': 'user',
                    'content': f'Analiza esta transcripción de llamada: {transcription}'
                }
            ]
        )
        return response['message']['content']
    except Exception as e:
        return json.dumps({
            "category": "error",
            "justification": f"Error al conectar con Ollama: {str(e)}"
        })

def parse_response(response_text):
    try:
        # Parsear la respuesta JSON
        response_json = json.loads(response_text)
        category = response_json.get('category', 'error')
        justification = response_json.get('justification', 'Respuesta JSON incompleta')
        return category, justification
    except json.JSONDecodeError:
        return 'error', f'Error: Respuesta no es un JSON válido: {response_text}'
    except Exception as e:
        return 'error', f'Error al parsear la respuesta: {str(e)}'

def process_csv(input_file, output_file):
    try:
        # Verificar conexión con Ollama
        if not check_ollama_connection():
            sys.exit(1)
        
        print(f"📁 Leyendo archivo: {input_file}")
        # Leer el CSV de entrada
        df = pd.read_csv(input_file)
        print(f"✅ CSV cargado con {len(df)} filas")
        
        # Crear o cargar el CSV de salida
        if os.path.exists(output_file):
            result_df = pd.read_csv(output_file)
            print(f"📊 CSV de resultados cargado con {len(result_df)} filas procesadas")
        else:
            # Crear DataFrame vacío con las columnas correctas
            base_columns = ['conversation_id', 'call_status', 'justification']
            all_columns = base_columns + list(df.columns)
            result_df = pd.DataFrame(columns=all_columns)
            print("🆕 Creando nuevo archivo de resultados")
        
        # Contadores
        processed = 0
        skipped = 0
        errors = 0
        
        # Procesar cada fila
        for index, row in df.iterrows():
            conversation_id = row.get('conversation_id', f'row_{index}')
            transcript = row.get('transcript', '[]')
            
            # Verificar si la llamada ya fue procesada
            if len(result_df) > 0 and conversation_id in result_df['conversation_id'].values:
                print(f"⏭️  Llamada {conversation_id} ya procesada, omitiendo...")
                skipped += 1
                continue
            
            print(f"🔍 Procesando llamada {conversation_id}...")
            
            # Analizar la transcripción
            response = analyze_transcription(transcript)
            category, justification = parse_response(response)
            
            # Crear nueva fila con los datos
            new_row = {
                'conversation_id': conversation_id, 
                'call_status': category, 
                'justification': justification
            }
            
            # Agregar todas las columnas del CSV original
            for col in df.columns:
                new_row[col] = row[col]
            
            # Crear DataFrame temporal para la nueva fila y asegurar índices únicos
            temp_df = pd.DataFrame([new_row])
            
            # Concatenar de manera segura con índices únicos
            if len(result_df) == 0:
                result_df = temp_df.copy()
            else:
                # Asegurar que los índices sean únicos
                result_df = result_df.reset_index(drop=True)
                temp_df = temp_df.reset_index(drop=True)
                result_df = pd.concat([result_df, temp_df], ignore_index=True)
            
            # Guardar el CSV de salida después de cada análisis
            result_df.to_csv(output_file, index=False)
            
            if category == 'error':
                errors += 1
                print(f"❌ Error en llamada {conversation_id}: {justification}")
            else:
                processed += 1
                print(f"✅ Procesada llamada {conversation_id}: {category}")
        
        print(f"\n📊 RESUMEN DEL PROCESAMIENTO:")
        print(f"✅ Procesadas: {processed}")
        print(f"⏭️  Omitidas: {skipped}")
        print(f"❌ Errores: {errors}")
        print(f"💾 Resultados guardados en {output_file}")
    
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    input_csv = "all_leads_ana (1).csv"  # CSV real del proyecto
    output_csv = "call_analysis_results.csv"  # CSV de resultados
    process_csv(input_csv, output_csv)