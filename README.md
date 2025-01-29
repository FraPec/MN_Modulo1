# Simulazione e Analisi del Modello XY in 3D
Nella seguente repository sono implementeate la simulazione e l'analisi del modello O(2) (noto anche come XY) al fine di studiarne la transizione di fase.
A meno di LICENSE, del .gitignore e del corrente README-md, la struttura della repository è la seguente: 
    - **simulations**: include tutto il codice C (e alcuni script bash) dell'algoritmo utile alla generazione dei dati (Catene di Markov in file binari)
    - **configs**: Contiene i file di configurazione di tipo .yaml utilizzati per impostare i parametri delle analisi fatte con Python.
    - **mcmc_thermalization_analysis**: Contiene codice Python per l'analisi della termalizzazione dei dati delle simulazioni.
    - **data_processing**: Contiene codice Python utile per l'elaborazione e la pulizia dei dati grezzi (file binari) ottenuti dalle simulazioni.
    - **data_analysis**: Contiene codice Python per effettuare l'analisi delle variabili primarie (blocking) e secondarie (blocking+Jackknife).
    - **fss**: Comprende codice Python relativo utile allo studio del Finite Size Scaling (FSS), per analizzare gli effetti della dimensione finita nei sistemi simulati ed ottenere i parametri critici del modello O(2).
    - **utils**: Racchiude funzioni e script utilitari che supportano varie parti del progetto, come strumenti di visualizzazione o funzioni ausiliarie.
