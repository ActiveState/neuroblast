/*The MIT License (MIT)

Copyright (c) 2017 ActiveState Software Inc.

Written by Pete Garcin @rawktron

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.*/

package main

import (
	"fmt"
	"log"
	"math/rand"
	"time"

	"math"

	"github.com/boltdb/bolt"
	tf "github.com/tensorflow/tensorflow/tensorflow/go"

	"github.com/faiface/pixel"
	"github.com/faiface/pixel/imdraw"
	"github.com/faiface/pixel/pixelgl"
	"github.com/faiface/pixel/text"
	"golang.org/x/image/colornames"
)

const playerVel float64 = 100
const bulletVel float64 = 320
const showDebug bool = false
const enemyDmg int = 10
const playerDmg int = 20
const health = 100

const (
	menu = iota
	play
	gameover
	leaderboard
)

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
	// Open the scores DB
	db, err := bolt.Open("scores.db", 0600, nil)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create the scores bucket if it doesn't exist
	db.Update(func(tx *bolt.Tx) error {
		_, err := tx.CreateBucketIfNotExists([]byte("scores"))
		if err != nil {
			return fmt.Errorf("create bucket: %s", err)
		}
		return nil
	})

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
	var vizUpdate float64

	rand.Seed(time.Now().UnixNano())

	imd := imdraw.New(nil)
	starfield := imdraw.New(nil)

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
	logopic, err := loadPicture("art/neuro-blast_logo.png")
	if err != nil {
		panic(err)
	}
	aslogopic, err := loadPicture("art/as-logo.png")
	if err != nil {
		panic(err)
	}

	var bullets []*bullet
	var enemybullets []*bullet
	var enemies []*actor
	var stars []*star

	// Generate the star field for parallax
	genStars(200, &stars)

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
	logo := pixel.NewSprite(logopic, logopic.Bounds())
	aslogo := pixel.NewSprite(aslogopic, aslogopic.Bounds())

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

		cooldown:    0.1,
		canfire:     true,
		health:      health,
		lives:       3,
		vel:         pixel.ZV,
		pos:         pixel.V(320, 100),
		rect:        pixel.R(0, 0, 96, 100),
		blinkcycles: 12,
		blinking:    false,
		blinkon:     false,
		blinks:      0,
		blinktime:   0.5,
		blinkcount:  0,
	}
	player.idleAnim.play("Idle", true)
	player.rect = player.rect.Moved(player.pos)

	canvas := pixelgl.NewCanvas(pixel.R(0, 0, 640, 720))
	vizcanvas := pixelgl.NewCanvas(pixel.R(0, 0, 640, 720))

	vizmd := imdraw.New(nil)

	// Load Fonts
	face, err := loadTTF("font/DeValencia-Regular.ttf", 24)
	if err != nil {
		panic(err)
	}

	atlas := text.NewAtlas(face, text.ASCII)
	txt := text.New(pixel.V(0, 700), atlas)

	txt.Color = colornames.White

	menutxt := text.New(canvas.Bounds().Center().Sub(pixel.V(0, 0)), atlas)
	menutxt.Color = colornames.White

	viztext := text.New(vizcanvas.Bounds().Center().Sub(pixel.V(0, 0)), atlas)
	viztext.Color = colornames.White

	graphtext := text.New(vizcanvas.Bounds().Center().Sub(pixel.V(0, 0)), atlas)
	graphtext.Color = colornames.Black

	// Viz NN
	var neuralnet network
	neuralnet.NewNetwork(vizmd, graphtext, []int{4, 6, 4, 4, 1})

	last := time.Now()

	scrollSpeed := 1
	spawnTimer := 0.0
	spawnBreak := 5.0
	var enemySpeed float64 = -10
	gameState := menu
	selectedOption := 0
	topY := 0 // As soon as topY because -720, next frame, flip it back to hscale-720

	quit := false
	var topScores []kv
	var playerName string

	for !win.Closed() && !quit {
		dt := time.Since(last).Seconds()
		last = time.Now()

		vizUpdate += dt

		viztext.Dot = viztext.Orig
		viztext.WriteString("NEURAL NET VISUALIZATION")

		if gameState == leaderboard {
			menutxt.Dot = menutxt.Orig
			txt.Dot = txt.Orig
			menutxt.WriteString("TOP GOPHERS\n\n")
			if win.JustReleased(pixelgl.KeyEnter) {
				gameState = menu
			}

			i := 0
			for _, kv := range topScores {
				fmt.Printf("%s, %d\n", kv.Key, kv.Value)

				line := fmt.Sprintf("%s : %d", kv.Key, kv.Value)
				txt.Dot.X -= txt.BoundsOf(line).W()
				fmt.Fprintln(txt, line)

				i++
				if i == 10 {
					break
				}
			}

			topY = renderBackground(topY, scrollSpeed, bgslice, background, bg, canvas)

			txt.Draw(canvas, pixel.IM.Moved(pixel.V(360, -96)))
			menutxt.Draw(canvas, pixel.IM.Moved(pixel.V(-80, 320)))
			menutxt.Clear()
			txt.Clear()
		} else if gameState == gameover {
			menutxt.Dot = menutxt.Orig
			menutxt.WriteString("GAME OVER\n\n")
			menutxt.Dot.X -= menutxt.BoundsOf("GAME OVER").W() / 2
			menutxt.WriteString("ENTER YOUR NAME:")
			txt.WriteString(win.Typed())
			playerName += win.Typed()
			if win.JustReleased(pixelgl.KeyEnter) {
				err := saveScore(db, playerName, player.score)
				if err != nil {
					panic(err)
				}
				player.score = 0
				playerName = ""
				topScores = getScores(db)
				gameState = leaderboard
			}

			topY = renderBackground(topY, scrollSpeed, bgslice, background, bg, canvas)

			txt.Draw(canvas, pixel.IM.Moved(pixel.V(280, -96)))
			menutxt.Draw(canvas, pixel.IM.Moved(pixel.V(-80, 320)))
			menutxt.Clear()

		} else if gameState == menu {
			topY = renderBackground(topY, scrollSpeed, bgslice, background, bg, canvas)

			logo.Draw(canvas, pixel.IM.Moved(canvas.Bounds().Center().Sub(pixel.V(0, -140))))
			aslogo.Draw(canvas, pixel.IM.Moved(canvas.Bounds().Center().Sub(pixel.V(0, 280))))

			// Draw text menu options
			if selectedOption == 0 {
				menutxt.WriteRune('\u00bb')
			} else {
				menutxt.WriteString(" ")
			}
			menutxt.WriteString("PLAY")
			menutxt.WriteRune('\n')
			menutxt.Dot.X = 0
			if selectedOption == 1 {
				menutxt.WriteRune('\u00bb')
			} else {
				menutxt.WriteString(" ")
			}
			menutxt.WriteString("EXIT")
			menutxt.Draw(canvas, pixel.IM.Moved(pixel.V(260, -480)))
			menutxt.Clear()
			menutxt.Dot = txt.Orig

			if win.JustReleased(pixelgl.KeyUp) {
				selectedOption--
			}
			if win.JustReleased(pixelgl.KeyDown) {
				selectedOption++
			}
			if selectedOption < 0 {
				selectedOption = 1
			}
			if selectedOption > 1 {
				selectedOption = 0
			}
			if win.JustReleased(pixelgl.KeyEnter) {
				if selectedOption == 0 {
					gameState = play
				}
				if selectedOption == 1 {
					quit = true
				}
			}

		} else if gameState == play {
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

					cooldown:  0.1,
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
			if win.Pressed(pixelgl.KeyEscape) {
				player.health = 100
				player.lives = 3
				player.score = 0
				spawnBreak = 5.0
				enemySpeed = -10
				enemies = nil
				enemybullets = nil
				gameState = menu
			}

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

				if vizUpdate >= 1 {
					vizUpdate = 0
					go neuralnet.Think([]float64{float64(dx), float64(dy), float64(du), float64(dv)})
				}

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
						player.score += 50
						if enemy.health <= 0 && !enemy.blowAnim.playing {
							enemy.blowAnim.play("Explode", false)
							player.score += 200
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

				if b.rect.Intersect(player.rect).Area() > 0 && !player.blinking {
					player.hitSpot = pixel.R(0, 0, 96, 100)
					player.hitSpot = player.hitSpot.Moved(b.rect.Center().Sub(pixel.V(48, 50)))
					player.hitAnim.play("Hit", false)
					player.health -= enemyDmg
					if player.health <= 0 && !player.blowAnim.playing {
						player.blowAnim.play("Explode", false)
						player.lives--
						if player.lives >= 0 {
							player.blinkcount = 0
							player.blinking = true
							player.blinks = 0
							player.health = 100
						} else {
							// Remember to erase player score when exiting gameover
							player.health = 100
							player.lives = 3
							spawnBreak = 5.0
							enemySpeed = -10
							enemies = nil
							enemybullets = nil
							gameState = gameover
						}
					}
					b = nil
				}

				// Only keep on-screen bullets
				if b != nil && b.pos.Y > 0 && enemybullets != nil {
					enemybullets[i] = b
					i++
				}
			}
			if enemybullets != nil {
				enemybullets = enemybullets[:i]
			}

			topY = renderBackground(topY, scrollSpeed, bgslice, background, bg, canvas)

			// Physics and animation updates
			player.idleAnim.update(dt, player)
			player.hitAnim.update(dt, player)
			player.blowAnim.update(dt, player)

			renderStars(starfield, stars)
			starfield.Draw(canvas)

			// Manage player blinking
			if player.blinking {
				player.blinkcount += dt
				if player.blinkcount >= player.blinktime {
					player.blinkon = !player.blinkon
					player.blinks++
					player.blinkcount = 0
					if player.blinks == player.blinkcycles {
						player.blinking = false
						player.blinkon = false
						player.blinks = 0
					}
				}
			}

			if player.idleAnim.playing && (!player.blinking || (player.blinking && player.blinkon)) {
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
			starfield.Clear()

			// Text Rendering
			s := fmt.Sprintf("Score: %d Health: %d Lives: %d", player.score, player.health, player.lives)
			txt.WriteString(s)
			txt.Draw(canvas, pixel.IM.Moved(pixel.V(0, 0)))
			txt.Clear()
			txt.Dot = txt.Orig
		}

		// Draw the visualization neural network
		vizcanvas.Clear(colornames.Black)
		graphtext.Dot = graphtext.Orig
		neuralnet.Draw()
		vizmd.Draw(vizcanvas)
		vizmd.Clear()

		viztext.Draw(vizcanvas, pixel.IM.Moved(pixel.V(-160, 320)))
		viztext.Clear()

		graphtext.Draw(vizcanvas, pixel.IM)
		graphtext.Clear()
		// stretch the canvas to the window
		win.Clear(colornames.White)
		canvas.Draw(win, pixel.IM.Moved(pixel.V(320, 360)))
		vizcanvas.Draw(win, pixel.IM.Moved(pixel.V(960, 360)))
		win.Update()
	}
}

func main() {
	pixelgl.Run(run)
}
