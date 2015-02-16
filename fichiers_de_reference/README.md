Les fichiers de référence contiennent les données de comparaison pour la détection de champs. Par ex: codes communes INSEE, noms de pays,
catégories socio professionelles de l'INSEE...

Les fichiers de réference doivent suivre les règles suivantes :

- Tous les fichiers de référence (à l'exception des codes) doivent être dans la forme standard (pas d'accents, ponctuation remplacée par des espaces...) qui peut être obtenue en utilisant la fonction process_text.py.
- Les codes, pour lesquels la casse est toujours la même restent comme tel. Ceux pour lesquels il y a plusieurs casses possiblent doivent être mis sous forme standard.
