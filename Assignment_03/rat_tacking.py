# Define the maze and the size (6x6)
maze = [[1, 0, 0, 0, 0, 0],
        [1, 1, 0, 1, 1, 0],
        [0, 1, 0, 1, 0, 0],
        [1, 1, 1, 1, 0, 1],
        [0, 0, 0, 1, 1, 1],
        [0, 0, 0, 0, 0, 1]]

# Size of the maze
N = 6

# Function to print the solution path
def print_solution(sol):
    for i in sol:
        print(i)

# Backtracking utility function
def is_safe(maze, x, y):
    # Check if x, y is within the maze bounds and the tile is walkable (1)
    if x >= 0 and x < N and y >= 0 and y < N and maze[x][y] == 1:
        return True
    return False

# Solving the maze using backtracking
def solve_maze(maze):
    # Initialize the solution matrix with 0s
    sol = [[0 for j in range(N)] for i in range(N)]

    if solve_maze_util(maze, 0, 0, sol) == False:
        print("No solution exists")
        return False

    print_solution(sol)
    return True

# Backtracking recursive utility
def solve_maze_util(maze, x, y, sol):
    # If the destination (bottom-right) is reached, mark as part of the solution
    if x == N - 1 and y == N - 1 and maze[x][y] == 1:
        sol[x][y] = 1
        return True

    # Check if current position is safe to move
    if is_safe(maze, x, y):
        # Mark current cell as part of the solution path
        sol[x][y] = 1

        # Move forward in the x direction
        if solve_maze_util(maze, x + 1, y, sol):
            return True

        # Move down in the y direction
        if solve_maze_util(maze, x, y + 1, sol):
            return True

        # If moving in x or y doesn't lead to a solution, backtrack (unmark this cell)
        sol[x][y] = 0
        return False

# Test the algorithm
solve_maze(maze)
