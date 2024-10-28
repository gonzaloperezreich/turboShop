from flask import Flask, request, jsonify
import spacy
from difflib import get_close_matches
from flask_cors import CORS

# Load the spaCy model
output_dir = "./modelo_repuestos_ner"
nlp = spacy.load(output_dir)

app = Flask(__name__)
# Configure CORS properly
CORS(app)
valid_combinations = {
    "toyota": ["corolla", "hilux", "rav4", "yaris", "fortuner", "land cruiser", "c-hr"],
    "nissan": ["navara", "x-trail", "kicks", "qashqai", "versa", "sentra", "march"],
    "hyundai": ["accent", "creta", "tucson", "santa fe", "i10", "i20", "kona","sonata", "genesis"],
    "kia": ["rio", "sportage", "seltos", "cerato", "sorento", "carnival", "picanto"],
    "chevrolet": ["sail", "onix", "tracker", "groove", "spark", "captiva", "equinox"],
    "suzuki": ["baleno", "vitara", "swift", "celerio", "s-presso", "jimny", "alto"],
    "ford": ["ranger", "everest", "escape", "explorer", "bronco", "f-150"],
    "mazda": ["cx-5", "mazda3", "cx-30", "mazda2", "cx-9", "bt-50"],
    "volkswagen": ["gol", "voyage", "tiguan", "amarok", "polo", "vento", "golf"],
    "renault": ["duster", "koleos", "stepway", "capture", "kwid", "symbol"],
    "subaru": ["forester", "outback", "crosstrek", "wrx", "legacy", "ascent"],
    "volvo": ["xc90", "xc60", "s60", "v60", "xc40"],
    "bmw": ["3 series", "x1", "x3", "x5", "2 series", "4 series"],
    "audi": ["a3", "q2", "q3", "a4", "q5", "a6"],
    "mercedes-benz": ["a-class", "c-class", "e-class", "glc", "gle"],
    "peugeot": ["208", "2008", "3008", "5008", "partner"],
    "fiat": ["500", "mobi", "strada", "fiorino"],
    "jeep": ["compass", "renegade", "wrangler", "grand cherokee"],
    "chery": ["tiggo 2", "tiggo 3", "tiggo 7", "arrizo 5"],
    "ssangyong": ["korando", "rexton", "musso", "actyon", "tivoli"]
}

def get_closest_brand(brand):
    """Find the closest matching brand from valid_combinations."""
    if brand.lower() in valid_combinations:
        return brand.lower()
    
    matches = get_close_matches(brand.lower(), valid_combinations.keys(), n=1, cutoff=0.7)
    if matches:
        return matches[0]
    return brand

def get_closest_model(brand, model):
    """Find the closest matching model for a given brand."""
    if brand in valid_combinations:
        matches = get_close_matches(model, valid_combinations[brand], n=1, cutoff=0.7)
        if matches:
            return matches[0]
    return model

def find_brand_by_model(model):
    """Find brand by exact model match."""
    for brand, models in valid_combinations.items():
        if model in models:
            return brand
    return None

def preprocess_text(text):
    """Preprocess text to correct potential brand misspellings."""
    words = text.split()
    processed_words = []
    
    for word in words:
        # Check if this word might be a brand
        closest_brand = get_closest_brand(word)
        if closest_brand in valid_combinations:
            processed_words.append(closest_brand)
        else:
            processed_words.append(word)
    
    return " ".join(processed_words)

def process_text_in_cases(text):
    """Process text in different cases after preprocessing."""
    # Preprocess the text first
    preprocessed_text = preprocess_text(text)
    
    lower_doc = nlp(preprocessed_text.lower())
    upper_doc = nlp(preprocessed_text.upper())
    mixed_doc = nlp(preprocessed_text)
    return [lower_doc, upper_doc, mixed_doc]

@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        texts = data.get("texts", [])
        if not texts:
            return jsonify({"error": "No texts provided"}), 400

        saved_entities = []

        for text in texts:
            docs = process_text_in_cases(text)
            entities = {"BRAND": None, "MODEL": [], "YEAR": None, "DATES": [], "DISPLACEMENT": None}

            for doc in docs:
                for ent in doc.ents:
                    if ent.label_ == "BRAND":
                        # Apply fuzzy matching to detected brand
                        closest_brand = get_closest_brand(ent.text)
                        if closest_brand in valid_combinations:
                            entities["BRAND"] = closest_brand
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
                    closest_model = get_closest_model(brand, model)
                    if closest_model in valid_combinations[brand]:
                        valid_pairs.append((brand, closest_model))

            combined_description = f"{entities['YEAR'] or ''} {entities['DISPLACEMENT'] or ''}".strip()
            
            saved_entities.append({
                "text": text,
                "valid_combinations": valid_pairs,
                "description": combined_description,
                "dates": entities["DATES"]
            })

        return jsonify(saved_entities)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500)