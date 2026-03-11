import os
from datetime import datetime

# Base de dados (volátil)
produtos = []       
pessoas = []        
solicitacoes = []   

usuarios = {
    "adm": {"senha": "1234", "tipo": "Administrador"}
}

# Utilitários
def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def obter_input(prompt, allow_empty=False):
    """
    Retorna None se usuário digitar 'V' (voltar).
    Se allow_empty=False, força entrada não vazia.
    """
    while True:
        val = input(prompt).strip()
        if val.lower() == 'v':
            return None
        if not allow_empty and val == "":
            print("Entrada não pode ser vazia. (Digite 'V' para voltar)")
            continue
        return val

def validar_data(data_str):
    """Retorna datetime ou None. Espera ddmmaaaa."""
    if not data_str or not data_str.isdigit() or len(data_str) != 8:
        return None
    try:
        return datetime.strptime(data_str, "%d%m%Y")
    except:
        return None

def dias_para_vencimento(data_str, hoje):
    d = validar_data(data_str)
    if not d:
        return 9999
    return (d - hoje).days

def formatar_qtd(q):
    s = str(q)
    if '.' in s:
        return s.replace('.', ',')
    return s

def formatar_data(data_str):
    try:
        return datetime.strptime(data_str, "%d%m%Y").strftime("%d/%m/%Y")
    except:
        return data_str

def gerar_codigo_produto():
    return 1 + (produtos[-1]['codigo'] if produtos else 0)

def gerar_id_solicitacao():
    return 1 + (solicitacoes[-1]['id'] if solicitacoes else 0)

# Login
def tela_login():
    while True:
        limpar_tela()
        print("=== Sistema PIM - Gestão de Produtos Colaborativos ===")
        print("1 - Entrar")
        print("2 - Recuperar senha")
        print("3 - Sair")
        opc = input("Escolha: ").strip()
        if opc == "1":
            tentativas = 3
            while tentativas > 0:
                usuario = input("Usuário (ou CPF criado): ").strip()
                if usuario.lower() == 'v': break
                senha = input("Senha: ").strip()
                u = usuarios.get(usuario)
                if u and u.get("senha") == senha:
                    print(f"\nBem-vindo(a) — nível: {u['tipo']}")
                    input("Enter para continuar...")
                    return usuario
                else:
                    tentativas -= 1
                    print(f"Usuário ou senha incorretos. Tentativas restantes: {tentativas}")
                    input("Enter para continuar...")
            print("Tentativas esgotadas. Retornando ao menu...")
            input("Enter para continuar...")
        elif opc == "2":
            usuario = input("Digite seu usuário para recuperar a senha (V para voltar): ").strip()
            if usuario.lower() == 'v': continue
            u = usuarios.get(usuario)
            if u:
                print(f"Sua senha é: {u['senha']}")
            else:
                print("Usuário não encontrado.")
            input("Enter para voltar...")
        elif opc == "3":
            print("Encerrando o sistema...")
            exit()
        else:
            input("Opção inválida. Enter para continuar...")

# CADASTROS
def cadastrar_produto(usuario):
    if usuarios[usuario]['tipo'] != "Administrador":
        input("Apenas administrador pode cadastrar produtos. Enter para voltar...")
        return
    limpar_tela()
    print("=== Cadastrar Produto (Digite V para voltar) ===")
    nome = obter_input("Nome do produto: ")
    if nome is None: return
    tipos_validos = ["alimento","brinquedo","remedio","higiene","outros"]
    while True:
        tipo = obter_input("Tipo (alimento, brinquedo, remedio, higiene, outros): ")
        if tipo is None: return
        if tipo.lower() in tipos_validos:
            tipo = tipo.capitalize()
            break
        print("Tipo inválido. Opções válidas:", ", ".join(tipos_validos))
    while True:
        peso = obter_input("Peso (kg, use vírgula para decimais): ")
        if peso is None: return
        try:
            peso_f = float(peso.replace(",","."))

            if peso_f <= 0:
                print("Peso deve ser maior que zero.")
            else:
                break
        except:
            print("Peso inválido. Use números (ex: 0,5).")
    while True:
        q = obter_input("Quantidade disponível (use vírgula para decimais): ")
        if q is None: return
        try:
            qf = float(q.replace(",",".")) 
            if qf <= 0:
                print("Quantidade deve ser maior que zero.")
            else:
                quantidade = qf
                break
        except:
            print("Quantidade inválida. Use número (ex: 2 ou 1,5).")
    while True:
        validade = obter_input("Validade (ddmmaaaa): ")
        if validade is None: return
        if validar_data(validade):
            break
        print("Data inválida. Formato correto: ddmmaaaa (ex: 01012026).")
    origem = obter_input("Origem da doação (nome do doador/instituição): ")
    if origem is None: return
    while True:
        data_ent = obter_input("Data de entrada (ddmmaaaa): ")
        if data_ent is None: return
        if validar_data(data_ent):
            break
        print("Data inválida.")
    codigo = gerar_codigo_produto()
    produtos.append({
        "codigo": codigo,
        "nome": nome,
        "tipo": tipo,
        "peso": peso_f,
        "quantidade": quantidade,
        "validade": validade,
        "origem": origem,
        "data_entrada": data_ent
    })
    print("Produto cadastrado com sucesso. Código:", codigo)
    input("Enter para voltar...")

