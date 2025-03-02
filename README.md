# 🎮 Pivy a simple ECS for Python

Welcome to my first ECS (Entity-Component-System) library for Python! 🚀 This project is designed for my personal use and is not intended to be a perfect or highly optimized solution. I'm still learning and improving, so don't expect industry-level standards. However, the goal is to keep it **simple, easy to use**, and to make **game development enjoyable**. 😊

---

## 📂 Project Structure

This repository serves as a **template** for structuring a game using this ECS. To get started, simply clone this repo and use it as a base for your project.

```
📦 my_game
 ┣ 📂 assets/          # 🎨 Sprites, sounds, fonts, etc.
 ┣ 📂 src/             # 📜 Game source code
 ┃ ┣ 📂 components/    # 🏗️ ECS components
 ┃ ┣ 📂 systems/       # 🔄 ECS systems
 ┃ ┣ 📂 scenes/        # 🎭 Game scenes
 ┃ ┣ 📂 events/        # 📢 Custom events
 ┃ ┣ 📂 core/          # 🛠️ ECS configuration and utilities
 ┃ ┃ ┣ __init__.py
 ┃ ┃ ┣ app.py          # 🎮 Main ECS setup
 ┃ ┃ ┗ game.py         # 🚀 Game entry point
 ┣ 📜 main.py          # 🏁 Run the game
 ┣ 📜 config.json      # ⚙️ General configuration (optional)
 ┗ 📜 README.md        # 📖 Project description
```

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/your-username/ecs-python-game-template.git
cd ecs-python-game-template
```

### 2️⃣ Install Dependencies (if any)
This ECS is built in pure Python, but if you need additional libraries (e.g., `pygame` for rendering), install them:
```sh
pip install pygame
```

### 3️⃣ Run the Game
```sh
python main.py
```

---

## 🏗️ How to Use the ECS

### ✨ Creating a Component
All components are simple classes that store data.
```python
# src/components/transform.py
class Transform:
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y
```

### 🔄 Creating a System
Systems are functions that process entities with specific components.
```python
# src/systems/movement.py
from core.ecs import debug_system

@debug_system  # Logs system execution
def movement_system(commands, query, event_bus):
    for entity in query.filter(Transform, Velocity):
        transform, velocity = query.get_all(entity, Transform, Velocity)
        transform.x += velocity.dx
        transform.y += velocity.dy
```

### 🎭 Creating a Scene
Scenes set up entities and components.
```python
# src/scenes/main_scene.py
def load_main_scene(app):
    player = app._commands.create_entity()
    app._commands.add_component(player, Transform(100, 200))
    app._commands.add_component(player, Velocity(2, 0))
```

### 🎮 Setting Up the Game
This is where everything comes together.
```python
# src/core/app.py
from core.ecs import App, SystemPhase
from systems.movement import movement_system
from scenes.main_scene import load_main_scene

def create_game():
    app = App()
    load_main_scene(app)
    app.add_systems(SystemPhase.UPDATE, movement_system)
    return app
```

### 🏁 Running the Game
The main entry point:
```python
# main.py
from core.app import create_game

if __name__ == "__main__":
    app = create_game()
    app.init()
    while True:
        app.update()
        app.draw()
```

---

## ❤️ Why Use This ECS?
✔ **Simple & beginner-friendly** – No complex setup or boilerplate.
✔ **Lightweight** – Pure Python, minimal dependencies.
✔ **Encourages modular design** – Clean separation of concerns.
✔ **Fun to use!** – Game development should be enjoyable. 😊

This ECS is not designed for high performance but rather for **ease of use** and **quick prototyping**. If you need something more optimized, consider engines like Unity, Godot.

---

## 🎯 Future Improvements
Since this is my first ECS, expect it to evolve over time! Some features I might add:
- 🛠️ More built-in utilities
- 🎨 Simple rendering system (probably using `pygame`, `Panda3D` or `raylib`)
- 🔧 Better debugging tools
- 📜 More documentation & examples

---

## 📢 Feedback & Contributions
This project is primarily for **personal use**, but if you find it helpful, feel free to use it! Suggestions are welcome, but keep in mind that I am still learning. 😃

If you have ideas or improvements, feel free to **open an issue** or **fork the project**.

---

### 📌 License
This project is under the MIT License – free to use and modify.

---

Thank you for checking out my first ECS! 🚀 Happy coding! 🎮