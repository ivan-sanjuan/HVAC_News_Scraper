'use strict';

// const name = 'Ivan'
// const age = 34

// function declareName(){
//     console.log(`My name is ${name}, i am ${age}`);
// }

// declareName();

// var x=30;
// var y=40;
// function addOperation(numOne,numTwo) {
//     console.log('Sum is: ', numOne+numTwo);
// }

// addOperation(x,y);
// addOperation(100,5);

// var array1 = [40,77,141,642,2132,6139]

// function evenOdd(array){
//     for (let num of array){
//         if (num % 2 == 0){
//             console.log('This is even number: ',num);
//         }
//         else{
//             console.log('This is odd: ',num);
//         }
//     }
// }

// function printNums(a,b){
//     for (let i=a;i<=b;i++){
//         if (i % 2 != 0){
//             console.log(i);
//         }
//     }
// }
// printNums(1,20);

// function inputName(){
//     let enteredName = document.getElementById('name').value;
//     let enteredAge = document.getElementById('age').value;
//     document.getElementById('name_output').value =  `I am ${enteredName} and i am ${enteredAge}`;
// }

// var fruitArray = ['apple','orange','mango','pineapple','avocado'];

// fruitArray.push('mangosteen');
// console.log(fruitArray);
// fruitArray.shift()
// fruitArray.sort()
// console.log(fruitArray)

// class Car{
//     constructor(brand,model,year){
//         this.brand = brand;
//         this.model = model;
//         this.year = year;
//     }
// }

// function printDefinition(){
//     console.log(`This is a ${this.brand}, ${this.model} in the year ${this.year}`);
// }

// var carOne = new Car('Honda','Civic',1998);
// printDefinition.call(carOne);

// for (let c=1;c<=100;c++){
//     if(c%3==0){
//         console.log('Fizz',c);
//     }
//     if(c%5==0){
//         console.log('Buzz',c);
//     }
//     if(c%3==0 && c%5==0){
//         console.log('FizzBuzz',c);
//     }
// }

// for(let i=1;i <= 100; i++){
//     if(i % 3 == 0 && i % 5 == 0){
//         console.log('FizzBuzz', i);
//     }
//     else if(i % 3 == 0){
//         console.log('Fizz',i);
//     }
//     else if(i % 5 == 0){
//         console.log('Buzz',i);
//     }
// }

// var phrase = 'supercalifragilisticexpialidocious';
// var vowels = ['a','e','i','o','u'];
// var counter = 0;

// for(let char of phrase){
//     if(vowels.includes(char)){
//         counter += 1;
//     }
// }
// console.log(counter);

// var paragraph = "There are many variations of passages of Lorem Ipsum available, but the majority have suffered alteration in some form, by injected humour, or randomised words which don't look even slightly believable. If you are going to use a passage of Lorem Ipsum, you need to be sure there isn't anything embarrassing hidden in the middle of text. All the Lorem Ipsum generators on the Internet tend to repeat predefined chunks as necessary, making this the first true generator on the Internet. It uses a dictionary of over 200 Latin words, combined with a handful of model sentence structures, to generate Lorem Ipsum which looks reasonable. The generated Lorem Ipsum is therefore always free from repetition, injected humour";
// var wordsArray = paragraph.split(' ');
// let longestWord = "";
// for(let word of wordsArray){
//     if(word.length > longestWord.length){
//         longestWord = word;
//     }
// }
// // console.log(longestWord);

// var words = ['every','good','boy','does','fine']
// for(let word of words){
//     let upperWord = word.charAt(0).toUpperCase() + word.slice(1);
//     console.log(upperWord)
// }

// var numArray = [213,4311,2315,123,4635,-12316];
// var absnumArray = numArray.map(num => Math.abs(num));
// var largest_num = 0;
// for(let num of absnumArray){
//     if(num > largest_num){
//         largest_num = num;
//     }
// }
// var absValues = numArray.map((num) => Math.abs(num))
// console.log(largest_num)

// for(let word of words){
//     let capitalized = word.charAt(0).toUpperCase() + word.slice(1);
//     console.log(capitalized)
// }

// var ceilingNum = numArray.map((num) => Math.sqrt(Math.abs(num)))
// var forEachNum = numArray.forEach((num) => num+1000);
// console.log(forEachNum);


// var nums = [6.5,71.34,12.01,9.86,34.97]
// var addedNums = nums.map((num) => Math.round(num)+5)
// console.log(addedNums)

// var combinedNums = addedNums.reduce((sum,a) => sum+a)
// console.log(combinedNums)

