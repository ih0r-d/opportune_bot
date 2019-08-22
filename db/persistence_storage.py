import shelve
from re import match


class SaveValueError(Exception):
    def __init__(self, message):
        self.message = message
        super(SaveValueError, self).__init__('{0}'.format(self.message))


class GetValueError(Exception):
    def __init__(self, message):
        self.message = message
        super(GetValueError, self).__init__('{0}'.format(self.message))


class NoKeyError(Exception):
    def __init__(self, message):
        self.message = message
        super(NoKeyError, self).__init__('{0}'.format(self.message))


class PersistenceStorage:
    def __init__(self, database):
        self.storage = shelve.open(database)

    def create_key(self, key):
        self.storage[key] = None
        return True

    def save(self, key, value, force_save=False):
        if not self.exists(key) and force_save is False:
            raise NoKeyError('No such key: {0!s}'.format(key))
        if not self.exists(key) and force_save is True:
            self.create_key(key)
            self.save(key, value)
            return True
        if self.exists(key):
            try:
                self.storage[key] = value
                return True
            except Exception as ex:
                raise SaveValueError('{0}: {1}'.format(type(ex).__name__, 'failed to save value'))

    def get(self, key):
        if key in self.storage:
            return self.storage[key]
        else:
            raise NoKeyError('No such key in offset_storage: ' + str(key))

    def get_with_create(self, key, default):
        try:
            if key in self.storage and not None:
                value = self.storage[key]
                return value
            else:
                self.create_key(key)
                self.save(key, default)
                return default
        except Exception as ex:
            raise GetValueError(
                '{0}: {1}'.format(type(ex).__name__, 'failed to get value from offset_storage'))

    def append(self, key, value, strict=True):
        if strict and key not in self.storage:
            raise NoKeyError('No such key in offset_storage: ' + str(key))
        else:
            tmp = list(self.get_with_create(key, []))
            tmp.append(value)
            self.save(key, tmp)
            return True

    def remove(self, key, value):
        if key in self.storage:
            tmp = list(self.storage[key])
            if value in tmp:
                tmp.remove(value)
            self.save(key, tmp)
            return True
        else:
            raise NoKeyError('No such key in offset_storage: ' + str(key))

    def find_all(self, pattern):
        keys = self.storage.keys()
        result = []
        for k in keys:
            if match(pattern, k):
                result.append(k)
        return result

    def find_single(self, pattern):
        keys = self.storage.keys()
        for k in keys:
            if match(pattern, k):
                return k
        else:
            return None

    def exists(self, key):
        if key in self.storage.keys():
            return True
        else:
            return False

    def close(self):
        self.storage.close()
