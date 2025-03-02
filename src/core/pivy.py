from collections import defaultdict
from enum import Enum
from typing import TypeVar, Callable, Generic, Dict, List, Type
import functools

# 🔹 Entity = Identificador único para cada entidad.
type Entity = int

# 🔹 Tipo base para los Componentes.
ComponentType = TypeVar('ComponentType')

# 🛠️ Almacén genérico de componentes.
class ComponentStorage(Generic[ComponentType]):
  def __init__(self) -> None:
    super().__init__()
    self._data: Dict[Entity, Dict[str, ComponentType]] = {}

  # ➕ Agrega un componente a una entidad.
  def add(self, entity: Entity, component: ComponentType) -> None:
    if entity not in self._data:
        self._data[entity] = {}
    self._data[entity][type(component).__name__] = component

  # 🔍 Obtiene todos los componentes de una entidad.
  def get(self, entity: Entity) -> Dict[str, ComponentType] | None :
    return self._data.get(entity)

  # 🔍 Obtiene todos los componentes de todas las entidades.
  def get_all(self) -> Dict[Entity, Dict[str, ComponentType]]:
    return self._data
  
  # ❓ Verifica si una entidad tiene componentes.
  def has(self, entity: Entity) -> bool:
    return entity in self._data

  # ❌ Elimina un componente específico de una entidad.
  def remove_component(self, entity: Entity, component_name: str) -> None:
    if entity in self._data and component_name in self._data[entity]:
      del self._data[entity][component_name]

  # 🗑️ Elimina todos los componentes de una entidad.
  def remove(self, entity: Entity) -> None:
    if entity in self._data:
      del self._data[entity]


# 🏗️ Almacén de entidades.
class EntityStorage:
  def __init__(self) -> None:
    self._entity_next_id: int = 0
    self._entities: List[Entity] = []

  # ➕ Crea una nueva entidad y devuelve su ID.
  def add(self) -> Entity:
    entity = self._entity_next_id
    self._entities.append(entity)
    self._entity_next_id += 1
    return entity

  # ❌ Elimina una entidad.
  def remove(self, entity: Entity) -> None:
    self._entities.remove(entity)

# 🔔 Sistema de señales para comunicación entre partes del ECS.
class Signal:
  def __init__(self):
    self._listeners: List[Callable[..., None]] = []

  # ➕ Conecta una función a la señal.
  def connect(self, listener: Callable[..., None]):
    self._listeners.append(listener)

  # 🚀 Emite la señal y notifica a los listeners.
  def emit(self, *args, **kwargs):
    for listener in self._listeners:
      listener(*args, **kwargs)

# 📡 Bus de señales centralizado.
class SignalBus:
  def __init__(self):
    self._signals: Dict[str, Signal] = {}

  # 🔍 Obtiene una señal por nombre (la crea si no existe).
  def get_signal(self, name: str) -> Signal:
    if name not in self._signals:
      self._signals[name] = Signal()
    return self._signals[name]

# 🎮 Comandos para modificar el estado del ECS.
class Commands:
  def __init__(self, entity_storage: EntityStorage, component_storage: ComponentStorage):
    self._entity_storage = entity_storage
    self._component_storage = component_storage
    self._pending_creations: List[tuple[Entity, List[object]]] = []
    self._pending_deletions: List[Entity] = []
    self._pending_add_components: List[tuple[Entity, object]] = []
    self._pending_remove_components: List[tuple[Entity, str]] = []
    self._signal_bus = SignalBus()

  # 🔔 Obtiene una señal del sistema.
  def get_signal(self, name: str) -> Signal:
    return self._signal_bus.get_signal(name)

  # ➕ Crea una entidad con sus componentes.
  def spawn(self, *components: object) -> Entity:
    entity = self._entity_storage.add()
    self._pending_creations.append((entity, list(components)))
    return entity

  # ❌ Marca una entidad para eliminación.
  def remove_entity(self, entity: Entity) -> None:
    self._pending_deletions.append(entity)

  # ➕ Marca un componente para ser agregado a una entidad.
  def add_component(self, entity: Entity, component: object) -> None:
    self._pending_add_components.append((entity, component))

  # ❌ Marca un componente específico para eliminación.
  def remove_component(self, entity: Entity, component_name: str) -> None:
    self._pending_remove_components.append((entity, component_name))

  # 🛠️ Aplica todos los cambios pendientes.
  def apply(self) -> None:
    # 🔹 Crear entidades con sus componentes
    for entity, components in self._pending_creations:
      for component in components:
        self._component_storage.add(entity, component)
    self._pending_creations.clear()

    # 🔹 Eliminar entidades y sus componentes
    for entity in self._pending_deletions:
      self._entity_storage.remove(entity)
      if self._component_storage.has(entity):
        self._component_storage.remove(entity)  # ← Asegura que los componentes también se eliminen

    # 🔹 Agregar componentes a entidades existentes
    for entity, component in self._pending_add_components:
      self._component_storage.add(entity, component)
    self._pending_add_components.clear()

    # 🔹 Eliminar componentes específicos
    for entity, component_name in self._pending_remove_components:
      self._component_storage.remove_component(entity, component_name)
    self._pending_remove_components.clear()