// var strSample = 'hello';
// var rearranged = strSample.split('').toReversed().join('');
// var capStr = strSample.charAt(0).toUpperCase() + strSample.slice(1);
// console.log(capStr)

// var strArray = ['hello','i','am','hitchcock'];
// var strArrayCap = strArray.map((str) => str.charAt(0).toUpperCase() + str.slice(1));
// console.log(strArrayCap);

// class NumOperations{
//     constructor (array){
//         this.array = array;
//     }

//     allFifty(){
//         console.log(this.array);
//         let plusFiftyArray = this.array.map((num) => num+50);
//         console.log(plusFiftyArray)
//     }

//     allTotal(){
//         console.log(this.array);
//         let allTotal = this.array.reduce((sum,num) => sum+num);
//         console.log(allTotal)
//     }

//     allSqrt(){
//         console.log(this.array);
//         let allSqrt = this.array.map((num) => Math.sqrt(Math.abs(num)));
//         console.log(allSqrt)
//     }
// }
// var sampleNumArray = [12,42,321,-775,0];
// var newNumsArray = new NumOperations(sampleNumArray).allFifty();

// class StringManip{
//     constructor (strArray2){
//         this.strArray = strArray2;
//     }
    
//     titleCase(){
//         console.log(this.strArray)
//         let strTitleCase = this.strArray.map((str) => str.charAt(0).toUpperCase() + str.slice(1));
//         console.log(strTitleCase);
//         let revstrTitleCase = this.strArray.map((str) => str.charAt(0).toUpperCase() + str.slice(1)); // Panic
//         revstrTitleCase = revstrTitleCase.map((str) => str.split('').toReversed().join(''));
//         console.log(revstrTitleCase);
//     }
// }
// var sampleStrArray = ['panic','at','the','disco'];
// var newStrArray = new StringManip(sampleStrArray).titleCase();

class Person{
    constructor(name,age){
        this.name = name;
        this.age = age;
    }
    introduce(){
        let capName = this.name[0].toUpperCase() + this.name.slice(1);
        console.log(`Hi, I'm ${capName} and i'm ${this.age} years old. `);
    }
}

var personOne = new Person('ivan',34).introduce();

class Rectangle{
    constructor(width,height){
        if (typeof width !== 'number' || typeof height !== 'number'){
            throw new TypeError('Width and Height must be numbers');
        }
        this.width = Math.abs(width);
        this.height = Math.abs(height);
    }
    area(){
        let area = this.width * this.height;
        return area;
    }
    perimeter(){
        let perimeter = 2*(this.width + this.height);
        return perimeter;
    }
    convertAreaCm(){
        let areaInCM = this.area() * 10000;
        return areaInCM;
    }
    convertPeriCm(){
        let periInCM = this.perimeter() * 100;
        return periInCM;
    }
}

var rect1 = new Rectangle(6,-7);
console.log(`${rect1.area()} sq.m`);
console.log(`${rect1.perimeter()} m`);
console.log(`${rect1.convertAreaCm()} sq.cm`);
console.log(`${rect1.convertPeriCm()} cm`);


class Client{
    constructor(owner,balance){
        if (typeof balance !== 'number'){
            throw new TypeError('Balance should be a number');
        }
        this.owner = owner;
        this.balance = balance;
        this.total = this.getBalance;
        this.transactions = [];
    }
    getBalance(){
        let total = this.balance;
        console.log(`TOTAL: $${total}`)
        return total;
    }
    deposit(amount){
        let sum = this.balance += amount;
        this.transactions.push({
            'Type':'Deposit',
            'Amount':amount,
            'Balance':this.balance,
            'TimeStamp':new Date().toLocaleString()
        });
        return sum;
    }
    withdraw(amount){
        let diff = this.balance -= amount;
        this.transactions.push({
            'Type':'Withdraw',
            'Amount':amount,
            'Balance':this.balance,
            'TimeStamp':new Date().toLocaleString()
        });
        return diff;
    }
    history(){
        console.log(`Transaction History for ${this.owner}`);
        this.transactions.forEach((hs,i) => {
            console.log(`${i+1}. ${hs.TimeStamp} : ${hs.Type.toUpperCase()} of ${hs.Amount} => Balance: ${hs.Balance}`);
        })
    }
}

var john = new Client('John',0)
john.deposit(100);
john.withdraw(25);
john.deposit(200);
john.deposit(1000);
john.withdraw(2000);
john.deposit(1000);
john.getBalance();
john.history();

var mary = new Client('Mary',5000);
mary.deposit(2000);
mary.deposit(3000);
mary.withdraw(200);
mary.withdraw(500);
mary.withdraw(1000);
mary.getBalance();
mary.history();