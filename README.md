# Documentazione del Sistema MusicRaccomandationSystem

## Panoramica del Sistema

Il Sistema MusicRac è una piattaforma avanzata per l'analisi e la raccomandazione musicale che si 
integra con le API di Spotify e Apple Music. Il sistema implementa un approccio matematico 
innovativo basato sulla teoria degli spazi vettoriali per generare raccomandazioni musicali personalizzate.

Il cuore del sistema si basa su una rappresentazione matematica dove ogni utente viene modellato
attraverso n sottospazi vettoriali {S₁, ..., Sₙ} all'interno di uno spazio vettoriale principale. 
Ogni sottospazio Sᵢ contiene un insieme denso di k canzoni: Sᵢ = {c₁, ..., cₖ}, dove ogni canzone 
viene rappresentata come una sfera n-dimensionale. Il volume di ciascuna sfera non è statico, 
ma aumenta dinamicamente in proporzione al numero di ascolti della canzone corrispondente. 

Questo meccanismo fa sì che il centro di massa del sottospazio si sposti progressivamente
verso le canzoni più ascoltate, che acquisiscono maggiore "peso" nel sistema grazie al loro 
volume crescente. La distanza di ciascuna canzone dal centro di massa del proprio sottospazio Sᵢ 
rappresenta il reale livello di gradimento dell'utente: più una canzone è vicina al centro di 
massa, maggiore è l'apprezzamento dell'utente per quella canzone, indipendentemente dal 
fatto che l'abbia salvata o meno nella sua libreria.

Questa rappresentazione geometrica permette di:
1. Calcolare il centro di massa di ogni sottospazio Sᵢ nello spazio n-dimensionale, 
   ottenendo così un punto di riferimento per il vero gusto musicale dell'utente
2. Tracciare l'evoluzione temporale dei gusti musicali dell'utente attraverso 
   il movimento dei centri di massa
3. Generare raccomandazioni analizzando le intersezioni e le vicinanze tra 
  le sfere musicali e i centri di massa, privilegiando canzoni che si trovano 
  più vicine al centro di massa di ciascun sottospazio
