/**
 * MEMOMU - JavaScript/Web Version
 * Mini Games Hub with Music Memory, Memory, Monluck, and Battle modes
 * Implements all layout and music memory mode fixes from PR #1
 */

// Color constants
const COLORS = {
    bg: '#000000',
    pink: '#ff69b4',
    lpink: '#ffc0cb',
    black: '#000000',
    white: '#ffffff',
    green: '#00ff00',
    red: '#ff0000'
};

// Game constants
const CANVAS_WIDTH = 800;
const CANVAS_HEIGHT = 700;

class MEMOMU {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.ui = document.getElementById('ui');
        
        // Game state
        this.state = 'menu';
        this.round = 0;
        this.score = 0;
        this.timer = 0;
        this.gameMode = '';
        
        // Sound management
        this.soundEnabled = true;
        this.musicPlaying = false;
        this.backgroundMusic = document.getElementById('backgroundMusic');
        this.sounds = {
            yupi: document.getElementById('yupiSound'),
            kuku: document.getElementById('kukuSound'),
            buuuu: document.getElementById('buuuuSound')
        };
        
        // Note sounds for music memory mode
        this.noteSounds = [];
        for (let i = 1; i <= 8; i++) {
            this.noteSounds.push(document.getElementById(`note${i}`));
        }
        
        // Game objects
        this.tiles = [];
        this.buttons = {};
        this.images = {};
        
        // Music Memory mode specific
        this.musicImageSequence = [];
        this.deceptionImageSequence = [];
        this.guess = 0;
        this.deceptionPlayed = 0;
        this.deceptionTimes = 1;
        
