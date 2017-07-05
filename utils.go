package main

import (
	"encoding/csv"
	"image"
	"io"
	"os"
	"strconv"

	_ "image/png"

	"github.com/faiface/pixel"
	"github.com/pkg/errors"
)

type spriteAnim struct {
	sheet pixel.Picture
	anims map[string][]pixel.Rect
	rate  float64

	//state   animState
	counter float64
	dir     float64

	frame pixel.Rect

	sprite *pixel.Sprite
}

func loadPicture(path string) (pixel.Picture, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()
	img, _, err := image.Decode(file)
	if err != nil {
		return nil, err
	}
	return pixel.PictureDataFromImage(img), nil
}

func loadAnimationSheet(sheetPath, descPath string, frameWidth float64) (sheet pixel.Picture, anims map[string][]pixel.Rect, err error) {
	// total hack, nicely format the error at the end, so I don't have to type it every time
	defer func() {
		if err != nil {
			err = errors.Wrap(err, "error loading animation sheet")
		}
	}()

	// open and load the spritesheet
	sheetFile, err := os.Open(sheetPath)
	if err != nil {
		return nil, nil, err
	}
	defer sheetFile.Close()
	sheetImg, _, err := image.Decode(sheetFile)
	if err != nil {
		return nil, nil, err
	}
	sheet = pixel.PictureDataFromImage(sheetImg)

	// create a slice of frames inside the spritesheet
	var frames []pixel.Rect
	for x := 0.0; x+frameWidth <= sheet.Bounds().Max.X; x += frameWidth {
		frames = append(frames, pixel.R(
			x,
			0,
			x+frameWidth,
			sheet.Bounds().H(),
		))
	}

	descFile, err := os.Open(descPath)
	if err != nil {
		return nil, nil, err
	}
	defer descFile.Close()

	anims = make(map[string][]pixel.Rect)

	// load the animation information, name and interval inside the spritesheet
	desc := csv.NewReader(descFile)
	for {
		anim, err := desc.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			return nil, nil, err
		}

		name := anim[0]
		start, _ := strconv.Atoi(anim[1])
		end, _ := strconv.Atoi(anim[2])

		anims[name] = frames[start : end+1]
	}

	return sheet, anims, nil
}

func (ga *spriteAnim) update(dt float64, phys *player) {
	ga.counter += dt
	ga.frame = ga.anims["Idle"][0]

	/*	// determine the new animation state
		var newState animState
		switch {
		case !phys.ground:
			newState = jumping
		case phys.vel.Len() == 0:
			newState = idle
		case phys.vel.Len() > 0:
			newState = running
		}

	*/ // reset the time counter if the state changed
	/*	if ga.state != newState {
			ga.state = newState
			ga.counter = 0
		}
	*/
	// determine the correct animation frame
	/*	switch ga.state {
		case idle:
			ga.frame = ga.anims["Front"][0]
		case running:
			i := int(math.Floor(ga.counter / ga.rate))
			ga.frame = ga.anims["Run"][i%len(ga.anims["Run"])]
		case jumping:
			speed := phys.vel.Y
			i := int((-speed/phys.jumpSpeed + 1) / 2 * float64(len(ga.anims["Jump"])))
			if i < 0 {
				i = 0
			}
			if i >= len(ga.anims["Jump"]) {
				i = len(ga.anims["Jump"]) - 1
			}
			ga.frame = ga.anims["Jump"][i]
		}

		// set the facing direction of the gopher
		if phys.vel.X != 0 {
			if phys.vel.X > 0 {
				ga.dir = +1
			} else {
				ga.dir = -1
			}
		}
	*/
}

func (ga *spriteAnim) draw(t pixel.Target, phys *player) {
	if ga.sprite == nil {
		ga.sprite = pixel.NewSprite(nil, pixel.Rect{})
	}
	// draw the correct frame with the correct position and direction
	ga.sprite.Set(ga.sheet, ga.frame)
	ga.sprite.Draw(t, pixel.IM.
		ScaledXY(pixel.ZV, pixel.V(
			phys.rect.W()/ga.sprite.Frame().W(),
			phys.rect.H()/ga.sprite.Frame().H(),
		)).
		ScaledXY(pixel.ZV, pixel.V(-ga.dir, 1)).
		Moved(phys.rect.Center().Add(phys.pos)),
	)
}
