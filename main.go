package main

import (
	"math/rand"
	"time"

	"github.com/faiface/pixel"
	"github.com/faiface/pixel/pixelgl"
	"golang.org/x/image/colornames"
)

const playerVel float64 = 100
const bulletVel float64 = 320

func run() {
	rand.Seed(time.Now().UnixNano())

	// Load Bullet sprites
	bulletpic, err := loadPicture("art/bullet.png")
	if err != nil {
		panic(err)
	}
	//enemybulletpic, err := loadPicture("art/enemybullet.png")
	if err != nil {
		panic(err)
	} // Load bg
	bg, err := loadPicture("art/python-game_background.png")
	if err != nil {
		panic(err)
	}

	//enemybullet := pixel.NewSprite(enemybulletpic, enemybulletpic.Bounds())

	var bullets []*bullet

	//sheet, anims, err := loadAnimationSheet("art/python-sprites.png", "sheet.csv", 12)
	sheet, anims, err := loadAnimationSheet("art/HeroSheet.png", "sheet.csv", 96)
	if err != nil {
		panic(err)
	}

	//enemysheet, enemyanims, err := loadAnimationSheet("art/enemy.png", "enemysheet.csv", 96)

	hitsheet, hitanims, err := loadAnimationSheet("art/bullethit.png", "bulletsheet.csv", 96)
	explodesheet, explodeanims, err := loadAnimationSheet("art/explosion.png", "explodesheet.csv", 96)

	cfg := pixelgl.WindowConfig{
		Title:  "Neuro/Blast",
		Bounds: pixel.R(0, 0, 1280, 720),
		VSync:  true,
	}
	win, err := pixelgl.NewWindow(cfg)
	if err != nil {
		panic(err)
	}

	// Background, should use 'Set' to reblit the viewport sized hunk
	// that is scrolling
	background := pixel.NewSprite(bg, bg.Bounds())
	bgslice := pixel.NewSprite(bg, pixel.R(0, 0, 0, 0))

	player := &player{
		idleAnim: &spriteAnim{
			sheet: sheet,
			anims: anims,
			rate:  1.0 / 10,
			dir:   +1,
		},
		hitAnim: &spriteAnim{
			sheet: hitsheet,
			anims: hitanims,
			rate:  1.0 / 10,
			dir:   +1,
		},
		blowAnim: &spriteAnim{
			sheet: explodesheet,
			anims: explodeanims,
			rate:  1.0 / 10,
			dir:   +1,
		},

		cooldown: 0.1,
		canfire:  true,
		vel:      pixel.ZV,
		pos:      pixel.V(320, 360),
		rect:     pixel.R(-48, -50, 48, 50),
	}
	player.idleAnim.play("Idle", true)

	canvas := pixelgl.NewCanvas(pixel.R(0, 0, 640, 720))

	last := time.Now()

	scrollSpeed := 1

	topY := 0 // As soon as topY because -720, next frame, flip it back to hscale-720
	for !win.Closed() {
		dt := time.Since(last).Seconds()
		last = time.Now()

		// Update cooldown timer
		if !player.canfire {
			player.bulcount += dt
			if player.bulcount >= player.cooldown {
				player.bulcount = 0
				player.canfire = true
			}
		}

		// control the gopher with keys
		ctrl := pixel.ZV
		if win.Pressed(pixelgl.KeyLeft) {
			ctrl.X = -1 * playerVel * dt
		}
		if win.Pressed(pixelgl.KeyRight) {
			ctrl.X = 1 * playerVel * dt
		}
		if win.Pressed(pixelgl.KeyUp) {
			ctrl.Y = 1 * playerVel * dt
		}
		if win.Pressed(pixelgl.KeyDown) {
			ctrl.Y = -1 * playerVel * dt
		}
		if win.Pressed(pixelgl.KeySpace) && player.canfire {

			bullet := &bullet{
				sprite: pixel.NewSprite(bulletpic, bulletpic.Bounds()),
				pos:    player.pos.Add(pixel.V(0, 48)),
				vel:    pixel.V(0, bulletVel),
			}

			bullets = append(bullets, bullet)
			player.canfire = false
			player.bulcount = 0
		}

		player.pos = player.pos.Add(ctrl)
		//fmt.Println(player.pos)
		// update the physics and animation
		/*		phys.update(dt, ctrl, platforms)
				gol.update(dt)
				anim.update(dt, phys)
		*/

		// UPDATE BULLETS!!!
		i := 0
		for _, b := range bullets {
			// Add bullet movement
			b.pos = b.pos.Add(b.vel.Scaled(dt))

			// Only keep on-screen bullets
			if b.pos.Y < 720 {
				bullets[i] = b
				i++
			}
		}
		bullets = bullets[:i]

		// UPDATE THE BACKGROUND SCROLLING
		topY += scrollSpeed
		height := 720
		offset := (topY + height) - 8000 // If topY becomes negative, we use this to seamlessly blit until it clears itself up
		if offset < 0 {
			offset = 0
		}
		y := topY
		blitStartY := 0
		if topY+height >= 8000 {
			blitStartY = 720 - offset
			height = 720 - offset
			y = 8000 - height

			//fmt.Printf("Wrap: offset: %d blitStart: %d height: %d y: %d\n", offset, blitStartY, height, y)
			bgslice.Set(bg, pixel.R(0, 0, 640, float64(offset)))
		}
		//		background.Set(bg, pixel.R(0, float64(y+height+1), 640, float64(y)))
		background.Set(bg, pixel.R(0, float64(y), 640, float64(y+height)))
		//fmt.Println(y)

		if topY >= 8000 {
			topY = 0
		}

		// END OF BACKGROUND SCROLLING

		// Physics and animation updates
		player.idleAnim.update(dt, player)
		// draw the scene to the canvas
		canvas.Clear(colornames.Black)
		bgslice.Draw(canvas, pixel.IM.Moved(pixel.V(320, float64(360+(blitStartY/2)))))
		background.Draw(canvas, pixel.IM.Moved(pixel.V(320, float64(360-(offset/2)))))
		player.idleAnim.draw(canvas, player)

		for _, b := range bullets {
			b.sprite.Draw(canvas, pixel.IM.Moved(b.pos))
		}

		// stretch the canvas to the window
		win.Clear(colornames.White)
		//win.SetMatrix(pixel.IM.Scaled(pixel.ZV,
		//	math.Min(
		//		win.Bounds().W()/canvas.Bounds().W(),
		//			win.Bounds().H()/canvas.Bounds().H(),
		//			),
		//		).Moved(win.Bounds().Center()))
		canvas.Draw(win, pixel.IM.Moved(pixel.V(320, 360)))
		win.Update()
	}
}

func main() {
	pixelgl.Run(run)
}