def cadastrar_pessoa_tipo(usuario, forcar_tipo=None):
    # somente admin cadastra
    if usuarios[usuario]['tipo'] != "Administrador":
        input("Apenas administrador pode cadastrar pessoas. Enter para voltar...")
        return
    limpar_tela()
    print("=== Cadastrar Pessoa (Digite V para voltar) ===")
    nome = obter_input("Nome completo: ")
    if nome is None: return
    while True:
        cpf = obter_input("CPF/CNPJ (somente números): ")
        if cpf is None: return
        if not cpf.isdigit():
            print("Digite apenas números.")
            continue
        if any(p['cpf'] == cpf for p in pessoas):
            print("CPF/CNPJ já cadastrado.")
            continue
        break
    telefone = obter_input("Telefone: ")
    if telefone is None: return
    if forcar_tipo:
        tipo = forcar_tipo
    else:
        while True:
            tipo = obter_input("Tipo (Doador, Voluntario, Solicitante, Beneficiario, Administrador): ")
            if tipo is None: return
            if tipo.lower() in ["doador","voluntario","solicitante","beneficiario","administrador"]:
                tipo = tipo.capitalize()
                break
            print("Tipo inválido.")
    pessoas.append({"nome": nome, "cpf": cpf, "telefone": telefone, "tipo": tipo})
    usuarios[cpf] = {"senha": "1234", "tipo": tipo}
    print(f"Pessoa cadastrada. Usuário criado: {cpf} (senha 1234) | Tipo: {tipo}")
    input("Enter para voltar...")

# Controle de Estoque
def filtrar_produtos(tipo=None, proximo_vencer=False, vencidos=False, nome_contains=None, origem=None):
    hoje = datetime.today()
    res = produtos
    if tipo:
        res = [p for p in res if p['tipo'].lower() == tipo.lower()]
    if proximo_vencer:
        res = [p for p in res if 0 <= dias_para_vencimento(p['validade'], hoje) <= 7]
    if vencidos:
        res = [p for p in res if dias_para_vencimento(p['validade'], hoje) < 0]
    if nome_contains:
        res = [p for p in res if nome_contains.lower() in p['nome'].lower()]
    if origem:
        res = [p for p in res if origem.lower() in p['origem'].lower()]
    return res

def mostrar_lista_produtos(lista):
    if not lista:
        print("Nenhum produto encontrado.")
        return
    hoje = datetime.today()
    for p in lista:
        dias = dias_para_vencimento(p['validade'], hoje)
        aviso = ""
        if dias < 0: aviso = "[VENCIDO] "
        elif dias <= 7: aviso = "[PRÓXIMO A VENCER] "
        print(f"{aviso}{p['codigo']} - {p['nome']} | Tipo: {p['tipo']} | Peso: {p['peso']}kg | Qtd: {formatar_qtd(p['quantidade'])} | Validade: {formatar_data(p['validade'])} | Origem: {p['origem']} | Entrada: {formatar_data(p['data_entrada'])}")

