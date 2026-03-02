========================================================================
                       DRAGON CHESS MAZE
                    by A_Mazing Designers (Shyam and Sam)
========================================================================

PROJECT OVERVIEW
----------------
This game a is hybrid game that combines 3D first-person exploration with a custom Chess AI.
Players must navigate a procedurally generated 3D maze to find and defeat 
Dragon Minions in games of chess. Defeating minions rewards the player with additional Queens for the final Boss encounter.

TECHNICAL ASPECTS:
----------------------
1. Graphics Engine:
   - 3D World: Rendered using ModernGL (OpenGL 3.3 core profile) with custom Vertex and Fragment shaders.
   - 2D UI: A layered system where Pygame surfaces are converted into 
     OpenGL textures and rendered as a HUD overlay.

2. Procedural Generation:
   - The maze is generated using a recursive backtracking algorithm.

3. Chess AI Engine:
   - Negamax (previously Minimax) Algorithm: The Dragon AI uses a recursive search algorithm with Alpha-Beta pruning to calculate moves in the least amount of time required.
   - Performance: High-speed move validation is handled using Numba JIT.
   - Move validation is implemented using bitwise logic, optimized loops using numba, and numpy vector operations.

4. Uses OOP:
    - This project uses object-oriented programming to structure all major game systems.
    - There is class inheritance for the different scenes, map-generation and the UI classes.

FEATURES
--------
- Procedurally generated 3D maze
- Chess battles powered by Minimax AI
- Boss battle progression system
- Customizable maze color themes
- 3D rendering using ModernGL shaders

WHAT I LEARNED
--------------
- OpenGL shader programming
- AI search algorithms
- Procedural generation techniques
- Object-oriented architecture
- Performance optimization using Numba

CONTROLS
--------
- MOVEMENT: WASD or Arrow Keys
- CAMERA: Mouse
- TOGGLE MOUSE LOCK: [ESC]
- CHESS ACTIONS: Left-Click pieces and destination squares
- SURRENDER BATTLE: Q or click the SURRENDER button (In the Chess Game)

HOW TO PLAY
-----------
1. Run the main.py file. 
2. When the program is started, a built-in installer script runs. In case the libraries are not installed, the player has to press enter to install the libraries. 
3. Customization: At the start screen, use the RGB Sliders to customize the colors of your Maze Walls and Dragon Portals.
4. Also, there is a difficulty slider that controls how much time the dragon (Chess AI) has to think, so the max (rightest) will give it an extra 15 seconds,
   whereas the minimum will give it only a fraction of a second.
5. Exploration: Enter the maze and find Purple Portals or the color you chose. Walk into them to start a Chess Battle.
6. Strategize: Defeat at least 2 Minions to unlock the Boss Portal.
   5.1 To defeat dragons, the player have to go through portals (try moving in them if it does not teleport the player in 5 seconds)
   5.2 The player can surrender or accept defeat if the game is too long, but that will cost a life. You can surrender by pressing Q or the surrender button.
7. Super Mode: If you defeat more than the minimum number of dragons (2), you will receive extra Queens to help you against the King Dragon!
8. Win: Checkmate the King Dragon to achieve total victory.

Note: Due to the complexity of the chess and AI initialization, there may be a brief delay when each chess battle begins.
Note 2: Due to the minimax algorithm, the last boss game is usually laggy, if the computer you are playing on cannot handle the lag, then on line 34ish of the dragon.py file change the dragon depth=4 parameter to depth=3 (it is commented there)

DEPENDENCIES
------------
- Python 3.13
- Pygame
- ModernGL
- NumPy
- Numba
- Pyrr

(The built-in installer will attempt to automatically install missing dependencies if allowed)

CREDITS
-------
Developed by: Shyam and Sam
School: Old Bridge High School
Date: February 2026
Images: From https://github.com/AlejoG10/python-chess-ai-yt
Also, for the GDD, some of the several images are AI-generated, but they are credited under the images.
3d Chess pieces (in taming section):
    - https://opengameart.org/content/chess-pieces-0
    - By Clint Bellanger under CCO license

This project represents my first major implementation using object-oriented programming. I learned many concepts and techniques from the following YouTube creators:
- Coding Spot
- LeMaster Tech
- Sebastian Lague.
The links to the videos I used:
For modernGl:
- https://youtu.be/LFbePt8i0DI?si=uUN8aOSwb6jsgSu3

For Chess:
- https://youtu.be/_vqlIPDR2TU?si=0uiNtLrtIJMjF8E1
- https://youtu.be/X-e0jk4I938?si=8ku0YFi0XqQldcXE
- https://youtu.be/OpL0Gcfn4B4?si=18hJkN6JzBymSZAr