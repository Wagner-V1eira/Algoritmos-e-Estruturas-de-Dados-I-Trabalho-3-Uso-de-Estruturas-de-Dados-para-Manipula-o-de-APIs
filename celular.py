import requests
import matplotlib.pyplot as plt
import numpy as np
import pwinput 

url = "http://localhost:3000/celular"
url_login = "http://localhost:3000/login"
url_usuario = "http://localhost:3000/usuarios"
url_celular = "http://localhost:3000/celular"

usuario = ""
usuario_id = ""
token = ""


def login():
    titulo("Login do Usuário")

    email = input("E-mail...: ")
    senha = pwinput.pwinput(prompt='Senha....: ')

    response = requests.post(url_login, json={
        "email": email,
        "senha": senha
    })

    if response.status_code == 200:
        resposta = response.json()
        global usuario
        global usuario_id
        global token
        usuario = resposta['nome']
        usuario_id = resposta['id']
        token = resposta['token']
        print(f"Ok! Bem-vindo {usuario}")
    else:
        print("Erro... Não foi possível realizar login no sistema.")


def inclusao():
    titulo("Inclusão de Celulares", "=")

    if token == "":
        print("Erro... Você precisa fazer login para incluir celulares!")
        return

    marca = input("Marca.......: ")
    modelo = input("Modelo......: ")
    memoriaRam = int(input("Memória Ram: "))
    armazenamento = int(input("Memória Int....: "))
    preco = float(input("Preço R$....: "))

    response = requests.post(url,
                             headers={"Authorization": f"Bearer {token}"},
                             json={
                                    "marca": marca,
                                    "modelo": modelo,
                                    "memoriaRam": memoriaRam,
                                    "armazenamento": armazenamento,
                                    "preco": preco,
                                    "usuarioId": usuario_id
                             })

    if response.status_code == 201:
        celular = response.json()
        print(f"Ok! Celular cadastrado com código: {celular['id']}")
    else:
        print("Erro... Não foi possível incluir o celular")


def listagem():
    titulo("Listagem dos Celulares Cadastrados.")

    response = requests.get(url)

    if response.status_code != 200:
        print("Erro... Não foi possível acessar a API")
        return

    celular = response.json()

    print("Cód. Marca.....: Modelo.........: Memória Ram: Memória Int.:  Preço R$:")
    print("----------------------------------------------------------------------------")

    for celular in celular:
        print(f"{celular['id']:3} {celular['marca']:10} {celular['modelo']:15} {celular['memoriaRam']:12} {celular['armazenamento']:13}    {float(celular['preco']):9.2f}")


def alteracao():
    listagem()

    if token == "":
        print("Erro... Você precisa fazer login para alterar os dados de um celular!")
        return
    usuario_id = int(input("Código do Usuário: "))
    celular_id = int(input("Código do Celular: "))
    marca = input("Marca: ")
    modelo = input("Modelo: ")
    memoriaRam = int(input("Memória Ram....: "))
    armazenamento = int(input("Memória Int....: "))
    preco = float(input("Preço R$....: "))
    response = requests.put(f"{url}/{celular_id}", headers = {"Authorization": f"Bearer {token}"}, json = {
        "marca": marca,
        "modelo": modelo,
        "memoriaRam": memoriaRam,
        "armazenamento": armazenamento,
        "preco": preco,
        "usuarioId": usuario_id
    })
    if response.status_code == 200:
        print("Ok! Dados do celular alterados com sucesso!")
    else:
        print("Erro... Não foi possível alterar os dados do celular")
    
def exclusao():
    if token == "":
        print("Erro... Você precisa fazer login para excluir um celular")
        return

    listagem()

    id = int(input("\nQual código do celular você deseja excluir (0: sair)? "))

    if id == 0:
        return

    response = requests.get(url)
    celular = response.json()

    celular = [x for x in celular if x['id'] == id]

    if len(celular) == 0:
        print("Erro... Informe um código existente")
        return

    print(f"\nMarca.......: {celular[0]['marca']}")
    print(f"Modelo.......: {celular[0]['modelo']}")
    print(f"Memória Ram.: {celular[0]['memoriaRam']}")
    print(f"Memória Int..: {celular[0]['armazenamento']}")
    print(f"Preço R$....: {float(celular[0]['preco']):9.2f}")
    
    confirma = input("Confirma a exclusão (S/N)? ").upper()

    if confirma == "S":
        response = requests.delete(f"{url}/{id}", headers={"Authorization": f"Bearer {token}"})

        if response.status_code == 200:
            celular = response.json()
            print("Ok! Celular excluído com sucesso!")
        else:
            print("Erro... Não foi possível excluir este celular")


