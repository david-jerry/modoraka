from django.db import models

class ListField(models.TextField):
    """Stores a list of IDs as a comma-separated string."""
    # def __init__(self, *args, **kwargs):
    #     self.token = kwargs.pop('token', ',')
    #     super().__init__(*args, **kwargs)

    # def to_python(self, value):
    #     if not value:
    #         return []
    #     return value.split(self.token)

    # def get_prep_value(self, value):
    #     if not value:
    #         return
    #     return self.token.join(map(str, value))

    # def add(self, obj, value):
    #     """Adds a value to the list, ensuring uniqueness."""
    #     current_list = getattr(obj, self.attname)
    #     current_list = set(current_list)  # Convert to set for efficient uniqueness check
    #     current_list.add(value)
    #     setattr(obj, self.attname, list(current_list))  # Convert back to list

    # def remove(self, obj, value):
    #     """Removes a value from the list."""
    #     current_list = getattr(obj, self.attname)
    #     current_list = [v for v in current_list if v != value]
    #     setattr(obj, self.attname, current_list)




    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._internal_value = []

    def from_db_value(self, value, expression, connection):
        if value is None:
            return []
        return value.split(',')

    def to_python(self, value):
        if isinstance(value, list):
            return value
        elif isinstance(value, str):
            return value.split(',')
        return []

    def get_prep_value(self, value):
        return ','.join(str(id) for id in value)

    def add(self, instance, id_to_add):
        if id_to_add not in self._internal_value:
            self._internal_value.append(id_to_add)
            setattr(instance, self.attname, self.get_prep_value(self._internal_value))

    def remove(self, instance, id_to_remove):
        if id_to_remove in self._internal_value:
            self._internal_value.remove(id_to_remove)
            setattr(instance, self.attname, self.get_prep_value(self._internal_value))
