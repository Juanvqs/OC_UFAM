import sys

# Registradores
registradores = {
    'r0': '00',
    'r1': '01',
    'r2': '10',
    'r3': '11'
}

# Operações, adicionando as que foram solicitadas
operacoes = {
    'add': '1000',
    'shr': '1001',
    'shl': '1010',
    'not': '1011',
    'and': '1100',
    'or': '1101',
    'xor': '1110',
    'cmp': '1111',
    'ld': '0000',
    'st': '0001',
    'data': '0010 00',
    'jmpr': '0011 00',
    'jmp': '0100 0000',
    'clf': '0110 0000',
    'in': '0111 0',
    'out': '0111 1',
    'swap': '1011',  # Definindo swap
    'halt': '1111111111111111'  # Definindo halt
}

# Operações do JCAEZ
jcaez_operacoes = {
    'jc': '0101 1000',
    'ja': '0101 0100',
    'je': '0101 0010',
    'jz': '0101 0001',
    'jca': '0101 1100',
    'jce': '0101 1010',
    'jcz': '0101 1001',
    'jae': '0101 0110',
    'jaz': '0101 0101',
    'jez': '0101 0011',
    'jcae': '0101 1110',
    'jcaz': '0101 1101',
    'jcez': '0101 1011',
    'jaez': '0101 0111',
    'jcaez': '0101 1111'
}

def ler_arquivo_fonte(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r') as arquivo:
            linhas = arquivo.readlines()
        return [linha.strip().lower() for linha in linhas if linha.strip() and not linha.strip().startswith(';')]
    except FileNotFoundError:
        print(f"Erro: O arquivo {caminho_arquivo} não foi encontrado.")
        return []

def dividir_linha(linha):
    partes = linha.split()
    if len(partes) == 0:
        return None, None
    
    instrucao = partes[0].lower()
    operandos = []
    
    if len(partes) > 1:
        operandos_str = ' '.join(partes[1:])
        operandos = [op.strip() for op in operandos_str.split(',')]
    
    return instrucao, operandos

def converter_para_codigo_maquina(linhas):
    codigo_maquina = []
    for linha in linhas:
        instrucao, operandos = dividir_linha(linha)
        if instrucao in operacoes:
            if instrucao in ['in', 'out']:
                if len(operandos) != 2:
                    raise ValueError(f"Erro: Instrução {instrucao} requer dois operandos.")
                if operandos[0] == 'data':
                    codigo_op = operacoes[instrucao] + '0' + registradores[operandos[1]]
                elif operandos[0] == 'addr' or operandos[0] == 'address':
                    codigo_op = operacoes[instrucao] + '1' + registradores[operandos[1]]
                else:
                    raise ValueError(f"Erro: Operando inválido para instrução {instrucao}.")
                codigo_maquina.append(codigo_op)
            elif instrucao in ['swap']:
                if len(operandos) != 2:
                    raise ValueError(f"Erro: Instrução {instrucao} requer dois operandos.")
                troca1 = operacoes['xor'] + registradores[operandos[0]] + registradores[operandos[1]]
                troca2 = operacoes['xor'] + registradores[operandos[1]] + registradores[operandos[0]]
                codigo_maquina.append(troca1)
                codigo_maquina.append(troca2)
                codigo_maquina.append(troca1)
            elif instrucao in ['halt']:
                codigo_maquina.append(operacoes['halt'])
            elif instrucao == 'data':
                if len(operandos) != 2:
                    raise ValueError(f"Erro: Instrução {instrucao} requer dois operandos.")
                if operandos[1].startswith('0x'):
                    valor = int(operandos[1], 16)
                elif operandos[1].startswith('0b'):
                    valor = int(operandos[1], 2)
                else:
                    valor = int(operandos[1])
                codigo_maquina.append(operacoes[instrucao] + registradores[operandos[0]])
                codigo_maquina.append(format(valor, '08b'))
            elif instrucao in ['clf']:
                codigo_maquina.append(operacoes[instrucao])
            elif instrucao in ['jmpr']:
                if len(operandos) != 1:
                    raise ValueError(f"Erro: Instrução {instrucao} requer um operando.")
                codigo_maquina.append(operacoes[instrucao] + registradores[operandos[0]])
            elif instrucao in ['jmp']:
                if len(operandos) != 1:
                    raise ValueError(f"Erro: Instrução {instrucao} requer um operando.")
                endereco = int(operandos[0], 0)
                codigo_maquina.append(operacoes[instrucao])
                codigo_maquina.append(format(endereco, '08b'))
            else:
                if len(operandos) != 2:
                    raise ValueError(f"Erro: Instrução {instrucao} requer dois operandos.")
                codigo_op = operacoes[instrucao] + registradores[operandos[0]] + registradores[operandos[1]]
                codigo_maquina.append(codigo_op)
        elif instrucao in jcaez_operacoes:
            if len(operandos) != 1:
                raise ValueError(f"Erro: Instrução {instrucao} requer um operando.")
            endereco = int(operandos[0], 0)
            codigo_maquina.append(jcaez_operacoes[instrucao])
            codigo_maquina.append(format(endereco, '08b'))
        else:
            raise ValueError(f"Erro: Instrução desconhecida: {instrucao}")
    return codigo_maquina

def converter_binario_para_hexadecimal(codigo_binario):
    codigo_binario = codigo_binario.replace(' ', '')
    return hex(int(codigo_binario, 2))[2:].upper().zfill(2)

def converter_para_hex(codigo_maquina):
    palavras_hex = []
    for codigo in codigo_maquina:
        palavra_hex = converter_binario_para_hexadecimal(codigo)
        palavras_hex.append(palavra_hex)
    return palavras_hex

def escrever_arquivo_saida(memoria, caminho):
    assert len(memoria) <= 256
    while len(memoria) < 256:
        memoria.append('00')
    with open(caminho, 'w') as arquivo_saida:
        arquivo_saida.write("v3.0 hex words addressed\n")
        for i in range(len(memoria)):
            arquivo_saida.write(f'{i:02x}: ')
            arquivo_saida.write(memoria[i] + "\n")

def montador(arquivo_fonte, caminho_arquivo_saida):
    linhas = ler_arquivo_fonte(arquivo_fonte)
    if not linhas:
        return
    try:
        codigo_binario = converter_para_codigo_maquina(linhas)
        codigo_hex = converter_para_hex(codigo_binario)
        escrever_arquivo_saida(codigo_hex, caminho_arquivo_saida)
        print(f"Arquivo de saída: {caminho_arquivo_saida} gerado com sucesso!")
    except ValueError as e:
        print(f"Erro durante a montagem: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python3 montador.py <arquivo.asm> <arquivo_saida.m>")
        sys.exit(1)
    arquivo_fonte = sys.argv[1]
    caminho_arquivo_saida = sys.argv[2]
    montador(arquivo_fonte, caminho_arquivo_saida)