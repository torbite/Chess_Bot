

console.log("[Init] Script loading...");

const FILES = ["a", "b", "c", "d", "e", "f", "g", "h"];

const PIECE_META = {
  wK: { src: "pieces_set_1/white_king.png", alt: "White King", scale: 0.82 },
  wQ: { src: "pieces_set_1/white_queen.png", alt: "White Queen", scale: 0.92 },
  wR: { src: "pieces_set_1/white_rook.png", alt: "White Rook", scale: 0.76 },
  wB: { src: "pieces_set_1/white_bishop.png", alt: "White Bishop", scale: 0.82 },
  wN: { src: "pieces_set_1/white_knight.png", alt: "White Knight", scale: 0.82 },
  wP: { src: "pieces_set_1/white_pawn.png", alt: "White Pawn", scale: 0.68 },
  bK: { src: "pieces_set_1/black_king.png", alt: "Black King", scale: 0.82 },
  bQ: { src: "pieces_set_1/black_queen.png", alt: "Black Queen", scale: 0.92 },
  bR: { src: "pieces_set_1/black_rook.png", alt: "Black Rook", scale: 0.76 },
  bB: { src: "pieces_set_1/black_bishop.png", alt: "Black Bishop", scale: 0.82 },
  bN: { src: "pieces_set_1/black_knight.png", alt: "Black Knight", scale: 0.82 },
  bP: { src: "pieces_set_1/black_pawns.png", alt: "Black Pawn", scale: 0.68 },
};

const state = {
  backendUrl: "http://127.0.0.1:8000",
  matchName: "default",
  game: null,
  selectedSquare: null,
  lastMove: null,
  availableMoves: new Set(),
  botPlaysWhite: false,
  botPlaysBlack: false,
  botMoveInProgress: false,
};

let boardElement;
let matchInput;
let loadGameButton;
let refreshButton;
let messageArea;
let turnIndicator;
let selectedIndicator;
let botWhiteToggle;
let botBlackToggle;

function initialiseFormDefaults() {
  matchInput.value = state.matchName;
}

function setMessage(text, type = "neutral") {
  messageArea.textContent = text;
  messageArea.classList.remove("positive", "negative");
  if (type === "positive") {
    messageArea.classList.add("positive");
  } else if (type === "negative") {
    messageArea.classList.add("negative");
  }
}

function updateIndicators() {
  const turn = state.game?.turn;
  turnIndicator.textContent =
    turn === "w" ? "White" : turn === "b" ? "Black" : "—";
  selectedIndicator.textContent = state.selectedSquare ?? "—";
}

function handleBotToggleChange() {
  state.botPlaysWhite = Boolean(botWhiteToggle?.checked);
  state.botPlaysBlack = Boolean(botBlackToggle?.checked);

  const activeSides = [];
  if (state.botPlaysWhite) {
    activeSides.push("White");
  }
  if (state.botPlaysBlack) {
    activeSides.push("Black");
  }

  if (state.game) {
    if (activeSides.length === 0) {
      setMessage("Bot control disabled. You're in charge.");
    } else {
      setMessage(`Bot will play as ${activeSides.join(" and ")}.`);
    }
  }

  maybeTriggerBot();
}

