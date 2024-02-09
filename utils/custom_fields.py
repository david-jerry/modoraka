from django.db import models

class ListField(models.TextField):
    """Stores a list of strings."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return []
        return [item.strip() for item in value.split(',')]

    def get_prep_value(self, value):
        if not value:
            return ''
        return value

    # def add(self, instance, word_to_add):
    #     current_words = getattr(instance, self.attname)
    #     if word_to_add.strip() not in current_words:
    #         current_words.append(word_to_add.strip())
    #         setattr(instance, self.attname, current_words)

    # def remove(self, instance, word_to_remove):
    #     current_words = getattr(instance, self.attname)
    #     updated_words = [word.strip() for word in current_words if word.strip() != word_to_remove.strip()]
    #     setattr(instance, self.attname, updated_words)

# class ListField(models.TextField):
#     """Stores a list of IDs as a comma-separated string."""
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     def to_python(self, value):
#         if not value:
#             return []
#         return [item.strip() for item in value.split(',')]

#     def get_prep_value(self, value):
#         if not value:
#             return ''
#         return ', '.join(str(item) for item in value)

#     def add(self, instance, word_to_add):
#         current_words = getattr(instance, self.attname)
#         if word_to_add.strip() not in current_words:
#             current_words.append(word_to_add.strip())
#             setattr(instance, self.attname, self.get_prep_value(current_words))

#     def remove(self, instance, word_to_remove):
#         current_words = getattr(instance, self.attname)
#         updated_words = [word.strip() for word in current_words if word.strip() != word_to_remove.strip()]
#         setattr(instance, self.attname, self.get_prep_value(updated_words))


