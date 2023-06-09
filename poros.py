from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from tensorflow.keras.preprocessing.sequence import pad_sequences

campeones = "Aatrox, Ahri, Akali, Akshan, Alistar, Amumu, Anivia, Annie, Aphelios, Ashe, Aurelion Sol, Azir, Bard, Bel'Veth, Blitzcrank, Brand, Braum, Caitlyn, Camille, Cassiopeia, Cho'Gath, Corki, Darius, Diana, Draven, Dr. Mundo, Ekko, Elise, Evelynn, Ezreal, Fiddlesticks, Fiora, Fizz, Galio, Gangplank, Garen, Gnar, Gragas, Graves, Gwen, Hecarim, Heimerdinger, Illaoi, Irelia, Ivern, Janna, Jarvan IV, Jax, Jayce, Jhin, Jinx, Kaisa, Kalista, Karma, Karthus, Kassadin, Katarina, Kayle, Kayn, Kennen, Kha'Zix, Kindred, Kled, Kog'Maw, K'Sante, LeBlanc, Lee Sin, Leona, Lillia, Lissandra, Lucian, Lulu, Lux, Malphite, Malzahar, Maokai, Master Yi, Milo, Miss Fortune, Mordekaiser, Morgana, Nami, Nasus, Nautilus, Neeko, Nidalee, Nilah, Nocturne, Nunu y Willump, Olaf, Orianna, Ornn, Pantheon, Poppy, Pyke, Qiyana, Quinn, Rakan, Rammus, Rek'Sai, Renata Glasc, Rell, Renekton, Rengar, Riven, Rumble, Ryze, Samira, Sejuani, Senna, Seraphine, Sett, Shaco, Shen, Shyvana, Singed, Sion, Sivir, Skarner, Sona, Soraka, Swain, Sylas, Syndra, Tahm Kench, Taliyah, Talon, Taric, Teemo, Thresh, Tristana, Trundle, Tryndamere, Twisted Fate, Twitch, Udyr, Urgot, Varus, Vayne, Veigar, Vel'Koz, Vex, Vi, Viego, Viktor, Vladimir, Volibear, Warwick, Wukong, Xayah, Xerath, Xin Zhao, Yasuo, Yone, Yorick, Yuumi, Zac, Zed, Zeri, Ziggs, Zilean, Zoe, Zyra"

def scrapping(urls, web_d_rute):
    df_acumulativo = pd.DataFrame()
    driver = webdriver.Edge(r'C:\\d_edge\\msedgedriver.exe')
    for j, url_og in enumerate(urls, start=1):
        for i in range(1, 11):
            url_participant = url_og + '#participant' + str(i)        
            driver.get(url_participant)
            # Obtener los elementos de las pestañas dentro del bucle
            pestañas = driver.find_elements(By.CSS_SELECTOR, "div.tab.firstLevelTab")
            if i <= len(pestañas):
                # Simular clic en la pestaña para actualizar la información
                pestaña = pestañas[i - 1]
                driver.execute_script("arguments[0].click();", pestaña)

                elements = driver.find_elements(By.CSS_SELECTOR, "div.tab.firstLevelTab.active img[title]")
                campeones = [element.get_attribute("title") for element in elements]
                frases = []
                elementos = driver.find_elements(By.CSS_SELECTOR, "div.box.tags-box div.tag.requireTooltip")
                for element in elementos:
                    frase = element.text.strip()
                    frases.append(frase)

                frases = [frase for frase in frases if frase.strip() != '']
                frases_combinadas = ', '.join(frases)

                try:
                    driver.find_element(By.CSS_SELECTOR, "th.text-left.no-padding-right span.victory")
                    if i < 6:
                        resultado = 1
                    else:
                        resultado = 0

                except NoSuchElementException:
                    try:
                        driver.find_element(By.CSS_SELECTOR, "th.text-left.no-padding-right span.defeat")
                        if i < 6:
                            resultado = 0
                        else:
                            resultado = 1
                    except NoSuchElementException:
                        resultado = None  # No se encontró ni "Victoria" ni "Derrota"


                game_id = url_participant.split('/')[-1]

                data = {
                    'game_id': [game_id],
                    'campeon': campeones,
                    'frases': [frases_combinadas],
                    'resultado': [resultado]
                }
                df = pd.DataFrame(data)
                df_acumulativo = df_acumulativo.append(df, ignore_index=True)

            else:
                print(f"No se encontró la pestaña para participant{i}")


    driver.quit()
    return df_acumulativo

def clean(data):

    df = data.copy()

    nombres_campeones = campeones.split(',')
    # Paso 2: Definir la palabra en común para reemplazar los nombres de campeones
    palabra_comun = ' CAMPEON'
    
    # Paso 4: Reemplazar los nombres de campeones en la columna "frases"
    for nombre_campeon in nombres_campeones:
        df['frases'] = df['frases'].str.replace(nombre_campeon, palabra_comun)
    
    return df

def new(text_input, model, max_seq_length, tokenizer):
    df = pd.DataFrame({'frases': [text_input]})
    df = clean(df)
    new_x = tokenizer.texts_to_sequences(df['frases'])
    new_x = pad_sequences(new_x, maxlen = max_seq_length, padding = 'post') 
    predict = model.predict(new_x)
    return new_x, predict
