package main

import "fmt"

func main() {
	var number uint16 = 260
	var number1 = 2
	var number2 = 3.5
	number3 := 6
	b1 := true
	var b2 bool
	var number4 uint64
	var testName string = "Hello World!"
	number += 100
	fmt.Println(testName, number)
	fmt.Printf("number 1: %T\n", number1)
	fmt.Printf("number 2: %T\n", number2)
	fmt.Printf("number 3: %T\n", number3)
	fmt.Printf("b1: %T\n", b1)
	fmt.Printf("b2: %T\n", b2)
	fmt.Println("b2: ", b2)
	fmt.Printf("number4: %T\n", number4)
	fmt.Printf("number4: %v\n", number4)

	fmt.Printf("3025 octal: %o\n", 3025)
	fmt.Printf("3025 hexdecimal (non-cap): %x\n", 3025)
	fmt.Printf("3025 hexdecimal (cap): %X\n", 3025)
	fmt.Printf("3025 binary: %b\n", 3025)

	fmt.Printf("String example: %s\n", "test")
	fmt.Printf("String example: %q\n", "test")

	fmt.Printf("Float number: %f\n", 3.1415927)
	fmt.Printf("Float number: %010f\n", 3.1415927)
	fmt.Printf("Float number: %9.5f\n", 3.1415927)
	fmt.Printf("Float number: %.4f\n", 3.1415927)

	fmt.Printf("INT padding: %09d\n", number)
	fmt.Printf("INT padding: %-4d\n", number) // left justify

	var out string = fmt.Sprintf("Number: %07d", 45)
	fmt.Println(out)
}
