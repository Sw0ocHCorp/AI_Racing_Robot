import arcade

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "My Game")
        arcade.set_background_color(arcade.color.WHITE)

        self.sprites = []
        for i in range(10):
            sprite = arcade.Sprite("Software_Game_Assets/Player_car_final.png")
            sprite.center_x = i * 50
            sprite.center_y = SCREEN_HEIGHT / 2
            sprite.change_x = 5
            self.sprites.append(sprite)

    def on_draw(self):
        arcade.start_render()
        for sprite in self.sprites:
            sprite.draw()
        arcade.finish_render()

    def on_update(self, delta_time):
        for sprite in self.sprites:
            sprite.update()

def main():
    game = MyGame()
    arcade.run()

if __name__ == "__main__":
    main()