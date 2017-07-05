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

/*	phys := &gopherPhys{
	gravity:   -512,
	runSpeed:  64,
	jumpSpeed: 192,
	rect:      pixel.R(-6, -7, 6, 7),
}*/

type bullet struct {
	pos    pixel.Vec
	vel    pixel.Vec
	rect   pixel.Rect
	sprite *pixel.Sprite
}

type player struct {
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
	// Function callbacks??? Channels?

}