def visualizar_produtos_interface():
    while True:
        limpar_tela()
        print("=== Visualizar Produtos ===")
        print("1 - Todos")
        print("2 - Por tipo")
        print("3 - Próximos a vencer (<=7 dias)")
        print("4 - Vencidos")
        print("5 - Buscar por nome")
        print("6 - Filtrar por doador/origem")
        print("7 - Voltar (ou V)")
        opc = obter_input("Escolha: ")
        if opc is None or opc == "7": return
        if opc == "1":
            res = filtrar_produtos()
        elif opc == "2":
            t = obter_input("Tipo: ")
            if t is None: continue
            res = filtrar_produtos(tipo=t)
        elif opc == "3":
            res = filtrar_produtos(proximo_vencer=True)
        elif opc == "4":
            res = filtrar_produtos(vencidos=True)
        elif opc == "5":
            s = obter_input("Texto no nome: ")
            if s is None: continue
            res = filtrar_produtos(nome_contains=s)
        elif opc == "6":
            s = obter_input("Nome/identificação do doador: ")
            if s is None: continue
            res = filtrar_produtos(origem=s)
        else:
            input("Opção inválida. Enter...")
            continue
        limpar_tela()
        mostrar_lista_produtos(res)
        input("\nEnter para voltar aos filtros...")

def atualizar_quantidade_produto(usuario):
    if usuarios[usuario]['tipo'] != "Administrador":
        input("Apenas administrador pode atualizar quantidades. Enter para voltar...")
        return
    limpar_tela()
    print("=== Atualizar Quantidade do Produto (Digite V para voltar) ===")
    if not produtos:
        print("Nenhum produto cadastrado.")
        input("Enter para voltar...")
        return
    try:
        codigo = obter_input("Código do produto: ")
        if codigo is None: return
        codigo = int(codigo)
    except:
        input("Código inválido. Enter para voltar...")
        return
    prod = next((p for p in produtos if p['codigo']==codigo), None)
    if not prod:
        input("Produto não encontrado. Enter para voltar...")
        return
    print("Produto encontrado:")
    mostrar_lista_produtos([prod])
    print("\nComo deseja atualizar a quantidade?")
    print("1 - Definir nova quantidade (substituir)")
    print("2 - Adicionar à quantidade atual")
    print("3 - Subtrair da quantidade atual")
    print("4 - Voltar (ou V)")
    opc = obter_input("Escolha: ")
    if opc is None or opc == "4": return
    if opc not in ["1","2","3"]:
        input("Opção inválida. Enter...")
        return
    valor = obter_input("Informe a quantidade (use vírgula para decimais): ")
    if valor is None: return
    try:
        valf = float(valor.replace(",","."))

        if valf < 0:
            input("Quantidade inválida. Enter...")
            return
    except:
        input("Valor inválido. Enter...")
        return
    if opc == "1":
        prod['quantidade'] = valf
    elif opc == "2":
        prod['quantidade'] += valf
    else:
        prod['quantidade'] -= valf
        if prod['quantidade'] < 0:
            prod['quantidade'] = 0
    print("Quantidade atualizada com sucesso.")
    input("Enter para voltar...")

