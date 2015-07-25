class BaseSettings(object):
    SECRET_KEY = '#1?m3m+1d9#0md40$41!idm410nd18nJ1301j380n83n%1dn3&011*30'

    DEBUG = False
    TESTING = False


class DevelopmentSettings(BaseSettings):
    DEBUG = True


class ProductionSettings(BaseSettings):
    pass
