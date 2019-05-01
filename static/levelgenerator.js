function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function generateLevel(radius) {
    var level = {
        radius: 1000,
        entities: new Set(),
        gameOver: false
    };
    for (let x=0; x<100; x++) {
        level.entities.add({
            it: "wall",
            x: getRandomInt(-radius, radius),
            y: getRandomInt(-radius, radius),
            velX: 0,
            velY: 0,
            radius: 50,
            color: "#ffffff",
            outline: "#eeeeee",
            lastUpdated: Date.now()/1000
        });
    }
}
