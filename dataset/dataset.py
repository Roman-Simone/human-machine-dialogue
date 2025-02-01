import logging
import pandas as pd

class MegaGymDataset:
    def __init__(self, csv_file="megaGymDataset/megaGymDataset.csv"):
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
                continue
            elif isinstance(value, dict):
                for slot_key, slot_value in value.items():
                    if slot_value is not None and slot_value != "null":
                        if slot_key == "title":
                            data_ret = self.filter_by_title(slot_value, data=data_ret)
                        elif slot_key == "level":
                            data_ret = self.filter_by_level(slot_value, data=data_ret)
                        elif slot_key == "type":
                            data_ret = self.filter_by_type(slot_value, data=data_ret)
                        elif slot_key == "body_part":
                            data_ret = self.filter_by_body_part(slot_value, data=data_ret)
                        elif slot_key == "equipment":
                            data_ret = self.filter_by_equipment(slot_value, data=data_ret)
                        elif slot_key == "rating":
                            data_ret = self.filter_by_rating(slot_value[0], slot_value[1], data=data_ret)
        
        data_ret_str = data_ret.to_string()
        
        return data_ret_str

    
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
            ret = self.data[self.data['Body Part'].str.lower() == body_part.lower()]
        else:
            ret = data[data['Body Part'].str.lower() == body_part.lower()]

        return ret
    
    def filter_by_equipment(self, equipment, data=None) -> pd.DataFrame:
        """Filter data by equipment."""
        if data is None:
            ret = self.data[self.data['Equipment'].str.lower() == equipment.lower()]
        else:
            ret = data[data['Equipment'].str.lower() == equipment.lower()]

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
    dataset = ExerciseDataset("dataset/megaGymDataset/megaGymDataset.csv")  # Sostituisci con il tuo file
    
    # Mostra tutti gli esercizi
    print(dataset.get_all_exercises())
    
    # Filtra per titolo
    print(dataset.filter_by_title("plank"))
    
    # Filtra per livello
    print(dataset.filter_by_level("Intermediate"))
    
    # Filtra per tipo
    print(dataset.filter_by_type("Strength"))
    
    # Filtra per parte del corpo
    print(dataset.filter_by_body_part("Abdominals"))
    
    # Filtra per attrezzatura
    print(dataset.filter_by_equipment("Bands"))
    
    # Filtra per rating
    print(dataset.filter_by_rating(min_rating=7, max_rating=10))
