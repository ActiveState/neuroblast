package main

import (
	"fmt"
	"math/rand"
	"time"

	"math"

	tf "github.com/tensorflow/tensorflow/tensorflow/go"

	"github.com/faiface/pixel"
	"github.com/faiface/pixel/imdraw"
	"github.com/faiface/pixel/pixelgl"
	"golang.org/x/image/colornames"
)

const playerVel float64 = 100
const bulletVel float64 = 320
const showDebug bool = false
const enemyDmg int = 10
const playerDmg int = 20
const health = 100

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
	// Tensorflow stuff
	bundle, err := tf.LoadSavedModel("exported_brain", []string{"train"}, nil)
	if err != nil {
		panic(err)
	}

	inputop := bundle.Graph.Operation("dense_1_input")
	outputop := bundle.Graph.Operation("dense_5/Sigmoid")

	// Tensorflow sanity check test code
	fmt.Println(inputop.Name())
	fmt.Println(outputop.Name())

	var column *tf.Tensor
	if column, err = tf.NewTensor([1][4]float32{{1, 1, 1, 1}}); err != nil {
		panic(err.Error())
	}

	results, err := bundle.Session.Run(map[tf.Output]*tf.Tensor{inputop.Output(0): column}, []tf.Output{outputop.Output(0)}, nil)
	if err != nil {
		panic(err)
	}

	for _, result := range results {
		fmt.Println(result.Value().([][]float32))

		if result.Value().([][]float32)[0][0] > 0.5 {
			fmt.Println("FIRE!!")
		}
	}
	// End of tensorflow check code

	rand.Seed(time.Now().UnixNano())

	imd := imdraw.New(nil)

	// Load Bullet sprites
	bulletpic, err := loadPicture("art/enemybullet.png")
	if err != nil {
		panic(err)
	}
	enemybulletpic, err := loadPicture("art/bullet.png")
	if err != nil {
		panic(err)
	} // Load bg
	bg, err := loadPicture("art/python-game_background.png")
	if err != nil {
		panic(err)
	}

	var bullets []*bullet
	var enemybullets []*bullet
	var enemies []*actor

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

	player := &actor{
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
		health:   health,
		lives:    3,
		vel:      pixel.ZV,
		pos:      pixel.V(320, 100),
		rect:     pixel.R(0, 0, 96, 100),
	}
	player.idleAnim.play("Idle", true)
	player.rect = player.rect.Moved(player.pos)

	canvas := pixelgl.NewCanvas(pixel.R(0, 0, 640, 720))

	last := time.Now()

	scrollSpeed := 1
	spawnTimer := 0.0
	spawnBreak := 5.0
	var enemySpeed float64 = -10

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

		// SPAWN  NEW ENEMIES HERE
		spawnTimer += dt
		if spawnTimer > spawnBreak {
			spawnBreak = math.Max(2, spawnBreak-0.5)
			enemySpeed = math.Max(-20, enemySpeed-2)
			enemy := &actor{
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

				cooldown:  0.2,
				canfire:   true,
				health:    health,
				vel:       pixel.ZV,
				pos:       pixel.V(rand.Float64()*640, 721),
				rect:      pixel.R(0, 0, 96, 184),
				spawnTime: time.Now(),
			}
			enemy.idleAnim.play("Idle", true)
			enemy.rect = enemy.rect.Moved(enemy.pos)

			enemies = append(enemies, enemy)

			spawnTimer = 0

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

		player.pos = player.pos.Add(ctrl)
		player.rect = player.rect.Moved(ctrl)
		player.vel = ctrl.Scaled(1 / dt)

		// Has to be outside the enemy loop in case there are no enemies
		for _, b := range bullets {
			// Add bullet movement
			b.pos = b.pos.Add(b.vel.Scaled(dt))
			b.rect = b.rect.Moved(b.vel.Scaled(dt))
		}

		// UPDATE ENEMIES
		//self.velx = math.sin((pygame.time.get_ticks()-self.spawntime)/1800) * 40
		//self.x += self.velx * dt
		//self.y += self.vely * dt

		j := 0
		for _, enemy := range enemies {

			if player.rect.Moved(ctrl).Intersect(enemy.rect).Area() > 0 {
				ctrl = pixel.ZV
			}

			enemyVel := math.Sin(time.Since(enemy.spawnTime).Seconds()*1000/1800) * 40

			enemyVec := pixel.V(enemyVel, enemySpeed).Scaled(dt)

			enemy.pos = enemy.pos.Add(enemyVec)
			enemy.rect = enemy.rect.Moved(enemyVec)
			enemy.vel = pixel.V(enemyVel, -10)

			enemy.bulcount += dt
			if enemy.bulcount >= enemy.cooldown {
				enemy.canfire = true
			}

			if enemy.pos.Y > 700 || enemy.blowAnim.playing {
				enemy.canfire = false
			}

			var dx, dy, du, dv float32
			// Normalized values
			dx = float32((enemy.pos.X - player.pos.X) / 640)
			dy = -float32((enemy.pos.Y - player.pos.Y) / 720)
			du = float32((enemy.vel.X - player.vel.X) / 60)
			dv = -float32((enemy.vel.Y - player.vel.Y) / 60)

			// Enemy shooting logic - This is the TensorFlow bit
			var column *tf.Tensor
			if column, err = tf.NewTensor([1][4]float32{{dx, dy, du, dv}}); err != nil {
				panic(err.Error())
			}

			results, err := bundle.Session.Run(map[tf.Output]*tf.Tensor{inputop.Output(0): column}, []tf.Output{outputop.Output(0)}, nil)
			if err != nil {
				panic(err)
			}

			for _, result := range results {
				fmt.Printf("Input: dx: %f dy: %f du: %f dv: %f\n", dx, dy, du, dv)
				fmt.Println(result.Value().([][]float32))

				if result.Value().([][]float32)[0][0] >= 0.5 && enemy.canfire {
					bullet := &bullet{
						sprite: pixel.NewSprite(enemybulletpic, enemybulletpic.Bounds()),
						pos:    enemy.pos.Add(pixel.V(40, 0)),
						vel:    pixel.V(0, -bulletVel),
						rect:   pixel.R(0, 0, 16, 16),
					}
					bullet.rect = bullet.rect.Moved(bullet.pos)

					enemybullets = append(enemybullets, bullet)
					enemy.canfire = false
					enemy.bulcount = 0
				}
			}

			// END OF ENEMY LOGIC UPDATES

			// UPDATE BULLETS!!!
			i := 0
			for _, b := range bullets {
				if b.rect.Intersect(enemy.rect).Area() > 0 {
					//fmt.Println("HIT")
					enemy.hitSpot = pixel.R(0, 0, 96, 100)
					enemy.hitSpot = enemy.hitSpot.Moved(b.rect.Center().Sub(pixel.V(48, 50)))
					enemy.hitAnim.play("Hit", false)
					enemy.health -= playerDmg
					if enemy.health <= 0 && !enemy.blowAnim.playing {
						enemy.blowAnim.play("Explode", false)
					}
					b = nil
				}

				// Only keep on-screen bullets
				if b != nil && b.pos.Y < 720 {
					bullets[i] = b
					i++
				}
			}
			bullets = bullets[:i]

			// Delete enemies who are dead AND have finished playing their explosion animation
			if enemy.health <= 0 && !enemy.blowAnim.playing {
				enemy = nil
			}
			if enemy != nil {
				enemies[j] = enemy
				j++
			}
			// LOOP FOR ALL ENEMIES
		}

		enemies = enemies[:j]

		// UPDATE ENEMY BULLETS!!!
		i := 0
		for _, b := range enemybullets {
			// Add bullet movement
			b.pos = b.pos.Add(b.vel.Scaled(dt))
			b.rect = b.rect.Moved(b.vel.Scaled(dt))

			if b.rect.Intersect(player.rect).Area() > 0 {
				//fmt.Println("HIT")
				player.hitSpot = pixel.R(0, 0, 96, 100)
				player.hitSpot = player.hitSpot.Moved(b.rect.Center().Sub(pixel.V(48, 50)))
				player.hitAnim.play("Hit", false)
				player.health -= enemyDmg
				if player.health <= 0 && !player.blowAnim.playing {
					player.blowAnim.play("Explode", false)
				}
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
		player.hitAnim.update(dt, player)
		player.blowAnim.update(dt, player)
		// draw the scene to the canvas
		canvas.Clear(colornames.Black)
		bgslice.Draw(canvas, pixel.IM.Moved(pixel.V(320, float64(360+(blitStartY/2)))))
		background.Draw(canvas, pixel.IM.Moved(pixel.V(320, float64(360-(offset/2)))))
		if player.idleAnim.playing {
			player.idleAnim.draw(canvas, player.rect)
		}
		if player.hitAnim.playing {
			player.hitAnim.draw(canvas, player.hitSpot)
		}
		if player.blowAnim.playing {
			player.blowAnim.draw(canvas, player.rect)
		}

		// Rendering and update for enemies
		for _, enemy := range enemies {
			enemy.idleAnim.update(dt, enemy)
			enemy.hitAnim.update(dt, enemy)
			enemy.blowAnim.update(dt, enemy)
			if enemy.idleAnim.playing {
				enemy.idleAnim.draw(canvas, enemy.rect)
			}
			if enemy.hitAnim.playing {
				enemy.hitAnim.draw(canvas, enemy.hitSpot)
			}
			if enemy.blowAnim.playing {
				enemy.blowAnim.draw(canvas, enemy.rect.Moved(pixel.V(0, -16)))
			}

			drawRect(imd, enemy.rect)
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
