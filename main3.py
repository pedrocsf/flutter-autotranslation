import json
import argparse
import os
import re
from typing import List, Dict, Set
import hashlib

def generate_key_from_value(value: str, existing_keys: Set[str]) -> str:
    """Gera uma chave única usando um hash do valor da string."""
    if not value.strip():
        return ""

    h = hashlib.sha1(value.encode('utf-8')).hexdigest()
    
    base_key = f"key_{h[:8]}"

    key = base_key
    counter = 1
    while key in existing_keys:
        key = f"{base_key}{counter}"
        counter += 1
    
    return key

def read_values_from_file(input_path: str) -> List[str]:
    """Lê uma lista de valores de um arquivo .json ou .txt."""
    _, ext = os.path.splitext(input_path)
    values = []

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            if ext == '.json':
                data = json.load(f)
                if isinstance(data, list):
                    values = [str(item) for item in data]
                else:
                    print(f"Aviso: O JSON em '{input_path}' não é uma lista. Tentando usar os valores do objeto.")
                    values = [str(v) for v in data.values()]
            elif ext == '.txt':
                values = [line.strip() for line in f if line.strip()]
            else:
                print(f"Erro: Formato de arquivo não suportado '{ext}'. Use .json ou .txt.")
    except FileNotFoundError:
        print(f"Erro: Arquivo de entrada não encontrado em '{input_path}'")
    except json.JSONDecodeError:
        print(f"Erro: O arquivo '{input_path}' não é um JSON válido.")
    except Exception as e:
        print(f"Erro ao ler o arquivo '{input_path}': {e}")
        
    return values

def generate_arb_from_values(input_path: str, output_path: str):
    """Gera um arquivo .arb com chaves a partir de um arquivo de valores."""
    values = read_values_from_file(input_path)
    if not values:
        print("Nenhum valor encontrado para processar.")
        return

    print(f"Encontrados {len(values)} valores em '{input_path}'. Gerando chaves...")

    generated_arb: Dict[str, str] = {}
    existing_keys: Set[str] = set()

    for value in values:
        key = generate_key_from_value(value, existing_keys)
        if key:
            generated_arb[key] = value
            existing_keys.add(key)
            print(f"  - Gerado: '{key}': '{value[:50]}...'")

    try:
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(generated_arb, f, ensure_ascii=False, indent=2)
        print(f"\nSucesso! Arquivo ARB gerado em: '{output_path}'")
    except IOError as e:
        print(f"Erro ao escrever o arquivo de saída '{output_path}': {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Gera chaves para um arquivo .arb a partir de uma lista de valores em um arquivo .json ou .txt.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--entrada',
        required=True,
        help="Caminho para o arquivo de origem com os valores (.json ou .txt).\nEx: 'strings.json' ou 'strings.txt'"
    )
    parser.add_argument(
        '--saida',
        required=True,
        help="Caminho para o novo arquivo .arb a ser gerado.\nEx: 'lib/l10n/app_pt.arb'"
    )

    args = parser.parse_args()
    generate_arb_from_values(args.entrada, args.saida)

if __name__ == "__main__":
    main()
