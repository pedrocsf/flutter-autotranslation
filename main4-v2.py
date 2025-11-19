import os
import re
import json
import argparse

BASE_DIR = os.getcwd()

OUTPUT_JSON_FILE = 'translations_pt.json'
UPPERCASE_WHITELIST = ['PAR-Q', 'ANT+', 'DESAFIO', 'SALVAR', 'PUBLICAR', 'CNPJ', 'CPF', 'ABC?']


extracted_strings = {}

ignoredCount = 0

STRING_REGEX = re.compile(
    r"""
    (
        ['"]
        (
            [^'"\n]*?
            [a-zA-ZáàâãéèêíïóôõúçñÁÀÂÃÉÈÊÍÏÓÔÕÚÇÑ]
            [^'"\n]*?
        )
        ['"]
    )
    """,
    re.VERBOSE
)

def format_string_to_key(text):
    text = re.sub(r'[^\w\s]', '', text).strip().lower()
    text = re.sub(r'\s+', '_', text)
    return text.strip('_')[:50]

def is_ignored(path):
    IGNORE_SUFFIXES  = [
        '.g.dart',
    ]

    if os.path.isdir(path) and not path.endswith('/'):
        path = path + '/'


    for pattern in IGNORE_SUFFIXES:
        if path.endswith(pattern):
            return True
        
    return False

def extract_from_file(filepath):
    global ignoredCount

    # ====================
    #        FILES
    # ====================
    # --
    if 'lib/packages/moovz_models' in filepath or 'lib/packages/moovz_services' in filepath:
        return
    
    # --
    if 'firebase_options.dart' in os.path.basename(filepath):
        return
    
    # --
    if 'FirebaseParQModelDocument.dart' in os.path.basename(filepath):
        return
    
    # --
    if 'lib/main.dart' in filepath:
        return
    
    if 'color_extensions.dart' in os.path.basename(filepath):
        return
    
    # --
    files_white_list = ['FIrebaseClassSessionModelRepository.dart',
                            'HeartRateZoneModelData.dart',
                            'i_base_firebase_repository.dart']
    
    is_file_white_list = any(filepath.__contains__(file) for file in files_white_list)

    if 'lib/packages/moovz_commons/src/repositories' in filepath:
        if not is_file_white_list:
            return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    matches_iter = STRING_REGEX.finditer(content)

    for match in matches_iter:
        full_match_content = match.group(2)
        start_index = match.start(1) # Posição inicial da string completa no arquivo

        # Divide a string por interpolações como ${...}, mantendo os delimitadores
        # Ex: 'Olá ${name}, bem-vindo!' -> ['Olá ', '${name}', ', bem-vindo!']
        string_parts = re.split(r'(\$\{.*?\})', full_match_content)

        for part in string_parts:
            text = part.strip()

        # ====================
        #       OBJECTS
        # ====================
            if not text or text.startswith('${'):
                continue

            if text.isnumeric() or text.startswith(('http', '/', ':')):
                continue
            
        # ====================
        #   MOST ARE IMPORTS
        # ====================
        if text.__contains__('/') and text.__contains__('package') and text.__contains__('.dart'):
            continue

        if text.__contains__('/') and text.__contains__('.dart'):
            continue

        if text.__contains__('dart'):
            continue
    
        # ====================
        #    LOG FUNCTIONS
        # ====================
        pre_text = content[max(0, start_index - 30):start_index]

        # --
        if re.search(r'(log|print|debugPrint|logEvent)\s*\(\s*', pre_text) and not pre_text.__contains__('alog'):
            continue

        # --
        if re.search(r'(inspectWithMessage|inspectWithMessageAndTrace|logger.e)\s*\(\s*', pre_text):
            continue

        # --
        if re.search(r'(logInfo|logWarning)\s*\(\s*title\s*:\s*', pre_text):
            continue

        # ====================
        #  MOST ARE VARIABLES
        # ====================
        # --
        if (text.__contains__('_') and text.isupper()) or (text.__contains__('_') and text.islower()):
            continue
        
        # --
        if (not re.search(r'[áàâãéèêíïóôõúçñÁÀÂÃÉÈÊÍÏÓÔÕÚÇÑ]', text)):
            is_strict_camel_case = re.search(r'^[a-z].*[A-Z]', text)
            contains_spaces = ' ' in text

            if is_strict_camel_case and not contains_spaces:
                continue

        # --
        if text.startswith('${') and text.endswith('}') and not ' ' in text:
            continue

        # --
        if text.startswith('${') and not ' ' in text:
            continue

        # --
        if text.startswith('$') and not ' ' in text:
            continue

        # --
        if text.__contains__('substring'):
            continue

        # -- constants uppercase
        have_one_lower_letter = any(letter.islower() for letter in text)
        is_white_list = any(text.__contains__(word) for word in UPPERCASE_WHITELIST)
        
        if not have_one_lower_letter and len(text) > 3 and not is_white_list:
            continue

        # -- from .get()
        if re.search(r'(get)\s*\(\s*', pre_text) and not 'dget' in pre_text and not 'title' in pre_text:
            continue

        # --

        # ====================
        #        FILES
        # ====================
        if text.__contains__('.dart') or text.__contains__('.onError') or text.__contains__('.json') or text.__contains__('.png'):
            continue

        if text.__contains__('.svg') or text.__contains__('jpeg'):
            continue
        
        # ====================
        #       OBJECTS
        # ====================
        if re.search(r'[A-Z][a-zA-Z]*\(.+?\$[a-zA-Z]', text):
            continue

        # ====================
        #  DATA and VARIATIONS
        # ====================
        # --
        if (re.search(r'(json)\s*\[\s*', pre_text) or
        re.search(r'(map)\s*\[\s*', pre_text) or
        re.search(r'(data)\s*\[\s*', pre_text) or
        re.search(r'(value)\s*\[\s*', pre_text) or
        re.search(r'(postBody)\s*\[\s*', pre_text) or
        re.search(r'(queryParameters)\s*\[\s*', pre_text) or
        re.search(r'(reqBody)\s*\[\s*', pre_text) or
        re.search(r'(updateData)\s*\[\s*', pre_text) or
        re.search(r'(memberData)\s*\[\s*', pre_text)):
            continue

        # --
        if (re.search(r'(collection)\s*\(\s*', pre_text) or
        re.search(r'(where)\s*\(\s*', pre_text)):
            continue

        # -- all like ['variable']
        VARIABLES = ['Janeiro', 'Início', 'Semanalmente', 'Péssimo']
        is_variable_white_list = any(text.__contains__(word) for word in VARIABLES)
        if re.search(r'\[\s*$', pre_text) and not ' ' in text and not is_variable_white_list:
            if not 'lowerCase' in pre_text and not 'upperCase' in pre_text:
                continue
        
        # ====================
        #   ENGLISH MESSAGES
        # ====================
        # -----------
        ENGLISH_WORDS = ['Unable', 'Failed', 'Error', '_getIndividualZonePercentageFromTotalTime']

        is_english_word = any(text.__contains__(word) for word in ENGLISH_WORDS)
        
        if is_english_word or 'user ' in text.lower():
            continue

        # ----------
        ENGLISH_WORDS_2 = ['Invalid', 'Unknown', 'parse', 'session', 'found', '.env', ' error',
                           'unauthorized', 'missing', 'failed']

        is_english_word_2 = any(text.__contains__(word) for word in ENGLISH_WORDS_2)

        if is_english_word_2 or ' text ' in text.lower() and not 'cm.' in text:
            continue

        # -----------
        ENGLISH_WORDS_3 = ['default', 'Could', '?.duration.inSeconds', 'Notifications',
                           'assets', 'signup', 'rovide', 'ercent', 'Missing', 'invalid',]

        is_english_word_3 = any(text.__contains__(word) for word in ENGLISH_WORDS_3)
        if is_english_word_3 or ('the' in text.lower() and not 'anos' in text):
            continue

        # -----------
        ENGLISH_WORDS_4 = ['newStatus', 'returned', 'vsfFDPBurro', '2346789bcdfghjkmnpqrtwxyz',
                           'path', 'leadingHashSign', 'json', 'questions', 'christmas']

        is_english_word_4 = any(text.__contains__(word) for word in ENGLISH_WORDS_4)
        if is_english_word_4:
            continue
        
            ignoredCount += 1
            print(f"{'=' * 30} | {ignoredCount} | {'=' * 30}")
            # print(filepath)
            print('-' * 70)
            print(pre_text + ' <-> ' + text)
            print('=' * 70)
            print(' ')
            print(' ')
            
        key = format_string_to_key(text)

        original_key = key
        counter = 1
        while key in extracted_strings and extracted_strings[key] != text:
            key = f"{original_key}_{counter}"
            counter += 1

        extracted_strings[key] = text

