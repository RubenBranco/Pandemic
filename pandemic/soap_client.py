import zeep
import uuid

def client_menu():
    cont = True
    while cont:
        print("# ===========PANDEMIC CLI=========== #")
        print("# [1] Info Jogo                  #")
        print("# [2] Faz Jogada                 #")
        print("# [3] Sair                       #")
        print("# ================================== #")
        response = input(" >> ")
        if response == "3":
            cont = False
            print("Saindo ...")
        elif response == "1":
            print("# ===========PANDEMIC CLI=========== #")
            print("# Insira o ID do jogo                #")
            print("# Ou escreva voltar para retroceder  #")
            print("# ================================== #")
            uuid = input(" >> ")
            if uuid != "voltar":
                print("# Resultado: {} #".format(InfoJogoServiceClient(uuid)))
        elif response == "2":
            print("# ===========PANDEMIC CLI=========== #")
            print("# Insira o ID do jogo                #")
            print("# Ou escreve voltar para retroceder  #")
            uuid = input(" >> ")
            if uuid != "voltar":
                print("# Insira o username do utilizador    #")
                username = input(" >> ")
                print("# Insira a password do utilizador    #")
                password = input(" >> ")
                print("# Insira a jogada que pretende fazer #")
                jogada = input(" >> ")
                print("# Insira o nome da cidade            #")
                cidade = input(" >> ")
                print("# Insira a cor da doença (Black, Yellow, Red ou Blue) #")
                doenca = input(" >> ")
                print("# ================================== #")
                print("# Resultado: {}".format(FazJogadaServiceClient(uuid, username, password, jogada, cidade, doenca)))

def recursive_dict(element):
    """
    Source: http://lxml.de/FAQ.html#how-can-i-map-an-xml-tree-into-a-dict-of-dicts
    """
    return element.tag, \
        dict(map(recursive_dict, element)) or element.text

def reconstruct_from_dict(dictionaries):
    dictionary = {}
    dictionaries = list(map(lambda x: recursive_dict(x), dictionaries))
    for tup in dictionaries:
        key = tup[0]
        value = tup[1]
        
        if key == "research_centers":
            value = [k.replace('_', ' ') for k in value]
        elif key == 'players':
            new_value = {}
            for player in value:
                player_value = {}
                player_value['position'] = value[player]['position'].replace('_',' ')
                player_value['neighbour_cities'] = [k.replace('_', ' ') for k in value[player]['neighbour_cities']]
            value = new_value
        else:
            new_value = {}
            for k in value:
                new_value[k.replace('_', ' ')] = {}
                for _k in value[k]:
                    new_value[k.replace('_', ' ')][_k.replace('_', ' ')] = value[k][_k]
            value = new_value
        dictionary[key] = value
        
    return dictionary

def InfoJogoServiceClient(id):
    wsdl = 'http://138.68.161.206/soap/info_jogo/'
    client = zeep.Client(wsdl=wsdl)
    res = client.service.info_jogo(id)
    return reconstruct_from_dict(res)

def FazJogadaServiceClient(id, username, password, jogada, cidade):
    wsdl = 'http://138.68.161.206/soap/faz_jogada/'
    client = zeep.Client(wsdl=wsdl)
    res = client.service.faz_jogada(id, username, password, jogada, cidade)
    return res

if __name__ == "__main__":
    client_menu()