def grafico_Grouped_bar_chart():
    try:
        response_usuarios = requests.get(f"{url_usuario}", headers={"Authorization": f"Bearer {token}"})
        response_usuarios.raise_for_status()
        usuarios = response_usuarios.json()

        response_celulares = requests.get(f"{url_celular}", headers={"Authorization": f"Bearer {token}"})
        response_celulares.raise_for_status()
        celulares = response_celulares.json()

        contagem_celulares = {}
        for celular in celulares:
            usuario_id = celular['usuarioId']
            marca = celular['marca']
            if usuario_id not in contagem_celulares:
                contagem_celulares[usuario_id] = {}
            if marca not in contagem_celulares[usuario_id]:
                contagem_celulares[usuario_id][marca] = 0
            contagem_celulares[usuario_id][marca] += 1

        usuarios_labels = [usuario['nome'] for usuario in usuarios if usuario['id'] in contagem_celulares]

        marcas = list(set(marca for usuario_celulares in contagem_celulares.values() for marca in usuario_celulares))

        dados_grafico = {marca: [] for marca in marcas}
        for usuario_id in contagem_celulares:
            for marca in marcas:
                dados_grafico[marca].append(contagem_celulares[usuario_id].get(marca, 0))

        x = np.arange(len(usuarios_labels))  
        width = 0.8 / len(marcas)  
        multiplier = 0

        fig, ax = plt.subplots(layout='constrained')

        for marca, contagem in dados_grafico.items():
            offset = width * multiplier
            rects = ax.bar(x + offset, contagem, width, label=marca)
            ax.bar_label(rects, padding=3)
            multiplier += 1

        ax.set_ylabel('Quantidade de Celulares')
        ax.set_title('Quantidade de Celulares por Usuário e Marca')
        ax.set_xticks(x + width * (len(marcas) - 1) / 2)
        ax.set_xticklabels(usuarios_labels)
        ax.legend(loc='upper left', ncols=len(marcas))
        ax.set_ylim(0, max(max(contagem) for contagem in dados_grafico.values()) + 1)

        plt.show()

    except requests.exceptions.RequestException as e:
        print("Erro na requisição à API:", e)
    except Exception as e:
        print("Erro ao gerar o gráfico:", e)

def grafico2():
    try:
        response_celulares = requests.get(f"{url_celular}", headers={"Authorization": f"Bearer {token}"})
        response_celulares.raise_for_status()
        celulares = response_celulares.json()

        contagem_marcas = {}
        for celular in celulares:
            marca = celular['marca']
            contagem_marcas[marca] = contagem_marcas.get(marca, 0) + 1

        marcas = list(contagem_marcas.keys())
        quantidades = list(contagem_marcas.values())

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(aspect="equal"))

        def func(pct, allvals):
            absolute = int(np.round(pct / 100. * np.sum(allvals)))
            return f"{pct:.1f}%\n({absolute} unidades)"

        wedges, texts, autotexts = ax.pie(
            quantidades,
            autopct=lambda pct: func(pct, quantidades),
            textprops=dict(color="w"),
            startangle=90
        )

        ax.legend(
            wedges, marcas,
            title="Marcas",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1)
        )

        plt.setp(autotexts, size=8, weight="bold")
        ax.set_title("Distribuição de Celulares por Marca")

        plt.show()

    except requests.exceptions.RequestException as e:
        print("Erro na requisição à API:", e)
    except Exception as e:
        print("Erro ao gerar o gráfico:", e)

def titulo(texto, traco="-"):
    print()
    print(texto)
    print(traco*40)

while True:
    titulo("Cadastro de Celulares")
    print("1. Login do Usuário")
    print("2. Inclusão de Celulares")
    print("3. Listagem de Celulares")
    print("4. Alteração de Celulares")
    print("5. Exclusão de Celulares")
    print("6. Gráfico de Marcas (Colunas Agrupadas)")
    print("7. Gráfico de Marcas (Pizza com Porcentagem)")
    print("8. Finalizar")
    opcao = int(input("Opção: "))
    if opcao == 1:
        login()
    elif opcao == 2:
        inclusao()
    elif opcao == 3:
        listagem()
    elif opcao == 4:
        alteracao()
    elif opcao == 5:
        exclusao()
    elif opcao == 6:
        grafico_Grouped_bar_chart()
    elif opcao == 7:
        grafico2()

    else:
        break
