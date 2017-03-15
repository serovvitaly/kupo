from abc import ABCMeta, abstractmethod, abstractproperty
import urllib.request


class AbstractOffer:
    """
    Базовый класс для всех моделей офферов
    is_valid - правильно ли заполнен оффер
    title - заголовок оффера
    revision_at - время ревизии
    """
    def __init__(self):
        self.url = None
        self.is_valid = False
        self.title = None
        self.rules = None
        self.likes_count = None
        self.purchases_count = None
        self.revision_at = None


class AbstractProvider:
    __metaclass__ = ABCMeta

    def get_content_by_url(self, url):
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request) as f:
            return f.read().decode('utf-8')

    @abstractproperty
    def find(self):
        pass
