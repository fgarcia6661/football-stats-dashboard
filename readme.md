# Especificación del Proyecto: Dashboard de Análisis y Scouting de Fútbol en Vivo (100% Gratuito)

## 1. Contexto y Propósito
Aplicación web interactiva para el análisis táctico, seguimiento del rendimiento de equipos y scouting avanzado de futbolistas. La plataforma opera de forma 100% gratuita utilizando librerías de scraping en vivo (`soccerdata` y `ScraperFC`) para consultar datos actualizados de **FBref**, **Understat** y **WhoScored** para las principales ligas y temporadas activas sin depender de APIs de pago ni de StatsBomb.

---

## 2. Pila Tecnológica y Dependencias
* **Lenguaje:** Python 3.11+
* **Framework Web:** Streamlit (interfaz reactiva y gestión de estado)
* **Motores de Extracción de Datos:**
  * `soccerdata` (scrapers de FBref, Understat, Club Elo, SoFIFA)
  * `ScraperFC` (scrapers de eventos y partidos de WhoScored)
  * `pandas`, `numpy`
* **Gráficos Tácticos y Visualización:** `mplsoccer`, `matplotlib`, `seaborn`
* **Rendimiento y Persistencia:**
  * Uso de `@st.cache_resource` para mantener de forma eficiente en memoria las instancias de los scrapers (conectores).
  * Caché de datos mediante `@st.cache_data(ttl=43200)` para invalidar y refrescar los datos automáticamente cada 12 horas, garantizando que el dashboard se autoactualice.
  * Uso combinado con la caché en disco local de `soccerdata` (`no_cache=False`) para mitigar los bloqueos HTTP 429.

---

## 3. Arquitectura y Requisitos Funcionales

### 3.1 Pipeline de Datos
1. **Selección de Competición y Temporada:** El usuario selecciona la liga (`ESP-La Liga`, `ENG-Premier League`, `ITA-Serie A`, `GER-Bundesliga`, `FRA-Ligue 1`) y la temporada en curso.
2. **Ingesta de Datos:**
   * **Módulo Understat:** Coordenadas de tiro `(x, y)`, modelos de goles esperados (`xG`) y resultado del remate.
   * **Módulo FBref:** Estadísticas agregadas de la temporada de jugadores y equipos (estándar, tiros, pases, defensa, posesión).
   * **Módulo WhoScored (vía ScraperFC):** Eventos tácticos a nivel de partido.
3. **Transformación y Normalización:**
   * Normalización de métricas por 90 minutos jugados (`P90`).
   * Filtro de minutos mínimos disputados (umbral por defecto: >= 450 minutos) para evitar sesgos de muestra pequeña.
   * Escalado de coordenadas espaciales al sistema de campo reglamentario de `mplsoccer`.

### 3.2 Módulos Funcionales

#### Módulo 1: Mapa de Tiros y Calidad de Ocasiones (Understat / ScraperFC)
* **Objetivo:** Analizar los remates de un equipo o futbolista en la temporada seleccionada o en un partido específico.
* **Lógica:**
  * Extraer eventos de tiro con coordenadas `(x, y)` y valor de `xG`.
  * Representar en campo táctico utilizando `mplsoccer.Pitch`.
  * Escalar el diámetro del marcador en función de la probabilidad de gol (`xG`).
  * Asignar color por resultado del remate: *Gol*, *Parado*, *Fuera*, *Bloqueado*.
  * Mostrar panel de métricas resumen: Goles Totales, Tiros Totales, xG Acumulado, xG por Tiro (calidad media).

#### Módulo 2: Radar Comparativo de Scouting (FBref vía soccerdata)
* **Objetivo:** Comparativa visual de rendimiento entre dos jugadores o entre un jugador y la mediana de su posición en la liga.
* **Lógica:**
  * Cargar métricas avanzadas por 90 minutos clasificadas por demarcación:
    * **Delanteros y Extremos:** xG, Tiros, Pases Clave, Regates Completados, Acciones de Creación de Tiro (SCA).
    * **Centrocampistas:** Pases Progresivos, % Acierto de Pase, Conducciones Progresivas, Recuperaciones de Balón.
    * **Defensas:** Entradas Ganadas, Intercepciones, % Duelos Aéreos Ganados, Despejes / Bloqueos.
  * Normalizar valores a percentiles (0-100) sobre la muestra de futbolistas de la misma posición.
  * Renderizar mediante `mplsoccer.Radar` con temática oscura.

#### Módulo 3: Matriz de Rendimiento de Equipos (FBref / Understat)
* **Objetivo:** Análisis comparativo del rendimiento colectivo de la competición.
* **Lógica:**
  * Generar gráficos de dispersión (*Scatter Plots*) configurables:
    * xG a favor vs. xG en contra.
    * Pases completados en último tercio vs. Acciones de presión alta.
  * Tabla clasificatoria avanzada con métricas de goles esperados y diferenciales de rendimiento (Goles - xG).

---

## 4. UI / UX y Localización

