import random
import string

def generate_password(length, include_uppercase=True, include_lowercase=True, include_digits=True, include_symbols=True):
    """
    Gera uma senha aleatória com base nos critérios fornecidos.

    Args:
        length (int): O comprimento desejado da senha.
        include_uppercase (bool): Se deve incluir letras maiúsculas (A-Z).
        include_lowercase (bool): Se deve incluir letras minúsculas (a-z).
        include_digits (bool): Se deve incluir dígitos (0-9).
        include_symbols (bool): Se deve incluir símbolos (!@#$%^&*()).

    Retorna:
        str: A senha gerada ou uma cadeia de caracteres vazia se nenhum tipo de caractere for selecionado.
    """
    characters = ''
    if include_uppercase:
        characters += string.ascii_uppercase
    if include_lowercase:
        characters += string.ascii_lowercase
    if include_digits:
        characters += string.digits
    if include_symbols:
        characters += string.punctuation

    if not characters:
        return "" #Retorna uma string vazia para indicar erro/nenhum caractere selecionado
    
    #Certifique-se de que pelo menos um caractere de cada tipo selecionado esteja na senha
    guaranteed_characters = []
    if include_uppercase:
        guaranteed_characters.append(random.choice(string.ascii_uppercase))
    if include_lowercase:
        guaranteed_characters.append(random.choice(string.ascii_lowercase))
    if include_digits:
        guaranteed_characters.append(random.choice(string.digits))
    if include_symbols:
        guaranteed_characters.append(random.choice(string.punctuation))
    
    #Preencha o restante da senha com caracteres aleatórios
    password_list = [random.choice(characters) for _ in range(length - len(guaranteed_characters))]
    password_list.extend(guaranteed_characters) #Adicione os caracteres garantidos
    random.shuffle(password_list) #Embaralhar para randomizar a posição dos caracteres garantidos

    return ''.join(password_list)