def editar_produto_interface(usuario):
    if usuarios[usuario]['tipo'] != "Administrador":
        input("Apenas administrador pode editar produtos. Enter para voltar...")
        return
    limpar_tela()
    print("=== Editar Produto (Digite V para voltar) ===")
    if not produtos:
        print("Nenhum produto cadastrado.")
        input("Enter para voltar...")
        return
    try:
        codigo = obter_input("Código do produto a editar: ")
        if codigo is None: return
        codigo = int(codigo)
    except:
        input("Código inválido. Enter para voltar...")
        return
    prod = next((p for p in produtos if p['codigo']==codigo), None)
    if not prod:
        input("Produto não encontrado. Enter para voltar...")
        return
    while True:
        limpar_tela()
        print("Produto atual:")
        mostrar_lista_produtos([prod])
        print("\nCampos para editar:")
        print("1 - Nome")
        print("2 - Tipo")
        print("3 - Peso")
        print("4 - Quantidade")
        print("5 - Validade")
        print("6 - Origem")
        print("7 - Data de entrada")
        print("8 - Remover produto")
        print("9 - Voltar (ou V)")
        opc = obter_input("Escolha: ")
        if opc is None or opc == "9": return
        if opc == "1":
            novo = obter_input("Novo nome: ")
            if novo is None: continue
            prod['nome'] = novo
        elif opc == "2":
            tipos_validos = ["alimento","brinquedo","remedio","higiene","outros"]
            novo = obter_input("Novo tipo: ")
            if novo is None: continue
            if novo.lower() in tipos_validos:
                prod['tipo'] = novo.capitalize()
            else:
                input("Tipo inválido. Enter...")
                continue
        elif opc == "3":
            novo = obter_input("Novo peso (use vírgula): ")
            if novo is None: continue
            try:
                pf = float(novo.replace(",","."))

                if pf <= 0:
                    input("Peso inválido. Enter...")
                    continue
                prod['peso'] = pf
            except:
                input("Peso inválido. Enter...")
                continue
        elif opc == "4":
            novo = obter_input("Nova quantidade (use vírgula): ")
            if novo is None: continue
            try:
                qf = float(novo.replace(",","."))

                if qf < 0:
                    input("Quantidade inválida. Enter...")
                    continue
                prod['quantidade'] = qf
            except:
                input("Quantidade inválida. Enter...")
                continue
        elif opc == "5":
            novo = obter_input("Nova validade (ddmmaaaa): ")
            if novo is None: continue
            if validar_data(novo):
                prod['validade'] = novo
            else:
                input("Data inválida. Enter...")
                continue
        elif opc == "6":
            novo = obter_input("Nova origem: ")
            if novo is None: continue
            prod['origem'] = novo
        elif opc == "7":
            novo = obter_input("Nova data de entrada (ddmmaaaa): ")
            if novo is None: continue
            if validar_data(novo):
                prod['data_entrada'] = novo
            else:
                input("Data inválida. Enter...")
                continue
        elif opc == "8":
            conf = obter_input("CONFIRMA REMOVER produto? Digite 'SIM' para confirmar: ", allow_empty=False)
            if conf is None: continue
            if conf.strip().upper() == "SIM":
                produtos.remove(prod)
                print("Produto removido.")
                input("Enter para voltar...")
                return
            else:
                input("Remoção cancelada. Enter...")
        else:
            input("Opção inválida. Enter...")
            continue
        print("Atualização realizada.")
        input("Enter para continuar editando...")

# Solicitações
def criar_solicitacao(usuario):
    cpf_user = usuario
    limpar_tela()
    print("=== Registrar Nova Solicitação (Digite V para voltar) ===")
    if not produtos:
        print("Não há produtos cadastrados.")
        input("Enter para voltar...")
        return
    try:
        codigo = obter_input("Código do produto desejado: ")
        if codigo is None: return
        codigo = int(codigo)
    except:
        input("Digite um número válido. Enter...")
        return
    produto = next((p for p in produtos if p['codigo']==codigo), None)
    if produto is None:
        input("Produto não encontrado. Enter...")
        return
    while True:
        qtd = obter_input(f"Quantidade desejada (disponível {produto['quantidade']}): ")
        if qtd is None: return
        try:
            qtdf = float(qtd.replace(",",".")) 
            if qtdf <= 0 or qtdf > produto['quantidade']:
                print("Quantidade inválida. Deve ser >0 e <= disponível.")
            else:
                break
        except:
            print("Digite um número válido.")
    id_solic = gerar_id_solicitacao()
    solicitacoes.append({
        "id": id_solic,
        "solicitante_cpf": cpf_user,
        "produto_codigo": produto['codigo'],
        "produto_nome": produto['nome'],
        "quantidade": qtdf,
        "status": "Pendente",
        "data": datetime.today().strftime("%d%m%Y"),
        "usuario_pediu": cpf_user
    })
    print("Solicitação criada com sucesso! ID:", id_solic)
    input("Enter para voltar...")

