import arcade
import os
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SPRITE_SCALING = 0.4
TEXTURE_LEFT = 0
TEXTURE_RIGHT = 1
TEXTURE_UP = 2
TEXTURE_DOWN = 3

CHARACTER_SCALING = 0.4
TILE_SCALING = 0.4
COIN_SCALING = 0.25
SPRITE_PIXEL_SIZE = 100
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)
SCREEN_TITLE = "Pacman Python"
GRAVITY = 1

SPRITE_IMAGE_SIZE = 100
SPRITE_SIZE = SPRITE_IMAGE_SIZE * SPRITE_SCALING

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 250
RIGHT_VIEWPORT_MARGIN = 250
BOTTOM_VIEWPORT_MARGIN = 100
TOP_VIEWPORT_MARGIN = 100

class Ghost(arcade.Sprite):

    direction = 'UP'
    repeat_direction = ''

    def follow_sprite(self, player_sprite, walls_sprite, pathToMove, SPRITE_SPEED):
        """
        This function will move the current sprite towards whatever
        other sprite is specified as a parameter.

        We use the 'min' function here to get the sprite to line up with
        the target sprite, and not jump around if the sprite is not off
        an exact multiple of SPRITE_SPEED.
        """
        if(pathToMove):
            if(len(pathToMove)>1):
                goX,goY = pathToMove[1]                
            else:
                goX,goY = pathToMove[0]

            temp = self
            old_center_x = self.center_x
            old_center_y = self.center_y

            if(goX==760):
                goX = 780
            if(goX==0):
                goX = 20
            if(goY==760):
                goY = 780

            # same X
            if(self.center_x == goX):
                #modify Y
                if(self.center_y < goY):
                    self.center_y += SPRITE_SPEED
                else:
                    self.center_y -= SPRITE_SPEED 
            else:
                if(self.center_x < goX):
                    if((self.center_x + SPRITE_SPEED)>=760):
                        self.center_x = 780
                    else:      
                        self.center_x += SPRITE_SPEED
                else:
                    if((self.center_x - SPRITE_SPEED)<20):
                        self.center_x = 20
                    else:      
                        self.center_x -= SPRITE_SPEED

            # same Y
            if(self.center_y == goY):
                #modify X
                if(self.center_x < goX):
                    self.center_x += SPRITE_SPEED
                else:
                    self.center_x -= SPRITE_SPEED 
            else:
                if(self.center_y < goY):
                    if((self.center_y + SPRITE_SPEED)>=760):
                        self.center_y = 780
                    else:      
                        self.center_y += SPRITE_SPEED
                else:
                    if((self.center_y - SPRITE_SPEED)<20):
                        self.center_y = 20
                    else:      
                        self.center_y -= SPRITE_SPEED

            hit_list = arcade.check_for_collision_with_list(temp, walls_sprite)
            if(len(hit_list)>0):
                #go back 
                temp.change_x = 0
                temp.change_y = 0
                temp.center_x = old_center_x
                temp.center_y = old_center_y     


class Player(arcade.Sprite):

    def __init__(self):
        super().__init__()

        self.textures = []
        # Load a left facing texture and a right facing texture.
        # flipped_horizontally=True will mirror the image we load.
        texture = arcade.load_texture("images/pacman.gif", mirrored=True)
        self.textures.append(texture)
        texture = arcade.load_texture("images/pacman.gif")
        self.textures.append(texture)
        texture = arcade.load_texture("images/pacman-up.gif")
        self.textures.append(texture)
        texture = arcade.load_texture("images/pacman-down.gif")
        self.textures.append(texture)

        self.scale = CHARACTER_SCALING

        # By default, face right.
        self.set_texture(TEXTURE_RIGHT)
     

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Figure out if we should face left or right
        if self.change_x < 0:
            self.texture = self.textures[TEXTURE_LEFT]
        elif self.change_x > 0:
            self.texture = self.textures[TEXTURE_RIGHT]
        if self.change_y < 0:
            self.texture = self.textures[TEXTURE_DOWN]
        elif self.change_y > 0:
            self.texture = self.textures[TEXTURE_UP]

        if self.left < 0:
            self.left = 0
        elif self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > SCREEN_HEIGHT - 1:
            self.top = SCREEN_HEIGHT - 1

