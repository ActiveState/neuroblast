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
*/

package main

import "github.com/faiface/pixel"
import "time"

type baseActor struct {
	lives       int
	health      int
	blinking    bool
	blinktime   float64
	blinkcycles int
	blinks      int
	blinkon     bool
	//Functioncallback

}

func (b *baseActor) TakeDamage(dmg int) {
	if b.health < 0 {
		return
	}

	b.health -= dmg

	if b.health <= 0 {
		b.lives--
	}
	//if b.deadcb:
	//	self.deadcb()
	if b.lives >= 0 {
		// DO something
		// Trigger Particle or something
		b.blinking = true
		b.blinks = 0
		b.health = 100
	}
}

type bullet struct {
	pos    pixel.Vec
	vel    pixel.Vec
	rect   pixel.Rect
	sprite *pixel.Sprite
}

type actor struct {
	hitAnim   *spriteAnim
	blowAnim  *spriteAnim
	idleAnim  *spriteAnim
	cooldown  float64
	canfire   bool
	bulcount  float64
	pos       pixel.Vec
	vel       pixel.Vec
	rect      pixel.Rect
	hitSpot   pixel.Rect
	spawnTime time.Time

	health int
	lives  int
	score  int

	blinking    bool
	blinktime   float64
	blinkcycles int
	blinks      int
	blinkon     bool
	blinkcount  float64
}
