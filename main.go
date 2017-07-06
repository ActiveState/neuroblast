package main

import (
	"math/rand"
	"time"

	"math"

	"github.com/faiface/pixel"
	"github.com/faiface/pixel/imdraw"
	"github.com/faiface/pixel/pixelgl"
	"golang.org/x/image/colornames"
)

const playerVel float64 = 100
const bulletVel float64 = 320
const showDebug bool = true

func drawRect(imd *imdraw.IMDraw, r pixel.Rect) {

	if !showDebug {
		return
	}

	imd.Color = pixel.RGB(1, 0, 0)
	imd.Push(pixel.V(r.Min.X, r.Min.Y))
	imd.Push(pixel.V(r.Min.X, r.Max.Y))
	imd.Push(pixel.V(r.Max.X, r.Max.Y))
	imd.Push(pixel.V(r.Max.X, r.Min.Y))
	imd.Push(pixel.V(r.Min.X, r.Min.Y))
	imd.Rectangle(1)
}

func run() {
	rand.Seed(time.Now().UnixNano())

	imd := imdraw.New(nil)

	// Load Bullet sprites
	bulletpic, err := loadPicture("art/bullet.png")
	if err != nil {
		panic(err)
	}
	enemybulletpic, err := loadPicture("art/enemybullet.png")
	if err != nil {
		panic(err)
	} // Load bg
	bg, err := loadPicture("art/python-game_background.png")
	if err != nil {
		panic(err)
	}

	var bullets []*bullet
	var enemybullets []*bullet

	//sheet, anims, err := loadAnimationSheet("art/python-sprites.png", "sheet.csv", 12)
	sheet, anims, err := loadAnimationSheet("art/HeroSheet.png", "sheet.csv", 96)
	if err != nil {
		panic(err)
	}

	enemysheet, enemyanims, err := loadAnimationSheet("art/enemy.png", "enemysheet.csv", 96)

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

	enemy := &player{
		idleAnim: &spriteAnim{
			sheet: enemysheet,
			anims: enemyanims,
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

		cooldown:  0.1,
		canfire:   true,
		vel:       pixel.ZV,
		pos:       pixel.V(320, 600),
		rect:      pixel.R(0, 0, 96, 184),
		spawnTime: time.Now(),
	}
	enemy.idleAnim.play("Idle", true)
	enemy.rect = enemy.rect.Moved(enemy.pos)

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
		pos:      pixel.V(320, 100),
		rect:     pixel.R(0, 0, 96, 100),
	}
	player.idleAnim.play("Idle", true)
	player.rect = player.rect.Moved(player.pos)

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
				pos:    player.pos.Add(pixel.V(40, 96)),
				vel:    pixel.V(0, bulletVel),
				rect:   pixel.R(0, 0, 16, 16),
			}
			bullet.rect = bullet.rect.Moved(bullet.pos)

			bullets = append(bullets, bullet)
			player.canfire = false
			player.bulcount = 0
		}

		if canvas.Bounds().Intersect(player.rect.Moved(ctrl)).Area() < player.rect.Area() {
			ctrl = pixel.ZV
		}

		if player.rect.Moved(ctrl).Intersect(enemy.rect).Area() > 0 {
			ctrl = pixel.ZV
		}

		player.pos = player.pos.Add(ctrl)
		player.rect = player.rect.Moved(ctrl)

		// UPDATE ENEMIES
		//self.velx = math.sin((pygame.time.get_ticks()-self.spawntime)/1800) * 40
		//self.x += self.velx * dt
		//self.y += self.vely * dt
		enemyVel := math.Sin(time.Since(enemy.spawnTime).Seconds()*1000/1800) * 40

		enemyVec := pixel.V(enemyVel, -10).Scaled(dt)

		enemy.pos = enemy.pos.Add(enemyVec)
		enemy.rect = enemy.rect.Moved(enemyVec)

		// ENemy shooting logic
		if rand.Intn(100) < 20 {
			bullet := &bullet{
				sprite: pixel.NewSprite(enemybulletpic, enemybulletpic.Bounds()),
				pos:    enemy.pos.Add(pixel.V(40, 0)),
				vel:    pixel.V(0, -bulletVel),
				rect:   pixel.R(0, 0, 16, 16),
			}
			bullet.rect = bullet.rect.Moved(bullet.pos)

			enemybullets = append(enemybullets, bullet)

		}

		// END OF ENEMY UPDATES

		// UPDATE BULLETS!!!
		i := 0
		for _, b := range bullets {
			// Add bullet movement
			b.pos = b.pos.Add(b.vel.Scaled(dt))
			b.rect = b.rect.Moved(b.vel.Scaled(dt))

			if b.rect.Intersect(enemy.rect).Area() > 0 {
				//fmt.Println("HIT")
				enemy.hitSpot = pixel.R(0, 0, 96, 100)
				enemy.hitSpot = enemy.hitSpot.Moved(b.rect.Center().Sub(pixel.V(48, 50)))
				enemy.hitAnim.play("Hit", false)
				b = nil
			}

			// Only keep on-screen bullets
			if b != nil && b.pos.Y < 720 {
				bullets[i] = b
				i++
			}
		}
		bullets = bullets[:i]

		// UPDATE ENEMY BULLETS!!!
		i = 0
		for _, b := range enemybullets {
			// Add bullet movement
			b.pos = b.pos.Add(b.vel.Scaled(dt))
			b.rect = b.rect.Moved(b.vel.Scaled(dt))

			if b.rect.Intersect(player.rect).Area() > 0 {
				//fmt.Println("HIT")
				player.hitSpot = pixel.R(0, 0, 96, 100)
				player.hitSpot = player.hitSpot.Moved(b.rect.Center().Sub(pixel.V(48, 50)))
				player.hitAnim.play("Hit", false)
				b = nil
			}

			// Only keep on-screen bullets
			if b != nil && b.pos.Y > 0 {
				enemybullets[i] = b
				i++
			}
		}
		enemybullets = enemybullets[:i]

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
		enemy.idleAnim.update(dt, enemy)
		enemy.hitAnim.update(dt, enemy)
		enemy.blowAnim.update(dt, enemy)
		player.hitAnim.update(dt, player)
		player.blowAnim.update(dt, player)
		// draw the scene to the canvas
		canvas.Clear(colornames.Black)
		bgslice.Draw(canvas, pixel.IM.Moved(pixel.V(320, float64(360+(blitStartY/2)))))
		background.Draw(canvas, pixel.IM.Moved(pixel.V(320, float64(360-(offset/2)))))
		if player.idleAnim.playing {
			player.idleAnim.draw(canvas, player.rect)
		}
		if enemy.idleAnim.playing {
			enemy.idleAnim.draw(canvas, enemy.rect)
		}

		if enemy.hitAnim.playing {
			enemy.hitAnim.draw(canvas, enemy.hitSpot)
		}
		if player.hitAnim.playing {
			player.hitAnim.draw(canvas, player.hitSpot)
		}

		for _, b := range bullets {
			b.sprite.Draw(canvas, pixel.IM.Moved(b.rect.Center()))
			drawRect(imd, b.rect)
		}
		for _, b := range enemybullets {
			b.sprite.Draw(canvas, pixel.IM.Moved(b.rect.Center()))
			drawRect(imd, b.rect)
		}

		drawRect(imd, player.rect)
		drawRect(imd, enemy.rect)

		imd.Draw(canvas)
		imd.Clear()

		// stretch the canvas to the window
		win.Clear(colornames.White)
		canvas.Draw(win, pixel.IM.Moved(pixel.V(320, 360)))
		win.Update()
	}
}

func main() {
	pixelgl.Run(run)
}
