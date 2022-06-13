# Webscraper ogłoszeń z Otodom.pl + baza MongoDB + raport z wizualizacją w Power BI

- Za orkiestrację odpowiada Airflow i stworzony w nim DAG
- Airflow uruchomiony jest w kontenerze Dockerowym
- Dane pobrane z serwisu Otodom przechowywane są bazie MongoDB. Pobierane zmienne to: tytuł ogłoszenia, cena, liczba pokoi, powierzchnia, lokalizacja, data dodania i data usunięcia ogłoszenia, czy ogłoszenie jest aktywne, link do ogłoszenia
- Na podstawie danych z MongoDB zbudowany został raport w Power BI, który pozwala filtrować ogłoszenia po dzielnicy, określać średnią cenę, liczbę pokoi i powierzchnię szukanego mieszkania. Dodatkowo w drugiej zakładce można podejrzeć posrtowane po cenie linki do ogłoszeń pasujących do ustawionych filtrów

# Raport w Power BI

![Power BI](/img/powerbi.png)

# DAG w Airflow

![Airflow](/img/airflow.png)

# Pliki
- get_data_for_PowerBI.py - zawiera skrypt pozwalający w łatwy sposób w PowerBI pobrać dane z bazy MongoDB
- webscraping.py - skrypt odpowiedzialny za pobieranie ogłoszeń
- werbscraping_dag.py - ten sam skrypt, zaimplementowany w formie DAGa w Airflow
- Dockerfile i docker-compose.yaml - pliki pozwalające uruchomić kontener Dockerowy zawierający Apache Airflow
