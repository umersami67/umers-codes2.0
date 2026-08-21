let dinoY = 300;
let dinoVY = 0;
let isJumping = false;
let obstacles = [];
let score = 0;
let spawnTimer = 0;
let gameOver = false;
let speedModifier = 0;

const groundY = 330;
const dinoSize = 30;
const gravity = 0.8;

function setup() {
  let canvas = createCanvas(600, 400);
  canvas.parent('game-board');
}

function draw() {
  background(244);

  // Ground line
  stroke(0);
  line(0, groundY, width, groundY);

  if (!gameOver) {
    // Jump physics
    if (isJumping) {
      dinoY += dinoVY;
      dinoVY += gravity;
      if (dinoY >= groundY - dinoSize) {
        dinoY = groundY - dinoSize;
        isJumping = false;
        dinoVY = 0;
      }
    }

    // Spawn obstacles
    spawnTimer++;
    if (spawnTimer > 90) {
      obstacles.push({ x: width, w: 20, h: 35 });
      spawnTimer = 0;
    }

    // Move obstacles
    let speed = 5 + speedModifier;
    for (let i = obstacles.length - 1; i >= 0; i--) {
      obstacles[i].x -= speed;

      // Collision check
      let dinoLeft = 50, dinoRight = 50 + dinoSize;
      let dinoTop = dinoY, dinoBottom = dinoY + dinoSize;
      let obsLeft = obstacles[i].x, obsRight = obstacles[i].x + obstacles[i].w;
      let obsTop = groundY - obstacles[i].h, obsBottom = groundY;

      if (dinoRight > obsLeft && dinoLeft < obsRight &&
          dinoBottom > obsTop && dinoTop < obsBottom) {
        gameOver = true;
      }

      // Remove off-screen obstacles, add score
      if (obstacles[i].x + obstacles[i].w < 0) {
        obstacles.splice(i, 1);
        score++;
        if (score % 5 === 0) speedModifier += 0.5;
      }
    }
  }

  // Draw dino block
  fill(42, 82, 152);
  noStroke();
  rect(50, dinoY, dinoSize, dinoSize, 4);

  // Draw obstacle blocks
  fill(192, 57, 43);
  for (let o of obstacles) {
    rect(o.x, groundY - o.h, o.w, o.h, 3);
  }

  // Score
  fill(0);
  textSize(16);
  text('Score: ' + score, width - 100, 20);

  // Game over text
  if (gameOver) {
    fill(192, 57, 43);
    textSize(24);
    textAlign(CENTER, CENTER);
    text('GAME OVER - Press SPACE to restart', width / 2, height / 2);
    textAlign(LEFT, BASELINE);
  }
}

function keyPressed() {
  if (key === ' ' || keyCode === UP_ARROW) {
    if (gameOver) {
      resetGame();
    } else if (!isJumping) {
      isJumping = true;
      dinoVY = -14;
    }
  }
}

function resetGame() {
  dinoY = groundY - dinoSize;
  dinoVY = 0;
  isJumping = false;
  obstacles = [];
  score = 0;
  spawnTimer = 0;
  speedModifier = 0;
  gameOver = false;
}