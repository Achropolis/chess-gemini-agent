import streamlit as st
import chess
import chess.svg
import google.generativeai as genai

# Configure Gemini API
st.sidebar.title("🔐 Gemini API Configuration")
api_key = st.sidebar.text_input("Enter your Gemini API key:", type="password")
if api_key:
    genai.configure(api_key=api_key)
    st.sidebar.success("✅ API key saved!")

# Initialize chess board
if "board" not in st.session_state:
    st.session_state.board = chess.Board()

st.title("♟️ Chess Move Suggestion with Gemini")

# Function to render the chess board
def render_chess_board(board):
    svg_data = chess.svg.board(board=board, size=400)
    st.components.v1.html(svg_data, height=450)

# Function to get move from Gemini
def get_move_from_gemini(board: chess.Board):
    legal_moves = [move.uci() for move in board.legal_moves]
    prompt = f"""
You are a professional chess player.
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

# Input for user move
user_move = st.text_input("Enter your move (in UCI format, e.g., e2e4):")

if user_move:
    try:
        move = chess.Move.from_uci(user_move)
        if st.session_state.board.is_legal(move):
            st.session_state.board.push(move)
        else:
            st.warning(f"❌ Illegal move: {user_move}")
    except Exception as e:
        st.error(f"❌ Failed to parse move: {user_move}, error: {e}")

# Render the current board
render_chess_board(st.session_state.board)

# Get move suggestion from Gemini
if st.button("Get Best Move from Gemini"):
    move_uci = get_move_from_gemini(st.session_state.board)
    if move_uci.startswith("error:"):
        st.error(move_uci)
    else:
        try:
            move = chess.Move.from_uci(move_uci)
            if st.session_state.board.is_legal(move):
                st.session_state.board.push(move)
                st.success(f"Gemini suggests move: **{move_uci}**")
            else:
                st.warning(f"❌ Gemini suggested illegal move: {move_uci}")
        except Exception as e:
            st.error(f"❌ Failed to parse Gemini's move: {move_uci}, error: {e}")

# Reset button
if st.button("🔄 Reset Game"):
    st.session_state.board.reset()
    st.success("Game reset!")

st.markdown("---")
st.markdown(
    "<p style='font-size:12px; color:#666;'>Developed with Streamlit and Gemini API.</p>",
    unsafe_allow_html=True,
)
