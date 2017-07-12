package main

import (
	"fmt"
	"sort"
	"strconv"

	"github.com/boltdb/bolt"
)

type kv struct {
	Key   string
	Value int
}

func saveScore(db *bolt.DB, name string, score int) error {
	err := db.Update(func(tx *bolt.Tx) error {
		fmt.Printf("name: %s score: %d", name, score)
		b := tx.Bucket([]byte("scores"))
		err := b.Put([]byte(name), []byte(strconv.Itoa(score)))
		return err
	})
	return err
}

func getScores(db *bolt.DB) []kv {
	var m map[string]int

	m = make(map[string]int)
	db.View(func(tx *bolt.Tx) error {
		// Assume bucket exists and has keys
		b := tx.Bucket([]byte("scores"))

		b.ForEach(func(k, v []byte) error {
			fmt.Printf("key=%s, value=%s\n", k, v)

			name := make([]byte, len(k))
			copy(name, k)
			score, _ := strconv.Atoi(string(v))

			m[string(name)] = score

			return nil
		})
		return nil
	})

	var ss []kv
	for k, v := range m {
		ss = append(ss, kv{k, v})
	}

	sort.Slice(ss, func(i, j int) bool {
		return ss[i].Value > ss[j].Value
	})

	return ss
}
