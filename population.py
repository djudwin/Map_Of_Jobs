# read 2016 city, state population data and write the data to a json file
import csv
import json
import unidecode

with open('city_state_2016.txt', "r", encoding="UTF-16") as f:
    data = csv.reader(f, delimiter='\t')

    to_json = []
    for row in data:
        for i in range(len(row)):
            row[i] = unidecode.unidecode(row[i])

        to_json.append({
                          "City": row[1],
                          "State": row[3],
                          "Population": row[4],
                          "Area": row[6], # area is in sq miles
                          "Population_Density": row[7],  # in population per sq mile
                        })
        with open("city_state_population.json", "w") as outfile:
            json.dump(to_json, outfile, indent=4)