def aprovar_reprovar_solicitacoes(usuario):
    if usuarios[usuario]['tipo'] != "Administrador":
        input("Apenas administrador pode aprovar/reprovar. Enter para voltar...")
        return
    while True:
        limpar_tela()
        pendentes = [s for s in solicitacoes if s['status']=="Pendente"]
        print("=== Aprovar / Reprovar Solicitações (Digite V para voltar) ===")
        if not pendentes:
            print("Nenhuma solicitação pendente.")
            input("Enter para voltar...")
            return
        for s in pendentes:
            print(f"ID {s['id']} | Produto: {s['produto_nome']} | Qt: {formatar_qtd(s['quantidade'])} | Solicitante: {s['solicitante_cpf']} | Data: {formatar_data(s['data'])}")
        id_s = obter_input("ID da solicitação a processar (V para voltar): ")
        if id_s is None: return
        try:
            id_s = int(id_s)
        except:
            input("ID inválido. Enter...")
            continue
        sol = next((s for s in solicitacoes if s['id']==id_s), None)
        if sol is None:
            input("Solicitação não encontrada. Enter...")
            continue
        print("1 - Aprovar")
        print("2 - Reprovar")
        print("3 - Voltar")
        opc = obter_input("Escolha: ")
        if opc is None or opc == "3": return
        if opc == "1":
            prod = next((p for p in produtos if p['codigo']==sol['produto_codigo']), None)
            if not prod:
                input("Produto não encontrado. Não é possível aprovar. Enter...")
                continue
            if sol['quantidade'] > prod['quantidade']:
                input("Quantidade solicitada maior que disponível. Não é possível aprovar. Enter...")
                continue
            prod['quantidade'] -= sol['quantidade']
            sol['status'] = "Aprovado"
            print("Solicitação aprovada e estoque atualizado.")
            input("Enter...")
        elif opc == "2":
            sol['status'] = "Reprovado"
            print("Solicitação reprovada.")
            input("Enter...")
        else:
            input("Opção inválida. Enter...")

def historico_solicitacoes(usuario):
    limpar_tela()
    print("=== Histórico de Solicitações ===")
    tipo_user = usuarios[usuario]['tipo']
    if tipo_user == "Administrador":
        lista = solicitacoes
    else:
        lista = [s for s in solicitacoes if s['solicitante_cpf']==usuario]
    if not lista:
        print("Nenhuma solicitação encontrada.")
        input("Enter para voltar...")
        return
    for s in lista:
        print(f"ID {s['id']} | Produto: {s['produto_nome']} | Qt: {formatar_qtd(s['quantidade'])} | Status: {s['status']} | Data: {formatar_data(s['data'])} | Solicitante: {s['solicitante_cpf']}")
    input("\nEnter para voltar...")

# Relatórios
def relatorio_entrada_saida():
    limpar_tela()
    print("=== Relatório de Entrada ===")
    for p in produtos:
        print(f"{p['codigo']} - {p['nome']} | Qt atual: {formatar_qtd(p['quantidade'])} | Entrada: {formatar_data(p['data_entrada'])}")
    print("\n=== Relatório de Saídas (Solicitações aprovadas) ===")
    for s in [x for x in solicitacoes if x['status']=="Aprovado"]:
        print(f"{s['id']} - {s['produto_nome']} | Qt: {formatar_qtd(s['quantidade'])} | Solicitante: {s['solicitante_cpf']} | Data: {formatar_data(s['data'])}")
    input("\nEnter para voltar...")

def relatorio_produtos_mais_solicitados():
    limpar_tela()
    print("=== Produtos Mais Solicitados ===")
    contagem = {}
    for s in solicitacoes:
        contagem[s['produto_nome']] = contagem.get(s['produto_nome'],0) + s['quantidade']
    if not contagem:
        print("Nenhuma solicitação registrada.")
    else:
        for nome, qtd in sorted(contagem.items(), key=lambda x: x[1], reverse=True):
            print(f"{nome} - Total solicitado: {formatar_qtd(qtd)}")
    input("\nEnter para voltar...")

def relatorio_doacoes_por_doador():
    limpar_tela()
    print("=== Doações por Doador ===")
    doadores = {}
    for p in produtos:
        doadores[p['origem']] = doadores.get(p['origem'],0) + p['quantidade']
    if not doadores:
        print("Nenhuma doação registrada.")
    else:
        for nome, qtd in doadores.items():
            print(f"{nome} - Total doado (estoque atual agregado): {formatar_qtd(qtd)}")
    input("\nEnter para voltar...")

