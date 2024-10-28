from flask import Flask, request, jsonify
import spacy
from difflib import get_close_matches

# Load the spaCy model
output_dir = "./modelo_repuestos_ner"
nlp = spacy.load(output_dir)

# Dictionary of valid brand-model combinati

app = Flask(__name__)
valid_combinations = {
    "toyota": ["corolla", "camry", "hilux", "rav4", "prius", "land cruiser", "fortuner", "yaris", "avensis", "c-hr"],
    "nissan": ["altima", "sentra", "rogue", "np300", "micra", "leaf", "juke", "x-trail", "maxima", "murano"],
    "hyundai": ["elantra", "sonata", "tucson", "santafe", "kona", "i30","i10", "veloster", "accent", "palisade", "ioniq"],
    "kia": ["sportage", "seltos", "optima", "rio", "sorento", "cerato", "niro", "carnival", "stinger", "picanto"],
    "chevrolet": ["spark", "malibu", "tracker", "camaro", "cruze", "s10", "captiva", "trailblazer", "equinox", "suburban"],
    "suzuki": ["swift", "vitara", "baleno", "s-cross", "jimny", "alto", "ignis", "celerio", "every", "gran vitara"],
    "ford": ["focus", "fiesta", "explorer", "mustang", "edge", "f-150", "escape", "fusion", "maverick", "bronco"],
    "mazda": ["cx-5", "mazda3", "mazda6", "cx-30", "mx-5", "cx-9", "mazda2", "rx-8", "b-series", "mx-30"],
    "volkswagen": ["golf", "jetta", "tiguan", "passat", "polo", "arteon", "id.4", "cc", "beetle", "touran"],
    "renault": ["clio", "kwid", "duster", "captur", "megane", "koleos", "talisman", "sandero", "laguna", "scenic"],
    "subaru": ["outback", "forester", "wrx", "ascent", "crosstrek", "legacy", "impreza", "brz", "tribeca", "solterra"],
    "volvo": ["xc90", "xc60", "s60", "v60", "s90", "v90", "xc40", "s40", "c30", "s80"],
    "bmw": ["3 series", "5 series", "x5", "x3", "x1", "m3", "m5", "4 series", "2 series", "7 series"],
    "audi": ["a3", "a4", "q5", "q7", "a6", "a8", "tt", "q3", "q8", "s4"],
    "mercedes-benz": ["c-class", "e-class", "s-class", "gle", "glc", "a-class", "b-class", "gls", "sl", "amg"],
    "peugeot": ["208", "308", "508", "3008", "5008", "partner", "expert", "boxer", "rcz", "3008 hybrid"],
    "fiat": ["500", "panda", "tipo", "ducato", "punto", "freemont", "linea", "lancia", "freemont", "strada"],
    "jaguar": ["f-type", "xe", "xf", "xj", "f-pace", "e-pace", "i-pace", "xk", "s-type", "x-type"],
    "land rover": ["range rover", "discovery", "defender", "discovery sport", "rangerover velar", "evoque", "freelander", "series", "defender 90", "defender 110"],
    "tesla": ["model s", "model 3", "model x", "model y", "roadster", "cybertruck", "model s plaid", "model 3 performance", "model x plaid", "model y long range"],
    "lamborghini": ["huracan", "aventador", "urus", "gallardo", "veneno", "sián", "estoque", "jalpa", "murciélago", "reventón"],
    "ferrari": ["488", "roma", "portofino", "f8 tributo", "sf90 stradale", "812 superfast", "gto", "california", "f12 berlinetta", "monza"],
    "porsche": ["911", "cayenne", "macan", "panamera", "taycan", "boxster", "cayman", "918 spyder", "targa", "944"],
    "bugatti": ["chiron", "veyron", "divo", "centodieci", "bugatti bolide", "la voiture noire", "bugatti pur sang", "bugatti eb110", "chiron sport", "chiron super sport"],
    "aston martin": ["db11", "vantage", "dbs", "rapide", "valkyrie", "dbx", "one-77", "vantage roadster", "virage", "lagonda"],
    "genesis": ["g80", "g70", "gv80", "gv70", "g90", "essentia", "x-85", "g70 shooting brake", "g90 ultimate", "g80 sport"],
}
# Función para encontrar el modelo más cercano válido dentro de una marca específica
def get_closest_model(brand, model):
    if brand in valid_combinations:
        # Buscar la coincidencia más cercana del modelo dentro de la marca
        matches = get_close_matches(model, valid_combinations[brand], n=1, cutoff=0.7)
        if matches:
            return matches[0]
    return model  # Si no hay coincidencia, devolver el modelo original

