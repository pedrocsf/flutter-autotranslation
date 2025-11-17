import os
import json
import argparse
from typing import Dict, List

def criar_mapa_de_substituicao(caminho_arquivo_arb: str) -> Dict[str, str]:
    try:
        with open(caminho_arquivo_arb, 'r', encoding='utf-8') as f:
            dados_arb = json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo .arb não encontrado em '{caminho_arquivo_arb}'")
        return {}
    except json.JSONDecodeError:
        print(f"Erro: O arquivo '{caminho_arquivo_arb}' não é um JSON válido.")
        return {}

    mapa_invertido = {
        valor: chave
        for chave, valor in dados_arb.items()
        if not chave.startswith('@') and isinstance(valor, str)
    }
    mapa_ordenado = dict(sorted(mapa_invertido.items(), key=lambda item: len(item[0]), reverse=True))

    return mapa_ordenado

def processar_arquivos_na_pasta(pasta_alvo: str, mapa_substituicao: Dict[str, str], extensoes_permitidas: List[str], caminhos_excluidos: List[str]):
    if not os.path.isdir(pasta_alvo):
        print(f"Erro: A pasta '{pasta_alvo}' não existe.")
        return

    total_substituicoes = 0
    arquivos_modificados = 0

    print(f"Iniciando busca na pasta '{pasta_alvo}'...")

    caminhos_excluidos_abs = [os.path.abspath(p) for p in caminhos_excluidos]

    for root, dirs, files in os.walk(pasta_alvo):
        dirs[:] = [d for d in dirs if os.path.abspath(os.path.join(root, d)) not in caminhos_excluidos_abs]

        for nome_arquivo in files:
            caminho_completo = os.path.join(root, nome_arquivo)

            if os.path.abspath(caminho_completo) in caminhos_excluidos_abs:
                continue

            if not any(nome_arquivo.endswith(ext) for ext in extensoes_permitidas):
                continue
            
            try:
                with open(caminho_completo, 'r', encoding='utf-8') as f:
                    conteudo_original = f.read()
            except Exception as e:
                print(f"Aviso: Não foi possível ler o arquivo '{caminho_completo}'. Erro: {e}")
                continue

            conteudo_modificado = conteudo_original
            substituicoes_neste_arquivo = 0

            for valor_string, chave_arb in mapa_substituicao.items():
                string_para_buscar = f'"{valor_string}"'
                string_de_substituicao = f'AppLocalizations.of(context)!.{chave_arb}'
                
                ocorrencias = conteudo_modificado.count(string_para_buscar)
                if ocorrencias > 0:
                    conteudo_modificado = conteudo_modificado.replace(string_para_buscar, string_de_substituicao)
                    substituicoes_neste_arquivo += ocorrencias
            
            if conteudo_modificado != conteudo_original:
                try:
                    with open(caminho_completo, 'w', encoding='utf-8') as f:
                        f.write(conteudo_modificado)
                    print(f"  -> Modificado '{caminho_completo}' ({substituicoes_neste_arquivo} substituições)")
                    total_substituicoes += substituicoes_neste_arquivo
                    arquivos_modificados += 1
                except Exception as e:
                    print(f"Erro: Não foi possível escrever no arquivo '{caminho_completo}'. Erro: {e}")

    print("\n--- Resumo ---")
    print(f"Processo concluído!")
    print(f"Arquivos modificados: {arquivos_modificados}")
    print(f"Total de substituições: {total_substituicoes}")

def main():
    parser = argparse.ArgumentParser(
        description="Substitui strings literais em arquivos por suas chaves de localização do Flutter (l10n).",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--arb',
        required=True,
        help="Caminho para o arquivo .arb de referência. Ex: lib/l10n/app_pt.arb"
    )
    parser.add_argument(
        '--pasta',
        required=True,
        help="Pasta para procurar e substituir as strings. Ex: lib"
    )
    parser.add_argument(
        '--ext',
        default=".dart",
        help="Extensões de arquivo a serem processadas, separadas por vírgula. Padrão: .dart"
    )
    parser.add_argument(
        '--excluir',
        nargs='*',
        default=[],
        help="Lista de arquivos ou pastas a serem ignorados durante a análise. Ex: lib/l10n.dart"
    )

    args = parser.parse_args()
    
    extensoes = [ext.strip() for ext in args.ext.split(',')]
    caminhos_excluidos = args.excluir

    mapa_substituicao = criar_mapa_de_substituicao(args.arb)

    if mapa_substituicao:
        processar_arquivos_na_pasta(args.pasta, mapa_substituicao, extensoes, caminhos_excluidos)

if __name__ == "__main__":
    main()