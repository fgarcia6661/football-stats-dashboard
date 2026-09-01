import streamlit as st
import time
import concurrent.futures
from streamlit.runtime.scriptrunner import add_script_run_ctx

def run_with_progress(func, *args, estimated_time=20, title="Cargando datos...", **kwargs):
    # Primero chequeamos si la función está en cache o es rápida,
    # pero como no sabemos si está en cache, no mostramos la barra 
    # hasta que pase 0.5s. Si pasa 0.5s y no ha terminado, mostramos progreso.
    
    progress_placeholder = st.empty()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        # Añadir el contexto de Streamlit al hilo para que st.cache_data funcione
        add_script_run_ctx(future)
        
        start_time = time.time()
        bar_created = False
        
        while not future.done():
            elapsed = time.time() - start_time
            if elapsed > 0.5:
                if not bar_created:
                    progress_bar = progress_placeholder.progress(0, text=f"{title} (0%)")
                    bar_created = True
                
                # Simulador de progreso logarítmico/lineal hasta 95%
                # Asumimos que webdriver + scrape = 20-30 segs la primera vez
                progress = min(95, int((elapsed / estimated_time) * 100))
                remaining = max(1, int(estimated_time - elapsed))
                
                progress_bar.progress(progress, text=f"{title} - {progress}% - Estimado restante: ~{remaining}s")
            
            time.sleep(0.5)
            
        if bar_created:
            progress_bar.progress(100, text=f"{title} - 100% - ¡Completado!")
            time.sleep(0.5)
            progress_placeholder.empty()
            
        return future.result()
