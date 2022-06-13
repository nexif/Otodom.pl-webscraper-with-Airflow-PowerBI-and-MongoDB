# Webscraper ogłoszeń z Otodom.pl + baza MongoDB + raport z wizualizacją w Power BI

- Za orkiestrację odpowiada Airflow i stworzony w nim DAG
- Dane pobrane z serwisu Otodom przechowywane są bazie MongoDB. Pobierane zmienne to: cena, liczba pokoi, powierzchnia, lokalizacja, data dodania i data usunięcia ogłoszenia, czy ogłoszenie jest aktywne, link do ogłoszenia
- Na podstawie danych z MongoDB zbudowany został raport w Power BI, który pozwala filtrować ogłoszenia po dzielnicy, określać średnią cenę, liczbę pokoi i powierzchnię szukanego mieszkania. Dodatkowo w drugiej zakładce można podejrzeć posrtowane po cenie linki do spełniających ustawione filtry ogłoszeń
