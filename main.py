from core.engine import GameEngine
from stages.start import StartScreen

def main():
    engine = GameEngine()
    engine.run(StartScreen(engine))

if __name__ == "__main__":
    main()
