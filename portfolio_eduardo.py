import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import base64
import os
from PIL import Image
import laspy
from stl import mesh
import fitz  # PyMuPDF

st.set_page_config(
    page_title="Eduardo's Portfolio",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS da página
st.markdown("""
    <style>
    /* 1. ESCONDER A FAIXA PRETA DO TOPO DO STREAMLIT */
    [data-testid="stHeader"] {
        display: none !important;
    }
    
    /* 2. FUNDO GERAL DA PÁGINA (AZUL MARINHO MUITO ESCURO) */
    .stApp {
        background-color: #0f172a !important; 
        color: #f8fafc !important; 
    }
    
    /* 3. HEADER AZUL (Hero Section) */
    .hero-section {
        background-color: #1e3a8a;
        padding: 3rem 2rem;
        border-radius: 0 0 20px 20px;
        color: white;
        margin-top: -3rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    .hero-section h1, .hero-section h3, .hero-section p {
        color: white !important;
    }
    
    /* 4. ESTILO DOS CARDS (Azul Ardósia Escuro) */
    .custom-card {
        background-color: #1e293b !important;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 1rem;
        transition: transform 0.2s, box-shadow 0.2s;
        color: #f8fafc;
    }
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0,0,0,0.5);
    }
    
    /* Card que recebe botão do Streamlit por baixo */
    .custom-card-com-botao {
        background-color: #1e293b !important;
        border-radius: 15px;
        padding: 15px 15px 52px 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 0px;
        color: #f8fafc;
        transition: transform 0.2s, box-shadow 0.2s;
    }

    /* Sobe APENAS o card e o botão da coluna onde o mouse está */
    div[data-testid="stColumn"]:has(.custom-card-com-botao:hover) .custom-card-com-botao,
    div[data-testid="stColumn"]:has(div.stButton:hover) .custom-card-com-botao {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0,0,0,0.5);
    }

    div[data-testid="stColumn"]:has(.custom-card-com-botao:hover) div.stButton,
    div[data-testid="stColumn"]:has(div.stButton:hover) div.stButton {
        transform: translateY(-5px);
    }

    /* 5. CORES DAS ABAS PARA LIGAR COM O MODO ESCURO */
    div[data-baseweb="tab-list"] {
        background-color: transparent;
        justify-content: center;
        gap: 2rem;
    }
    div[data-baseweb="tab"] {
        font-size: 1.1rem;
        font-weight: 600;
        color: #64748b !important;
    }
    div[data-baseweb="tab"][aria-selected="true"] {
        color: #38bdf8 !important;
    }

    /* 6. BOTÃO "VER DETALHES" IDÊNTICO AO ORIGINAL E DENTRO DO CARD */
    div.stButton {
        margin-top: -46px !important;
        margin-left: 15px !important;
        margin-bottom: 25px !important;
        position: relative;
        z-index: 10;
        transition: transform 0.2s;
    }
    div.stButton > button {
        background-color: #f1f5f9 !important;
        color: #3b82f6 !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 5px 10px !important;
        font-size: 0.8rem !important;
        font-weight: 400 !important;
        min-height: 0px !important;
        height: auto !important;
        width: auto !important;
        line-height: 1.2 !important;
        box-shadow: none !important;
    }
    div.stButton > button:hover {
        background-color: #e2e8f0 !important;
        color: #2563eb !important;
    }
    div.stButton > button p {
        font-size: 0.8rem !important;
        color: #3b82f6 !important;
        margin: 0 !important;
    }

    /* 7. ESTILO DO MODAL POP-UP (Mantém só a barra interna do PDF) */
    div[data-testid="stDialog"] div[role="dialog"] {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border-radius: 15px !important;
        border: 1px solid #334155 !important;
        width: 90vw !important;
        max-width: 1000px !important;
        overflow: hidden !important;
    }
    div[data-testid="stDialog"] [data-testid="stDialogBody"] {
        overflow: hidden !important;
        padding-bottom: 0.5rem !important;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def gerar_preview_pdf(caminho_pdf):
    if os.path.exists(caminho_pdf):
        try:
            doc = fitz.open(caminho_pdf)
            pagina = doc.load_page(0)
            pix = pagina.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            img_b64 = base64.b64encode(pix.tobytes("png")).decode("utf-8")
            doc.close()
            return f"data:image/png;base64,{img_b64}"
        except Exception:
            pass
    return "https://placehold.co/400x250/1e3a8a/ffffff?text=Projeto"

@st.cache_data
def carregar_imagem_fundo(caminho_imagem):
    if os.path.exists(caminho_imagem):
        try:
            with open(caminho_imagem, "rb") as img_file:
                img_b64 = base64.b64encode(img_file.read()).decode("utf-8")
            ext = os.path.splitext(caminho_imagem)[1].lower().replace(".", "")
            if ext == "jpg":
                ext = "jpeg"
            return f"data:image/{ext};base64,{img_b64}"
        except Exception:
            pass
    return ""

CAMINHO_FUNDO_GERAL = "Data/Images/fundo_geral.jpg"
img_geral_b64 = carregar_imagem_fundo(CAMINHO_FUNDO_GERAL)

if img_geral_b64:
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(15, 23, 42, 0.78), rgba(15, 23, 42, 0.85)), url("{img_geral_b64}") !important;
            background-size: cover !important;
            background-position: center center !important;
            background-attachment: fixed !important;
            background-repeat: no-repeat !important;
        }}
        </style>
    """, unsafe_allow_html=True)

@st.dialog("📄 Detalhes do Projeto - Resumo Completo", width="large")
def abrir_popup_pdf(caminho_pdf, titulo=""):
    if titulo:
        st.markdown(f"<h4 style='margin-top: -10px; color: #38bdf8;'>{titulo}</h4>", unsafe_allow_html=True)
    if not os.path.exists(caminho_pdf):
        st.error(f"Arquivo PDF não encontrado no caminho:\n`{caminho_pdf}`")
        return
    try:
        doc = fitz.open(caminho_pdf)
        imagens_html = ""
        for num_pagina in range(len(doc)):
            pagina = doc.load_page(num_pagina)
            pix = pagina.get_pixmap(matrix=fitz.Matrix(2.5, 2.5))
            img_b64 = base64.b64encode(pix.tobytes("png")).decode("utf-8")
            imagens_html += f'<img src="data:image/png;base64,{img_b64}" style="width: 75%; height: auto; border-radius: 6px; box-shadow: 0 8px 25px rgba(0,0,0,0.6); margin-bottom: 24px; display: block;" />'
        doc.close()

        html_viewer = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://unpkg.com/@panzoom/panzoom@4.5.1/dist/panzoom.min.js"></script>
            <style>
                body, html {
                    margin: 0;
                    padding: 0;
                    background-color: #0f172a;
                    border-radius: 10px;
                    overflow: hidden;
                    font-family: sans-serif;
                }
                #viewport {
                    width: 100%;
                    height: 550px;
                    overflow-y: scroll;
                    overflow-x: hidden;
                    box-sizing: border-box;
                }
                #viewport::-webkit-scrollbar { width: 12px; }
                #viewport::-webkit-scrollbar-track { background: #0f172a; border-radius: 0 10px 10px 0; }
                #viewport::-webkit-scrollbar-thumb { background: #475569; border-radius: 6px; border: 2px solid #0f172a; }
                #viewport::-webkit-scrollbar-thumb:hover { background: #38bdf8; }
                #zoom-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: flex-start;
                    width: 100%;
                    padding: 25px 0;
                    transform-origin: center top;
                }
                .dica-zoom {
                    position: fixed;
                    bottom: 12px;
                    left: 15px;
                    background: rgba(30, 41, 59, 0.9);
                    color: #94a3b8;
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                    pointer-events: none;
                    border: 1px solid #334155;
                    z-index: 99;
                }
                .btn-reset {
                    position: fixed;
                    bottom: 12px;
                    right: 25px;
                    background: #2563eb;
                    color: white;
                    border: none;
                    padding: 6px 14px;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 600;
                    cursor: pointer;
                    z-index: 99;
                }
                .btn-reset:hover { background: #3b82f6; }
            </style>
        </head>
        <body>
            <div class="dica-zoom">💡 Role para descer as páginas | Ctrl + Scroll (ou pinça) para Zoom | Arraste para mover</div>
            <button class="btn-reset" id="reset-btn">Resetar Visão</button>
            <div id="viewport">
                <div id="zoom-container">__IMAGENS_PDF__</div>
            </div>
            <script>
                const elem = document.getElementById('zoom-container');
                const viewport = document.getElementById('viewport');
                const panzoom = Panzoom(elem, {
                    maxScale: 6, minScale: 0.5, step: 1.5, contain: false, canvas: false
                });
                viewport.addEventListener('wheel', function(event) {
                    if (event.ctrlKey) {
                        event.preventDefault();
                        const fatorSensibilidade = Math.abs(event.deltaY) < 15 ? 1.5 : 0.7;
                        panzoom.zoomWithWheel(event, { step: fatorSensibilidade });
                    }
                }, { passive: false });
                document.getElementById('reset-btn').addEventListener('click', () => {
                    panzoom.reset();
                    viewport.scrollTop = 0;
                });
            </script>
        </body>
        </html>
        """.replace("__IMAGENS_PDF__", imagens_html)
        components.html(html_viewer, height=555, scrolling=False)
    except Exception as e:
        st.error(f"Erro ao carregar o PDF: {e}")


@st.dialog("📖 Guia de Utilização - LiDAR Processing GUI", width="large")
def abrir_guia_tucupi():
    st.markdown("""
    ### 1. ABA ALS (Processamento Base)
    * **Motor C++ (`lidR` vs `lasR`):**
      * `lidR`: Mais completo, suporta todos os algoritmos avançados.
      * `lasR`: Otimizado para velocidade extrema em C++.
    * **Denoise (SOR) K/M:** Remove pontos de ruído.
    * **Filtro de Solo (Ground Filter):** `PTD`, `PMF`, `CSF` e `MCC`.
    * **Algoritmo DTM & CHM:** Suporte a `TIN`, `KNNIDW`, `Kriging` e `p2r`.
    """)

CAMINHO_BANNER_FUNDO = "Data/Images/background.jpg"
img_fundo_b64 = carregar_imagem_fundo(CAMINHO_BANNER_FUNDO)

if img_fundo_b64:
    estilo_fundo_hero = f"background-image: linear-gradient(rgba(15, 23, 42, 0.55), rgba(30, 58, 138, 0.70)), url('{img_fundo_b64}'); background-size: cover; background-position: center center; background-repeat: no-repeat;"
else:
    estilo_fundo_hero = "background-color: #1e3a8a;"

st.markdown(f"""
<div class="hero-section" style="{estilo_fundo_hero}">
    <div style="display: flex; align-items: center; gap: 2rem; max-width: 1200px; margin: 0 auto;">
        <div style="flex-shrink: 0;">
            <div style="width: 120px; height: 120px; background-color: #93c5fd; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 3rem; color: #1e3a8a; font-weight: bold; border: 4px solid #bfdbfe;">
                E
            </div>
        </div>
        <div>
            <h1 style="margin: 0; font-size: 2.5rem;">Eduardo O. Toledo</h1>
            <h3 style="margin: 0.5rem 0; color: #93c5fd !important; font-weight: 400;">Geoprocessing Specialist, GIS & LiDAR</h3>
            <p style="margin-top: 1rem; max-width: 600px; opacity: 0.9;">Transforming spatial data into clear visualizations.</p>
            <div style="margin-top: 1.5rem; display: flex; gap: 1rem; align-items: center;">
                <span style="background-color: #60a5fa; padding: 0.5rem 1.5rem; border-radius: 20px; font-weight: bold; cursor: pointer;">Contact</span>
                <span style="background-color: #60a5fa; padding: 0.5rem 1.5rem; border-radius: 20px; font-weight: bold; cursor: pointer;">Curriculum</span>
                <a href="https://www.linkedin.com/in/eduardo-oliveira-toledo-790a4a276" target="_blank" style="background-color: #60a5fa; padding: 0.5rem 1.5rem; border-radius: 20px; font-weight: bold; cursor: pointer; text-decoration: none; color: #f8fafc;">LinkedIn</a>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

aba_visao_geral, aba_lidar, aba_mapas, aba_projetos, aba_bacia, aba_certificados = st.tabs([
    "📊 Overview", 
    "🧊 3D Visualization (LiDAR / STL)", 
    "🗺️ WebGIS", 
    "📁 Past Projects",
    "⛰️ Watershed 3D",
    "🏆 Certificates"
])

with aba_visao_geral:
    st.markdown("### Highlights")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        try:
            st.image(Image.open("Data/Images/Plots_ID.png"), use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao carregar a imagem do Projeto A: {e}")
            
        st.image("https://placehold.co/400x300/3b82f6/ffffff?text=WebGIS", use_container_width=True)
        
    with col2:
        st.image("https://placehold.co/400x300/60a5fa/ffffff?text=Satélite", use_container_width=True)
        try:
            st.image(Image.open("Data/Images/ground_segmentation_and_dtm.png"), use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao carregar a imagem de segmentação: {e}")
            
    with col3:
        try:
            st.image(Image.open("Data/Images/Comparacao_DAP_Global.png"), use_container_width=True)
        except Exception as e:
            st.error(f"Erro: {e}")
        try:
            st.image(Image.open("Data/Mapas/Mapa_TCC_IPE.png"), use_container_width=True)
        except Exception as e:
            st.error(f"Erro: {e}")
            
    with col4:
        try:
            st.image(Image.open("Data/Images/patriarca_qsm.png"), use_container_width=True)
        except Exception as e:
            st.error(f"Erro: {e}")
        st.image("https://placehold.co/400x200/bfdbfe/1e3a8a?text=Dados", use_container_width=True)

    st.markdown("---")
    st.markdown("### Area of Activity")

    mapa_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/globe.gl@2.32.1/dist/globe.gl.min.js"></script>
        <style>
            body, html { margin: 0; padding: 0; width: 100%; height: 450px; background-color: transparent; overflow: hidden; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            #globeViz { width: 100%; height: 450px; display: flex; justify-content: center; align-items: center; }
            .scene-tooltip { background: transparent !important; border: none !important; box-shadow: none !important; padding: 0 !important; }
            @keyframes surgirPopup { 0% { opacity: 0; transform: translateY(12px) scale(0.85); } 100% { opacity: 1; transform: translateY(0) scale(1); } }
            .popup-cidade { background: rgba(15, 23, 42, 0.92); backdrop-filter: blur(8px); border: 1px solid #38bdf8; border-radius: 12px; padding: 12px 16px; color: #f8fafc; width: 260px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6), 0 0 15px rgba(56, 189, 248, 0.25); animation: surgirPopup 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards; pointer-events: none; }
            .popup-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
            .popup-titulo { font-size: 1rem; font-weight: 700; color: #38bdf8; margin: 0; }
            .popup-tag { background: rgba(56, 189, 248, 0.15); color: #93c5fd; font-size: 0.7rem; padding: 2px 8px; border-radius: 10px; font-weight: 600; }
            .popup-divisor { height: 2px; width: 35px; background-color: #2563eb; margin-bottom: 8px; }
            .popup-texto { font-size: 0.82rem; color: #cbd5e1; line-height: 1.45; margin: 0; white-space: normal; }
        </style>
    </head>
    <body>
        <div id="globeViz"></div>
        <script>
            const markerData = [
                { lat: -22.7390, lng: -47.6462, name: 'Piracicaba - Brazil', tag: 'ESALQ / USP', descricao: 'Forest Engineering Degree, UAV-LiDAR processing, 3D forest modeling, and ecological restoration projects.' },
                { lat: -23.5505, lng: -46.6333, name: 'São Paulo - Brazil', tag: 'Summit', descricao: 'Presented: Ecological corridor modeling and spatial connectivity analysis at the MapBiomas User Summit.' },
                { lat: 40.4168, lng: -3.7038, name: 'Madrid - Spain', tag: 'UPM / BEPE-FAPESP', descricao: 'Research internship at Universidad Politécnica de Madrid applying graph theory and Conefor to model landscape connectivity.' },
                { lat: 55.9533, lng: -3.1883, name: 'Edinburgh - Scotland', tag: 'BES Annual Meeting', descricao: 'Poster presentation on ecological corridor modeling and environmental offsets at the British Ecological Society Annual Meeting.' }
            ];
            const container = document.getElementById('globeViz');
            let globeInstance = null;
            let pontoHover = null;
            function initGlobe(width) {
                globeInstance = Globe()(container)
                    .globeImageUrl('https://cdn.jsdelivr.net/npm/three-globe/example/img/earth-blue-marble.jpg')
                    .backgroundColor('rgba(0,0,0,0)')
                    .pointsData(markerData)
                    .pointAltitude(d => d === pontoHover ? 0.09 : 0.04)
                    .pointColor(d => d === pontoHover ? '#38bdf8' : '#3b82f6')
                    .pointRadius(d => d === pontoHover ? 0.65 : 0.45)
                    .pointsTransitionDuration(250)
                    .pointLabel(d => `<div class="popup-cidade"><div class="popup-header"><h4 class="popup-titulo">📍 ${d.name}</h4><span class="popup-tag">${d.tag}</span></div><div class="popup-divisor"></div><p class="popup-texto">${d.descricao}</p></div>`)
                    .onPointHover(hoverPoint => {
                        pontoHover = hoverPoint;
                        container.style.cursor = hoverPoint ? 'pointer' : 'grab';
                        globeInstance.pointAltitude(globeInstance.pointAltitude()).pointColor(globeInstance.pointColor()).pointRadius(globeInstance.pointRadius());
                    })
                    .width(width)
                    .height(450);
                globeInstance.pointOfView({ lat: -18, lng: -48, altitude: 1.4 }, 1000);
                globeInstance.controls().enableZoom = true;
                globeInstance.controls().minDistance = 100;
                globeInstance.controls().maxDistance = 300;
            }
            const observer = new ResizeObserver(entries => {
                for (let entry of entries) {
                    const width = entry.contentRect.width;
                    if (width > 0) {
                        if (!globeInstance) initGlobe(width);
                        else globeInstance.width(width);
                    }
                }
            });
            observer.observe(document.body);
        </script>
    </body>
    </html>
    """
    components.html(mapa_html, height=450)

with aba_lidar:
    st.markdown("### Visualização de Modelos 3D")
    
    @st.cache_data
    def carregar_lidar_otimizado(caminho_arquivo=None, max_pontos=50000):
        import laspy
        import numpy as np
        if caminho_arquivo and os.path.exists(caminho_arquivo):
            try:
                las = laspy.read(caminho_arquivo)
                pontos = np.vstack((las.x, las.y, las.z)).transpose()
                z_elevacao = las.z
                
                mask_folhas = np.zeros(len(pontos), dtype=bool)
                achou_dim = False
                
                dim_names = [d.name.lower() for d in las.point_format.dimensions]
                if 'wood' in dim_names:
                    mask_folhas = (las['wood'] == 0)
                    achou_dim = True
                elif 'foliage' in dim_names:
                    mask_folhas = (las['foliage'] > 0)
                    achou_dim = True
                
                if not achou_dim:
                    try:
                        classes = las.classification
                        classes_unicas = np.unique(classes)
                        if len(classes_unicas) >= 2:
                            c1, c2 = classes_unicas[0], classes_unicas[1]
                            z_c1 = np.mean(z_elevacao[classes == c1])
                            z_c2 = np.mean(z_elevacao[classes == c2])
                            
                            if z_c1 > z_c2:
                                mask_folhas = (classes == c1)
                            else:
                                mask_folhas = (classes == c2)
                    except:
                        pass
                        
                if len(pontos) > max_pontos:
                    indices = np.random.choice(len(pontos), max_pontos, replace=False)
                    x, y, z = pontos[indices, 0], pontos[indices, 1], pontos[indices, 2]
                    cor = z_elevacao[indices]
                    mask_folhas = mask_folhas[indices]
                else:
                    x, y, z = pontos[:, 0], pontos[:, 1], pontos[:, 2]
                    cor = z_elevacao
                    
                x = x - np.mean(x)
                y = y - np.mean(y)
                z = z - np.min(z)
                
                return x, y, z, cor, mask_folhas
            except Exception as e:
                st.error(f"Erro ao ler LiDAR: {e}")
                
        x = np.random.uniform(-50, 50, max_pontos)
        y = np.random.uniform(-50, 50, max_pontos)
        z = (np.sin(x * 0.1) * 8) + (np.cos(y * 0.1) * 8) + np.random.normal(0, 0.5, max_pontos)
        return x, y, z, z, np.ones(max_pontos, dtype=bool)

    @st.cache_data
    def carregar_obj_otimizado(caminho_arquivo=None):
        import trimesh
        import numpy as np
        import os
        if caminho_arquivo and os.path.exists(caminho_arquivo):
            try:
                malha = trimesh.load(caminho_arquivo, force='mesh')
                x = malha.vertices[:, 0] - np.mean(malha.vertices[:, 0])
                y = malha.vertices[:, 1] - np.mean(malha.vertices[:, 1])
                z = malha.vertices[:, 2] - np.min(malha.vertices[:, 2])
                i = malha.faces[:, 0]
                j = malha.faces[:, 1]
                k = malha.faces[:, 2]
                return x, y, z, i, j, k, z
            except Exception as e:
                st.error(f"Erro ao processar malha OBJ: {e}")
        else:
            if caminho_arquivo:
                st.warning(f"⚠️ Ficheiro não encontrado: {caminho_arquivo}")
        x_sim = np.array([0, -10, 10, 10, -10, 0, 0, 0])
        y_sim = np.array([0, -10, -10, 10, 10, -10, 10, 0])
        z_sim = np.array([15, 0, 0, 0, 0, 0, 0, 0])
        i_sim = np.array([0, 0, 0, 0, 1])
        j_sim = np.array([1, 2, 3, 4, 2])
        k_sim = np.array([2, 3, 4, 1, 3])
        return x_sim, y_sim, z_sim, i_sim, j_sim, k_sim, z_sim

    tipo_dado = st.radio("Select the view type:", ["Point Clouds (.laz / .las)", "3D Models (.obj)"], horizontal=True)
    
    col_3d, col_texto = st.columns([2.2, 1], gap="medium")
    
    with col_texto:
        if tipo_dado == "Point Clouds (.laz / .las)":
            estilo_caixa = "box-sizing: border-box; height: 510px; margin-top: 42px; overflow-y: auto; padding: 25px; border: 1px solid #334155; background-color: #1e293b; border-radius: 15px; color: #e2e8f0;"
        else:
            estilo_caixa = "box-sizing: border-box; height: 550px; margin-top: 0px; overflow-y: auto; padding: 25px; border: 1px solid #334155; background-color: #1e293b; border-radius: 15px; color: #e2e8f0;"
            
        st.markdown(f'<div style="{estilo_caixa}"><p style="text-align: justify; font-size: 0.92em; line-height: 1.6; margin-top: 0;">High-resolution <b>Light Detection and Ranging (LiDAR)</b> via UAVs enables the precise capture of complex forest structures. Aerial and terrestrial laser scanning systems generate dense point clouds that represent the exact 3D geometry of individual trees.</p><p style="text-align: justify; font-size: 0.92em; line-height: 1.6;">Processing these massive datasets requires specialized workflows in R and Python. Ground returns are filtered out, leaving a highly detailed architectural model of the canopy, branches, and trunk.</p><p style="text-align: justify; font-size: 0.92em; line-height: 1.6;">By applying advanced algorithms like <b>Quantitative Structure Models (TreeQSM)</b> to point clouds—such as scans of monumental species like the Jequitibá-rosa—the raw data is mathematically reconstructed into a series of connected cylinders that match the tree\'s natural topology.</p><p style="text-align: justify; font-size: 0.92em; line-height: 1.6;">This methodology allows for highly accurate, non-destructive evaluations of <b>aboveground biomass (AGB)</b> across different seasonal conditions, providing critical metrics for carbon stock assessments and structural analysis.</p></div>', unsafe_allow_html=True)

    with col_3d:
        camara_fixa = dict(
            eye=dict(x=2.4, y=2.4, z=0.8), 
            center=dict(x=0, y=0, z=-0.1)
        )

        if tipo_dado == "Point Clouds (.laz / .las)":
            mostrar_folhas = st.toggle("🌿 Show Foliage", value=True)
            
            ARQUIVO_LAS = "Data/LiDAR/Tree_43.laz"
            x_vals, y_vals, z_vals, cores_vals, mask_f = carregar_lidar_otimizado(ARQUIVO_LAS)
            
            fig_3d = go.Figure()
            mask_m = ~mask_f
            
            if np.any(mask_m):
                fig_3d.add_trace(go.Scatter3d(
                    x=x_vals[mask_m], y=y_vals[mask_m], z=z_vals[mask_m],
                    mode='markers', marker=dict(size=2.5, color='#d97706', opacity=1.0),
                    name='Wood'
                ))
            
            if np.any(mask_f) and mostrar_folhas:
                fig_3d.add_trace(go.Scatter3d(
                    x=x_vals[mask_f], y=y_vals[mask_f], z=z_vals[mask_f],
                    mode='markers', marker=dict(size=1.5, color='#4ade80', opacity=0.7),
                    name='Foliage'
                ))
                
            if not np.any(mask_m) and not np.any(mask_f):
                fig_3d.add_trace(go.Scatter3d(x=x_vals, y=y_vals, z=z_vals, mode='markers', marker=dict(size=1.5, color=cores_vals, colorscale='Blues', opacity=0.8), name='Tree'))
            
            fig_3d.update_layout(
                height=510, margin=dict(l=0, r=0, b=0, t=0), paper_bgcolor='#1e293b', 
                scene=dict(aspectmode='manual', aspectratio=dict(x=1, y=1, z=1.8), camera=camara_fixa),
                showlegend=False 
            )
            st.plotly_chart(fig_3d, use_container_width=True, height=510, key="plot_nuvem_classificada")
            
        else:
            ARQUIVO_OBJ = "Data/Obj/tree_43.obj"
            x_s, y_s, z_s, i_s, j_s, k_s, cor_s = carregar_obj_otimizado(ARQUIVO_OBJ)
            fig_obj = go.Figure(data=[go.Mesh3d(x=x_s, y=y_s, z=z_s, i=i_s, j=j_s, k=k_s, color='lightpink', opacity=0.8)])
            fig_obj.update_layout(height=550, margin=dict(l=0, r=0, b=0, t=0), paper_bgcolor='#1e293b', scene=dict(aspectmode='manual', aspectratio=dict(x=1, y=1, z=1.8), camera=camara_fixa))
            st.plotly_chart(fig_obj, use_container_width=True, height=550, key="plot_obj")

with aba_mapas:
    st.markdown("### Interactive WebGIS")
    st.write("Explore the interactive maps and spatial analyses directly in the interface below:")
    
    codigo_mapa = """
    <!DOCTYPE html>
    <html>
    <head><style>body { margin: 0; padding: 0; background-color: transparent; } </style></head>
    <body>
        <iframe id="mapa-netlify" width="100%" height="620" style="border:none; border-radius: 15px;"></iframe>
        <script>
            const iframe = document.getElementById('mapa-netlify');
            const observer = new ResizeObserver(entries => {
                for (let entry of entries) {
                    if (entry.contentRect.width > 0 && !iframe.src) {
                        iframe.src = "https://deluxe-capybara-bce9ef.netlify.app/";
                    }
                }
            });
            observer.observe(document.body);
        </script>
    </body>
    </html>
    """
    components.html(codigo_mapa, height=640)

with aba_projetos:
    st.markdown("### Past Projects")
    
    CAMINHO_PDF_TOPOGRAFIA = "Data/Projects summary/BANNER_BES.pdf"
    CAMINHO_PDF_MDT = "Data/Projects summary/Apresentacao_Oral_SIICUSP.pdf"
    CAMINHO_PDF_CADASTRO = "Data/Projects summary/Apresentação Summit MapBiomas.pdf"
    CAMINHO_PDF_PROCESSAMENTO = "Data/Projects summary/Submissao_SBSR.pdf"
    CAMINHO_PDF_GEOREFERENCIAMENTO = "Data/Projects summary/Apresentação LARM Eduardo Ingles.pdf"
    
    p_col1, p_col2, p_col3 = st.columns(3)
    
    with p_col1:
        capa_topografia = gerar_preview_pdf(CAMINHO_PDF_TOPOGRAFIA)
        st.markdown(f"""
        <div class="custom-card-com-botao">
            <img src="{capa_topografia}" style="width: 100%; height: 200px; object-fit: cover; object-position: top; border-radius: 8px; margin-bottom: 10px;">
            <h4 style="margin:0;">British Ecological Society (BES) Presentation</h4>
            <div style="height: 4px; width: 40px; background-color: #2563eb; margin: 10px 0;"></div>
            <p style="color: #64748b; font-size: 0.9rem;">Execution of planimetric survey and aerophotogrammetry for contour generation.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ver detalhes →", key="btn_pdf_topografia"): abrir_popup_pdf(CAMINHO_PDF_TOPOGRAFIA, "Topographic Survey")

    with p_col2:
        capa_mdt = gerar_preview_pdf(CAMINHO_PDF_MDT)
        st.markdown(f"""
        <div class="custom-card-com-botao">
            <img src="{capa_mdt}" style="width: 100%; height: 200px; object-fit: cover; object-position: top; border-radius: 8px; margin-bottom: 10px;">
            <h4 style="margin:0;">USP International Symposium Presentation</h4>
            <div style="height: 4px; width: 40px; background-color: #2563eb; margin: 10px 0;"></div>
            <p style="color: #64748b; font-size: 0.9rem;">Technical summary of the project, technologies used, and results achieved with data processing.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ver detalhes →", key="btn_pdf_mdt"): abrir_popup_pdf(CAMINHO_PDF_MDT, "Digital Model (MDT)")

    with p_col3:
        capa_cadastro = gerar_preview_pdf(CAMINHO_PDF_CADASTRO)
        st.markdown(f"""
        <div class="custom-card-com-botao">
            <img src="{capa_cadastro}" style="width: 100%; height: 200px; object-fit: cover; object-position: top; border-radius: 8px; margin-bottom: 10px;">
            <h4 style="margin:0;">MapBiomas Summit Presentation</h4>
            <div style="height: 4px; width: 40px; background-color: #2563eb; margin: 10px 0;"></div>
            <p style="color: #64748b; font-size: 0.9rem;">Technical summary of the project, technologies used, and results achieved with data processing.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ver detalhes →", key="btn_pdf_cadastro"): abrir_popup_pdf(CAMINHO_PDF_CADASTRO, "Urban Registration")
            
    st.markdown("<br>", unsafe_allow_html=True)
    p_col4, p_col5, p_col6 = st.columns(3)
    
    with p_col4:
        capa_processamento = gerar_preview_pdf(CAMINHO_PDF_PROCESSAMENTO)
        st.markdown(f"""
        <div class="custom-card-com-botao">
            <img src="{capa_processamento}" style="width: 100%; height: 200px; object-fit: cover; object-position: top; border-radius: 8px; margin-bottom: 10px;">
            <h4 style="margin:0;">Brazilian Symposium on Remote Sensing Presentation</h4>
            <div style="height: 4px; width: 40px; background-color: #2563eb; margin: 10px 0;"></div>
            <p style="color: #64748b; font-size: 0.9rem;">Technical summary focused on the geospatial methodologies applied.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ver detalhes →", key="btn_pdf_processamento"): abrir_popup_pdf(CAMINHO_PDF_PROCESSAMENTO, "Image Processing")

    with p_col5:
        capa_geo = gerar_preview_pdf(CAMINHO_PDF_GEOREFERENCIAMENTO)
        st.markdown(f"""
        <div class="custom-card-com-botao">
            <img src="{capa_geo}" style="width: 100%; height: 200px; object-fit: cover; object-position: top; border-radius: 8px; margin-bottom: 10px;">
            <h4 style="margin:0;">Latin American Regional Meeting Presentation</h4>
            <div style="height: 4px; width: 40px; background-color: #2563eb; margin: 10px 0;"></div>
            <p style="color: #64748b; font-size: 0.9rem;">Technical summary focused on the geospatial methodologies applied.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ver detalhes →", key="btn_pdf_geo"): abrir_popup_pdf(CAMINHO_PDF_GEOREFERENCIAMENTO, "Georeferencing")

    with p_col6:
        st.markdown(f"""
        <div class="custom-card" style="background-color: #1e293b; color: white;">
            <img src="https://placehold.co/400x250/1e40af/ffffff?text=Projeto" style="width:100%; height: 200px; object-fit: cover; border-radius: 8px; margin-bottom: 10px;">
            <h4 style="margin:0; color: white;">Forest Restoration Workshop Organization</h4>
            <div style="height: 4px; width: 40px; background-color: #60a5fa; margin: 10px 0;"></div>
            <p style="color: #94a3b8; font-size: 0.9rem;">Technical summary focused on the geospatial methodologies applied.</p>
        </div>
        """, unsafe_allow_html=True)

with aba_bacia:
    col_titulo, col_info = st.columns([2, 1])
    with col_titulo:
        st.markdown("### ⛰️ Modelo Digital de Terreno (MDT) em 3D")
        st.write("Detailed topographic visualization with hydrography aligned to the terrain.")
    
    CAMINHO_MDT = "Data/Watershed/MDT_Bacia.tif"
    CAMINHO_RIOS = "Data/Watershed/Rios_Simples_Bacia.gpkg" 
    CAMINHO_NASCENTES = "Data/Watershed/Nascentes_Bacia.gpkg"

    @st.cache_data
    def processar_modelo_e_vetores(caminho_raster, cam_rios, cam_nascentes, downsample=4):
        try:
            import rasterio
            import geopandas as gpd
            import numpy as np

            with rasterio.open(caminho_raster) as src:
                z_raw = src.read(1).astype(float)
                nodata = src.nodata
                if nodata is not None:
                    z_raw[z_raw == nodata] = np.nan
                else:
                    z_raw[z_raw < -9000] = np.nan

                # Garante que a malha 3D não ultrapasse ~300x300 para não travar o navegador
                passo = max(downsample, int(np.ceil(max(z_raw.shape) / 300)))
                z_reduzido_orig = z_raw[::passo, ::passo]
                height_orig, width_orig = z_reduzido_orig.shape
                pad = 3
                z_reduzido = np.pad(z_reduzido_orig, pad_width=pad, mode='constant', constant_values=np.nan)
                
                mascara = ~np.isnan(z_reduzido)
                borda = np.copy(mascara)
                for _ in range(2):
                    temp = np.copy(borda)
                    temp[:-1, :] |= borda[1:, :]
                    temp[1:, :] |= borda[:-1, :]
                    temp[:, :-1] |= borda[:, 1:]
                    temp[:, 1:] |= borda[:, :-1]
                    temp[:-1, :-1] |= borda[1:, 1:]
                    temp[1:, 1:] |= borda[:-1, :-1]
                    temp[:-1, 1:] |= borda[1:, :-1]
                    temp[1:, :-1] |= borda[:-1, 1:]
                    borda = temp
                parede = borda & ~mascara
                z_reduzido[parede] = 0
                
                cols = np.arange(-pad * passo, (width_orig + pad) * passo, passo)
                rows = np.arange(-pad * passo, (height_orig + pad) * passo, passo)
                cols = cols[:z_reduzido.shape[1]]
                rows = rows[:z_reduzido.shape[0]]
                cols_grid, rows_grid = np.meshgrid(cols, rows)
                X, Y = src.transform * (cols_grid, rows_grid) 
                X = np.array(X)
                Y = np.array(Y)

                # Busca de elevação direto em memória (muito mais rápido que src.sample no loop)
                def pegar_elevacao(px, py):
                    try:
                        row, col = src.index(px, py)
                        if 0 <= row < z_raw.shape[0] and 0 <= col < z_raw.shape[1]:
                            val = z_raw[row, col]
                            if not np.isnan(val) and val > 0:
                                return float(val)
                    except Exception:
                        pass
                    return None

                rios_x, rios_y, rios_z = [], [], []
                if os.path.exists(cam_rios):
                    try:
                        gdf_rios = gpd.read_file(cam_rios)
                        if src.crs and gdf_rios.crs and gdf_rios.crs != src.crs:
                            gdf_rios = gdf_rios.to_crs(src.crs)
                        for geom in gdf_rios.geometry:
                            if geom is None or geom.is_empty:
                                continue
                            if geom.geom_type == 'MultiLineString':
                                linhas_geom = geom.geoms
                            elif geom.geom_type == 'LineString':
                                linhas_geom = [geom]
                            else:
                                continue
                            for linha in linhas_geom:
                                for coord in linha.coords:
                                    px, py = coord[0], coord[1]
                                    alt = pegar_elevacao(px, py)
                                    if alt is None:
                                        rios_x.append(None); rios_y.append(None); rios_z.append(None)
                                    else:
                                        rios_x.append(px); rios_y.append(py); rios_z.append(alt + 3)
                                rios_x.append(None); rios_y.append(None); rios_z.append(None)
                    except Exception as e:
                        print(f"Erro nos rios: {e}")

                nasc_x, nasc_y, nasc_z = [], [], []
                if os.path.exists(cam_nascentes):
                    try:
                        gdf_nasc = gpd.read_file(cam_nascentes)
                        if src.crs and gdf_nasc.crs and gdf_nasc.crs != src.crs:
                            gdf_nasc = gdf_nasc.to_crs(src.crs)
                        for geom in gdf_nasc.geometry:
                            if geom is None or geom.is_empty:
                                continue
                            if geom.geom_type == 'MultiPoint':
                                pontos_geom = geom.geoms
                            elif geom.geom_type == 'Point':
                                pontos_geom = [geom]
                            else:
                                continue
                            for pt in pontos_geom:
                                nx_coord, ny_coord = pt.x, pt.y
                                alt = pegar_elevacao(nx_coord, ny_coord)
                                if alt is not None:
                                    nasc_x.append(nx_coord); nasc_y.append(ny_coord); nasc_z.append(alt + 5)
                    except Exception as e:
                        print(f"Erro nas nascentes: {e}")

                return X, Y, z_reduzido, rios_x, rios_y, rios_z, nasc_x, nasc_y, nasc_z, None
        except Exception as e:
            return None, None, None, None, None, None, None, None, None, str(e)

    if not os.path.exists(CAMINHO_MDT):
        st.error(f"Arquivo MDT não encontrado em: `{CAMINHO_MDT}`")
    else:
        X, Y, Z, rx, ry, rz, nx, ny, nz, erro_bacia = processar_modelo_e_vetores(CAMINHO_MDT, CAMINHO_RIOS, CAMINHO_NASCENTES)
        if erro_bacia:
            st.error(f"Erro ao processar a bacia 3D: `{erro_bacia}`")
        elif X is not None:
            fig_bacia = go.Figure()
            fig_bacia.add_trace(go.Surface(
                x=X, y=Y, z=Z, colorscale='Viridis', showscale=True,
                colorbar=dict(title=dict(text="Elevation (m)", font=dict(color="#38bdf8")), len=0.7, thickness=15, tickfont=dict(color="#f8fafc")),
                name="Terreno"
            ))
            if rx and len(rx) > 0:
                fig_bacia.add_trace(go.Scatter3d(x=rx, y=ry, z=rz, mode='lines', line=dict(color='#0ea5e9', width=4), name='Hidrography'))
            if nx and len(nx) > 0:
                fig_bacia.add_trace(go.Scatter3d(x=nx, y=ny, z=nz, mode='markers', marker=dict(size=4, color='#22d3ee', symbol='circle', line=dict(color='#ffffff', width=1)), name='Water Spring'))
            
            fig_bacia.update_layout(
                margin=dict(l=0, r=0, b=0, t=30), paper_bgcolor='#1e293b', font=dict(color='#f8fafc'),
                scene=dict(xaxis=dict(showgrid=False, zeroline=False, showbackground=False, visible=False),
                           yaxis=dict(showgrid=False, zeroline=False, showbackground=False, visible=False),
                           zaxis=dict(showgrid=True, gridcolor='#334155', zeroline=False, showbackground=False, title="Elevation (m)"),
                           aspectmode='manual', aspectratio=dict(x=1.2, y=1.2, z=0.25), 
                           camera=dict(eye=dict(x=1.0, y=-1.0, z=0.8), center=dict(x=0, y=0, z=-0.15))),
                height=550, showlegend=True, legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.05, bgcolor="rgba(15, 23, 42, 0.8)")
            )
            col_3d, col_texto = st.columns([2.2, 1], gap="medium")
            with col_3d:
                st.plotly_chart(fig_bacia, use_container_width=True, key="grafico_mdt_3d")
            with col_texto:
                st.markdown('''
                <div style="height: 550px; overflow-y: auto; padding: 25px; border: 1px solid #334155; background-color: rgba(30, 41, 59, 0.5); border-radius: 8px; color: #e2e8f0; margin-top: 0px;">
                    <p style="text-align: justify; font-size: 0.92em; line-height: 1.6; margin-top: 0;">The extraction of hydrological features, such as drainage networks, basin boundaries, and springs, relies heavily on <b>Digital Elevation Models (DEMs)</b>.</p>
                    <p style="text-align: justify; font-size: 0.92em; line-height: 1.6;">Datasets obtained from spaceborne missions, like the <b>Shuttle Radar Topography Mission (SRTM)</b>, provide the essential topographic framework. These active sensors emit microwave pulses to Earth and measure the backscattered signal's time-of-flight, generating highly accurate global elevation grids.</p>
                    <p style="text-align: justify; font-size: 0.92em; line-height: 1.6;">Using geoprocessing algorithms (such as the D8 flow direction method), we simulate how gravity dictates water movement across this digital landscape. The software calculates <b>flow accumulation</b> to identify pixels where runoff naturally concentrates, effectively carving out virtual streams and river networks.</p>
                    <p style="text-align: justify; font-size: 0.92em; line-height: 1.6;"><b>Springs</b> are modeled at the origin nodes of these high-accumulation pathways.</p>
                    <p style="text-align: justify; font-size: 0.92em; line-height: 1.6;">By overlaying these vector geometries onto a 3D topographic surface, we achieve a comprehensive spatial understanding critical for water resource management and ecological restoration.</p>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("Não foi possível carregar os dados. Verifique se os caminhos dos ficheiros estão corretos.")

@st.cache_data
def renderizar_pdf_certificado_html(caminho_pdf):
    if not os.path.exists(caminho_pdf):
        return None
    try:
        doc = fitz.open(caminho_pdf)
        imagens_html = ""
        for num_pagina in range(len(doc)):
            pagina = doc.load_page(num_pagina)
            pix = pagina.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
            img_b64 = base64.b64encode(pix.tobytes("png")).decode("utf-8")
            imagens_html += f'<img src="data:image/png;base64,{img_b64}" style="width: 92%; height: auto; border-radius: 8px; box-shadow: 0 8px 25px rgba(0,0,0,0.5); margin-bottom: 16px; display: block;" />'
        doc.close()

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://unpkg.com/@panzoom/panzoom@4.5.1/dist/panzoom.min.js"></script>
            <style>
                body, html {{ margin: 0; padding: 0; background-color: #0f172a; border-radius: 12px; overflow: hidden; font-family: sans-serif; }}
                #viewport {{ width: 100%; height: 540px; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; }}
                #zoom-container {{ display: flex; flex-direction: column; align-items: center; padding: 18px 0; transform-origin: center top; }}
                .dica {{ position: fixed; bottom: 10px; left: 12px; background: rgba(30, 41, 59, 0.9); color: #94a3b8; padding: 5px 10px; border-radius: 6px; font-size: 11px; border: 1px solid #334155; pointer-events: none; }}
                .btn-reset {{ position: fixed; bottom: 10px; right: 18px; background: #2563eb; color: white; border: none; padding: 5px 12px; border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer; }}
                .btn-reset:hover {{ background: #3b82f6; }}
            </style>
        </head>
        <body>
            <div class="dica">💡 Ctrl + Scroll to Zoom | Drag to pan</div>
            <button class="btn-reset" id="reset-btn">Reset View</button>
            <div id="viewport"><div id="zoom-container">{imagens_html}</div></div>
            <script>
                const elem = document.getElementById('zoom-container');
                const viewport = document.getElementById('viewport');
                const panzoom = Panzoom(elem, {{ maxScale: 5, minScale: 0.6, step: 1.2 }});
                viewport.addEventListener('wheel', function(event) {{
                    if (event.ctrlKey) {{
                        event.preventDefault();
                        panzoom.zoomWithWheel(event);
                    }}
                }}, {{ passive: false }});
                document.getElementById('reset-btn').addEventListener('click', () => {{
                    panzoom.reset();
                    viewport.scrollTop = 0;
                }});
            </script>
        </body>
        </html>
        """
    except Exception:
        return None


with aba_certificados:
    st.markdown("### 🏆 Certificates & Credentials")

    PASTA_CERTIFICADOS = "Data/Certificates"

    CERTIFICADOS = [
        {
            "titulo": "Oral Presenter — 34th SIICUSP",
            "instituicao": "University of São Paulo (ESALQ/USP)",
            "data": "07/10/2026",
            "local": "Piracicaba, São Paulo, Brazil",
            "categoria": "Oral Presentation",
            "descricao": "Delivered an oral presentation titled \"Quantitative Structure Modeling Using LiDAR of the Patriarch (Cariniana legalis) in Vassununga State Park\" at the 34th SIICUSP. The study used Aerial Laser Scanning (DJI Matrice 350 with a Zenmuse L2 sensor), CloudCompare, and the TreeQSM algorithm in MATLAB to generate a 3D structural model of the tree and estimate its volume (255.18 m³), aboveground biomass, and carbon stock.",
            "arquivo": f"{PASTA_CERTIFICADOS}/siicusp_2026.pdf"
        },
        {
            "titulo": "Workshop Speaker — Latin American Regional Meeting (LARM / IFSA)",
            "instituicao": "International Forestry Students' Association (IFSA)",
            "data": "09/08/2026",
            "local": "Piracicaba, São Paulo, Brazil",
            "categoria": "Workshop Speaker",
            "descricao": "Delivered a workshop in Spanish titled \"Discovering Brazil: Biomes, Territory, and the MapBiomas Network\" for forestry students at the IFSA Latin American Regional Meeting (LARM). Introduced Brazil's six terrestrial biomes alongside foundational remote sensing concepts, including satellite monitoring history, radiance, and spectral reflectance. Presented the MapBiomas Network's open-science methodology, combining satellite imagery and machine learning, and demonstrated its thematic platforms for monitoring land-use change, fire, deforestation alerts, surface water, and ecological recovery across Latin America. Concluded with an applied case study on landscape connectivity and ecological corridor modeling between protected areas in the Atlantic Forest.",
            "arquivo": f"{PASTA_CERTIFICADOS}/larm_ifsa_2026.pdf"
        },
        {
            "titulo": "Presenter — MapBiomas User Summit 2026",
            "instituicao": "Instituto de Apoio ao MapBiomas (INSPER)",
            "data": "08/07/2026 - 09/07/2026",
            "local": "São Paulo, São Paulo, Brazil",
            "categoria": "Conference",
            "descricao": "Attended the MapBiomas User Summit 2026, organized by the Instituto de Apoio ao MapBiomas at INSPER in São Paulo. Presented the research work entitled \"Integrating native vegetation deficits into the modeling of ecological corridors between Protected Areas in Brazil\" during the Landscape Ecology and Regional Scale Conservation session.",
            "arquivo": f"{PASTA_CERTIFICADOS}/mapbiomas_summit_2026.pdf"
        },
        {
            "titulo": "Landscape Ecology Modeling Workshop Speaker",
            "instituicao": "Luiz de Queiroz College of Agriculture (ESALQ/USP)",
            "data": "18/04/2026",
            "local": "Piracicaba, São Paulo, Brazil",
            "categoria": "Workshop Speaker",
            "descricao": "Organized and instructed an intensive practical workshop on landscape ecology modeling for 40 undergraduate Forest Engineering students at ESALQ/USP. Guided participants through core theoretical concepts and spatial analysis workflows in a geographic information system, focusing on ecological corridor simulation and landscape connectivity assessment using specialized tools such as LSCorridors and Conefor.",
            "arquivo": f"{PASTA_CERTIFICADOS}/landscape_ecology_workshop_2026.pdf"
        },
        {
            "titulo": "Poster Presenter — British Ecological Society Annual Meeting",
            "instituicao": "British Ecological Society (BES)",
            "data": "16/12/2025 - 19/12/2025",
            "local": "Edinburgh, Scotland",
            "categoria": "International Conference",
            "descricao": "Presented the research poster titled \"From Legal Restoration to Functional Corridors: Modeling Landscape Connectivity in São Paulo State, Brazil\" at the British Ecological Society Annual Meeting in Edinburgh, Scotland.",
            "arquivo": f"{PASTA_CERTIFICADOS}/bes_annual_meeting_2025.pdf"
        },
        {
            "titulo": "Organizing Coordinator — 10th Workshop on Forest Restoration",
            "instituicao": "Luiz de Queiroz College of Agriculture (ESALQ/USP)",
            "data": "25/08/2023 - 27/08/2023",
            "local": "Piracicaba, São Paulo, Brazil",
            "categoria": "Event Coordination",
            "descricao": "Coordinated the 10th Workshop on Forest Restoration (Special Edition: Forest and Water) at ESALQ/USP. Managed the event structure for over 250 researchers and professionals, coordinating thematic sessions on restoration ecology, large-scale projects, public policies, and the ecohydrological dynamics of watersheds.",
            "arquivo": f"{PASTA_CERTIFICADOS}/10th_workshop_restoration_2023.pdf"
        },
        {
            "titulo": "Organizing Committee — 9th Workshop on Forest Restoration",
            "instituicao": "Luiz de Queiroz College of Agriculture (ESALQ/USP)",
            "data": "23/09/2022 - 25/09/2022",
            "local": "Piracicaba, São Paulo, Brazil",
            "categoria": "Event Organization",
            "descricao": "Served on the organizing committee for the 9th Workshop on Forest Restoration. Supported the dissemination of scientific research and fostered discussions on applied forest ecology and restoration practices within the academic community.",
            "arquivo": f"{PASTA_CERTIFICADOS}/9th_workshop_restoration_2022.pdf"
        },
    ]

    col_lista, col_viewer = st.columns([1.15, 2], gap="large")

    with col_lista:
        titulos = [c["titulo"] for c in CERTIFICADOS]
        selecionado = st.radio(
            "Select a certificate to inspect:",
            titulos,
            key="radio_certificados"
        )
        cert_atual = next(c for c in CERTIFICADOS if c["titulo"] == selecionado)

        st.markdown(f"""
        <div style="background-color: #1e293b; border: 1px solid #334155; border-left: 4px solid #38bdf8; border-radius: 12px; padding: 18px; margin-top: 14px; max-height: 320px; overflow-y: auto;">
            <span style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; font-size: 0.72rem; font-weight: 600; padding: 3px 10px; border-radius: 12px; text-transform: uppercase;">
                {cert_atual['categoria']}
            </span>
            <h4 style="margin: 10px 0 4px 0; color: #f8fafc;">{cert_atual['titulo']}</h4>
            <p style="margin: 0 0 4px 0; color: #93c5fd; font-size: 0.86rem; font-weight: 500;">{cert_atual['instituicao']}</p>
            <p style="margin: 0 0 12px 0; color: #94a3b8; font-size: 0.8rem;">📅 {cert_atual['data']} &nbsp;|&nbsp; 📍 {cert_atual['local']}</p>
            <p style="margin: 0; color: #cbd5e1; font-size: 0.88rem; line-height: 1.55; text-align: justify;">{cert_atual['descricao']}</p>
        </div>
        """, unsafe_allow_html=True)

    with col_viewer:
        caminho = cert_atual["arquivo"]
        if os.path.exists(caminho):
            if caminho.lower().endswith(".pdf"):
                html_cert = renderizar_pdf_certificado_html(caminho)
                if html_cert:
                    components.html(html_cert, height=545, scrolling=False)
                else:
                    st.error("Error rendering the certificate PDF.")
            else:
                st.image(Image.open(caminho), use_container_width=True)
        else:
            st.warning(f"File not found at:\n`{caminho}`")
            st.image("https://placehold.co/900x600/1e293b/38bdf8?text=Certificate+Preview", use_container_width=True)

st.markdown("---")
st.markdown("<div style='text-align: center; color: #94a3b8;'>© 2026 Eduardo - Desenvolvido com Streamlit</div>", unsafe_allow_html=True)