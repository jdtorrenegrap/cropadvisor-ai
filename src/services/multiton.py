class MultitonMeta(type):
    """Metaclase para implementar el patrón Multiton."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        # Usa el `model_path` como clave para identificar instancias únicas
        key = kwargs.get('model_path', None)
        if key is None:
            raise ValueError("Se requiere un 'model_path' para usar el patrón Multiton.")
        
        if key not in cls._instances:
            # Si no existe una instancia para esta clave, créala
            instance = super().__call__(*args, **kwargs)
            cls._instances[key] = instance
   
        return cls._instances[key]