async function requestBotMove(turn) {
  const payload = {
    matchname: state.matchName,
  };

  console.groupCollapsed("[API] /get_bot_move");
  console.log("URL:", `${state.backendUrl}/get_bot_move`);
  console.log("Headers:", { "Content-Type": "application/json" });
  console.log("Body:", payload);

  try {
    const response = await fetch(`${state.backendUrl}/get_bot_move`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const responseHeaders = {};
    response.headers.forEach((value, key) => {
      responseHeaders[key] = value;
    });

    if (!response.ok) {
      console.log("Response status:", response.status, response.statusText);
      console.log("Response headers:", responseHeaders);
      const errorText = await response.text();
      console.log("Response body:", errorText);
      console.groupEnd();
      setMessage("Bot could not move. Verify the backend state.", "negative");
      return false;
    }

    const data = await response.clone().json();

    console.log("Response status:", response.status, response.statusText);
    console.log("Response headers:", responseHeaders);
    console.log("Response body:", data);
    console.groupEnd();

    if (!data || !Array.isArray(data.board)) {
      setMessage("Bot returned an invalid game state.", "negative");
      return false;
    }

    state.game = data;
    state.selectedSquare = null;
    state.availableMoves = new Set();
    state.lastMove = data.last_move ?? null;

    const sideLabel = turn === "w" ? "White" : "Black";
    setMessage(`Bot moved for ${sideLabel}.`, "positive");

    renderBoard(state.game);
    return true;
  } catch (error) {
    console.error(error);
    console.groupEnd();
    setMessage("Bot move failed. Check the backend server.", "negative");
    return false;
  }
}

async function maybeTriggerBot() {
  if (!state.game || state.botMoveInProgress) {
    return;
  }

  const turn = state.game.turn;
  const shouldBotMove =
    (turn === "w" && state.botPlaysWhite) ||
    (turn === "b" && state.botPlaysBlack);

  if (!shouldBotMove) {
    return;
  }

  state.botMoveInProgress = true;
  let botMoved = false;
  try {
    botMoved = await requestBotMove(turn);
  } finally {
    state.botMoveInProgress = false;
  }

  if (botMoved) {
    await maybeTriggerBot();
  }
}

function squareCoordinate(rowIndex, columnIndex) {
  return `${FILES[columnIndex]}${8 - rowIndex}`;
}

function createBoardSkeleton() {
  boardElement.innerHTML = "";

  for (let row = 0; row < 8; row += 1) {
    for (let col = 0; col < 8; col += 1) {
      const square = document.createElement("button");
      square.type = "button";
      square.className = `square ${(row + col) % 2 === 0 ? "light" : "dark"}`;
      const coordinate = squareCoordinate(row, col);
      square.dataset.square = coordinate;
      square.ariaLabel = `Square ${coordinate}`;
      square.addEventListener("click", () => handleSquareClick(square));
      boardElement.appendChild(square);
    }
  }
}

function clearSquareHighlights() {
  boardElement
    .querySelectorAll(".square.selected, .square.last-move, .square.potential-move")
    .forEach((sq) => {
      sq.classList.remove("selected", "last-move", "potential-move");
    });
}

function renderBoard(gameState) {
  if (!gameState?.board) {
    return;
  }

  const flatBoard = gameState.board.flat();

  boardElement.querySelectorAll(".square").forEach((square) => {
    const { square: coordinate } = square.dataset;
    const index = coordinateToIndex(coordinate);
    const pieceCode = flatBoard[index];
    square.replaceChildren();
    const pieceMeta = pieceCode ? PIECE_META[pieceCode] : null;
    if (pieceMeta?.src) {
      const img = document.createElement("img");
      img.src = pieceMeta.src;
      img.alt = pieceMeta.alt;
      img.className = "piece-image";
      const scale = pieceMeta.scale ?? 0.82;
      img.style.width = `${Math.round(scale * 100)}%`;
      square.appendChild(img);
    }
    square.dataset.piece = pieceCode ?? "";
  });

  clearSquareHighlights();

  if (state.selectedSquare) {
    const selectedSquareElement = boardElement.querySelector(
      `[data-square="${state.selectedSquare}"]`
    );
    selectedSquareElement?.classList.add("selected");
  }

  if (state.lastMove) {
    for (const key of ["from", "to"]) {
      const element = boardElement.querySelector(
        `[data-square="${state.lastMove[key]}"]`
      );
      element?.classList.add("last-move");
    }
  }

  if (state.availableMoves?.size) {
    state.availableMoves.forEach((coordinate) => {
      const element = boardElement.querySelector(
        `[data-square="${coordinate}"]`
      );
      element?.classList.add("potential-move");
    });
  }

  updateIndicators();
}

function coordinateToIndex(coordinate) {
  const file = coordinate[0];
  const rank = Number.parseInt(coordinate[1], 10);
  const columnIndex = FILES.indexOf(file);
  const rowIndex = 8 - rank;
  return rowIndex * 8 + columnIndex;
}

async function fetchGame({ quiet = false } = {}) {
  const payload = {
    matchname: state.matchName,
  };

  console.groupCollapsed("[API] /get_game");
  console.log("URL:", `${state.backendUrl}/get_game`);
  console.log("Headers:", { "Content-Type": "application/json" });
  console.log("Body:", payload);

  try {
    const response = await fetch(`${state.backendUrl}/get_game`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const responseHeaders = {};
    response.headers.forEach((value, key) => {
      responseHeaders[key] = value;
    });

    if (!response.ok) {
      console.log("Response status:", response.status, response.statusText);
      console.log("Response headers:", responseHeaders);
      const errorText = await response.text();
      console.log("Response body:", errorText);
      console.groupEnd();
      throw new Error(`GET_GAME_FAILED_${response.status}`);
    }

    const data = await response.clone().json();

    console.log("Response status:", response.status, response.statusText);
    console.log("Response headers:", responseHeaders);
    console.log("Response body:", data);
    console.groupEnd();

    state.game = data;
    state.selectedSquare = null;
    state.availableMoves = new Set();
    state.lastMove = data.last_move ?? null;

    if (!quiet) {
      setMessage("Game loaded successfully.", "positive");
    }

    renderBoard(state.game);
    await maybeTriggerBot();
  } catch (error) {
    console.error(error);
    console.groupEnd();
    setMessage(
      "Unable to load game. Confirm the backend URL, match name, and server status.",
      "negative"
    );
  }
}

async function submitMove(from, to) {
  const payload = {
    matchname: state.matchName,
    move_positions: [from, to],
  };

  console.groupCollapsed("[API] /move_piece");
  console.log("URL:", `${state.backendUrl}/move_piece`);
  console.log("Headers:", { "Content-Type": "application/json" });
  console.log("Body:", payload);

  try {
    const response = await fetch(`${state.backendUrl}/move_piece`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const responseHeaders = {};
    response.headers.forEach((value, key) => {
      responseHeaders[key] = value;
    });

    if (!response.ok) {
      console.log("Response status:", response.status, response.statusText);
      console.log("Response headers:", responseHeaders);
      const errorText = await response.text();
      console.log("Response body:", errorText);
      console.groupEnd();
      throw new Error(`MOVE_FAILED_${response.status}`);
    }

    const data = await response.clone().json();

    console.log("Response status:", response.status, response.statusText);
    console.log("Response headers:", responseHeaders);
    console.log("Response body:", data);
    console.groupEnd();

    if (!data || !Array.isArray(data.board)) {
      throw new Error("INVALID_RESPONSE");
    }

    const boardBefore = JSON.stringify(state.game?.board);
    const boardAfter = JSON.stringify(data.board);

    state.game = data;
    state.selectedSquare = null;
    state.availableMoves = new Set();

    if (boardBefore === boardAfter) {
      setMessage("Illegal move. Try another square.", "negative");
      state.lastMove = null;
    } else {
      state.lastMove = { from, to };
      setMessage(`Moved from ${from} to ${to}.`, "positive");
    }

    renderBoard(state.game);
    await maybeTriggerBot();
  } catch (error) {
    console.error(error);
    console.groupEnd();
    setMessage(
      "Unable to submit move. Make sure the backend is reachable.",
      "negative"
    );
  }
}

async function fetchAvailableMoves(square) {
  const payload = {
    matchname: state.matchName,
    piece_position: square,
  };

  console.groupCollapsed("[API] /get_piece_moves");
  console.log("URL:", `${state.backendUrl}/get_piece_moves`);
  console.log("Headers:", { "Content-Type": "application/json" });
  console.log("Body:", payload);

  try {
    const response = await fetch(`${state.backendUrl}/get_piece_moves`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const responseHeaders = {};
    response.headers.forEach((value, key) => {
      responseHeaders[key] = value;
    });

    if (!response.ok) {
      console.log("Response status:", response.status, response.statusText);
      console.log("Response headers:", responseHeaders);
      const errorText = await response.text();
      console.log("Response body:", errorText);
      console.groupEnd();
      throw new Error(`GET_PIECE_MOVES_FAILED_${response.status}`);
    }

    const data = await response.clone().json();

    console.log("Response status:", response.status, response.statusText);
    console.log("Response headers:", responseHeaders);
    console.log("Response body:", data);
    console.groupEnd();

    if (!Array.isArray(data)) {
      return new Set();
    }

    const moves = new Set();
    data.forEach((row, rowIndex) => {
      if (!Array.isArray(row)) {
        return;
      }
      row.forEach((cell, columnIndex) => {
        if (typeof cell === "string" && cell.endsWith("X")) {
          const coord = squareCoordinate(rowIndex, columnIndex);
          moves.add(coord);
        }
      });
    });

    return moves;
  } catch (error) {
    console.error(error);
    console.groupEnd();
    setMessage(
      "Unable to load available moves. Check the backend server.",
      "negative"
    );
    return new Set();
  }
}

async function handleSquareClick(squareElement) {
  const coordinate = squareElement.dataset.square;
  const pieceCode = squareElement.dataset.piece ?? "";

  if (!state.game) {
    setMessage("Load a game before making moves.", "negative");
    return;
  }

  const isFriendlyPiece =
    pieceCode && pieceCode.startsWith(state.game.turn ?? "");

  if (!state.selectedSquare) {
    if (!isFriendlyPiece) {
      setMessage("Select a piece that matches the current turn.", "negative");
      return;
    }

    state.selectedSquare = coordinate;
    state.availableMoves = await fetchAvailableMoves(coordinate);
    setMessage(`Piece selected on ${coordinate}. Choose a destination.`);
  } else if (state.selectedSquare === coordinate) {
    state.selectedSquare = null;
    state.availableMoves = new Set();
    setMessage("Selection cleared.");
  } else {
    const fromSquare = state.selectedSquare;
    state.selectedSquare = null;
    state.availableMoves = new Set();
    submitMove(fromSquare, coordinate);
    return;
  }

  renderBoard(state.game);
}

function handleLoadGame() {
  console.log("[UI] Load Game button clicked");
  state.matchName = matchInput.value.trim() || state.matchName;
  state.selectedSquare = null;
  state.lastMove = null;
  fetchGame();
}

function handleRefreshGame() {
  state.matchName = matchInput.value.trim() || state.matchName;
  fetchGame({ quiet: true });
}

function bootstrap() {
  console.log("[Init] Bootstrapping frontend");
  boardElement = document.getElementById("board");
  matchInput = document.getElementById("match-name");
  loadGameButton = document.getElementById("load-game");
  refreshButton = document.getElementById("refresh-game");
  messageArea = document.getElementById("message-area");
  turnIndicator = document.getElementById("turn-indicator");
  selectedIndicator = document.getElementById("selected-indicator");
  botWhiteToggle = document.getElementById("bot-white-toggle");
  botBlackToggle = document.getElementById("bot-black-toggle");

  initialiseFormDefaults();
  createBoardSkeleton();
  loadGameButton.addEventListener("click", handleLoadGame);
  refreshButton.addEventListener("click", handleRefreshGame);
  botWhiteToggle?.addEventListener("change", handleBotToggleChange);
  botBlackToggle?.addEventListener("change", handleBotToggleChange);
  fetchGame({ quiet: true });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", bootstrap);
} else {
  bootstrap();
}

