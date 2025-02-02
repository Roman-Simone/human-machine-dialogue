import json
import logging
import pandas as pd

class MegaGymDataset:
    def __init__(self, csv_file="dataset/megaGymDataset/megaGymDataset.csv"):
        """
        Inizializza il dataset caricando il file CSV.
        """
        self.data = pd.read_csv(csv_file)
        self.logger = logging.getLogger(__name__)

    def filter_by_intent(self, intent:dict) -> str:

        data_ret = self.data

        for key, value in intent.items():
            if value is None:
                continue
            elif isinstance(value, str):
                if value is not None and value != "null":
                    if key == "title":
                        data_ret = self.filter_by_title(value, data=data_ret)
                    elif key == "level":
                        data_ret = self.filter_by_level(value, data=data_ret)
                    elif key == "type":
                        data_ret = self.filter_by_type(value, data=data_ret)
                    elif key == "body_part":
                        data_ret = self.filter_by_body_part(value, data=data_ret)
                    elif key == "equipment":
                        data_ret = self.filter_by_equipment(value, data=data_ret)
                    elif key == "rating":
                        data_ret = self.filter_by_rating(value[0], value[1], data=data_ret)
        

        if len(data_ret) > 5:
            data_ret = data_ret.sample(5)

        data_ret_str = self.format_json(data_ret)
        
        return data_ret_str
    

    def format_json(self, data:pd.DataFrame) -> str:
        formatted_exercises = []

        original_json = data.to_json()

        for key in original_json["Unnamed: 0"]:
            exercise = {
                "id": key,
                "title": original_json["Title"].get(str(key), ""),
                "description": original_json["Desc"].get(str(key), ""),
                "type": original_json["Type"].get(str(key), ""),
                "body_part": original_json["BodyPart"].get(str(key), ""),
                "equipment": original_json["Equipment"].get(str(key), ""),
                "level": original_json["Level"].get(str(key), ""),
                "rating": original_json["Rating"].get(str(key), 0)
            }
        formatted_exercises.append(exercise)

        # Output formatted JSON
        formatted_json = {"exercises": formatted_exercises}

        # Print result
        str = json.dumps(formatted_json, indent=4)

        return str

    
    def get_all_exercises(self):
        """Return all exercises."""
        return self.data
    
    def filter_by_title(self, title, data=None) -> pd.DataFrame:
        """Filter data by title."""
        if data is None:
            ret = self.data[self.data['Title'].str.contains(title, case=False, na=False)]
        else:
            ret = data[data['Title'].str.contains(title, case=False, na=False)]
        
        return ret
    
    def filter_by_level(self, level, data=None) -> pd.DataFrame:
        """Filter data bu level."""
        if data is None:
            ret = self.data[self.data['Level'].str.lower() == level.lower()]
        else:
            ret = data[data['Level'].str.lower() == level.lower()]
        
        return ret
    
    def filter_by_type(self, exercise_type, data=None) -> pd.DataFrame:
        """Filter data by type."""
        if data is None:
            ret = self.data[self.data['Type'].str.lower() == exercise_type.lower()]
        else:
            ret = data[data['Type'].str.lower() == exercise_type.lower()]

        return ret
    
    def filter_by_body_part(self, body_part, data=None) -> pd.DataFrame:
        """Filter data by body part."""
        if data is None:
            ret = self.data[self.data['BodyPart'].str.lower() == body_part.lower()]
        else:
            ret = data[data['BodyPart'].str.lower() == body_part.lower()]

        return ret
    
    def filter_by_equipment(self, equipment, data=None) -> pd.DataFrame:
        """Filter data by equipment."""
        if data is None:
            ret = self.data[equipment.lower() in self.data['Equipment'].str.lower()]
        else:
            ret = data[data['Equipment'].str.lower().str.contains(equipment.lower(), na=False)]


        return ret
    
    def filter_by_rating(self, min_rating=0, max_rating=10, data=None) -> pd.DataFrame:
        """Filter data by rating."""
        if data is None:
            ret = self.data[(self.data['Rating'] >= min_rating) & (self.data['Rating'] <= max_rating)]   
        else:
            ret = data[(data['Rating'] >= min_rating) & (data['Rating'] <= max_rating)]

        return ret





# Example
if __name__ == "__main__":
    dataset = MegaGymDataset("dataset/megaGymDataset/megaGymDataset.csv")  # Sostituisci con il tuo file
    
    # # Mostra tutti gli esercizi
    # print(dataset.get_all_exercises())
    
    # # Filtra per titolo
    # print(dataset.filter_by_title("plank"))
    
    # # Filtra per livello
    # print(dataset.filter_by_level("Intermediate"))
    
    # # Filtra per tipo
    # print(dataset.filter_by_type("Strength"))
    
    # Filtra per parte del corpo
    print(dataset.filter_by_body_part(body_part="Chest"))
    
    # # Filtra per attrezzatura
    # print(dataset.filter_by_equipment("Bands"))
    
    # # Filtra per rating
    # print(dataset.filter_by_rating(min_rating=7, max_rating=10))