# Menus
def menu_cadastrar(usuario):
    while True:
        limpar_tela()
        print("=== CADASTRAR ===")
        print("1 - Cadastrar produto")
        print("2 - Cadastrar doador/solicitante")
        print("3 - Cadastrar voluntário")
        print("4 - Voltar (ou V)")
        opc = obter_input("Escolha: ")
        if opc is None or opc == "4": return
        if opc == "1":
            cadastrar_produto(usuario)
        elif opc == "2":
            cadastrar_pessoa_tipo(usuario, forcar_tipo="Doador")
        elif opc == "3":
            cadastrar_pessoa_tipo(usuario, forcar_tipo="Voluntario")
        else:
            input("Opção inválida. Enter...")

def menu_controle_estoque(usuario):
    while True:
        limpar_tela()
        print("=== CONTROLE DE ESTOQUE ===")
        print("1 - Visualizar produtos")
        print("2 - Atualizar quantidades")
        print("3 - Editar produto")
        print("4 - Alertas de validade (próximos/vencidos)")
        print("5 - Voltar (ou V)")
        opc = obter_input("Escolha: ")
        if opc is None or opc == "5": return
        if opc == "1":
            visualizar_produtos_interface()
        elif opc == "2":
            atualizar_quantidade_produto(usuario)
        elif opc == "3":
            editar_produto_interface(usuario)
        elif opc == "4":
            limpar_tela()
            print("=== Alertas de Validade ===")
            proximos = filtrar_produtos(proximo_vencer=True)
            vencidos = filtrar_produtos(vencidos=True)
            print("\n-- Próximos a vencer (<=7 dias) --")
            mostrar_lista_produtos(proximos)
            print("\n-- Vencidos --")
            mostrar_lista_produtos(vencidos)
            input("\nEnter para voltar...")
        else:
            input("Opção inválida. Enter...")

def menu_solicitacoes(usuario):
    while True:
        limpar_tela()
        print("=== SOLICITAÇÕES ===")
        print("1 - Registrar nova solicitação")
        print("2 - Aprovar/Reprovar solicitações (admin)")
        print("3 - Histórico de solicitações")
        print("4 - Voltar (ou V)")
        opc = obter_input("Escolha: ")
        if opc is None or opc == "4": return
        if opc == "1":
            criar_solicitacao(usuario)
        elif opc == "2":
            aprovar_reprovar_solicitacoes(usuario)
        elif opc == "3":
            historico_solicitacoes(usuario)
        else:
            input("Opção inválida. Enter...")

def menu_relatorios(usuario):
    if usuarios[usuario]['tipo'] != "Administrador":
        input("Apenas administrador pode acessar relatórios. Enter para voltar...")
        return
    while True:
        limpar_tela()
        print("=== RELATÓRIOS ===")
        print("1 - Relatório de entrada e saída")
        print("2 - Produtos mais solicitados")
        print("3 - Doações por doador")
        print("4 - Voltar (ou V)")
        opc = obter_input("Escolha: ")
        if opc is None or opc == "4": return
        if opc == "1":
            relatorio_entrada_saida()
        elif opc == "2":
            relatorio_produtos_mais_solicitados()
        elif opc == "3":
            relatorio_doacoes_por_doador()
        else:
            input("Opção inválida. Enter...")

def menu_principal(usuario):
    while True:
        limpar_tela()
        tipo_user = usuarios[usuario]['tipo']
        print(f"=== TELA INICIAL - Usuário: {usuario} ({tipo_user}) ===")
        print("1 - Cadastrar")
        print("2 - Controle de Estoque")
        print("3 - Solicitações")
        print("4 - Relatórios")
        print("5 - Voltar para Login")
        opc = obter_input("Escolha: ")
        if opc is None:
            continue
        if opc == "1":
            menu_cadastrar(usuario)
        elif opc == "2":
            menu_controle_estoque(usuario)
        elif opc == "3":
            menu_solicitacoes(usuario)
        elif opc == "4":
            menu_relatorios(usuario)
        elif opc == "5":
            print("Retornando para tela de login...")
            return
        else:
            input("Opção inválida. Enter...")

# Execução
if __name__ == "__main__":
    while True:
        usuario_logado = tela_login()
        menu_principal(usuario_logado)

