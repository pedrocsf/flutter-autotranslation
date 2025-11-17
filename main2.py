import json
import argparse
import os
from deep_translator import GoogleTranslator
from typing import Dict, Any

def traduzir_arquivo_arb(caminho_entrada: str, caminho_saida: str, idioma_alvo: str, idioma_fonte: str = 'auto'):
    try:
        with open(caminho_entrada, 'r', encoding='utf-8') as f:
            dados_arb = json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo de entrada não encontrado em '{caminho_entrada}'")
        return
    except json.JSONDecodeError:
        print(f"Erro: O arquivo '{caminho_entrada}' não é um JSON válido.")
        return

    dados_traduzidos: Dict[str, Any] = {}
    tradutor = GoogleTranslator(source=idioma_fonte, target=idioma_alvo)

    print(f"Traduzindo de '{idioma_fonte}' para '{idioma_alvo}'...")

    total_chaves = len([k for k in dados_arb if not k.startswith('@')])
    chaves_processadas = 0

    for chave, valor in dados_arb.items():
        if chave.startswith('@'):
            dados_traduzidos[chave] = valor
            continue

        try:
            if isinstance(valor, str):
                valor_traduzido = tradutor.translate(valor)
                dados_traduzidos[chave] = valor_traduzido
                chaves_processadas += 1
                print(f"  ({chaves_processadas}/{total_chaves}) '{chave}': '{valor}' -> '{valor_traduzido}'")
            else:
                dados_traduzidos[chave] = valor
        except Exception as e:
            print(f"Erro ao traduzir a chave '{chave}': {e}")
            dados_traduzidos[chave] = valor
    
    try:
        diretorio_saida = os.path.dirname(caminho_saida)
        if diretorio_saida:
            os.makedirs(diretorio_saida, exist_ok=True)
        
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            json.dump(dados_traduzidos, f, ensure_ascii=False, indent=2)
        print(f"\nTradução concluída! Arquivo salvo em: '{caminho_saida}'")
    except IOError as e:
        print(f"Erro ao escrever o arquivo de saída '{caminho_saida}': {e}")


def main2():
    parser = argparse.ArgumentParser(
        description="Traduz os valores de um arquivo .arb do Flutter para um novo idioma.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--entrada',
        required=True,
        help="Caminho para o arquivo .arb de origem. Ex: lib/l10n/app_pt.arb"
    )
    parser.add_argument(
        '--saida',
        required=True,
        help="Caminho para o novo arquivo .arb traduzido. Ex: lib/l10n/app_es.arb"
    )
    parser.add_argument(
        '--idioma',
        required=True,
        help="Código do idioma de destino para a tradução. Ex: es (espanhol), en (inglês)"
    )
    parser.add_argument(
        '--fonte',
        default='auto',
        help="(Opcional) Código do idioma de origem. Padrão: 'auto' para detecção automática."
    )

    args = parser.parse_args()
    
    traduzir_arquivo_arb(args.entrada, args.saida, args.idioma, args.fonte)

if __name__ == "__main__":
    main2()
