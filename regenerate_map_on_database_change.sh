db_file="qso_database.sqlite"
output_file="map.png"
xml_file="cty.xml"

while true; do
    #wait for database to change
    /usr/bin/inotifywait --event modify $db_file

    #regenerate map
    echo "Regenerate map"
    /usr/bin/python3 generate_map_from_qsos.py --db-file=$db_file --output-file=$output_file --prefix-xml-file=$xml_file
done
