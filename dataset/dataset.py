import csv
import json
import logging
import pandas as pd
from copy import deepcopy
from rapidfuzz import process

class MegaGymDataset:
    '''
    MegaGymDataset class to handle the dataset of exercises.
    '''

    def __init__(self, csv_file="dataset/megaGymDataset/megaGymDataset.csv"):
        """
        MegaGymDataset class constructor
        """
        self.path_csv = csv_file
        self.data = pd.read_csv(self.path_csv )
        self.logger = logging.getLogger(__name__)
        self.limit = len(self.data)


    def filter_by_intent(self, intent:dict, num_max_exercise = 5) -> str:
        '''
        General filter function to filter the dataset by the intent.
        
        Args:
            intent (dict): dictionary with the intent to filter the dataset.
            num_max_exercise (int): maximum number of exercises to return.
        
        Returns:
            data_ret_str (str): string with the filtered exercises in JSON format.
        '''

        data_ret = deepcopy(self.data)

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
        
        if len(data_ret) == 0:
            return False

        if len(data_ret) > 5:
            data_ret = data_ret.sample(5)

        data_ret_str = self.format_json(data_ret)
        
        return data_ret_str


    def get_schedule(self, intent:dict) -> str:
        '''
        Function to get a workout schedule. 
        Return 4 exercises: 2 strength, 1 stretching, 1 cardio.
        
        Args:
            intent (dict): dictionary with the intent to filter the dataset.
        
        Returns:
            ret (str): string with the workout schedule in JSON format.
        '''
        
        data_ret = self.data

        for key, value in intent.items():
            if value is None:
                continue
            elif isinstance(value, str):
                if value is not None and value != "null":
                    if key == "level":
                        data_ret = self.filter_by_level(value, data=data_ret)
                    elif key == "rating":
                        data_ret = self.filter_by_rating(value[0], value[1], data=data_ret)
        

        # Number of sessions requested
        n_sessions = intent.get("n_session", 1)
        try:
            n_sessions = int(n_sessions)
        except ValueError:
            n_sessions = 1  # Default to 1 session if invalid input

        schedule = []

        for _ in range(n_sessions):
            session = {
                "strength": self.format_json(self.filter_by_type(exercise_type="Strength", data=data_ret).sample(2)),
                "stretching": self.format_json(self.filter_by_type(exercise_type="Stretching", data=data_ret).sample(1)),
                "cardio": self.format_json(self.filter_by_type(exercise_type="Cardio", data=data_ret).sample(1))
            }
            schedule.append(session)

        if len(schedule) == 0:
            return False

        ret = json.dumps({"sessions": schedule}, indent=4)

        return ret


    def save_exercise(self, intent: dict) -> str:
        '''
        Function to save an exercise in the dataset.
        
        Args:
            intent (dict): dictionary with the intent to save the exercise.
            
        Returns:
            str: string with the result of the operation.
        '''

        new_exercise = {
            "Id": len(self.data),
            "Title": intent.get("title"),
            "Desc": intent.get("description"),
            "Type": intent.get("type"),
            "BodyPart": intent.get("body_part"),
            "Equipment": intent.get("equipment"),
            "Level": intent.get("level"),
            "Rating": intent.get("rating"),
            "Duration": intent.get("duration")
        }

        new_df = pd.DataFrame([new_exercise])

        new_df = new_df.dropna(axis=1, how='all')

        if not self.data.empty and "Id" in self.data.columns:
            new_df["Id"] = self.data["Id"].max() + 1
        else:
            new_df["Id"] = 1  # Assign ID 1 if data is empty

        if not new_df.empty:
            self.data = pd.concat([self.data, new_df], ignore_index=True)

        self.data.to_csv(self.path_csv, index=False, quoting=csv.QUOTE_MINIMAL)

        return "Exercise saved successfully."


    def add_favorite(self, intent: dict, threshold = 95) -> str:
        '''
        Function to add an exercise to the favorite list.

        Args:
            intent (dict): dictionary with the intent to add the exercise to the favorite list.

        Returns:
            str: string with the result of the operation.
        '''
        title = intent.get("title")

        data = deepcopy(self.data)

        flag_find = False

        while(not flag_find):

            matches = process.extract(title, data['Title'], score_cutoff=threshold, limit = self.limit)
            matched_titles = [match[0] for match in matches]
            ret = data[data['Title'].isin(matched_titles)]

            if len(ret) == 0:
                if threshold <= 65:
                    break
                threshold -= 5
            elif len(ret) > 5:
                if threshold >= 100:
                    break
                threshold += 3
            else:
                flag_find = True
        
        if not ret.empty:
            if not ret.empty:
                self.data.loc[data['Title'].isin(ret['Title']), 'Favorite'] = True  # Update the original data
                self.data.to_csv(self.path_csv, index=False)  # Save the updated data
                self.data = pd.read_csv(self.path_csv)  # Reload the updated data
            
        return flag_find


    def remove_favorite(self, intent: dict, threshold = 70) -> str:
        '''
        Function to remove an exercise from the favorite list.
        
        Args:
            intent (dict): dictionary with the intent to remove the exercise from the favorite list.
        
        Returns:
            str: string with the result of the operation.
        '''

        title = intent.get("title")

        data = deepcopy(self.data)

        flag_find = False

        while(not flag_find):

            matches = process.extract(title, data['Title'], score_cutoff=threshold, limit = self.limit)
            matched_titles = [match[0] for match in matches]
            ret = data[data['Title'].isin(matched_titles)]

            if len(ret) == 0:
                if threshold <= 65:
                    break
                threshold -= 5
            elif len(ret) > 5:
                if threshold >= 100:
                    break
                threshold += 3
            else:
                flag_find = True
        
        if not ret.empty:
            if not ret.empty:
                self.data.loc[data['Title'].isin(ret['Title']), 'Favorite'] = False
                self.data.to_csv(self.path_csv, index=False)  # Save the updated data
                self.data = pd.read_csv(self.path_csv)  # Reload the updated data
        
        return flag_find


    def list_favorite(self, intent: dict) -> str:
        '''
        Function to list the favorite exercises.
        
        Args:
            intent (dict): dictionary with the intent to list the favorite exercises.
        
        Returns:
            str: string with the favorite exercises in JSON format.
        '''

        data = self.data[self.data['Favorite'] == True]
        # filter also by type and body part
        if intent.get("type") is not None:
            data = self.filter_by_type(intent.get("type"), data=data)
        if intent.get("body_part") is not None:
            data = self.filter_by_body_part(intent.get("body_part"), data=data)

        return self.format_json(data)
    

    def format_json(self, data:pd.DataFrame) -> str:
        '''
        Function to format the dataset in JSON format.
        
        Args:  
            data (pd.DataFrame): dataset to format.
        
        Returns:
            str: string with the formatted dataset in JSON format.
        '''

        formatted_exercises = []

        original_json = data.to_dict()

        for key in original_json["Id"]:
            exercise = {
                "id": key,
                "title": original_json["Title"].get(key),
                "description": original_json["Desc"].get(key),
                "type": original_json["Type"].get(key),
                "body_part": original_json["BodyPart"].get(key),
                "equipment": original_json["Equipment"].get(key),
                "level": original_json["Level"].get(key),
                "rating": original_json["Rating"].get(key)
            }
            formatted_exercises.append(exercise)

        # Output formatted JSON
        formatted_json = {"exercises": formatted_exercises}

        # Print result
        str_ret = json.dumps(formatted_json, indent=4)

        return str_ret


    def get_all_exercises(self):
        """Return all exercises."""
        return self.data


    def filter_by_title(self, title, data=None, threshold = 97) -> pd.DataFrame:
        """Filter data by title."""
        if data is None:
            data = self.data

        flag_find = False

        while(not flag_find):

            matches = process.extract(title, data['Title'], score_cutoff=threshold, limit = self.limit)
            matched_titles = [match[0] for match in matches]
            ret = data[data['Title'].isin(matched_titles)]

            if len(ret) == 0:
                if threshold <= 30:
                    break
                threshold -= 5
            elif len(ret) > 5:
                if threshold >= 100:
                    break
                threshold += 3
            else:
                flag_find = True

        return ret


    def filter_by_level(self, level, data=None, threshold = 80) -> pd.DataFrame:
        """Filter data bu level."""
        if data is None:
            data = self.data
        
        matches = process.extract(level, data['Level'], score_cutoff=threshold, limit = self.limit)
        matched_levels = [match[0] for match in matches]

        ret = data[data['Level'].isin(matched_levels)]
        
        return ret


    def filter_by_type(self, exercise_type, data=None, threshold = 80) -> pd.DataFrame:
        """Filter data by type."""
        if data is None:
            data = self.data
        
        matches = process.extract(exercise_type, data['Type'], score_cutoff=threshold, limit = self.limit)
        matched_types = [match[0] for match in matches]
        ret = data[data['Type'].isin(matched_types)]

        return ret


    def filter_by_body_part(self, body_part, data=None, threshold = 80) -> pd.DataFrame:
        """Filter data by body part."""
        if data is None:
            data = self.data
        
        matches = process.extract(body_part, data['BodyPart'], score_cutoff=threshold, limit = self.limit)
        matched_body_parts = [match[0] for match in matches]
        ret = data[data['BodyPart'].isin(matched_body_parts)]

        return ret


    def filter_by_equipment(self, equipment, data=None, threshold = 60) -> pd.DataFrame:
        """Filter data by equipment."""
        if data is None:
            data = self.data

        matches = process.extract(equipment, data['Equipment'], score_cutoff=threshold, limit = self.limit)
        matched_equipment = [match[0] for match in matches]
        ret = data[data['Equipment'].isin(matched_equipment)]

        return ret


    def filter_by_rating(self, min_rating=0, data=None) -> pd.DataFrame:
        """Filter data by rating."""
        if data is None:
            data = self.data
        
        ret = data[(int(data['Rating']) >= int(min_rating))]

        return ret


# Example
if __name__ == "__main__":
    dataset = MegaGymDataset("dataset/megaGymDataset/megaGymDataset.csv")  # Sostituisci con il tuo file
    
    # # Mostra tutti gli esercizi
    # print(dataset.get_all_exercises())
    
    # Filtra per titolo
    # print(dataset.filter_by_title("Roll-Out"))
    
    # # Filtra per livello
    # print(dataset.filter_by_level("Intermediate"))
    
    # # Filtra per tipo
    # print(dataset.filter_by_type("Strength"))
    
    # Filtra per parte del corpo
    # print(dataset.filter_by_body_part(body_part="Chest"))
    
    # # Filtra per attrezzatura
    # print(dataset.filter_by_equipment("Bands"))
    
    # # Filtra per rating
    # print(dataset.filter_by_rating(min_rating=7, max_rating=10))


    # test add_favorite
    intent = {"title": "oregvfibgviwebvidshvbidsvbsivbsibvsivbisbvdisubvsivbsiuvsi"}
    print(dataset.add_favorite(intent))
