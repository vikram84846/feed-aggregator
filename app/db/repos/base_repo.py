"""Abstract class  repo that list the  required abstract methods by derived classes"""


from abc import ABC, abstractmethod


class BaseRepository(ABC):

    @abstractmethod
    async def create(self):
        '''This method is used to create the record for model in database'''
        pass

    @abstractmethod
    async def get_by_id(self,id:str,include_deleted:bool):
        """ This method is used to fetch record for model from database if exists """
        pass

    @abstractmethod
    async def delete(self,id:str):
        """ This method is used to soft-delete the record for model from database if exists """
        pass