def run_extraction(target_dir, output_file):
    if os.path.isabs(target_dir):
        full_dir_path = target_dir
    else:
        full_dir_path = os.path.join(BASE_DIR, target_dir)

    if not os.path.exists(full_dir_path):
        print(f"Diretório de código não encontrado: {full_dir_path}")
        return
    
    for root, dirs, files in os.walk(full_dir_path):
        # dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d))]

        for file in files:
            if file.endswith('.dart'):
                filepath = os.path.join(root, file)
                if is_ignored(filepath):
                    continue

                extract_from_file(filepath)
    
    print("-" * 30)
    print(f"Total de {len(extracted_strings)} strings únicas encontradas.")

    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(extracted_strings, f, ensure_ascii=False, indent=2)
    
    print(f"Arquivo JSON de tradução salvo em: {os.path.join(BASE_DIR, output_file)}")
    print("-" * 30)

# --- EXECUÇÃO FINAL ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrai strings de um projeto Flutter para um arquivo JSON.")
    parser.add_argument('--pasta', required=True, help="Caminho para a pasta a ser analisada.")
    parser.add_argument('--saida', default=OUTPUT_JSON_FILE, help="Nome do arquivo JSON de saída. Padrão: translations_pt.json")
    args = parser.parse_args()
    
    run_extraction(args.pasta, args.saida)