# Función para buscar la marca en base al modelo si no hay marca en el texto
def find_brand_by_model(model):
    for brand, models in valid_combinations.items():
        if model in models:
            return brand
    return None

# Procesar el texto en diferentes casos (minúsculas, mayúsculas, mixto)
def process_text_in_cases(text):
    lower_doc = nlp(text.lower())
    upper_doc = nlp(text.upper())
    mixed_doc = nlp(text)
    return [lower_doc, upper_doc, mixed_doc]

app = Flask(__name__)

# Función para encontrar el modelo más cercano válido dentro de una marca específica
def get_closest_model(brand, model):
    if brand in valid_combinations:
        matches = get_close_matches(model, valid_combinations[brand], n=1, cutoff=0.7)
        if matches:
            return matches[0]
    return model

# Función para buscar la marca en base al modelo si no hay marca en el texto
def find_brand_by_model(model):
    for brand, models in valid_combinations.items():
        if model in models:
            return brand
    return None

# Procesar el texto en diferentes casos (minúsculas, mayúsculas, mixto)
def process_text_in_cases(text):
    lower_doc = nlp(text.lower())
    upper_doc = nlp(text.upper())
    mixed_doc = nlp(text)
    return [lower_doc, upper_doc, mixed_doc]

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    texts = data.get("texts", [])
    saved_entities = []

    for text in texts:
        docs = process_text_in_cases(text)
        entities = {"BRAND": None, "MODEL": [], "YEAR": None, "DATES": [], "DISPLACEMENT": None}

        for doc in docs:
            for ent in doc.ents:
                if ent.label_ == "BRAND" and ent.text.lower() in valid_combinations:
                    entities["BRAND"] = ent.text.lower()
                elif ent.label_ == "MODEL":
                    entities["MODEL"].append(ent.text.lower())
                elif ent.label_ == "YEAR":
                    entities["YEAR"] = ent.text
                elif ent.label_ == "DATE":
                    entities["DATES"].append(ent.text)
                elif ent.label_ == "DISPLACEMENT":
                    entities["DISPLACEMENT"] = ent.text

        valid_pairs = []
        brand = entities["BRAND"]

        if not brand and entities["MODEL"]:
            for model in set(entities["MODEL"]):
                brand = find_brand_by_model(model)
                if brand:
                    closest_model = get_closest_model(brand, model)
                    valid_pairs.append((brand, closest_model))
        elif brand:
            for model in set(entities["MODEL"]):
                if model in valid_combinations[brand]:
                    valid_pairs.append((brand, model))
                else:
                    closest_model = get_closest_model(brand, model)
                    if closest_model in valid_combinations[brand]:
                        valid_pairs.append((brand, closest_model))

        # Concatenate year and displacement into the description field
        combined_description = f"{entities['YEAR'] or ''} {entities['DISPLACEMENT'] or ''}".strip()
        
        saved_entities.append({
            "text": text,
            "valid_combinations": valid_pairs,
            "description": combined_description,  # Year and displacement combined
            "dates": entities["DATES"]
        })

    return jsonify(saved_entities)

if __name__ == '__main__':
    app.run(port=5000)