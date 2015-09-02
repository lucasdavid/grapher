from .core import settings
from .core.settings import Development as Dev, Testing as Tes, Production as Pro

Dev.SECRET_KEY = '0A7AIJTUZ15QZFGQGLYRH04ZIEM1CIB9BLDH278UFWE7I5L001H4C9N8CQP7P55U'

settings.effective = Dev
