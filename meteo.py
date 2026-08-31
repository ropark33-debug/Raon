import turtle as t
import random

screen = t.Screen()
screen.title("Dodge the Meteors")
screen.bgcolor("black")
screen.setup(600, 600)
screen.tracer(0)

# Player
player = t.Turtle()
player.shape("circle")
player.color("cyan")
player.penup()
player.goto(0, -250)

# Meteor
meteors = []

for i in range(5):      # Number of meteors
    meteor = t.Turtle()
    meteor.shape("triangle")
    meteor.color("brown")
    meteor.penup()
    meteor.goto(random.randint(-280, 280),
                random.randint(100, 500))
    meteors.append(meteor)

score = 0
game_over = False

# Score display
pen = t.Turtle()
pen.hideturtle()
pen.color("white")
pen.penup()
pen.goto(0, 260)

def update_score():
    pen.clear()
    pen.write(f"Score: {score}", align="center",
              font=("Arial", 16, "normal"))

update_score()

# Controls
def left():
    x = player.xcor() - 25
    if x < -280:
        x = -280
    player.setx(x)

def right():
    x = player.xcor() + 25
    if x > 280:
        x = 280
    player.setx(x)

screen.listen()
screen.onkeypress(left, "Left")
screen.onkeypress(right, "Right")

speed = 4

while not game_over:

    for meteor in meteors:
        meteor.sety(meteor.ycor() - speed)

    for meteor in meteors:
        if meteor.ycor() < -300:
            meteor.goto(random.randint(-280, 280), 300)
            score += 1
        update_score()

    for meteor in meteors:
        if player.distance(meteor) < 20:
            game_over = True

    screen.update()

pen.goto(0, 0)
pen.write("GAME OVER",
          align="center",
          font=("Arial", 28, "bold"))

screen.mainloop()