document.addEventListener('DOMContentLoaded', function() {
    const gameBoardDiv = document.getElementById('game-board');
    const statusMessageDiv = document.getElementById('status-message');
    const resetButton = document.getElementById('reset-button');

    let currentBoard = Array(9).fill(0); // 0: empty, 1: X, 2: O
    let currentPlayer = 1; // 1 for X, 2 for O
    let gameIsOver = false;

    // Helper function to map player numbers to X/O
    const playerMark = (playerNum) => (playerNum === 1 ? 'X' : 'O');

    // Function to render the board based on the current state
    function renderBoard() {
        gameBoardDiv.innerHTML = ''; // Clear existing cells
        currentBoard.forEach((cellValue, index) => {
            const cell = document.createElement('div');
            cell.classList.add('cell');
            cell.dataset.index = index; // Store index for easy access

            if (cellValue === 1) {
                cell.textContent = 'X';
                cell.classList.add('x');
                cell.classList.add('animate'); // Add animation class
                cell.classList.add('disabled'); // Make cells with marks unclickable
            } else if (cellValue === 2) {
                cell.textContent = 'O';
                cell.classList.add('o');
                cell.classList.add('animate'); // Add animation class
                cell.classList.add('disabled');
            } else {
                // Only add click listener if the cell is empty and game is not over
                if (!gameIsOver) {
                    cell.addEventListener('click', handleCellClick);
                }
            }

            if (gameIsOver) {
                 cell.classList.add('disabled'); // Disable all cells if game is over
            }

            gameBoardDiv.appendChild(cell);
        });
    }

    // Function to update status message
    function updateStatusMessage(message) {
        statusMessageDiv.textContent = message;
    }

    // Handle a cell click
    function handleCellClick(event) {
        if (gameIsOver) return; // Prevent moves if game is over

        const cellIndex = parseInt(event.target.dataset.index);

        // Immediately disable all cells to prevent multiple clicks before server response
        Array.from(gameBoardDiv.children).forEach(cell => cell.classList.add('disabled'));
        updateStatusMessage("Processing move..."); // Provide immediate feedback

        // Send human's move to backend
        fetch('/make_move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ cell_index: cellIndex })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                currentBoard = data.board;
                gameIsOver = data.game_over;
                let nextPlayer = data.current_player; // This will be 1 (Human) if game continues

                renderBoard(); // Re-render the board with updated state (human + computer moves)

                if (gameIsOver) {
                    if (data.winner === 1) {
                        updateStatusMessage('Player X (You) wins!');
                    } else if (data.winner === 2) {
                        updateStatusMessage('Player O (Computer) wins!');
                    } else {
                        updateStatusMessage("It's a draw!");
                    }
                    // All cells are already disabled by renderBoard if gameIsOver
                } else {
                    updateStatusMessage(`Player ${playerMark(nextPlayer)}'s Turn`);
                     // Re-enable only empty cells for the next human turn
                    Array.from(gameBoardDiv.children).forEach((cell, idx) => {
                        if (currentBoard[idx] === 0) {
                            cell.classList.remove('disabled');
                        }
                    });
                }
            } else {
                // Handle invalid moves or errors from backend
                console.error('Error from backend:', data.message);
                updateStatusMessage('Invalid move. Try again.');
                // Re-enable cells if the move was invalid so user can retry
                Array.from(gameBoardDiv.children).forEach((cell, idx) => {
                    if (currentBoard[idx] === 0) {
                        cell.classList.remove('disabled');
                    }
                });
            }
        })
        .catch(error => {
            console.error('Error making move:', error);
            updateStatusMessage('Error: Could not make move. Try again.');
             // Re-enable cells if there's a network error
            Array.from(gameBoardDiv.children).forEach((cell, idx) => {
                if (currentBoard[idx] === 0) {
                    cell.classList.remove('disabled');
                }
            });
        });
    }

    // Handle reset button click
    resetButton.addEventListener('click', function() {
        fetch('/reset_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                currentBoard = data.board;
                currentPlayer = data.current_player; // Will be 1 (human)
                gameIsOver = data.game_over;
                updateStatusMessage(`Player ${playerMark(currentPlayer)}'s Turn`);
                renderBoard(); // Render the reset board
            } else {
                console.error('Error resetting game:', data.message);
            }
        })
        .catch(error => {
            console.error('Error during reset:', error);
            updateStatusMessage('Error: Could not reset game.');
        });
    });

    // Initial render when the page loads
    renderBoard();
    updateStatusMessage(`Player ${playerMark(currentPlayer)}'s Turn`);
});