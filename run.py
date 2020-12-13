import argparse

if __name__ == "__main__":
    # get args
    from maze import load_maze
    from road import load_road

    parser = argparse.ArgumentParser(description="""Python Dijkstras Implementation with GUI-- \n\n
                                                    Calculating the shortest distance between Nodes.                                                     
                                                 """)
    parser.add_argument("--width", default=1600, type=int,
                        help="Width of the 'map' in pixels")
    parser.add_argument("--height", default=800, type=int, help="Height of the 'map' in pixels")
    parser.add_argument("--maze", default=0, type=int, help="Set to 1 if you want to view the maze and not the road version")

    args = parser.parse_args()

    # get height width of board
    height = args.height
    width = args.width
    maze = args.maze

    # cv2 window details
    window_name = "Dijkstras"

    # if not maze
    if maze == 0:
        load_road(height,width,window_name)
    else:
        load_maze(height,width,window_name)