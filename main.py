import streamlit as st
import hashlib
import base64

# Simple XOR encryption using passkey-derived key
def xor_encrypt_decrypt(text, passkey):
    # Create a key from hashed passkey
    key = hashlib.sha256(passkey.encode()).digest()
    text_bytes = text.encode()
    result = bytes([b ^ key[i % len(key)] for i, b in enumerate(text_bytes)])
    return base64.urlsafe_b64encode(result).decode()

def xor_decrypt(encrypted_text, passkey):
    try:
        key = hashlib.sha256(passkey.encode()).digest()
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode())
        result = bytes([b ^ key[i % len(key)] for i, b in enumerate(encrypted_bytes)])
        return result.decode()
    except:
        return None

# Hash passkey for verification
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

# Session state setup
if "stored_data" not in st.session_state:
    st.session_state.stored_data = {}

if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

# Streamlit UI
st.title("🔐 Secure Data Encryption System (No Cryptography)")

pages = ["Home", "Store Data", "Retrieve Data", "Login"]
current_page = st.sidebar.selectbox("Go to", pages)

if current_page == "Home":
    st.subheader("🏠 Hello there!")
    st.write("This app lets you encrypt sensitive text and retrieve it later with a unique passkey.")
    st.info("⚠️ Uses simple XOR encryption — not for real-world secrets.")

elif current_page == "Store Data":
    st.subheader("📥 Store Something Secret")
    user_input = st.text_area("Type the text you want to protect:")
    passkey = st.text_input("Choose a secret passkey:", type="password")

    if st.button("Encrypt & Save"):
        if user_input and passkey:
            encrypted = xor_encrypt_decrypt(user_input, passkey)
            hashed_key = hash_passkey(passkey)

            st.session_state.stored_data[encrypted] = {
                "encrypted_text": encrypted,
                "passkey": hashed_key
            }

            st.success("Done! Your data is now encrypted and safe.")
            st.code(encrypted, language="text")
            st.caption("Copy this encrypted string — you’ll need it later to decrypt.")
        else:
            st.warning("You left something blank. Both fields are required.")

elif current_page == "Retrieve Data":
    if st.session_state.failed_attempts >= 3:
        st.warning("😬 Too many incorrect attempts. You'll need to reauthorize first.")
        st.stop()

    st.subheader("🔎 Retrieve Your Secret")
    encrypted_input = st.text_area("Paste your encrypted string here:")
    passkey = st.text_input("Enter the original passkey:", type="password")

    if st.button("Decrypt"):
        if encrypted_input and passkey:
            hashed = hash_passkey(passkey)
            record = st.session_state.stored_data.get(encrypted_input)

            if record and record["passkey"] == hashed:
                decrypted = xor_decrypt(encrypted_input, passkey)
                if decrypted:
                    st.success("🎉 Success! Here's your original text:")
                    st.text_area("Decrypted Text", decrypted, height=100)
                    st.session_state.failed_attempts = 0
                else:
                    st.error("Decryption failed. Is the string or passkey incorrect?")
            else:
                st.session_state.failed_attempts += 1
                remaining = 3 - st.session_state.failed_attempts
                st.error(f"Oops! That passkey doesn’t match. You have {remaining} tries left.")
        else:
            st.warning("Both fields are needed to decrypt properly.")

elif current_page == "Login":
    st.subheader("🔑 Login to Try Again")
    login_input = st.text_input("Master Password:", type="password")

    if st.button("Login"):
        if login_input == "admin123":
            st.session_state.failed_attempts = 0
            st.success("Back in! Try retrieving your data again.")
            st.stop()
        else:
            st.error("Nope, that wasn’t it.")