### 4.1 Localización e Idioma (es-ES)
* **Idioma principal:** Castellano de España (`es-ES`) de forma obligatoria en el 100% de la interfaz, selectores, tooltips, títulos, ejes y leyendas de gráficos.
* **Glosario de métricas y términos:**
  * `Shot Map` -> *Mapa de Tiros*
  * `Player Radar Comparison` -> *Comparador de Jugadores (Radar)*
  * `Team Scatter Plot` -> *Matriz de Rendimiento de Equipos*
  * `Expected Goals (xG)` -> *Goles Esperados (xG)*
  * `Expected Assists (xA)` -> *Asistencias Esperadas (xA)*
  * `Progressive Passes (PrgP)` -> *Pases Progresivos*
  * `Progressive Carries (PrgC)` -> *Conducciones Progresivas*
  * `Shot-Creating Actions (SCA)` -> *Acciones de Creación de Tiro*
  * `Tackles + Interceptions (Tkl+Int)` -> *Entradas + Intercepciones*
  * `Minutes Played` -> *Minutos Jugados*

### 4.2 Navegación de la Interfaz
* **Barra lateral (Sidebar):**
  * Selector de Módulo: `Scouting y Radares de Jugadores` | `Mapa de Tiros (xG)` | `Métricas de Equipos`.
  * Filtros dinámicos: Liga, Temporada, Equipo, Jugador A, Jugador B, Posición táctica.
  * Configuración: Umbral de minutos mínimos jugados.
* **Área Principal:**
  * Resumen contextual de la selección.
  * Visualización táctica central (tema oscuro `#1e1e1e` / `#111827`).
  * Tablas de datos detalladas expandibles con opción de exportación a CSV.

---

## 5. Plan de Ejecución por Pasos

### Paso 1: Configuración del Entorno y Dependencias
* Crear archivo `requirements.txt` con las dependencias: streamlit, soccerdata, ScraperFC, mplsoccer, pandas, numpy, matplotlib, seaborn, requests, lxml.
* Estructura modular de directorios:
  football-analytics-app/
  ├── app.py
  ├── requirements.txt
  ├── src/
  │   ├── data_loaders/
  │   │   ├── __init__.py
  │   │   ├── fbref_loader.py
  │   │   └── understat_loader.py
  │   ├── visualizers.py
  │   ├── i18n.py
  │   └── utils.py
  └── README.md

### Paso 2: Módulo de Internacionalización (src/i18n.py)
* Implementar diccionarios maestros para traducir automáticamente columnas, estados y métricas a castellano de España.

### Paso 3: Conectores de Datos (src/data_loaders/)
* `fbref_loader.py`:
  * Inicializar `soccerdata.FBref` con almacenamiento en disco habilitado (`no_cache=False`) persistido en memoria mediante `@st.cache_resource`.
  * Métodos con expiración de 12h (`@st.cache_data(ttl=43200)`): `load_player_season_stats()`, `load_team_season_stats()`.
* `understat_loader.py`:
  * Inicializar `soccerdata.Understat` gestionado con `@st.cache_resource`.
  * Métodos con expiración de 12h: `load_team_shots()`, `load_match_shots()`.

### Paso 4: Visualizadores Tácticos (src/visualizers.py)
* `plot_shot_map(shots_df, team_name)`: Mapa de tiros escalado y traducido.
* `plot_player_radar(player_a_stats, player_b_stats, metrics, params_dict)`: Radar percentílico con `mplsoccer.Radar`.
* `plot_team_scatter(teams_df, x_col, y_col)`: Gráfico de dispersión con cuadrantes y etiquetas en español.

### Paso 5: Orquestación en Streamlit (app.py)
* Configurar `layout="wide"`.
* Conectar la barra lateral reactiva con la renderización de las vistas correspondientes.

---

## 6. Casos Límite y Robustez
* **Control de Rate-Limiting:** Forzar la persistencia en disco de `soccerdata` (`no_cache=False`) para no volver a descargar tablas de FBref en cada interacción de la UI.
* **Aplanado de Índices:** Procesar y aplanar los multi-índices de columnas devueltos por FBref antes de generar DataFrames limpios.
* **Muestras Insuficientes:** Mostrar aviso visual cuando un jugador seleccionado no alcance el mínimo de minutos disputados.
* **Coordenadas Nulas:** Filtrar registros sin localización antes de proyectarlos en `mplsoccer`.

---

## 7. Criterios de Aceptación
1. La aplicación inicia localmente mediante `streamlit run app.py` sin errores de importación ni excepciones.
2. Permite seleccionar competiciones actuales de las grandes ligas y descargar datos reales mediante `soccerdata`.
3. El comparador genera radares de percentiles precisos entre dos jugadores de la misma posición.
4. El mapa de tiros posiciona correctamente los remates con su respectivo valor de xG.
5. El 100% de la interfaz visible (textos, títulos, selectores, tooltips y leyendas de gráficos) está en castellano de España (`es-ES`).