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
	"encoding/csv"
	"image"
	"io"
	"io/ioutil"
	"math/rand"
	"os"
	"strconv"

	"golang.org/x/image/colornames"
	"golang.org/x/image/font"

	_ "image/png"

	"github.com/faiface/pixel"
	"github.com/faiface/pixel/imdraw"
	"github.com/faiface/pixel/pixelgl"
	"github.com/golang/freetype/truetype"
	"github.com/pkg/errors"
)

type star struct {
	pos   pixel.Vec
	layer int
}

type spriteAnim struct {
	sheet pixel.Picture
	anims map[string][]pixel.Rect
	rate  float64

	counter float64
	dir     float64

	currentAnim  string
	currentFrame int
	loop         bool
	playing      bool

	frame pixel.Rect

	sprite *pixel.Sprite
}

func genStars(numStars int, stars *[]*star) {
	for i := 0; i < numStars; i++ {
		newStar := &star{
			pos:   pixel.V(rand.Float64()*640, rand.Float64()*720),
			layer: rand.Intn(3),
		}
		*stars = append(*stars, newStar)
	}
}

func renderStars(imd *imdraw.IMDraw, stars []*star) {
	for _, s := range stars {
		s.pos = s.pos.Add(pixel.V(0, -float64(s.layer+2)))
		if s.pos.Y < 0 {
			s.pos = pixel.V(rand.Float64()*640, 724)
		}
		if s.layer == 0 {
			imd.Color = pixel.RGB(0.75, 0, 0.75).Mul(pixel.Alpha(0.5))
		} else if s.layer == 1 {
			imd.Color = pixel.RGB(0, 0.5, 0.75).Mul(pixel.Alpha(0.3))
		} else {
			imd.Color = pixel.RGB(1, 1, 1).Mul(pixel.Alpha(0.1))
		}
		imd.Push(pixel.V(s.pos.X, s.pos.Y))
		imd.Circle(float64(s.layer+1), 0)
	}
}

func renderBackground(topY, scrollSpeed int, bgslice, background *pixel.Sprite, bg pixel.Picture, canvas *pixelgl.Canvas) int {
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

		bgslice.Set(bg, pixel.R(0, 0, 640, float64(offset)))
	}
	background.Set(bg, pixel.R(0, float64(y), 640, float64(y+height)))

	if topY >= 8000 {
		topY = 0
	}

	// draw the scene to the canvas
	canvas.Clear(colornames.Black)
	bgslice.Draw(canvas, pixel.IM.Moved(pixel.V(320, float64(360+(blitStartY/2)))))
	background.Draw(canvas, pixel.IM.Moved(pixel.V(320, float64(360-(offset/2)))))

	return topY
}

func loadTTF(path string, size float64) (font.Face, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	bytes, err := ioutil.ReadAll(file)
	if err != nil {
		return nil, err
	}

	font, err := truetype.Parse(bytes)
	if err != nil {
		return nil, err
	}

	return truetype.NewFace(font, &truetype.Options{
		Size:              size,
		GlyphCacheEntries: 1,
	}), nil
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

func (ga *spriteAnim) play(anim string, loop bool) {
	ga.currentAnim = anim
	ga.counter = 0
	ga.currentFrame = 0
	ga.loop = loop
	ga.playing = true
}

func (ga *spriteAnim) update(dt float64, phys *actor) {
	if !ga.playing {
		return
	}

	ga.counter += dt

	if ga.counter >= ga.rate {
		ga.currentFrame++
		ga.counter = 0
		if ga.loop {
			if ga.currentFrame >= len(ga.anims[ga.currentAnim]) {
				ga.currentFrame = 0
			}
		} else {
			if ga.currentFrame >= len(ga.anims[ga.currentAnim]) {
				ga.currentFrame = len(ga.anims[ga.currentAnim]) - 1
				ga.playing = false
			}
		}
	}

	ga.frame = ga.anims[ga.currentAnim][ga.currentFrame]
}

func (ga *spriteAnim) draw(t pixel.Target, rect pixel.Rect) {
	if ga.sprite == nil {
		ga.sprite = pixel.NewSprite(nil, pixel.Rect{})
	}
	// draw the correct frame with the correct position and direction
	ga.sprite.Set(ga.sheet, ga.frame)
	ga.sprite.Draw(t, pixel.IM.
		Moved(rect.Center()),
	)
}
