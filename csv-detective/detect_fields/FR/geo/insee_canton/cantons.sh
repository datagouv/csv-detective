# préparation liste des noms de cantons

csvcut -e iso8859-1 -t -c NCC canton2017.txt \
| tail -n +1 \
| sed 's/-/ /g' > cantons.txt
