package main

import (
	"math/rand"
	"time"

	"fmt"

	"github.com/faiface/pixel"
	"github.com/faiface/pixel/pixelgl"
	"golang.org/x/image/colornames"
)

func run() {
	rand.Seed(time.Now().UnixNano())

	// Load bg
	bg, err := loadPicture("art/python-game_background.png")
	if err != nil {
		panic(err)
	}

	//sheet, anims, err := loadAnimationSheet("art/python-sprites.png", "sheet.csv", 12)
	sheet, anims, err := loadAnimationSheet("art/HeroSheet.png", "sheet.csv", 96)
	if err != nil {
		panic(err)
	}

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
		hitAnim: &spriteAnim{
			sheet: sheet,
			anims: anims,
			rate:  1.0 / 10,
			dir:   +1,
		},

		vel:  pixel.ZV,
		pos:  pixel.V(320, 360),
		rect: pixel.R(-48, -50, 48, 50),
	}

	/*	anim := &gopherAnim{
		sheet: sheet,
		anims: anims,
		rate:  1.0 / 10,
		dir:   +1,
	}*/
	//camPos := pixel.ZV
	canvas := pixelgl.NewCanvas(pixel.R(0, 0, 640, 720))

	last := time.Now()

	scrollSpeed := 1

	// Optimized method for scrolling background continuously
	//	topY := 8000 - 720 // As soon as topY because -720, next frame, flip it back to hscale-720

	topY := 6500 // As soon as topY because -720, next frame, flip it back to hscale-720
	for !win.Closed() {
		dt := time.Since(last).Seconds()
		last = time.Now()

		// lerp the camera position towards the ship
		//		camPos = pixel.Lerp(camPos, player.rect.Center(), 1-math.Pow(1.0/128, dt))
		//camPos = pixel.Lerp(camPos, player.rect.Center(), 0)
		//cam := pixel.IM.Moved(camPos.Scaled(-1))
		//canvas.SetMatrix(cam)

		/*		// restart the level on pressing enter
				if win.JustPressed(pixelgl.KeyEnter) {
					phys.rect = phys.rect.Moved(phys.rect.Center().Scaled(-1))
					phys.vel = pixel.ZV
				}
		*/
		// control the gopher with keys
		ctrl := pixel.ZV
		if win.Pressed(pixelgl.KeyLeft) {
			ctrl.X = -1
		}
		if win.Pressed(pixelgl.KeyRight) {
			ctrl.X = 1
		}
		if win.Pressed(pixelgl.KeyUp) {
			ctrl.Y = 1
		}
		if win.Pressed(pixelgl.KeyDown) {
			ctrl.Y = -1
		}

		player.pos = player.pos.Add(ctrl)
		//fmt.Println(player.pos)
		// update the physics and animation
		/*		phys.update(dt, ctrl, platforms)
				gol.update(dt)
				anim.update(dt, phys)
		*/

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

			fmt.Printf("Wrap: offset: %d blitStart: %d height: %d y: %d\n", offset, blitStartY, height, y)
			bgslice.Set(bg, pixel.R(0, 0, 640, float64(offset)))
		}
		//		background.Set(bg, pixel.R(0, float64(y+height+1), 640, float64(y)))
		background.Set(bg, pixel.R(0, float64(y), 640, float64(y+height)))
		fmt.Println(y)

		if topY >= 8000 {
			topY = 0
		}

		// END OF BACKGROUND SCROLLING

		player.hitAnim.update(dt, player)
		// draw the scene to the canvas using IMDraw
		canvas.Clear(colornames.Black)
		bgslice.Draw(canvas, pixel.IM.Moved(pixel.V(320, float64(360+(blitStartY/2)))))
		background.Draw(canvas, pixel.IM.Moved(pixel.V(320, float64(360-(offset/2)))))
		player.hitAnim.draw(canvas, player)
		/*		gol.draw(imd)
				anim.draw(imd, phys)
				imd.Draw(canvas)
		*/
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
