let playerX = 250;
let playerY = 350;
let playerSpeed = 6;

let itemX = 200;
let itemY = 0;
let itemSpeed = 4;

let score = 0;
let lives = 3;

function setup() {
  createCanvas(600, 400);
  resetItem();
}

function draw() {
  background(50);

  if (lives > 0) {
    // Movement with A / D or Left / Right Arrows
    if (keyIsDown(LEFT_ARROW) || keyIsDown(65) || keyIsDown(97)) {
      playerX -= playerSpeed;
    }
    if (keyIsDown(RIGHT_ARROW) || keyIsDown(68) || keyIsDown(100)) {
      playerX += playerSpeed;
    }

    playerX = constrain(playerX, 0, width - 100);

    // Draw Paddle
    fill(255);
    rect(playerX, playerY, 100, 20);

    // Ball movement
    itemY += itemSpeed;

    // Draw Big White Ball
    fill(255);
    circle(itemX, itemY, 40);

    // Catch Check
    if (itemY + 20 >= playerY && itemY - 20 <= playerY + 20) {
      if (itemX >= playerX && itemX <= playerX + 100) {
        score++;
        itemSpeed += 0.5;
        resetItem();
      }
    }

    // Missed Ball
    if (itemY > height) {
      lives--;
      resetItem();
    }

    // Score & Lives Display
    fill(255);
    textSize(20);
    textAlign(LEFT);
    text("Score: " + score, 20, 30);
    text("Lives: " + lives, 480, 30);

  } else {
    // Game Over screen
    fill(255, 50, 50);
    textSize(40);
    textAlign(CENTER, CENTER);
    text("GAME OVER", width / 2, height / 2 - 30);

    textSize(20);
    fill(255);
    text("Final Score: " + score, width / 2, height / 2 + 10);
    text("Press 'R' to Restart", width / 2, height / 2 + 50);
  }
}

// Restart with R key when game over
function keyPressed() {
  if (lives <= 0) {
    if (key === 'r' || key === 'R') {
      restartGame();
    }
  }
}

function resetItem() {
  itemY = 0;
  itemX = random(30, width - 30);
}

function restartGame() {
  score = 0;
  lives = 3;
  itemSpeed = 4;
  playerX = 250;
  resetItem();
}