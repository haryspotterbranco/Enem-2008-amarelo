from PIL import Image
import os

def converter_cor_gimp_para_rgb(gimp_r, gimp_g, gimp_b):
    """
    Converte valores do GIMP (0-100) para RGB (0-255)
    """
    r = int((gimp_r / 100) * 255)
    g = int((gimp_g / 100) * 255)
    b = int((gimp_b / 100) * 255)
    return (r, g, b)

def encontrar_faixa_cinza(imagem, cor_alvo, tolerancia=15):
    """
    Encontra posições de corte baseadas em uma faixa cinza de altura entre 34 e 40 pixels (37 +/- 3),
    analisando a faixa horizontal dos pixels 110 a 120 de largura.
    Retorna uma lista de tuplas contendo: (posicao_corte, proximo_inicio_da_imagem)
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    # 1. Identifica quais linhas (y) atendem ao critério de cor nas colunas de 110 a 120
    linhas_com_padrao = []
    for y in range(altura):
        linha_valida = True
        for x in range(110, 121):  # Percorre as colunas de 110 a 120 inclusive
            if x >= largura:
                linha_valida = False
                break
            
            pixel = pixels[x, y]
            if len(pixel) == 4:  # Se for imagem contendo canal Alpha (RGBA)
                r, g, b, a = pixel
            else:  # RGB padrão
                r, g, b = pixel[:3]
            
            # Verifica se a cor do pixel está fora da tolerância estipulada
            if (abs(r - cor_alvo[0]) > tolerancia or 
                abs(g - cor_alvo[1]) > tolerancia or 
                abs(b - cor_alvo[2]) > tolerancia):
                linha_valida = False
                break
        
        if linha_valida:
            linhas_com_padrao.append(y)
            
    posicoes_corte = []
    if not linhas_com_padrao:
        return posicoes_corte
        
    # 2. Agrupa as linhas consecutivas encontradas para medir a altura real da faixa cinza
    inicio_bloco = linhas_com_padrao[0]
    fim_bloco = linhas_com_padrao[0]
    
    for y in linhas_com_padrao[1:]:
        if y == fim_bloco + 1:
            fim_bloco = y
        else:
            altura_bloco = fim_bloco - inicio_bloco + 1
            # Altura ideal: 37 pixels. Margem de erro aplicada: +/- 3 pixels (34 a 40)
            if 34 <= altura_bloco <= 40:
                pos_corte = inicio_bloco - 5  # Corta 5 pixels antes do padrão iniciar
                if pos_corte < 0:
                    pos_corte = 0
                proximo_inicio = fim_bloco + 1  # Próxima questão começa logo após a faixa terminar
                posicoes_corte.append((pos_corte, proximo_inicio))
                print(f"Faixa cinza detectada: y={inicio_bloco} até y={fim_bloco} (Altura={altura_bloco}px). Cortando em y={pos_corte}")
            
            inicio_bloco = y
            fim_bloco = y
            
    # Verifica e processa o último bloco pendente do loop
    altura_bloco = fim_bloco - inicio_bloco + 1
    if 34 <= altura_bloco <= 40:
        pos_corte = inicio_bloco - 5
        if pos_corte < 0:
            pos_corte = 0
        proximo_inicio = fim_bloco + 1
        posicoes_corte.append((pos_corte, proximo_inicio))
        print(f"Faixa cinza detectada: y={inicio_bloco} até y={fim_bloco} (Altura={altura_bloco}px). Cortando em y={pos_corte}")
        
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem verticalmente utilizando as coordenadas dinâmicas detectadas
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Busca os pontos exatos de corte baseados no novo padrão cinza
    posicoes_corte = encontrar_faixa_cinza(imagem, cor_alvo)
    
    if not posicoes_corte:
        print("Nenhuma faixa cinza dentro dos padrões foi encontrada na imagem!")
        return
    
    print(f"Encontradas {len(posicoes_corte)} faixas cinzas para realizar o corte.")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, (pos_corte, proximo_inicio) in enumerate(posicoes_corte):
        if pos_corte <= posicao_anterior:
            continue
            
        # Realiza o recorte da questão (do ponto final da última até 5 pixels antes da faixa atual)
        area_corte = (0, posicao_anterior, largura, pos_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # O início do próximo bloco pula de forma limpa para o final da faixa cinza real detectada
        posicao_anterior = proximo_inicio
    
    # Recorta o trecho final (o espaço após a última faixa cinza detectada)
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    # ATUALIZE as linhas abaixo de acordo com seus arquivos (OBS7)
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Substitua pelo nome ou caminho da imagem da prova
    pasta_saida = "divididas"           # Substitua pelo nome da pasta onde salvar as questões

    # Configuração direta baseada no padrão RGB informado (204, 204, 204)
    cor_do_padrao = (204, 204, 204)
    print(f"Cor configurada para busca: RGB {cor_do_padrao}")
    
    # Execução da automação
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    print("Divisão concluída com sucesso!")