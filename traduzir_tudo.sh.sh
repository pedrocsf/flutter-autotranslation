#!/bin/bash

# Diretório onde o script main2.py está localizado
SCRIPT_DIR="/home/pacto/Documentos/Github/flutter-autotranslation"

# Arquivo de entrada .arb
ARQUIVO_ENTRADA="app_pt.arb"

# Idioma de origem
IDIOMA_FONTE="pt"

# Lista de códigos de idioma para tradução
IDIOMAS=(
    "af" "sq" "am" "ar" "hy" "as" "ay" "az" "bm" "eu" "be" "bn" "bho" "bs" "bg" "ca" "ceb" "ny" "zh-CN" 
    "zh-TW" "co" "hr" "cs" "da" "dv" "doi" "nl" "en" "eo" "et" "ee" "tl" "fi" "fr" "fy" "gl" "ka" "de" 
    "el" "gn" "gu" "ht" "ha" "haw" "iw" "hi" "hmong" "hu" "is" "ig" "ilo" "id" "ga" "it" "ja" "jw" "kn" 
    "kk" "km" "rw" "gom" "ko" "kri" "ku" "ckb" "ky" "lo" "la" "lv" "ln" "lt" "lg" "lb" "mk" "mai" "mg" 
    "ms" "ml" "mt" "mi" "mr" "mni-Mtei" "lus" "mn" "my" "ne" "no" "or" "om" "ps" "fa" "pl" "pt" "pa" 
    "qu" "ro" "ru" "sm" "sa" "gd" "nso" "sr" "st" "sn" "sd" "si" "sk" "sl" "so" "es" "su" "sw" "sv" 
    "tg" "ta" "tt" "te" "th" "ti" "ts" "tr" "tk" "ak" "uk" "ur" "ug" "uz" "vi" "cy" "xh" "yi" "yo" "zu"
)

# Garante que o arquivo de entrada existe
if [ ! -f "$SCRIPT_DIR/$ARQUIVO_ENTRADA" ]; then
    echo "Erro: Arquivo de entrada '$SCRIPT_DIR/$ARQUIVO_ENTRADA' não encontrado."
    exit 1
fi

# Loop para executar a tradução para cada idioma
for idioma_alvo in "${IDIOMAS[@]}"; do
    # Substitui hifens por underscores para nomes de arquivo, se necessário (ex: zh-CN -> zh_CN)
    nome_arquivo_idioma=${idioma_alvo//-/_}
    ARQUIVO_SAIDA="app_${nome_arquivo_idioma}.arb"
    
    echo "--------------------------------------------------"
    echo "Traduzindo de '$IDIOMA_FONTE' para '$idioma_alvo'..."
    echo "Arquivo de saída: $ARQUIVO_SAIDA"
    
    /bin/python3 "$SCRIPT_DIR/main2.py" \
        --entrada "$SCRIPT_DIR/$ARQUIVO_ENTRADA" \
        --saida "$SCRIPT_DIR/$ARQUIVO_SAIDA" \
        --idioma "$idioma_alvo" \
        --fonte "$IDIOMA_FONTE"
        
    echo "Tradução para '$idioma_alvo' concluída."
    echo "--------------------------------------------------"
    echo ""
done

echo "Todas as traduções foram concluídas!"