        // Initialize game
        this.init();
    }

    async init() {
        this.setupCanvas();
        this.loadImages();
        this.createButtons();
        this.setupEventListeners();
        this.startMusic();
        this.gameLoop();
    }

    setupCanvas() {
        // Set up canvas for high DPI displays
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        
        this.canvasScale = { x: scaleX, y: scaleY };
        
        // Set canvas size to match container
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
    }

    loadImages() {
        // Create placeholder images (in real implementation, these would load actual assets)
        this.images = {
            logo: this.createPlaceholderImage(688, 344, 'MEMOMU'), // 25% larger than original 550x275
            tiles: [],
            avatars: [],
            battleTiles: []
        };
        
        // Create placeholder tile images
        for (let i = 0; i < 34; i++) {
            this.images.tiles.push(this.createPlaceholderImage(100, 100, `T${i + 1}`));
        }
        
        // Create placeholder avatar images
        for (let i = 0; i < 13; i++) {
            this.images.avatars.push(this.createPlaceholderImage(100, 100, `A${i + 1}`));
        }
    }

    createPlaceholderImage(width, height, text) {
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        
        // Create gradient background
        const gradient = ctx.createLinearGradient(0, 0, width, height);
        gradient.addColorStop(0, COLORS.pink);
        gradient.addColorStop(1, '#ff1493');
        
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, width, height);
        
        // Add border
        ctx.strokeStyle = COLORS.white;
        ctx.lineWidth = 2;
        ctx.strokeRect(1, 1, width - 2, height - 2);
        
        // Add text
        ctx.fillStyle = COLORS.white;
        ctx.font = `bold ${Math.min(width, height) / 4}px Arial`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text, width / 2, height / 2);
        
        return canvas;
    }

    createButtons() {
        const W = CANVAS_WIDTH;
        const H = CANVAS_HEIGHT;
        
        this.buttons = {
            menu: [
                // NEW GAME button moved down by 71px (425 + 71 = 496)
                new Button('NEW GAME', W/2, 496, 325, 66, 'large'),
                new Button('SOUND', W - 101, 51, 150, 50, 'small'),
                // QUIT button moved down by 71px (504 + 71 = 575)
                new Button('QUIT', W/2, 575, 200, 60, 'large')
            ],
            mode: [
                // Mode buttons 20% smaller and properly spaced
                new Button('MUSIC MEMORY', W/2, 295, 176, 45, 'medium'),
                new Button('MEMORY', W/2, 350, 144, 45, 'medium'),
                new Button('MONLUCK', W/2, 405, 144, 45, 'medium'),
                new Button('BATTLE', W/2, 460, 144, 45, 'medium'),
                new Button('SOUND', W - 101, 51, 150, 50, 'small'),
                new Button('BACK', W/2, 535, 144, 45, 'medium'),
                // New QUIT button under BATTLE
                new Button('QUIT', W/2, 590, 144, 45, 'medium')
            ],
            memoryPhase: [
                new Button('GO', W/2, H/2, 100, 50, 'medium'),
                new Button('QUIT', W/2, H/2 + 75, 100, 44, 'small')
            ],
            memGuess: [
                new Button('QUIT', W/2, H/2 + 75, 100, 44, 'small')
            ]
        };
    }

    setupEventListeners() {
        this.canvas.addEventListener('click', (e) => this.handleClick(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        
        // Touch events for mobile
        this.canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('click', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            this.canvas.dispatchEvent(mouseEvent);
        });
        
        // Keyboard events
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        
        // Window resize
        window.addEventListener('resize', () => this.handleResize());
    }

    getCanvasCoordinates(clientX, clientY) {
        const rect = this.canvas.getBoundingClientRect();
        const x = (clientX - rect.left) * this.canvasScale.x;
        const y = (clientY - rect.top) * this.canvasScale.y;
        return { x, y };
    }

    handleClick(e) {
        const coords = this.getCanvasCoordinates(e.clientX, e.clientY);
        this.click(coords.x, coords.y);
    }

    handleMouseMove(e) {
        const coords = this.getCanvasCoordinates(e.clientX, e.clientY);
        this.updateHover(coords.x, coords.y);
    }

    handleKeyDown(e) {
        switch (e.key) {
            case 'Escape':
                if (this.state !== 'menu') {
                    this.state = 'menu';
                }
                break;
            case 'm':
            case 'M':
                this.toggleSound();
                break;
        }
    }

    handleResize() {
        this.setupCanvas();
    }

    startMusic() {
        if (this.soundEnabled && !this.musicPlaying) {
            this.backgroundMusic.volume = 0.56;
            this.backgroundMusic.play().catch(() => {
                // Handle autoplay restrictions
                console.log('Autoplay prevented - user interaction required');
            });
            this.musicPlaying = true;
        }
    }

    stopMusic() {
        this.backgroundMusic.pause();
        this.musicPlaying = false;
    }

    toggleSound() {
        this.soundEnabled = !this.soundEnabled;
        if (this.soundEnabled) {
            this.startMusic();
        } else {
            this.stopMusic();
        }
    }

    playSound(soundName) {
        if (this.soundEnabled && this.sounds[soundName]) {
            this.sounds[soundName].currentTime = 0;
            this.sounds[soundName].play().catch(() => {});
        }
    }

    playNote(noteIndex) {
        if (this.soundEnabled && this.noteSounds[noteIndex % 8]) {
            this.noteSounds[noteIndex % 8].currentTime = 0;
            this.noteSounds[noteIndex % 8].play().catch(() => {});
        }
    }

    click(x, y) {
        const state = this.state;
        
        if (state === 'menu') {
            this.handleMenuClick(x, y);
        } else if (state === 'mode') {
            this.handleModeClick(x, y);
        } else if (state === 'musicMemRules') {
            this.handleMusicMemRulesClick(x, y);
        } else if (state === 'memoryPhase') {
            this.handleMemoryPhaseClick(x, y);
        } else if (state === 'deceivingPhase') {
            this.handleDeceivingPhaseClick(x, y);
        } else if (state === 'guessingPhase') {
            this.handleGuessingPhaseClick(x, y);
        }
    }

    handleMenuClick(x, y) {
        if (this.buttons.menu[0].hit(x, y)) {
            // NEW GAME
            this.state = 'mode';
        } else if (this.buttons.menu[1].hit(x, y)) {
            // SOUND
            this.toggleSound();
        } else if (this.buttons.menu[2].hit(x, y)) {
            // QUIT
            this.quit();
        }
    }

    handleModeClick(x, y) {
        const buttons = this.buttons.mode;
        
        if (buttons[0].hit(x, y)) {
            // MUSIC MEMORY
            this.gameMode = 'musicMemory';
            this.setupMusicMemoryMode();
        } else if (buttons[1].hit(x, y)) {
            // MEMORY
            this.gameMode = 'memory';
            this.setupMemoryMode();
        } else if (buttons[2].hit(x, y)) {
            // MONLUCK
            this.gameMode = 'monluck';
            this.setupMonluckMode();
        } else if (buttons[3].hit(x, y)) {
            // BATTLE
            this.gameMode = 'battle';
            this.setupBattleMode();
        } else if (buttons[4].hit(x, y)) {
            // SOUND
            this.toggleSound();
        } else if (buttons[5].hit(x, y)) {
            // BACK
            this.state = 'menu';
        } else if (buttons[6].hit(x, y)) {
            // QUIT
            this.quit();
        }
    }

    handleMusicMemRulesClick(x, y) {
        // Implementation for music memory rules screen
        this.state = 'memoryPhase';
        this.setupMemoryPhase();
    }

    async handleMemoryPhaseClick(x, y) {
        if (this.buttons.memoryPhase[0].hit(x, y)) {
            // GO button - start memory phase
            await this.playMemorySequence();
        } else if (this.buttons.memGuess[0].hit(x, y)) {
            // QUIT
            this.state = 'menu';
        }
    }

    handleDeceivingPhaseClick(x, y) {
        if (this.buttons.memGuess[0].hit(x, y)) {
            // QUIT
            this.state = 'menu';
        }
    }

    handleGuessingPhaseClick(x, y) {
        // Check tile clicks
        for (let tile of this.tiles) {
            if (tile.hit(x, y)) {
                this.processTileGuess(tile);
                break;
            }
        }
        
        if (this.buttons.memGuess[0].hit(x, y)) {
            // QUIT
            this.state = 'menu';
        }
    }

    setupMusicMemoryMode() {
        this.state = 'musicMemRules';
        this.round = 0;
        this.score = 0;
        this.tiles = [];
        
        // Create music memory tiles
        const positions = [
            {x: 300, y: 300}, {x: 400, y: 300}, {x: 500, y: 300},
            {x: 300, y: 400}, {x: 400, y: 400}, {x: 500, y: 400},
            {x: 300, y: 500}, {x: 400, y: 500}, {x: 500, y: 500}
        ];
        
        for (let i = 0; i < 9; i++) {
            const tile = new Tile(
                positions[i].x, 
                positions[i].y, 
                this.images.tiles[i], 
                i,
                i % 8 // note index
            );
            this.tiles.push(tile);
        }
        
        this.generateMusicSequence();
    }

    generateMusicSequence() {
        // Generate sequence based on round (similar to Python version)
        const sequenceLength = Math.min(4 + this.round, 8);
        this.musicImageSequence = [];
        
        for (let i = 0; i < sequenceLength; i++) {
            this.musicImageSequence.push(Math.floor(Math.random() * 9));
        }
        
        // Generate deception sequence (different from real sequence)
        this.deceptionImageSequence = [];
        for (let i = 0; i < sequenceLength; i++) {
            let idx;
            do {
                idx = Math.floor(Math.random() * 9);
            } while (idx === this.musicImageSequence[i]);
            this.deceptionImageSequence.push(idx);
        }
    }

    setupMemoryPhase() {
        this.state = 'memoryPhase';
        for (let tile of this.tiles) {
            tile.visible = false;
        }
    }

    async playMemorySequence() {
        // Implementation of the three-phase memory sequence from PR #1
        
        // First show blank tiles
        for (let tile of this.tiles) {
            tile.visible = false;
        }
        this.draw();
        await this.sleep(500);
        
        // Determine number of plays based on round
        const times = this.round + 1 <= 3 ? 1 : (this.round + 1 <= 8 ? 2 : 3);
        
        // Play the sequence with perfect synchronization
        for (let playCount = 0; playCount < times; playCount++) {
            for (let imgIdx of this.musicImageSequence) {
                // Show tile and play sound simultaneously
                for (let tile of this.tiles) {
                    tile.visible = tile.index === imgIdx;
                }
                
                // Play sound exactly when tile shows
                const visibleTile = this.tiles.find(t => t.visible);
                if (visibleTile) {
                    this.playNote(visibleTile.note);
                }
                
                this.draw();
                await this.sleep(500);
                
                // Hide tile
                for (let tile of this.tiles) {
                    tile.visible = false;
                }
                this.draw();
                await this.sleep(100);
            }
            await this.sleep(500);
        }
        
        this.state = 'deceivingPhase';
        this.deceptionTimes = times;
        this.deceptionPlayed = 0;
        await this.playDeceptionSequence();
    }

    async playDeceptionSequence() {
        // Play the "tricky tricky!" phase
        while (this.deceptionPlayed < this.deceptionTimes) {
            for (let imgIdx of this.deceptionImageSequence) {
                // Show tile and play sound simultaneously
                for (let tile of this.tiles) {
                    tile.visible = tile.index === imgIdx;
                }
                
                // Play sound exactly when tile shows
                const visibleTile = this.tiles.find(t => t.visible);
                if (visibleTile) {
                    this.playNote(visibleTile.note);
                }
                
                this.draw();
                await this.sleep(500);
                
                // Hide tile
                for (let tile of this.tiles) {
                    tile.visible = false;
                }
                this.draw();
                await this.sleep(100);
            }
            this.deceptionPlayed++;
            await this.sleep(500);
        }
        
        // Move to guessing phase
        this.state = 'guessingPhase';
        for (let tile of this.tiles) {
            tile.visible = true;
        }
        this.timer = Date.now();
        this.guess = 0;
    }

    processTileGuess(tile) {
        const expectedIndex = this.musicImageSequence[this.guess];
        
        if (tile.index === expectedIndex) {
            // Correct guess
            this.score += 1;
            this.guess++;
            tile.showFeedback(true);
            this.playSound('yupi');
            
            if (this.guess >= this.musicImageSequence.length) {
                // Perfect completion
                this.score += 2; // Bonus for perfect completion
                
                // Time bonus (1 point per second remaining if perfect)
                const timeLimit = 20 + this.round * 3;
                const timeElapsed = (Date.now() - this.timer) / 1000;
                const timeLeft = Math.max(0, timeLimit - timeElapsed);
                this.score += Math.floor(timeLeft);
                
                this.nextRound();
            }
        } else {
            // Wrong guess - end round
            tile.showFeedback(false);
            this.playSound('buuuu');
            this.nextRound();
        }
    }

    nextRound() {
        this.round++;
        if (this.round >= 13) {
            this.endGame();
        } else {
            this.generateMusicSequence();
            this.setupMemoryPhase();
        }
    }

    endGame() {
        // Show final score and return to menu
        alert(`Game Over! Final Score: ${this.score}`);
        this.state = 'menu';
    }

    setupMemoryMode() {
        // Placeholder for memory mode
        alert('Memory mode not yet implemented');
        this.state = 'menu';
    }

    setupMonluckMode() {
        // Placeholder for monluck mode
        alert('Monluck mode not yet implemented');
        this.state = 'menu';
    }

    setupBattleMode() {
        // Placeholder for battle mode
        alert('Battle mode not yet implemented');
        this.state = 'menu';
    }

    updateHover(x, y) {
        // Update button hover states
        const buttonArrays = Object.values(this.buttons);
        for (let buttons of buttonArrays) {
            for (let button of buttons) {
                button.updateHover(x, y);
            }
        }
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    quit() {
        if (confirm('Are you sure you want to quit?')) {
            window.close();
        }
    }

    draw() {
        // Clear canvas
        this.ctx.fillStyle = COLORS.bg;
        this.ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        
        const state = this.state;
        
        if (state === 'menu') {
            this.drawMenu();
        } else if (state === 'mode') {
            this.drawModeSelection();
        } else if (state === 'musicMemRules') {
            this.drawMusicMemoryRules();
        } else if (state === 'memoryPhase') {
            this.drawMemoryPhase();
        } else if (state === 'deceivingPhase') {
            this.drawDeceivingPhase();
        } else if (state === 'guessingPhase') {
            this.drawGuessingPhase();
        }
        
        this.drawSoundIndicator();
    }

    drawMenu() {
        // Draw MEMOMU logo (shifted 23px right from center)
        const logoX = CANVAS_WIDTH/2 - this.images.logo.width/2 + 23;
        const logoY = 50;
        this.ctx.drawImage(this.images.logo, logoX, logoY);
        
        // Draw buttons
        for (let button of this.buttons.menu) {
            button.draw(this.ctx);
        }
        
        // Draw credits button
        this.drawText('CREDITS', CANVAS_WIDTH - 95, CANVAS_HEIGHT - 40, '18px Arial', COLORS.lpink);
    }

    drawModeSelection() {
        // Draw MEMOMU logo (same position as menu)
        const logoX = CANVAS_WIDTH/2 - this.images.logo.width/2 + 23;
        const logoY = 50;
        this.ctx.drawImage(this.images.logo, logoX, logoY);
        
        // Draw "Choose game mode" text
        this.drawText('Choose game mode', CANVAS_WIDTH/2, 180, 'bold 32px Arial', COLORS.lpink, 'center', 'middle');
        
        // Draw mode buttons
        for (let button of this.buttons.mode) {
            button.draw(this.ctx);
        }
    }

    drawMusicMemoryRules() {
        // Draw rules box
        this.ctx.fillStyle = COLORS.lpink;
        this.ctx.fillRect(CANVAS_WIDTH/2 - 340, CANVAS_HEIGHT/2 - 220, 680, 380);
        
        this.ctx.strokeStyle = COLORS.pink;
        this.ctx.lineWidth = 4;
        this.ctx.strokeRect(CANVAS_WIDTH/2 - 340, CANVAS_HEIGHT/2 - 220, 680, 380);
        
        // Rules text
        this.drawText('MUSIC MEMORY RULES:', CANVAS_WIDTH/2, CANVAS_HEIGHT/2 - 180, 'bold 32px Arial', COLORS.black, 'center');
        
        const rules = [
            '- Listen to the melody and remember the sequence',
            '- Three phases: Memory, Tricky, and Guessing',
            '- In guessing phase, click tiles in correct order',
            '- +1 point per correct tile, +2 bonus for perfect',
            '- +1 point per second remaining (if perfect)',
            '- Wrong click ends the round!',
            'Click anywhere to continue...'
        ];
        
        for (let i = 0; i < rules.length; i++) {
            this.drawText(rules[i], CANVAS_WIDTH/2 - 320, CANVAS_HEIGHT/2 - 140 + i * 30, '20px Arial', COLORS.black);
        }
    }

    drawMemoryPhase() {
        // Draw "listen and remember" message
        this.drawText('listen and remember', CANVAS_WIDTH/2, 66, '34px Arial', COLORS.lpink, 'center');
        
        // Draw score and round
        this.drawText(`Score: ${this.score}`, 10, 30, '24px Arial', COLORS.pink);
        this.drawText(`Round: ${this.round + 1}/13`, 10, 60, '24px Arial', COLORS.pink);
        
        // Draw tiles
        for (let tile of this.tiles) {
            tile.draw(this.ctx);
        }
        
        // Draw buttons
        for (let button of this.buttons.memoryPhase) {
            button.draw(this.ctx);
        }
        
        if (this.buttons.memGuess[0]) {
            this.buttons.memGuess[0].draw(this.ctx);
        }
    }

    drawDeceivingPhase() {
        // Draw "tricky tricky!" message
        this.drawText('tricky tricky!', CANVAS_WIDTH/2, 66, '34px Arial', COLORS.lpink, 'center');
        
        // Draw score and round
        this.drawText(`Score: ${this.score}`, 10, 30, '24px Arial', COLORS.pink);
        this.drawText(`Round: ${this.round + 1}/13`, 10, 60, '24px Arial', COLORS.pink);
        
        // Draw tiles
        for (let tile of this.tiles) {
            tile.draw(this.ctx);
        }
        
        // Draw quit button
        if (this.buttons.memGuess[0]) {
            this.buttons.memGuess[0].draw(this.ctx);
        }
    }

    drawGuessingPhase() {
        // Draw "Play now!" message
        this.drawText('Play now!', CANVAS_WIDTH/2, 66, '34px Arial', COLORS.lpink, 'center');
        
        // Draw score and round
        this.drawText(`Score: ${this.score}`, 10, 30, '24px Arial', COLORS.pink);
        this.drawText(`Round: ${this.round + 1}/13`, 10, 60, '24px Arial', COLORS.pink);
        
        // Draw timer
        const timeLimit = 20 + this.round * 3;
        const timeElapsed = (Date.now() - this.timer) / 1000;
        const timeLeft = Math.max(0, timeLimit - timeElapsed);
        
        // Timer bar
        const barWidth = 200;
        const barHeight = 50;
        const barX = CANVAS_WIDTH - 210;
        const barY = 100;
        
        this.ctx.fillStyle = COLORS.bg;
        this.ctx.fillRect(barX, barY, barWidth, barHeight);
        
        this.ctx.fillStyle = COLORS.pink;
        this.ctx.fillRect(barX, barY, (timeLeft / timeLimit) * barWidth, barHeight);
        
        this.ctx.strokeStyle = COLORS.white;
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(barX, barY, barWidth, barHeight);
        
        this.drawText(`${Math.ceil(timeLeft)}s`, barX + barWidth/2, barY + barHeight/2, '20px Arial', COLORS.white, 'center');
        
        // Draw tiles
        for (let tile of this.tiles) {
            tile.draw(this.ctx);
        }
        
        // Draw quit button
        if (this.buttons.memGuess[0]) {
            this.buttons.memGuess[0].draw(this.ctx);
        }
        
        // Check for timeout
        if (timeLeft <= 0) {
            this.nextRound();
        }
    }

    drawSoundIndicator() {
        const text = this.soundEnabled ? 'SOUND ON' : 'SOUND OFF';
        this.drawText(text, CANVAS_WIDTH - 10, 30, '18px Arial', COLORS.lpink, 'right');
    }

    drawText(text, x, y, font, color, align = 'left', baseline = 'top') {
        this.ctx.font = font;
        this.ctx.fillStyle = color;
        this.ctx.textAlign = align;
        this.ctx.textBaseline = baseline;
        this.ctx.fillText(text, x, y);
    }

    gameLoop() {
        this.draw();
        requestAnimationFrame(() => this.gameLoop());
    }
}

// Button class
class Button {
    constructor(text, x, y, width, height, size = 'medium') {
        this.text = text;
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.size = size;
        this.hovered = false;
    }

    hit(x, y) {
        return x >= this.x - this.width/2 && x <= this.x + this.width/2 &&
               y >= this.y - this.height/2 && y <= this.y + this.height/2;
    }

    updateHover(x, y) {
        this.hovered = this.hit(x, y);
    }

    draw(ctx) {
        // Draw button background
        ctx.fillStyle = this.hovered ? '#ff1493' : COLORS.pink;
        ctx.fillRect(this.x - this.width/2, this.y - this.height/2, this.width, this.height);
        
        // Draw button border
        ctx.strokeStyle = COLORS.white;
        ctx.lineWidth = 2;
        ctx.strokeRect(this.x - this.width/2, this.y - this.height/2, this.width, this.height);
        
        // Draw button text
        let fontSize;
        switch (this.size) {
            case 'large': fontSize = '32px'; break;
            case 'medium': fontSize = '24px'; break;
            case 'small': fontSize = '18px'; break;
            default: fontSize = '24px';
        }
        
        ctx.font = `bold ${fontSize} Arial`;
        ctx.fillStyle = COLORS.white;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(this.text, this.x, this.y);
    }
}

// Tile class
class Tile {
    constructor(x, y, image, index, note = null) {
        this.x = x;
        this.y = y;
        this.image = image;
        this.index = index;
        this.note = note;
        this.visible = true;
        this.feedbackColor = null;
        this.feedbackTime = 0;
        this.size = 100;
    }

    hit(x, y) {
        return x >= this.x - this.size/2 && x <= this.x + this.size/2 &&
               y >= this.y - this.size/2 && y <= this.y + this.size/2;
    }

    showFeedback(good) {
        this.feedbackColor = good ? COLORS.green : COLORS.red;
        this.feedbackTime = Date.now() + 300;
    }

    draw(ctx) {
        if (!this.visible) return;
        
        // Draw tile image
        ctx.drawImage(this.image, this.x - this.size/2, this.y - this.size/2, this.size, this.size);
        
        // Draw feedback border if active
        if (this.feedbackTime > Date.now()) {
            ctx.strokeStyle = this.feedbackColor;
            ctx.lineWidth = 4;
            ctx.strokeRect(this.x - this.size/2 - 2, this.y - this.size/2 - 2, this.size + 4, this.size + 4);
        }
    }
}

// Initialize game when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.memomu = new MEMOMU();
});