class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, SCREEN_TITLE):
        super().__init__(width, height, SCREEN_TITLE, resizable=True)

        self.MOVEMENT_SPEED = 0.5
        self.SPRITE_SPEED = 0.5

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.totalCoins = 0
        self.score = 0
        self.isGameOver = False
        self.level = 1

        # Our physics engine
        self.physics_engine = None

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.coin_list = None
        self.wall_list = None
        self.player_list = None
        self.ghost_list = None
        self.barrier_list = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        #arcade.set_background_color(arcade.color.WHITE)

    def on_resize(self, width, height):
        """ This method is automatically called when the window is resized. """

        # Call the parent. Failing to do this will mess up the coordinates, and default to 0,0 at the center and the
        # edges being -1 to 1.
        super().on_resize(width, height)


    def setup(self):
        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True, spatial_hash_cell_size=128)
        self.coin_list = arcade.SpriteList(use_spatial_hash=True, spatial_hash_cell_size=128)
        self.ghost_list = arcade.SpriteList()

        ghost = Ghost("images/ghost.png", CHARACTER_SCALING)
        ghost.center_x = 20
        ghost.center_y = 460    # 40 increase
        self.ghost_list.append(ghost)
        ghost = Ghost("images/ghost.png", CHARACTER_SCALING)
        ghost.center_x = 20
        ghost.center_y = 280    # 40 increase
        self.ghost_list.append(ghost)
        ghost = Ghost("images/ghost.png", CHARACTER_SCALING)
        ghost.center_x = 780
        ghost.center_y = 580    # 40 increase
        self.ghost_list.append(ghost)
        ghost = Ghost("images/ghost.png", CHARACTER_SCALING)
        ghost.center_x = 780
        ghost.center_y = 320    # 40 increase
        self.ghost_list.append(ghost)

        # Set up the player
        self.player_sprite = Player()
        self.player_sprite.center_x = 380
        self.player_sprite.center_y = 240
        self.player_list.append(self.player_sprite)

        self.path = None
        # --- Load in a map from the tiled editor ---

        # Name of map file to load
        map_name = "resources/map.tmx"
        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = my_map.map_size.width * GRID_PIXEL_SIZE
        # Name of the layer in the file that has our platforms/walls
        # Name of the layer that has items for pick-up
        coins_layer_name = 'Coins'
        dont_touch_layer_name = "Don't Touch"

        # -- Coins
        self.coin_list = arcade.tilemap.process_layer(my_map,
                                                      coins_layer_name,
                                                      TILE_SCALING)

        # -- Don't Touch Layer
        self.wall_list = arcade.tilemap.process_layer(my_map,
                                                            dont_touch_layer_name,
                                                            TILE_SCALING)

        self.totalCoins = len(self.coin_list.sprite_list)

        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

        # Calculate the playing field size. We can't generate paths outside of
        # this.
        grid_size = SPRITE_SIZE

        playing_field_left_boundary = 20 #SPRITE_SIZE * 0.95 
        playing_field_right_boundary = 850 #SPRITE_SIZE * 20
        playing_field_top_boundary = 850 #SPRITE_SIZE * 20
        playing_field_bottom_boundary = 10 #SPRITE_SIZE * 0.95 
        # Note: If the enemy sprites are the same size, we only need to calculate
        # one of these. We do NOT need a different one for each enemy. The sprite
        # is just used for a size calculation.
        self.barrier_list = arcade.AStarBarrierList(self.ghost_list[0],
                                                    self.wall_list,
                                                    grid_size,
                                                    playing_field_left_boundary,
                                                    playing_field_right_boundary,
                                                    playing_field_bottom_boundary,
                                                    playing_field_top_boundary)
        
        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             0.0)
                                                       

    def draw_game_over(self):
        """
        Draw "Game over" across the screen.
        """
        output = "Game Over"
        arcade.draw_text(output, 240, 450, arcade.color.WHITE, 54)

        output = "Press Space to restart"
        arcade.draw_text(output, 280, 330, arcade.color.WHITE, 24)


    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()
        # Your drawing code goes here
        # Draw our sprites
        self.coin_list.draw()
        self.wall_list.draw()
        self.player_list.draw()
        self.ghost_list.draw()

        # for ghost in self.ghost_list:
        #     if(ghost.path):
        #         arcade.draw_line_strip(ghost.path, arcade.color.BLUE, 2)
        
        output = f"Score: {self.score}"
        arcade.draw_text(output, 5, 780, arcade.color.WHITE, 14)
        output = f"Level: {self.level}"
        arcade.draw_text(output, 730, 780, arcade.color.WHITE, 14)
        output = "Q to exit"
        arcade.draw_text(output, 700, 10, arcade.color.WHITE, 14)

        if(self.isGameOver == True):
            self.draw_game_over()

    def on_update(self, delta_time):
        """ Movement and game logic """

        if(self.isGameOver == False):
            # Move the player with the physics engine
            self.physics_engine.update()      

            # See if we hit any coins
            coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                                self.coin_list)

            # Loop through each coin we hit (if any) and remove it
            for coin in coin_hit_list:
                # Remove the coin
                coin.remove_from_sprite_lists()
                self.score = self.score + 1
                self.totalCoins = self.totalCoins - 1

            if(self.totalCoins<=0):
                # new level
                self.level = self.level + 1
                self.MOVEMENT_SPEED = self.MOVEMENT_SPEED + 0.15
                self.SPRITE_SPEED = self.SPRITE_SPEED + 0.15
                self.setup()

            # Calculate speed based on the keys pressed
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0

            if self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = self.MOVEMENT_SPEED
            elif self.down_pressed and not self.up_pressed:
                self.player_sprite.change_y = -self.MOVEMENT_SPEED
            if self.left_pressed and not self.right_pressed:
                self.player_sprite.change_x = -self.MOVEMENT_SPEED
            elif self.right_pressed and not self.left_pressed:
                self.player_sprite.change_x = self.MOVEMENT_SPEED

            # Call update to move the sprite
            # If using a physics engine, call update on it instead of the sprite
            # list.
            self.player_list.update()

            # Set to True if we can move diagonally. Note that diagnonal movement
            # might cause the enemy to clip corners.
            for ghost in self.ghost_list:
                ghost.path = arcade.astar_calculate_path(ghost.position,
                                            self.player_sprite.position,
                                            self.barrier_list,
                                            diagonal_movement=False)

                ghost.follow_sprite(self.player_sprite, self.wall_list, ghost.path, self.SPRITE_SPEED)

            # See if we hit any coins
            ghostPacman = arcade.check_for_collision_with_list(self.player_sprite,self.ghost_list)

            if(ghostPacman):
                self.isGameOver = True
        

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

        if(key == arcade.key.SPACE) and (self.isGameOver==True):
            self.setup()
            self.score = 0
            self.level = 1
            self.isGameOver = False

        if(key == arcade.key.Q):
            arcade.close_window()

def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()