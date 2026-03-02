Game Design Document: Dragon Chess Maze
By Shyam Parikh

1. #Project Overview
    This game has been a massive journey where I got to learn so much. Whether I was coding the camera via matricies or navigating in the chess AI code, I've started to realize the importance of the small things, like how a forgotten return statement can lead you to a 'extremely fun' debugging experience - definately not sarcasm. Dragon Chess Maze is where I learned OOP, graphics via the GPU, and much more. It is a hybrid world where exploration and simulation collide.

2. Core Loop:
    2.1 Exploring the Unknown
        The vision included a myster, randomly generated maze that the player had to navigate.
        - Recursive Bactracking: When you begin the maze, it is created via a depth-first search algorithm.
        - To optimize on time, I explored the numba (njit) to make it run as fast as possible.
        - PC Controls: Based on the success of the PC platform from the KPIs, the design uses keyboard controls W and S, or the arrow keys, to move.
        - The mouse was used to change the perspective.
        - Collision Check: The player is not merely moving, but interacting, with each movement being checked for collisions and only acting accordingly.

    2.2 Strategy
        When you enter into a portal, the perspective shifts from 3D to 2D.
        - The AI, made from the classic minimax algorithm (see Sebastian Lague's video if you want to learn)
        - Bits: To enhance the speed of the game, numba, numpy as well as bitwise functions are used.
        - Stakes: The player starts with 3 lives. 
        - Losing / Surrendering:
            - Losing / surrendering a battle leads to the player losing 1 life.
            - When all three lives are lost, the player loses and has to restart.
    
3. RPG Growth: Whats up Super Mode
    One of my favorite features is the super mode that follows the following:
    - Taming: Every minion the player defeats increases the dragons beaten counter.
    - Reward: The player receives extra Queens based on how many dragons tamed (defeated).
    - Scoring: The Player receives a higher score for defeating the boss dragon.

4. Strategic Design (There is always a method to the madness)
    The mechanics are based on the KPIs to ensure success:
    - The Platform: PC remains the most profitable platform in the long term, earning about $59,519.66 on average, which is why I focused on W and S and mouse input.
    - The Genres: Action and RPG are earning over $54k on average, and Simulation has the longest historical engagement times at nearly 60 minutes. My chess battles leverage that high retention.
    - Stream Value: The FPS aspect ensures high-stress moments that are popular for viewership and the AI battles keep the players engaged.

5. The Technical Aspect:
 - Rendering Engine: The custom-built engine is constructed via ModernGL and shaders for high-performance rendering - to ensure a adequate frame rate despite the complexity.
  - Overlay: PyGame surfaces are used as textures to display the chess board and stats to enjoy the best of both worlds: PyGame for user input (via the UI classes) and ModernGl for rendering.
  - Architecture: Everything is done via classes and Object Oriented Programming and this is performed via a Scene management system that handles transitions from the 3D maze to the 2D chess board.

6. Win/Lose Conditions:
 - Victory: The player has to tame atleast 2 dragon minions to be worthy of defeating the final Boss. Once you find the boss portal (in red), you have to checkmate the dragon to win.
 - Failure: If the player loses all three lives, the game is over.  

Author's Notes:
Building this has been an thrilling experience, except the debugging. It was truly fun. If anyone else would like to make something similar, feel free to use the code, just give credit. Also, here are some videos that helped me learn all this that I would suggest for you:

    For modernGl:
    - https://youtu.be/LFbePt8i0DI?si=uUN8aOSwb6jsgSu3
    For Chess:
    - https://youtu.be/_vqlIPDR2TU?si=0uiNtLrtIJMjF8E1
    - https://youtu.be/X-e0jk4I938?si=8ku0YFi0XqQldcXE
    - https://youtu.be/OpL0Gcfn4B4?si=18hJkN6JzBymSZAr