# 📊 Consulta de entidades y componentes.
class Query:
  def __init__(self, component_storage: ComponentStorage):
    self._component_storage = component_storage

  # 🔍 Filtra entidades que tengan los componentes especificados.
  def filter(self, *component_types: type) -> List[Entity]:
    required_components = {comp.__name__ for comp in component_types}
    return [entity for entity, components in self._component_storage.get_all().items()
            if required_components.issubset(components.keys())]

  # 📌 Devuelve los componentes de una entidad si existen
  def get_all(self, entity: Entity, *component_types: type) -> List[object] | None:
    entity_components = self._component_storage.get(entity)
    if not entity_components:
      return None
    return [entity_components[comp.__name__] for comp in component_types if comp.__name__ in entity_components]
  
  # 📌 Devuelve el componente de una entidad si existe
  def get(self, entity: Entity, component: type) -> object | None:
    entity_components = self._component_storage.get(entity)
    if not entity_components:
      return None
    return entity_components[component.__name__]


# 🎭 Base para eventos.
class Event:
  pass

# 🚀 Sistema de ejecución de eventos.
class EventBus:
  def __init__(self):
    self._listeners: Dict[Type[Event], List[Callable[[Event], None]]] = defaultdict(list)
    self._queue: List[Event] = []

  # 📡 Suscribe un listener a un evento
  def subscribe(self, event_type: Type[Event], listener: Callable[[Event], None]) -> None:
    self._listeners[event_type].append(listener)

  # 📢 Emite un evento, agregándolo a la cola.
  def emit(self, event: Event) -> None:
    self._queue.append(event)

  # 🔄 Procesa todos los eventos en la cola.
  def process(self) -> None:
    while self._queue:
      event = self._queue.pop(0)
      for listener in self._listeners[type(event)]:
        listener(event)

# ⚙️ Tipo de función que representa un sistema.
System = Callable[[Commands, Query, EventBus], None]

def debug_system(system: System):
  """ Decorador que imprime los datos de entrada y salida del sistema. """
  @functools.wraps(system)
  def wrapper(commands, query, event_bus):
    print(f"🔍 Ejecutando sistema: {system.__name__}")
    print(f"📌 Entidades en escena: {query.filter()}")
        
    # Inspecciona eventos en la cola
    if event_bus._queue:
      print(f"📢 Eventos en cola: {[type(event).__name__ for event in event_bus._queue]}")

    # Llamar al sistema
    system(commands, query, event_bus)

    print(f"✅ Sistema {system.__name__} finalizado.\n")

  return wrapper

# 🕹️ Fases de ejecución del sistema.
class SystemPhase(Enum):
  """ 🕹️ Fases de ejecución del sistema. """
  INIT = 1             # 🚀 Inicialización.
  PREUPDATE = 2        # ⏳ Pre-actualización.
  UPDATE = 3           # 🔄 Actualización principal.
  POSTUPDATE = 4       # ✅ Post-actualización.
  DRAW = 5             # 🎨 Renderizado.
  UNLOAD = 6           # 🗑️ Liberación de recursos.

# 🎮 Aplicación principal del ECS.
class App:
  def __init__(self) -> None:
    self._system_storage: Dict[SystemPhase, List[System]] = defaultdict(list)
    self._component_storage = ComponentStorage()
    self._entity_storage = EntityStorage()
    self._commands = Commands(self._entity_storage, self._component_storage)
    self._query = Query(self._component_storage)
    self._event_bus = EventBus()

  # ➕ Agrega sistemas a una fase específica.
  def add_systems(self, phase: SystemPhase, *systems: System):
    self._system_storage[phase].extend(systems)
    return self

  # 🚀 Inicializa los sistemas de la fase INIT.
  def init(self) -> None:
    for system in self._system_storage[SystemPhase.INIT]:
      system(self._commands, self._query, self._event_bus)
    self._commands.apply()

  # 🔄 Ejecuta la lógica de actualización.
  def update(self) -> None:
    self._event_bus.process() # 📢 Procesa eventos antes de actualizar.
    for system in self._system_storage[SystemPhase.UPDATE]:
      system(self._commands, self._query, self._event_bus)
    self._commands.apply()

  # 🎨 Llama a los sistemas de renderizado.
  def draw(self) -> None:
    for system in self._system_storage[SystemPhase.DRAW]:
      system(self._commands, self._query, self._event_bus)
    self._commands.apply()
