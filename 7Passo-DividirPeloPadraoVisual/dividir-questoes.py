"""
Propósito: Dividir as questões por padrão de linhas divisórias (Preto/Cinza) do ENEM 2008.
Autor: Adaptado para ENEM 2008
"""

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

def encontrar_linha_divisoria(imagem, cor_alvo, tolerancia=30, altura_faixa=2):
    """
    Encontra posições onde há uma linha horizontal escura indicando separação ou início
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Percorre a imagem de cima para baixo
    y = 0
    while y < altura - altura_faixa:
        faixa_encontrada = True
        
        for dy in range(altura_faixa):
            # Analisa o penúltimo pixel da direita (conforme OBS2 original)
            # Dica: Se a linha divisória não tocar a borda, mude 'largura-2' para o meio 'largura // 2'
            pixel = pixels[largura - 2, y + dy]
            
            if len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
            else:  # RGB
                r, g, b = pixel[:3]
            
            # Verifica se o pixel é escuro o suficiente (próximo do preto da linha/texto)
            if (abs(r - cor_alvo[0]) > tolerancia or 
                abs(g - cor_alvo[1]) > tolerancia or 
                abs(b - cor_alvo[2]) > tolerancia):
                faixa_encontrada = False
                break
        
        if faixa_encontrada:
            # Ponto de corte ajustado para não cortar o topo do enunciado (15 pixels acima)
            posicao_corte = y - 22
            if posicao_corte < 0:
                posicao_corte = 0
                
            posicoes_corte.append(posicao_corte)
            print(f"Linha de corte encontrada em y={y}, recortando em y={posicao_corte}")
            y += altura_faixa + 20  # Pula a região para evitar múltiplas detecções próximas
        else:
            y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem verticalmente com base nos pontos de corte mapeados
    """
    if not os.path.exists(caminho_imagem):
        print(f"Erro: O arquivo '{caminho_imagem}' não foi encontrado!")
        return

    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada com sucesso: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_linha_divisoria(imagem, cor_alvo)
    
    if not posicoes_corte:
        print("Nenhum padrão visual de divisão foi encontrado. Verifique a cor alvo ou a coluna X analisada.")
        return
    
    print(f"Encontradas {len(posicoes_corte)} demarcações para separação.")
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"questao_{i+1:02d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo com sucesso: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte
    
    # Seção final da última questão até o rodapé
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"questao_{len(posicoes_corte)+1:02d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo seção final: {caminho_completo}")

if __name__ == "__main__":
    # --- CONFIGURAÇÃO PARA COLUNAS CONCATENADAS ---
    caminho_imagem = "colunas_concatenadas_verticalmente.png"
    pasta_saida = "questoes_colunas"

    # --- DESCOMENTE ABAIXO QUANDO FOR PROCESSAR PÁGINAS INTEIRAS ---
    # caminho_imagem = "./inteiras/pagina_enem_15.png"
    # pasta_saida = "pagina_15"
    
    # No ENEM 2008, buscamos as linhas pretas/escuras de divisão (RGB próximo a 0, 0, 0)
    # Valores de exemplo coletados via GIMP (0 a 100%): R: 5.0%, G: 5.0%, B: 5.0%
    cor_do_padrao = converter_cor_gimp_para_rgb(5.0, 5.0, 5.0)
    print(f"Analisando matriz de pixels baseada na cor: RGB {cor_do_padrao}")
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    print("Processamento concluído com sucesso!")
