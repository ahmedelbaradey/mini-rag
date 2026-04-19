import os
import re

from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
from .ProjectController import ProjectController 


class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576 
    
    def validate_uploaded_file(self,file:UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False ,ResponseSignal.FILE_TYPE_NOT_SUPPORTED
        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale :
            return False , ResponseSignal.FILE_SIZE_EXCEEDED
        return True , ResponseSignal.FILE_VALIDATED_SUCCESS
    
    
    def generate_unique_filename(self, original_file_name:str , project_id:str):
        random_file_name = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)
        cleaned_file_name = self.get_clean_file_name(original_file_name= original_file_name)
        new_file_path = os.path.join (
            project_path ,
            random_file_name + "_" + cleaned_file_name
        )
        
        while os.path.exists(new_file_path):
             random_file_name = self.generate_random_string()
             new_file_path = os.path.join(
                 project_path ,
                 random_file_name + "_" + cleaned_file_name
             )
        return new_file_path ,random_file_name + "_" + cleaned_file_name
            


    def get_clean_file_name (self,original_file_name:str):
        cleaned_file_name = re.sub(r'[^\w.]','',original_file_name)
        cleaned_file_name = cleaned_file_name.replace(" ","_")
        return cleaned_file_name
    



        