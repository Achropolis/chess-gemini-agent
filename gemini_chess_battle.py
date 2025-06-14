import streamlit as st
import streamlit.components.v1 as components
import chess
import chess.svg
import google.generativeai as genai

# Konfigurasi API Gemini
st.sidebar.title("🔐 Gemini API Configuration")
api_key = st.sidebar.text_input("Enter your Gemini API key:", type="password")
if api_key:
    genai.configure(api_key=api_key)
    st.sidebar.success("✅ API key saved!")

# Inisialisasi state
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "move_history" not in st.session_state:
    st.session_state.move_history = []
if "max_turns" not in st.session_state:
    st.session_state.max_turns = 10
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0

st.title("♟️ Gemini Chess AI Battle")

# Set maksimal giliran
max_turns = st.sidebar.number_input("🎯 Max Turns", 1, 200, st.session_state.max_turns)
st.session_state.max_turns = max_turns

# Fungsi bantu: tampilkan papan
def render_board_svg(board, last_move=None):
    svg_data = chess.svg.board(board=board, size=400,
                                arrows=[last_move] if last_move else [])
    components.html(svg_data, height=450)

# Fungsi bantu: dapatkan langkah dari Gemini (diperbaiki)
def get_move_from_gemini(board: chess.Board, role="white"):
    legal_moves = [move.uci() for move in board.legal_moves]
    prompt = f"""
You are a professional chess player playing as {role}.
The current board state in FEN is:
{board.fen()}

These are the legal moves:
{', '.join(legal_moves)}

Choose ONE move from this list and respond with ONLY the move in UCI format (e.g. e2e4).
Do not explain anything. Just respond with the move.
"""
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(prompt)
        move = response.text.strip().split()[0].lower()
        return move
    except Exception as e:
        return f"error:{str(e)}"

# Tombol mulai game
if st.button("🚀 Start Game"):
    st.session_state.board.reset()
    st.session_state.move_history = []
    st.session_state.turn_count = 0
    st.success("Game started!")

    while not st.session_state.board.is_game_over() and st.session_state.turn_count < st.session_state.max_turns:
        role = "white" if st.session_state.board.turn == chess.WHITE else "black"
        move_uci = get_move_from_gemini(st.session_state.board, role)

        if move_uci.startswith("error:"):
            st.error(move_uci)
            break

        try:
            move = chess.Move.from_uci(move_uci)
            if st.session_state.board.is_legal(move):
                st.session_state.board.push(move)
                last_move = (move.from_square, move.to_square)
                st.session_state.move_history.append((role.capitalize(), st.session_state.board.copy(), last_move))
                st.session_state.turn_count += 1
            else:
                st.warning(f"❌ Gemini suggested illegal move: {move_uci}")
                st.text(f"FEN: {st.session_state.board.fen()}")
                st.text(f"Legal Moves: {[m.uci() for m in st.session_state.board.legal_moves]}")
                break
        except Exception as e:
            st.error(f"❌ Failed to parse move: {move_uci}, error: {e}")
            break

    # Kondisi akhir
    if st.session_state.board.is_checkmate():
        winner = "Black" if st.session_state.board.turn == chess.WHITE else "White"
        st.success(f"🏁 Checkmate! {winner} wins.")
    elif st.session_state.board.is_stalemate():
        st.info("⚖️ Game ends in stalemate.")
    elif st.session_state.board.is_insufficient_material():
        st.info("⚖️ Draw due to insufficient material.")
    else:
        st.info("🔚 Max turns reached or unexpected ending.")

# Tombol reset
if st.button("🔄 Reset Game"):
    st.session_state.board.reset()
    st.session_state.move_history = []
    st.session_state.turn_count = 0
    st.success("Game reset!")

# Tampilkan riwayat
if st.session_state.move_history:
    st.subheader("📜 Move History")
    for i, (player, board_snapshot, last_move) in enumerate(st.session_state.move_history):
        st.markdown(f"**Turn {i + 1} - {player}**")
        render_board_svg(board_snapshot, last_move)
